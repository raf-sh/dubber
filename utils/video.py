import os
import subprocess
from urllib.parse import parse_qs, urlparse
import yt_dlp

def get_video_id(url):
    """Extract video ID from a YouTube URL"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'v' in query_params:
        return query_params['v'][0]  # Get the first value of 'v'
    else:
        raise ValueError("Incorrect YouTube URL passed")

def download_video_and_subtitles(config):
    """Download a YouTube video and its subtitles"""
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'subtitleslangs': ['en.*'],
        'subtitlesformat': 'vtt',
        'writesubtitles': True,
        'outtmpl': os.path.join(config.project_dir, 'video.%(ext)s')
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([config.youtube_url])

    # Find the subtitle file
    for file in os.listdir(config.project_dir):
        if file.endswith('.vtt'):
            subtitle_file = os.path.join(config.project_dir, file)
            # Copy to standard location
            subprocess.run(f"cp {subtitle_file} {config.subtitle_file}", shell=True)
            return config.subtitle_file
    return None

def extract_audio(config):
    """Extract audio from video file"""
    command = f"ffmpeg -i {config.video_file} -q:a 0 -map a {config.original_audio_file}"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return config.original_audio_file

def separate_audio(config):
    """Separate voice from background audio"""
    # Skip spleeter run if files already exist (for debugging)
    if os.path.exists(config.voice_file) and os.path.exists(config.bg_file):
        return config.voice_file, config.bg_file
        
    command = f"spleeter separate -o {config.audio_path} -p spleeter:2stems {config.original_audio_file}"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    # Rename output files to standard locations
    stems_dir = os.path.join(config.audio_path, "original_audio")
    if os.path.exists(stems_dir):
        os.rename(os.path.join(stems_dir, "vocals.wav"), config.voice_file)
        os.rename(os.path.join(stems_dir, "accompaniment.wav"), config.bg_file)
    
    return config.voice_file, config.bg_file
