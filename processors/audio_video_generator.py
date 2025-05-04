from utils.audio import create_adjusted_audio_video
from processors.base import Processor

class AudioVideoGenerator(Processor):
    def process(self, data=None):
        """Generate final video with translated audio"""
        speech_files = data.get("speech_files", [])
        if not speech_files:
            print("No speech files provided for video generation")
            return {"output_video": None}
        
        # Create adjusted audio video
        output_video = create_adjusted_audio_video(self.config, speech_files)
        
        return {"output_video": output_video}