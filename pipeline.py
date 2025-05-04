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

    def run_from_step(self, start_processor_name=None):
        """Run the pipeline starting from a specific step"""
        start_processing = start_processor_name is None
        data = {}

        for processor in self.processors:
            processor_name = processor.__class__.__name__

            if not start_processing:
                if processor_name == start_processor_name:
                    start_processing = True
                else:
                    # Load intermediate results for skipped steps
                    print(f"Loading results for skipped processor: {processor_name}")
                    saved_data = processor.load_output(f"{processor_name}_output.json")
                    if saved_data is not None:
                        data.update(saved_data)
                    continue

            print(f"Running processor: {processor_name}")
            data = processor.process(data)  # Pass data to the processor and update it