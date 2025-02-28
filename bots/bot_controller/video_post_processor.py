import os
import subprocess
import logging
from pathlib import Path
import boto3

class VideoPostProcessor:
    def __init__(self, bucket):
        """Initialize with S3 bucket name."""
        self.s3_client = boto3.client('s3')
        self.bucket = bucket

    def process_video(self, key):
        """Download, process, and re-upload a video file."""
        try:
            # Create temp file paths
            input_path = Path('/tmp') / f'input_{Path(key).name}'
            output_path = Path('/tmp') / f'output_{Path(key).name}'

            # Download the file
            print(f"Downloading {key} from S3")
            self.s3_client.download_file(self.bucket, key, str(input_path))

            # Process with ffmpeg
            print(f"Processing {input_path}")
            self._move_moov_atom(input_path, output_path)

            # Upload processed file back to S3
            print(f"Uploading processed file back to S3")
            self.s3_client.upload_file(str(output_path), self.bucket, key)

            # Clean up temporary files
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)

            logging.info(f"Successfully processed {key}")
            return True

        except Exception as e:
            logging.error(f"Error processing video {key}: {str(e)}")
            # Clean up any temporary files that might exist
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            raise

    def _move_moov_atom(self, input_path, output_path):
        """Use ffmpeg to move the moov atom to the beginning of the file."""
        command = [
            'ffmpeg',
            '-i', str(input_path),
            '-movflags', '+faststart',
            '-c', 'copy',  # Copy without re-encoding
            str(output_path)
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
