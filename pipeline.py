from config import Config

# Import processors
from processors.video_downloader import VideoDownloader
from processors.audio_extractor import AudioExtractor
from processors.subtitle_processor import SubtitleProcessor
from processors.translator import TranslationProcessor
from processors.tts import TTSProcessor
from processors.audio_video_generator import AudioVideoGenerator

class Pipeline:
    """Pipeline orchestration class"""
    def __init__(self, config):
        self.config = config
        self.processors = []
        self._setup_default_processors()
        
    def _setup_default_processors(self):
        """Setup default processing pipeline"""
        self.processors = [
            VideoDownloader(self.config),
            SubtitleProcessor(self.config),
            TranslationProcessor(self.config),
            AudioExtractor(self.config),
            TTSProcessor(self.config),
            AudioVideoGenerator(self.config)
        ]
    
    def run(self):
        """Run the entire pipeline"""
        data = {}
        for processor in self.processors:
            print(f"Running {processor.name}...")
            result = processor.process(data)
            # Update data with result for next processor
            if result:
                data.update(result)
        return data
    
    def run_from_step(self, step_name, input_data=None):
        """Run pipeline from a specific step"""
        found = False