from utils.video import extract_audio, separate_audio
from processors.base import Processor

class AudioExtractor(Processor):
    def process(self, data=None):
        """Extract and separate audio from video"""
        original_audio = extract_audio(self.config)
        voice_file, bg_file = separate_audio(self.config)
        
        return {
            "original_audio": original_audio,
            "voice_file": voice_file,
            "bg_file": bg_file
        }