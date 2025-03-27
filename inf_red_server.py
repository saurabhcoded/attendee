import io
import subprocess
import sys
import time
import shutil # To check for ffmpeg executable
from flask import Flask, Response, stream_with_context

app = Flask(__name__)
CHUNK_SIZE = 1024 * 10 # Read in 10KB chunks (adjust as needed)
RED_WEBM_SEGMENT_DATA = None # Global variable to hold the generated segment

def check_ffmpeg():
    """Checks if FFmpeg executable is available in PATH."""
    if shutil.which("ffmpeg") is None:
        print("ERROR: FFmpeg command not found.")
        print("Please install FFmpeg and ensure it's in your system's PATH.")
        print("Download from: https://ffmpeg.org/download.html")
        return False
    print("FFmpeg found.")
    return True

def generate_webm_segment_in_memory():
    """
    Calls FFmpeg to generate a short video segment with a changing pattern
    and captures its output directly into memory (bytes).
    """
    global RED_WEBM_SEGMENT_DATA
    print("Generating WebM segment in memory using FFmpeg...")

    # Try a simpler animated pattern that's more widely supported
    command = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=size=640x480:rate=30',  # Simple test pattern with color bars and motion
        '-t', '10.0',                           # 3 second duration
        '-c:v', 'libvpx-vp9',
        '-pix_fmt', 'yuv420p',
        '-an',                                 # No audio
        '-f', 'webm',
        '-'                                    # Output to stdout
    ]

    try:
        # Run FFmpeg, capture both stdout and stderr
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,            # Capture standard output
            stderr=subprocess.PIPE,            # Capture stderr for debugging
            check=True                         # Raise CalledProcessError if FFmpeg fails
        )
        RED_WEBM_SEGMENT_DATA = process.stdout
        if not RED_WEBM_SEGMENT_DATA:
            print("ERROR: FFmpeg generated empty output.")
            return False
        print(f"Successfully generated WebM segment in memory ({len(RED_WEBM_SEGMENT_DATA)} bytes).")
        return True
    except FileNotFoundError:
        print("ERROR: FFmpeg command not found during execution (should have been caught earlier).")
        return False
    except subprocess.CalledProcessError as e:
        print(f"ERROR: FFmpeg failed with exit code {e.returncode}")
        # Print the error output to help diagnose the issue
        print("FFmpeg error output:", e.stderr.decode())
        return False
    except Exception as e:
        print(f"An unexpected error occurred during FFmpeg execution: {e}")
        return False

def generate_video_stream():
    """
    Generator function that continuously yields chunks
    of the in-memory red video segment data.
    """
    print("Starting video stream generation from memory...")

    if not RED_WEBM_SEGMENT_DATA:
         print("Error: Video segment data not generated or empty.")
         yield b"Error: Video segment data missing or invalid on server."
         return # Stop the generator

    try:
        while True:
            # Create an in-memory file-like object from the segment data
            # This allows us to easily read it in chunks for each loop
            segment_stream = io.BytesIO(RED_WEBM_SEGMENT_DATA)
            while True:
                chunk = segment_stream.read(CHUNK_SIZE)
                if not chunk:
                    # End of the in-memory segment, break inner loop to restart
                    # print("Looping segment...") # Debugging
                    break
                # print(f"Yielding chunk of size {len(chunk)}") # Debugging
                yield chunk
                # Optional small delay to prevent overwhelming CPU,
                # but often not needed as network I/O provides backpressure.
                # time.sleep(0.001)
    except GeneratorExit:
        # This happens when the client disconnects
        print("Client disconnected.")
    except Exception as e:
        print(f"Error during streaming: {e}")
    finally:
        print("Video stream generation stopped.")


@app.route('/fakevid/video.webm')
def stream_fake_video():
    """
    Route to serve the infinitely streaming red video.
    """
    print(f"Request received for /fakevid/video.webm")
    if not RED_WEBM_SEGMENT_DATA:
        return "Error: Video segment data could not be generated.", 500

    # Use stream_with_context for efficient streaming
    response = Response(stream_with_context(generate_video_stream()), mimetype='video/webm')
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    # 1. Check if FFmpeg is available
    if not check_ffmpeg():
        sys.exit(1) # Exit if FFmpeg is not found

    # 2. Generate the segment into the global variable ONCE at startup
    if not generate_webm_segment_in_memory():
        print("Exiting due to failure in generating video segment.")
        sys.exit(1) # Exit if generation fails

    # 3. Start the Flask server
    print(f"Starting Flask server on http://localhost:5005")
    # Use debug=False for stable streaming
    # Use threaded=True to handle multiple potential viewers
    app.run(host='0.0.0.0', port=5005, debug=False, threaded=True)