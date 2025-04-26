from utils.translation import get_translator
from processors.base import Processor

class TranslationProcessor(Processor):
    def process(self, data=None):
        """Translate subtitles"""
        subtitles = data.get("subtitles", [])
        if not subtitles:
            print("No subtitles provided for translation")
            return {"translated_subtitles": []}
        
        # Get translator based on config
        translation_service = self.config.default_translation
        translator = get_translator(translation_service, self.config)
        
        # Translate subtitles
        translated_subtitles = translator.translate(subtitles)
        
        # Save output
        self.save_output(translated_subtitles, f"{translation_service}_translated.json")
        
        return {"translated_subtitles": translated_subtitles}