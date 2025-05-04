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
    parser.add_argument("--youtube-cookies-path", "-c", type=str, default=None, help="Use YouTube cookies to download videos")
    parser.add_argument("--start-step", type=str, default=None, help="Processor class name to start the pipeline from.")

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
    config.youtube_cookies_path = args.youtube_cookies_path
    
    # Create and run pipeline
    pipeline = Pipeline(config)
    
    print(f"Processing YouTube video: {args.youtube_url}")
    print(f"Target language: {args.language}")
    print(f"Work directory: {args.work_dir}")

    # import os
    # stems_dir = os.path.join(config.audio_path, "htdemucs", os.path.basename(config.original_audio_file).split('.')[0])
    # print(f"Stems directory: {stems_dir}")
    # if os.path.exists(stems_dir):
    #     os.rename(os.path.join(stems_dir, "vocals.wav"), config.voice_file)
    #     os.rename(os.path.join(stems_dir, "no_vocals.wav"), config.bg_file)
    # print(f"Voice file: {config.voice_file}, old: {os.path.join(stems_dir, 'vocals.wav')}")
    # print(f"bg_file file: {config.bg_file}, old: {os.path.join(stems_dir, 'no_vocals.wav')}")

    # return
    try:
        if args.start_step:
            print(f"Starting pipeline from step: {args.start_step}")
            result = pipeline.run_from_step(args.start_step)
        else:
            print("Running the entire pipeline...")
            result = pipeline.run()
        if result.get("output_video"):
            print(f"Success! Output video created at: {result['output_video']}")
        else:
            print("Pipeline completed but no output video was created.")
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    main()