import asyncio
import os
import subprocess
import click
import datetime
import requests
import json
import threading
import wave
import numpy as np
import cv2

import time
from time import sleep

import undetected_chromedriver as uc
from pyvirtualdisplay import Display

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import websockets
from websockets.sync.server import serve
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bots.bot_adapter import BotAdapter


def scale_i420(frame, frame_size, new_size):
    new_width, new_height = new_size
    orig_width, orig_height = frame_size

    # Calculate plane sizes
    y_plane_size = orig_width * orig_height
    uv_plane_size = (orig_width // 2) * (orig_height // 2)

    # Extract Y, U, V planes directly from the byte array
    y = np.frombuffer(frame[0:y_plane_size], dtype=np.uint8)
    u = np.frombuffer(frame[y_plane_size:y_plane_size + uv_plane_size], dtype=np.uint8)
    v = np.frombuffer(frame[y_plane_size + uv_plane_size:], dtype=np.uint8)

    # Reshape planes
    y = y.reshape(orig_height, orig_width)
    u = u.reshape(orig_height//2, orig_width//2)
    v = v.reshape(orig_height//2, orig_width//2)

    # 2) Determine scale preserving aspect ratio
    input_aspect = orig_width / orig_height
    output_aspect = new_width / new_height

    if abs(input_aspect - output_aspect) < 1e-6:
        # Aspect ratios match (or extremely close). Just do a simple stretch to (new_width, new_height).
        scaled_y = cv2.resize(y, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        scaled_u = cv2.resize(u, (new_width//2, new_height//2), interpolation=cv2.INTER_LINEAR)
        scaled_v = cv2.resize(v, (new_width//2, new_height//2), interpolation=cv2.INTER_LINEAR)

        # Flatten and return
        return np.concatenate([
            scaled_y.flatten(),
            scaled_u.flatten(),
            scaled_v.flatten()
        ]).astype(np.uint8).tobytes()

    # Otherwise, the aspect ratios differ => letterbox or pillarbox
    # 3) Compute scaled dimensions that fit entirely within (new_width, new_height)
    if input_aspect > output_aspect:
        # The image is relatively wider => match width, shrink height
        scaled_width = new_width
        scaled_height = int(round(new_width / input_aspect))
    else:
        # The image is relatively taller => match height, shrink width
        scaled_height = new_height
        scaled_width = int(round(new_height * input_aspect))

    # 4) Resize Y, U, and V to the scaled dimensions
    scaled_y = cv2.resize(y, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)
    scaled_u = cv2.resize(u, (scaled_width//2, scaled_height//2), interpolation=cv2.INTER_LINEAR)
    scaled_v = cv2.resize(v, (scaled_width//2, scaled_height//2), interpolation=cv2.INTER_LINEAR)

    # 5) Create the black background only if needed
    # For I420, black is typically (Y=0, U=128, V=128) or (Y=16, U=128, V=128).
    # We'll use Y=0, U=128, V=128 for "dark" black.
    final_y = np.zeros((new_height, new_width), dtype=np.uint8)
    final_u = np.full((new_height//2, new_width//2), 128, dtype=np.uint8)
    final_v = np.full((new_height//2, new_width//2), 128, dtype=np.uint8)

    # 6) Compute centering offsets for each plane
    # For Y-plane
    offset_y = (new_height - scaled_height) // 2
    offset_x = (new_width - scaled_width) // 2

    # Insert Y
    final_y[offset_y:offset_y+scaled_height, offset_x:offset_x+scaled_width] = scaled_y

    # For U, V planes (subsampled by 2 in each dimension)
    offset_y_uv = offset_y // 2
    offset_x_uv = offset_x // 2

    final_u[offset_y_uv:offset_y_uv+(scaled_height//2),
            offset_x_uv:offset_x_uv+(scaled_width//2)] = scaled_u
    final_v[offset_y_uv:offset_y_uv+(scaled_height//2),
            offset_x_uv:offset_x_uv+(scaled_width//2)] = scaled_v

    # 7) Flatten back to I420 layout and return bytes
    return np.concatenate([
        final_y.flatten(),
        final_u.flatten(),
        final_v.flatten()
    ]).astype(np.uint8).tobytes()

class GoogleMeetBotAdapter(BotAdapter):

    def __init__(self, *, display_name, send_message_callback, meeting_url, add_video_frame_callback, wants_any_video_frames_callback, add_mixed_audio_chunk_callback):
        self.display_name = display_name
        self.send_message_callback = send_message_callback
        self.add_mixed_audio_chunk_callback = add_mixed_audio_chunk_callback
        self.add_video_frame_callback = add_video_frame_callback
        self.wants_any_video_frames_callback = wants_any_video_frames_callback

        self.meeting_url = meeting_url

        self.video_frame_size = (1920, 1080)

        self.driver = None

        self.send_frames = True

        self.left_meeting = False

        self.websocket_port = None
        self.websocket_server = None
        self.websocket_thread = None
        self.last_websocket_message_processed_time = None

    def handle_websocket(self, websocket):
        audio_file = None
        audio_format = None
        frame_counter = 0  # Add frame counter
        output_dir = 'frames'  # Add output directory
        
        # Create frames directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        try:
            for message in websocket:
                # Get first 4 bytes as message type
                message_type = int.from_bytes(message[:4], byteorder='little')
                
                if message_type == 1:  # JSON
                    json_data = json.loads(message[4:].decode('utf-8'))
                    print("Received JSON message:", json_data)
                    
                    # Handle audio format information
                    if isinstance(json_data, dict):
                        if json_data.get('type') == 'AudioFormatUpdate':
                            audio_format = json_data['format']
                            # Create a new WAV file
                            audio_file = wave.open('recorded_audio.wav', 'wb')
                            audio_file.setnchannels(audio_format['numberOfChannels'])
                            audio_file.setsampwidth(4)  # 4 bytes for float32
                            audio_file.setframerate(audio_format['sampleRate']/2)
                        
                elif message_type == 2:  # VIDEO
                    if len(message) > 24:  # Minimum length check
                        # Bytes 4-12 contain the timestamp
                        timestamp = int.from_bytes(message[4:12], byteorder='little')

                        # Get stream ID length and string
                        stream_id_length = int.from_bytes(message[12:16], byteorder='little')
                        stream_id = message[16:16+stream_id_length].decode('utf-8')

                        # Get width and height after stream ID
                        offset = 16 + stream_id_length
                        width = int.from_bytes(message[offset:offset+4], byteorder='little')
                        height = int.from_bytes(message[offset+4:offset+8], byteorder='little')
                        #print("video dimensions", width, height)
                    
                        # Convert I420 format to BGR for OpenCV
                        video_data = np.frombuffer(message[offset+8:], dtype=np.uint8)
                        
                        scaled_i420_frame = scale_i420(video_data, (width, height), (1920, 1080))
                        if self.wants_any_video_frames_callback() and self.send_frames:                
                            self.add_video_frame_callback(scaled_i420_frame, timestamp * 1000)
                        
                elif message_type == 3:  # AUDIO
                    if audio_file is not None and len(message) > 12:
                        # Bytes 4-12 contain the timestamp
                        timestamp = int.from_bytes(message[4:12], byteorder='little')
                        # Convert the float32 audio data to int16 for WAV file
                        audio_data = np.frombuffer(message[12:], dtype=np.float32)

                        if self.wants_any_video_frames_callback() and self.send_frames:  
                            self.add_mixed_audio_chunk_callback(audio_data.tobytes(), timestamp * 1000)
                    
                self.last_websocket_message_processed_time = time.time()
        except Exception as e:
            print(f"Websocket error: {e}")


    def run_websocket_server(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        port = 8765
        max_retries = 10
        
        for attempt in range(max_retries):
            try:
                self.websocket_server = serve(self.handle_websocket, 
                                           "localhost", 
                                           port,
                                           compression=None,
                                           max_size=None)
                print(f"Websocket server started on ws://localhost:{port}")
                self.websocket_port = port
                self.websocket_server.serve_forever()
                break
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    print(f"Port {port} is already in use, trying next port...")
                    port += 1
                    if attempt == max_retries - 1:
                        raise Exception(f"Could not find available port after {max_retries} attempts")
                    continue
                raise  # Re-raise other OSErrors

    def init(self):
        if os.environ.get('DISPLAY') is None:
            # Create virtual display only if no real display is available
            display = Display(visible=0, size=(1920, 1080))
            display.start()
        
        # Start websocket server in a separate thread
        websocket_thread = threading.Thread(target=self.run_websocket_server, daemon=True)
        websocket_thread.start()
        
        sleep(0.5)  # Give the websocketserver time to start
        if not self.websocket_port:
            raise Exception("WebSocket server failed to start")

        meet_link = self.meeting_url
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

        self.driver = uc.Chrome(service_log_path=log_path, use_subprocess=True, options=options)

        self.driver.set_window_size(1920, 1080)

        initial_data_code = f"window.initialData = {{websocketPort: {self.websocket_port}}}"

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
        
        # Get directory of current file
        current_dir = os.path.dirname(os.path.abspath(__file__))        
        # Read your payload using path relative to current file
        with open(os.path.join(current_dir, 'chromedriver_payload.js'), 'r') as file:
            payload_code = file.read()
        
        # Combine them ensuring libraries load first
        combined_code = f"""
            {initial_data_code}
            {libraries_code}
            {payload_code}
        """
        
        # Add the combined script to execute on new document
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': combined_code
        })

        self.driver.get(meet_link)

        self.driver.execute_cdp_cmd(
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
        name_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="text"][aria-label="Your name"]')
        
        print("Waiting for 1 second...")
        sleep(1)
        
        print("Filling the input field with the name...")
        full_name = "Mr Bot!"
        name_input.send_keys(full_name)
        
        print("Waiting for the 'Ask to join' button...")
        join_button = self.driver.find_element(By.XPATH, '//button[.//span[text()="Ask to join"]]')
        
        print("Clicking the 'Ask to join' button...")
        join_button.click()


        print("Waiting for captions button...")
        captions_button = WebDriverWait(self.driver, 600).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Turn on captions"]'))
        )
        print("Clicking captions button...")
        captions_button.click()

        print("Waiting for the more options button...")
        MORE_OPTIONS_BUTTON_SELECTOR = 'button[jsname="NakZHc"][aria-label="More options"]'
        more_options_button = WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, MORE_OPTIONS_BUTTON_SELECTOR))
        )
        print("Clicking the more options button...")
        more_options_button.click()

        print("Waiting for the 'Change layout' list item...")
        change_layout_list_item = WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, '//li[.//span[text()="Change layout"]]'))
        )
        print("Clicking the 'Change layout' list item...")
        change_layout_list_item.click()

        print("Waiting for the 'Spotlight' label element")
        spotlight_label = WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, '//label[.//span[text()="Spotlight"]]'))
        )
        print("Clicking the 'Spotlight' label element")
        spotlight_label.click()
        
        print("Waiting for the close button")
        close_button = WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Close"]'))
        )
        print("Clicking the close button")
        close_button.click()

        self.send_message_callback({'message': self.Messages.BOT_JOINED_MEETING})
        self.send_message_callback({'message': self.Messages.BOT_RECORDING_PERMISSION_GRANTED})

        self.send_frames = True
        self.driver.execute_script("window.ws.enableMediaSending();")
        
    def leave(self):
        if self.left_meeting:
            return

        try:
            print("disable media sending")
            self.driver.execute_script("window.ws.disableMediaSending();")
            
            print("Waiting for the leave button")
            leave_button = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[jsname="CQylAd"][aria-label="Leave call"]'))
            )
            print("Clicking the leave button")
            leave_button.click()
        except Exception as e:
            print(f"Error during leave: {e}")
        finally:
            self.send_message_callback({'message': self.Messages.MEETING_ENDED})
            self.left_meeting = True

    def cleanup(self):
        try:
            print("disable media sending")
            self.driver.execute_script("window.ws.disableMediaSending();")
        except Exception as e:
            print(f"Error during media sending disable: {e}")

        # Wait for websocket buffers to be processed
        if self.last_websocket_message_processed_time:
            while time.time() - self.last_websocket_message_processed_time < 2:
                print(f"Waiting until it's 2 seconds since last websockets message was processed. Currently it is {time.time() - self.last_websocket_message_processed_time} seconds")
                sleep(0.5)

        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")

        # Properly shutdown the websocket server
        if self.websocket_server:
            try:
                self.websocket_server.shutdown()
            except Exception as e:
                print(f"Error shutting down websocket server: {e}")