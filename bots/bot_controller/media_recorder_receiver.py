import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class MediaRecorderReceiver:
    def __init__(self, file_location):
        self.file_location = file_location
        self.ffmpeg_proc = None
        self.screen_dimensions = (1920, 1080)

    def start_recording(self, display_var):
        logger.info(f"Starting screen recorder for display {display_var} with dimensions {self.screen_dimensions} and file location {self.file_location}")
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-thread_queue_size", "4096",
            "-framerate", "30",
            "-video_size", f"{self.screen_dimensions[0]}x{self.screen_dimensions[1]}",
            "-f", "x11grab",
            "-draw_mouse", "0",
            "-i", display_var,
            "-thread_queue_size", "4096",
            "-f", "pulse",
            "-i", "default",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-strict", "experimental",
            "-b:a", "128k",
            self.file_location
        ]
        
        logger.info(f"Starting FFmpeg command: {' '.join(ffmpeg_cmd)}")
        self.ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def stop_recording(self):
        if not self.ffmpeg_proc:
            return
        self.ffmpeg_proc.terminate()
        self.ffmpeg_proc.wait()
        logger.info(f"Stopped debug screen recorder for display with dimensions {self.screen_dimensions} and file location {self.file_location}")

    def cleanup(self):
        self.make_file_seekable()

    def get_seekable_path(self, path):
        """
        Transform a file path to include '.seekable' before the extension.
        Example: /tmp/file.webm -> /tmp/file.seekable.webm
        """
        base, ext = os.path.splitext(path)
        return f"{base}.seekable{ext}"

    def make_file_seekable(self):
        input_path = self.file_location
        output_path = self.get_seekable_path(self.file_location)

        # Check if input file exists
        if not os.path.exists(input_path):
            logger.info(f"Input file does not exist at {input_path}, creating empty file")
            with open(input_path, "wb"):
                pass  # Create empty file
            return

        """Use ffmpeg to move the moov atom to the beginning of the file."""
        logger.info(f"Making file seekable: {input_path} -> {output_path}")
        # log how many bytes are in the file
        logger.info(f"File size: {os.path.getsize(input_path)} bytes")
        command = [
            "ffmpeg",
            "-i",
            str(input_path),
            "-c",
            "copy",  # Copy without re-encoding
            "-movflags",
            "+faststart",
            "-y",  # Overwrite output file without asking
            str(output_path),
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        # Replace the original file with the seekable version
        try:
            os.replace(str(output_path), str(input_path))
            logger.info(f"Replaced original file with seekable version: {input_path}")
        except Exception as e:
            logger.error(f"Failed to replace original file with seekable version: {e}")
            raise RuntimeError(f"Failed to replace original file: {e}")
