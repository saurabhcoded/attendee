from flask import Flask, Response, request
import subprocess

app = Flask(__name__)
current_source = 'black'

def generate_black_video():
    command = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'color=c=red:s=1280x720:r=30',
        '-f', 'lavfi',
        '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-shortest',
        '-c:v', 'libvpx-vp9',
        '-b:v', '1M',
        '-c:a', 'libopus',
        '-f', 'webm',
        'pipe:1'
    ]
    return command

def generate_webm_file(path):
    command = [
        'ffmpeg',
        '-re',
        '-i', path,
        '-c:v', 'libvpx-vp9',
        '-deadline', 'realtime',
        '-cpu-used', '4',
        '-b:v', '800k',
        '-bufsize', '1600k',
        '-c:a', 'libopus',
        '-b:a', '128k',
        '-f', 'webm',
        '-flush_packets', '1',
        'pipe:1'
    ]
    return command

@app.route('/video.webm')
def video():
    def generate_ffmpeg_output(cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
        try:
            while True:
                chunk = process.stdout.read(1024*16)
                if not chunk:
                    break
                yield chunk
        finally:
            process.kill()
            process.stdout.close()
            process.stderr.close()

    #if current_source == 'black':
    #    ffmpeg_cmd = generate_black_video()
    #else:
    #    ffmpeg_cmd = generate_webm_file(current_source)
    ffmpeg_cmd = generate_webm_file("/home/nduncan/Downloads/testfudge.webm")

    return Response(
        generate_ffmpeg_output(ffmpeg_cmd),
        mimetype='video/webm',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Connection': 'keep-alive',
            'Content-Type': 'video/webm',
            'Access-Control-Allow-Origin': '*',
            'Expires': '0',
            'Pragma': 'no-cache'
        }
    )

@app.route('/switch/<source>')
def switch_source(source):
    global current_source
    if source == 'black':
        current_source = 'black'
    else:
        current_source = f'/path/to/{source}.webm'
    return f"Switched source to {current_source}"

if __name__ == '__main__':
    app.run(port=5005, debug=True)