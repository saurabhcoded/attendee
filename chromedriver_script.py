import asyncio
import os
import subprocess
import click
import datetime
import requests
import json
import threading

from time import sleep

import undetected_chromedriver as uc

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import websockets
from websockets.sync.server import serve
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def handle_websocket(websocket):
    try:
        for message in websocket:
            print("received via websocket:", message)
            # You can add message handling logic here
            # websocket.send("response") # Example of sending a response
    except Exception as e:
        print(f"Websocket error: {e}")

def run_websocket_server():
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    with serve(handle_websocket, "localhost", 8765) as server:
        print("Websocket server started on ws://localhost:8765")
        server.serve_forever()

async def join_meet():
    # Start websocket server in a separate thread
    websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
    websocket_thread.start()
    
    meet_link = os.getenv("GMEET_LINK", "https://meet.google.com/mvp-pmnh-mfk")
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
        'https://cdnjs.cloudflare.com/ajax/libs/protobufjs/7.4.0/protobuf.min.js',
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


    print("Waiting for captions button...")
    captions_button = WebDriverWait(driver, 600).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Turn on captions"]'))
    )
    print("Clicking captions button...")
    captions_button.click()

    print("- End of work")
    sleep(10000)


if __name__ == "__main__":
    click.echo("starting google meet recorder...")
    asyncio.run(join_meet())
    click.echo("finished recording google meet.")