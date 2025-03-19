import logging
import subprocess
import threading

logger = logging.getLogger(__name__)


class RTMPClient:
    def __init__(self, rtmp_url):
        """
        Initialize the RTMP client for streaming FLV data to an RTMP endpoint.

        Args:
            rtmp_url (str): The RTMP endpoint URL
        """
        self.rtmp_url = rtmp_url
        self.ffmpeg_process = None
        self.is_running = False
        self.stderr_thread = None

    def _log_stderr(self):
        """Read and log FFmpeg's stderr output"""
        while self.is_running and self.ffmpeg_process:
            try:
                line = self.ffmpeg_process.stderr.readline().decode('utf-8', errors='replace')
                if not line:
                    break
                logger.info(f"FFmpeg: {line.strip()}")
            except Exception as e:
                logger.error(f"Error reading FFmpeg stderr: {e}")
                break

    def start(self):
        """Start the RTMP streaming process"""
        if self.is_running:
            return False

        # Configure FFmpeg command with transcoding for FLV compatibility
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # Overwrite output if needed
            "-f", "webm",  # Input format is WebM
            "-i", "pipe:0",  # Read from stdin
            "-c:v", "libx264",  # Transcode video to H.264 (FLV compatible)
            "-preset", "veryfast",  # Use fast encoding preset for lower latency
            "-tune", "zerolatency",  # Optimize for streaming
            "-profile:v", "baseline",  # Use baseline profile for compatibility
            "-pix_fmt", "yuv420p",  # Standard pixel format
            "-r", "30",  # 30fps output
            "-g", "60",  # Keyframe every 2 seconds (30fps*2)
            "-c:a", "aac",  # Transcode audio to AAC (FLV compatible)
            "-b:a", "128k",  # Audio bitrate
            "-ar", "44100",  # Audio sample rate
            "-f", "flv",  # Output format
            self.rtmp_url,  # RTMP destination
        ]

        # Start FFmpeg process
        try:
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8,
            )
            self.is_running = True
            
            # Start a thread to read stderr output
            self.stderr_thread = threading.Thread(target=self._log_stderr)
            self.stderr_thread.daemon = True
            self.stderr_thread.start()
            
            logger.info(f"FFmpeg RTMP client started with PID {self.ffmpeg_process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start FFmpeg process: {e}")
            return False

    def write_data(self, flv_data):
        """
        Write WebM data to the RTMP stream.

        Args:
            flv_data (bytes): WebM formatted data containing audio and video

        Returns:
            bool: True if data was written, False if failed
        """
        if not self.is_running or not self.ffmpeg_process:
            return False

        logger.info(f"Writing data to FFmpeg: {len(flv_data)} bytes")

        try:
            self.ffmpeg_process.stdin.write(flv_data)
            self.ffmpeg_process.stdin.flush()
            
            # Check if process is still alive
            if self.ffmpeg_process.poll() is not None:
                logger.error(f"FFmpeg process exited with code {self.ffmpeg_process.returncode}")
                self.is_running = False
                return False
                
            return True
        except BrokenPipeError:
            logger.error("FFmpeg pipe broken - stream may have failed")
            self.is_running = False
            return False
        except Exception as e:
            logger.error(f"Error writing data to FFmpeg: {e}")
            self.is_running = False
            return False

    def stop(self):
        """Stop the RTMP streaming process"""
        self.is_running = False

        if self.ffmpeg_process:
            try:
                # Send EOF to stdin
                self.ffmpeg_process.stdin.close()
                
                # Wait for process to terminate
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5.0)
            except Exception as e:
                logger.error(f"Error stopping FFmpeg process: {e}")
                # Force kill if graceful shutdown fails
                try:
                    self.ffmpeg_process.kill()
                except Exception:
                    pass

            self.ffmpeg_process = None
            
            # Wait for stderr thread to finish
            if self.stderr_thread and self.stderr_thread.is_alive():
                self.stderr_thread.join(timeout=2.0)
