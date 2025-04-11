import os
from utils import create_adjusted_audio_video, create_folders, download_video_and_subtitles, extract_audio, generate_speech, parse_vtt, separate_audio, translate_subtitles


download_path_base = "downloads"


# run all steps
def main(youtube_url, target_language="es"):
    download_path = os.path.join(download_path_base, "video_name")
    audio_path = os.path.join(download_path, "audio")
    subtitles_path = os.path.join(download_path, "subtitles")

    create_folders(audio_path, subtitles_path)

    video_file = os.path.join(download_path, "video.webm")
    subtitle_file = download_video_and_subtitles(youtube_url, download_path)
    if subtitle_file:
        original_audio_file = extract_audio(video_file, audio_path)
        voice_file, bg_file = separate_audio(original_audio_file, audio_path)
        original_subtitles = parse_vtt(subtitle_file)
        translated_subtitles = translate_subtitles(original_subtitles, target_language)
        print("Generate speech")
        speech_files = generate_speech(translated_subtitles, audio_path, target_language)

        if speech_files:
            create_adjusted_audio_video(video_file, speech_files, bg_file, audio_path)
        else:
            print("Error: No speech files generated.")
    else:
        print("Error: No subtitles downloaded.")

if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=NLtnm_bRzPw" # Replace with your YouTube URL
    target_language = "tt" # Replace with your target language code (e.g., "es" for Spanish)
    main(youtube_url, target_language)