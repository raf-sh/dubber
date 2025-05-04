import os
import json
import torch
import torchaudio

class SileroTTS:
    def __init__(self, config):
        self.config = config
        # Load model only when needed
        self.model = None
        self.sample_rate = config.sample_rate
        
    def _load_model(self):
        """Load Silero TTS model if not already loaded"""
        if self.model is None:
            tts_lang = self.config.language_tts_map.get(self.config.target_language, self.config.target_language)
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language=tts_lang,
                speaker=f'v3_{tts_lang}'
            )
            self.model.to(torch.device('cpu'))
    
    def generate(self, translated_subtitles):
        """Generate speech for translated subtitles"""
        try:
            self._load_model()
            speech_files = []
            
            speaker = self.config.speaker_map.get(self.config.target_language, 'random')
            
            for subtitle in translated_subtitles:
                gen_audio_path = os.path.join(self.config.tts_path, f"speech_{subtitle['index']}.wav")
                try:
                    audio = self.model.apply_tts(
                        text=subtitle['text'], 
                        sample_rate=self.sample_rate, 
                        speaker=speaker, 
                        put_accent=True, 
                        put_yo=True
                    )
                    # torchaudio.save(gen_audio_path, audio.unsqueeze(0), self.sample_rate, backend="ffmpeg")
                    torchaudio.save(gen_audio_path, audio.unsqueeze(0), self.sample_rate)
                    speech_files.append({
                        'file': gen_audio_path,
                        'start': subtitle['start'],
                        'end': subtitle['end'],
                        'text': subtitle['text'],
                        'orig_text': subtitle['orig_text'],
                    })
                except Exception as e:
                    print(f"Error generating speech for subtitle {subtitle['index']}: {e}")
            
            # Save speech file metadata
            output_meta = os.path.join(self.config.tts_path, f"silero_{self.config.target_language}_metadata.json")
            with open(output_meta, 'w', encoding='utf-8') as f:
                json.dump(speech_files, f, ensure_ascii=False, indent=2)
                
            return speech_files
        except Exception as e:
            print(f"Error loading TTS model for language '{self.config.target_language}': {e}")
            return []

def get_tts_system(system_name, config):
    """Factory function to get TTS system based on name"""
    if system_name == "silero":
        return SileroTTS(config)
    # Add more TTS systems here as they're implemented
    else:
        raise ValueError(f"Unknown TTS system: {system_name}")
