#!/usr/bin/env python3
import argparse
from config import Config
from pipeline import Pipeline

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="YouTube Video Auto-Dubber")
    parser.add_argument("youtube_url", help="YouTube video URL to process")
    parser.add_argument("--language", "-l", default="tt", help="Target language code (default: tt for Tatar)")
    parser.add_argument("--work-dir", "-w", default="downloads", help="Working directory (default: downloads)")
    parser.add_argument("--merge-segments", "-m", action="store_true", help="Merge subtitle segments")
    parser.add_argument("--add-silence", "-s", action="store_true", help="Add silence buffers instead of speeding up")
    
    args = parser.parse_args()
    
    # Create configuration
    config = Config(
        youtube_url=args.youtube_url,
        target_language=args.language,
        work_dir=args.work_dir
    )
    
    # Configure optional features
    config.enable_segment_merging = args.merge_segments
    config.add_silence_buffers = args.add_silence
    
    # Create and run pipeline
    pipeline = Pipeline(config)
    
    print(f"Processing YouTube video: {args.youtube_url}")
    print(f"Target language: {args.language}")
    print(f"Work directory: {args.work_dir}")
    
    try:
        result = pipeline.run()
        if result.get("output_video"):
            print(f"Success! Output video created at: {result['output_video']}")
        else:
            print("Pipeline completed but no output video was created.")
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    main()