from utils.subtitles import parse_vtt, merge_subtitle_segments
from processors.base import Processor

class SubtitleProcessor(Processor):
    def process(self, data=None):
        """Process subtitles - parse and optionally merge segments"""
        subtitle_file = data.get("subtitle_file") if data else self.config.subtitle_file
        
        # Parse VTT file
        subtitles = parse_vtt(subtitle_file)
        
        # Merge subtitle segments if enabled
        if getattr(self.config, "enable_segment_merging", True):
            merged_subtitles = merge_subtitle_segments(subtitles, self.config)
            
            # Save both original and merged subtitles
            self.save_output(subtitles, "original_subtitles.json")
            self.save_output(merged_subtitles, "merged_subtitles.json")
            
            return {"subtitles": merged_subtitles, "original_subtitles": subtitles}
        else:
            self.save_output(subtitles, "subtitles.json")
            return {"subtitles": subtitles}