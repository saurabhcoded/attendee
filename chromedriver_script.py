import asyncio
import os
import subprocess
import click
import datetime
import requests
import json

from time import sleep

import undetected_chromedriver as uc

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

async def join_meet():
    meet_link = os.getenv("GMEET_LINK", "https://meet.google.com/ijm-gzad-mie")
    print(f"start recorder for {meet_link}")

    options = uc.ChromeOptions()

    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    # options.add_argument('--headless=new')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    log_path = "chromedriver.log"

    driver = uc.Chrome(service_log_path=log_path, use_subprocess=False, options=options)

    driver.set_window_size(1920, 1080)

    # Define the CDN libraries needed
    CDN_LIBRARIES = [
        'https://cdnjs.cloudflare.com/ajax/libs/protobufjs/7.4.0/light/protobuf.min.js',
    ]

    # Download all library code
    libraries_code = ""
    for url in CDN_LIBRARIES:
        response = requests.get(url)
        if response.status_code == 200:
            libraries_code += response.text + "\n"
        else:
            raise Exception(f"Failed to download library from {url}")
    
    # Read your payload
    with open('chromedriver_payload.js', 'r') as file:
        payload_code = file.read()
    
    # Combine them ensuring libraries load first
    combined_code = f"""
        {libraries_code}
        {payload_code}
    """
    
    # Add the combined script to execute on new document
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': combined_code
    })

    driver.get(meet_link)

    driver.execute_cdp_cmd(
        "Browser.grantPermissions",
        {
            "origin": meet_link,
            "permissions": [
                "geolocation",
                "audioCapture",
                "displayCapture",
                "videoCapture",
                "videoCapturePanTiltZoom",
            ],
        },
    )

    print("Waiting for the name input field...")
    name_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][aria-label="Your name"]')
    
    print("Waiting for 1 second...")
    sleep(1)
    
    print("Filling the input field with the name...")
    full_name = "Mr Bot!"
    name_input.send_keys(full_name)
    
    print("Waiting for the 'Ask to join' button...")
    join_button = driver.find_element(By.XPATH, '//button[.//span[text()="Ask to join"]]')
    
    print("Clicking the 'Ask to join' button...")
    join_button.click()

    print("- End of work")
    sleep(10000)


if __name__ == "__main__":
    click.echo("starting google meet recorder...")
    asyncio.run(join_meet())
    click.echo("finished recording google meet.")