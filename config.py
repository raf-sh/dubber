import os

class Config:
    def __init__(self, youtube_url=None, target_language="tt", work_dir="downloads"):
        self.youtube_url = youtube_url
        self.target_language = target_language
        self.work_dir = work_dir
        
        # Language mapping for TTS systems
        self.language_tts_map = {
            "tt": "tt",  # Tatar
            "es": "es",  # Spanish
            # Add more languages here
        }
        
        # Speaker mapping for TTS systems
        self.speaker_map = {
            "tt": "dilyara",
            "es": "lj_speech",
            # Add more speakers here
        }
        
        # TTS system options
        self.tts_systems = ["silero"]  # Add more TTS systems as they become available
        self.default_tts = "silero"
        
        # Translation service options
        self.translation_services = ["google", "google_gemini"]  # Add more services as they're implemented
        self.default_translation = "google_gemini"
        self.google_model_name = "gemini-2.0-flash"  # Default model for Google Gemini
        self.google_api_key = os.getenv("GOOGLE_GENAI_API_KEY", None)  # Ensure this is set in your environment

        # Audio processing options
        self.sample_rate = 48000
        self.audio_format = "wav"
        
        # Subtitle processing options
        self.max_segment_merge_duration = 10  # Max seconds for merging segments
        self.segment_merge_threshold = 0.3   # Max gap between segments to consider merging
        
        # Set up paths
        self._setup_paths()
    
    def _setup_paths(self):
        if self.youtube_url:
            # Create a directory based on video ID
            from utils.video import get_video_id
            video_id = get_video_id(self.youtube_url)
            self.project_dir = os.path.join(self.work_dir, video_id)
        else:
            self.project_dir = os.path.join(self.work_dir, "video_name")
            
        # Create specific directories for each processing step
        self.audio_path = os.path.join(self.project_dir, "audio")
        self.subtitles_path = os.path.join(self.project_dir, "subtitles")
        self.translations_path = os.path.join(self.project_dir, "translations")
        self.tts_path = os.path.join(self.project_dir, "tts")
        self.output_path = os.path.join(self.project_dir, "output")
        
        # Create directories
        for path in [self.audio_path, self.subtitles_path, self.translations_path, 
                    self.tts_path, self.output_path]:
            os.makedirs(path, exist_ok=True)
        
        # Set up file paths
        self.video_file = os.path.join(self.project_dir, "video.webm")
        self.subtitle_file = os.path.join(self.subtitles_path, "original.vtt")
        self.original_audio_file = os.path.join(self.audio_path, "original_audio.wav")
        self.voice_file = os.path.join(self.audio_path, "voice.wav")
        self.bg_file = os.path.join(self.audio_path, "background.wav")
        self.final_output = os.path.join(self.output_path, f"translated_video_{self.target_language}.mp4")
