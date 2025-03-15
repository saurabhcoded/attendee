import os
import subprocess
import logging
from pathlib import Path
import boto3

logger = logging.getLogger(__name__)

class VideoPostProcessor:
    def make_file_seekable(self, input_path, output_path):
        """Use ffmpeg to move the moov atom to the beginning of the file."""
        logger.info(f"Making file seekable: {input_path} -> {output_path}")
        # log how many bytes are in the file
        logger.info(f"File size: {os.path.getsize(input_path)} bytes")
        command = [
            'ffmpeg',
            '-i', str(input_path),
            '-c', 'copy',  # Copy without re-encoding
            '-movflags', '+faststart',
            '-y',  # Overwrite output file without asking
            str(output_path)
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")