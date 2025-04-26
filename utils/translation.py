import json
import os
from googletrans import Translator

from utils.subtitles import convert_num_to_words

class GoogleTranslator:
    def __init__(self, config):
        self.config = config
        self.translator = Translator()
        
    def translate(self, subtitles):
        """Translate subtitles using Google Translate"""
        translated_subtitles = []
        
        for subtitle in subtitles:
            orig_text = convert_num_to_words(subtitle['text'])
            translated_text = self.translator.translate(orig_text, dest=self.config.target_language).text
            translated_subtitles.append({
                'index': subtitle['index'],
                'start': subtitle['start'],
                'end': subtitle['end'],
                'text': translated_text,
                'orig_text': orig_text,
            })
        
        # Save translations
        output_file = os.path.join(self.config.translations_path, f"google_{self.config.target_language}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_subtitles, f, ensure_ascii=False, indent=2)
            
        return translated_subtitles

def get_translator(service_name, config):
    """Factory function to get translator based on service name"""
    if service_name == "google":
        return GoogleTranslator(config)
    # Add more translation services here as they're implemented
    else:
        raise ValueError(f"Unknown translation service: {service_name}")