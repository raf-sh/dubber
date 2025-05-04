from utils.tts import get_tts_system
from processors.base import Processor

class TTSProcessor(Processor):
    def process(self, data=None):
        """Generate speech from translated subtitles"""
        translated_subtitles = data.get("translated_subtitles", [])
        if not translated_subtitles:
            print("No translated subtitles provided for TTS")
            return {"speech_files": []}
        
        # Get TTS system based on config
        tts_system_name = self.config.default_tts
        tts_system = get_tts_system(tts_system_name, self.config)
        
        # Generate speech
        speech_files = tts_system.generate(translated_subtitles)
        
        # Save output
        self.save_output(speech_files, f"{tts_system_name}_speech_files.json")
        self.save_output(speech_files, f"output.json")
        
        return {"speech_files": speech_files}