import time
import threading
import queue
from .text_to_speech import generate_audio_from_text
from bots.utils import mp3_to_pcm

class AudioOutputManager:
    SAMPLE_RATE = 44100

    def __init__(self, currently_playing_audio_media_request_finished_callback, play_raw_audio_callback):
        self.currently_playing_audio_media_request = None
        self.currently_playing_audio_media_request_started_at = None
        self.currently_playing_audio_media_request_duration_ms = None
        self.currently_playing_audio_media_request_finished_callback = currently_playing_audio_media_request_finished_callback
        self.play_raw_audio_callback = play_raw_audio_callback
        self.currently_playing_audio_media_request_raw_audio_pcm_bytes = None
        self.audio_thread = None
        self.stop_audio_thread = False
        self.audio_queue = queue.Queue()
        self.playback_thread = None

    def _generate_audio_chunks(self):
        bytes_per_sample = 2
        chunk_for_adapter_size = self.SAMPLE_RATE * bytes_per_sample
        audio_media_request = self.currently_playing_audio_media_request
        accumulated_chunks_from_provider = b''
        for chunk_from_provider in generate_audio_from_text(
                text=audio_media_request.text_to_speak,
                settings=audio_media_request.text_to_speech_settings,
                sample_rate=self.SAMPLE_RATE,
                bot=audio_media_request.bot
        ):
            if self.stop_audio_thread:
                return
            print("chunk_from_provider", len(chunk_from_provider))
            accumulated_chunks_from_provider += chunk_from_provider
            if len(accumulated_chunks_from_provider) >= chunk_for_adapter_size:
                first_chunk = accumulated_chunks_from_provider[:chunk_for_adapter_size]
                self.audio_queue.put(first_chunk)
                accumulated_chunks_from_provider = accumulated_chunks_from_provider[chunk_for_adapter_size:]
        self.audio_queue.put(None)  # Signal end of chunks
        print('dunzo')

    def _play_audio_chunks(self):
        while not self.stop_audio_thread:
            chunk = self.audio_queue.get()
            if chunk is None:  # End of audio signal
                break
            print("playing chunk", len(chunk))
            self.play_raw_audio_callback(bytes=chunk, sample_rate=self.SAMPLE_RATE)
            time.sleep(0.9)  # Sleep only in playback thread
        
        self.currently_playing_audio_media_request_duration_ms = 10

    def _stop_audio_thread(self):
        """Stop the currently running audio thread if it exists."""
        self.stop_audio_thread = True
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join()
        self.stop_audio_thread = False
        # Clear any remaining items in queue
        while not self.audio_queue.empty():
            self.audio_queue.get()

    def start_playing_audio_media_request(self, audio_media_request):
        # Stop any existing audio playback
        self._stop_audio_thread()

        if audio_media_request.media_blob:
            # Handle raw audio blob case
            self.currently_playing_audio_media_request_raw_audio_pcm_bytes = mp3_to_pcm(audio_media_request.media_blob.blob, sample_rate=self.SAMPLE_RATE)
            self.currently_playing_audio_media_request_duration_ms = audio_media_request.media_blob.duration_ms
        else:
            # Handle text-to-speech case
            self.currently_playing_audio_media_request_duration_ms = 10000000

        self.currently_playing_audio_media_request = audio_media_request
        self.currently_playing_audio_media_request_started_at = time.time()
        
        # Start generator thread
        self.audio_thread = threading.Thread(target=self._generate_audio_chunks)
        self.audio_thread.start()
        
        # Start playback thread
        self.playback_thread = threading.Thread(target=self._play_audio_chunks)
        self.playback_thread.start()

    def currently_playing_audio_media_request_is_finished(self):
        if not self.currently_playing_audio_media_request or not self.currently_playing_audio_media_request_started_at:
            return False
        elapsed_ms = (time.time() - self.currently_playing_audio_media_request_started_at) * 1000
        if elapsed_ms > self.currently_playing_audio_media_request_duration_ms:
            return True
        return False
    
    def clear_currently_playing_audio_media_request(self):
        self._stop_audio_thread()
        self.currently_playing_audio_media_request = None
        self.currently_playing_audio_media_request_started_at = None

    def monitor_currently_playing_audio_media_request(self):
        if self.currently_playing_audio_media_request_is_finished():
            temp_currently_playing_audio_media_request = self.currently_playing_audio_media_request
            self.clear_currently_playing_audio_media_request()
            self.currently_playing_audio_media_request_finished_callback(temp_currently_playing_audio_media_request)
