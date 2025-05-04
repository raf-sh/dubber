from utils.video import download_video_and_subtitles
from processors.base import Processor

class VideoDownloader(Processor):
    def process(self, data=None):
        """Download video and subtitles"""
        subtitle_file = download_video_and_subtitles(self.config)
        return {"subtitle_file": subtitle_file}