import os
import subprocess
import re
from urllib.parse import parse_qs, urlparse
import yt_dlp
from googletrans import Translator
import torch
import torchaudio
from num2words import num2words
import ffmpeg


def get_video_id(url: str) -> str:
    """Extract v, https://www.youtube.com/watch?v=NLtnm_bRzPw"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'v' in query_params:
        return query_params['v'][0]  # Get the first value of 'v'
    else:
        raise ValueError("Incorrect Youtube URL passed")

def create_folders(audio_path: str, subtitles_path: str) -> None:
    os.makedirs(audio_path, exist_ok=True)
    os.makedirs(subtitles_path, exist_ok=True)

def download_video_and_subtitles(youtube_url, download_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'subtitleslangs': ['en.*'],
        'subtitlesformat': 'vtt',
        'writesubtitles': True,
        'outtmpl': os.path.join(download_path, 'video.%(ext)s')
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    # Find the subtitle file
    for file in os.listdir(download_path):
        if file.endswith('.vtt'):
            return os.path.join(download_path, file)
    return None


def extract_audio(video_file, audio_path):
    audio_file = os.path.join(audio_path, "original_audio.wav")
    command = f"ffmpeg -i {video_file} -q:a 0 -map a {audio_file}"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return audio_file


def separate_audio(audio_file, audio_path):
    voice_file = os.path.join(audio_path, "voice.wav")
    bg_file = os.path.join(audio_path, "background.wav")
    command = f"spleeter separate -o {audio_path} -p spleeter:2stems {audio_file}"

    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    os.rename(os.path.join(audio_path, "vocals.wav"), voice_file)
    os.rename(os.path.join(audio_path, "accompaniment.wav"), bg_file)
    return voice_file, bg_file


def parse_vtt(vtt_file):
    with open(vtt_file, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)\n\n', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for index, match in enumerate(matches):
        start, end, text = match
        subtitles.append({
            'index': index + 1,
            'start': start.replace('.', ','),
            'end': end.replace('.', ','),
            'text': text.replace('\n', ' ')
        })

    return subtitles


def convert_num_to_words(utterance):
      utterance = ' '.join([num2words(i) if i.isdigit() else i for i in utterance.split()])
      return utterance


def translate_subtitles(subtitles, target_language="tt"):
    translator = Translator()
    translated_subtitles = []

    for subtitle in subtitles:
        orig_text = convert_num_to_words(subtitle['text'])
        translated_text = translator.translate(orig_text, dest=target_language).text
        translated_subtitles.append({
            'index': subtitle['index'],
            'start': subtitle['start'],
            'end': subtitle['end'],
            'text': translated_text,
            'orig_text': orig_text,
        })

    return translated_subtitles


def generate_speech(translated_subtitles, audio_path, target_language="tt"):
    try:
        model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                             model='silero_tts',
                                             language=target_language,
                                             speaker='v3_' + target_language)
        device = torch.device('cpu')
        model.to(device)

        speech_files = []
        sample_rate = 48000
        speaker = 'random' # You might need to adjust the speaker based on the language
        if target_language == 'tt':
            speaker = 'dilyara'
        elif target_language == 'es':
            speaker = 'lj_speech'

        for subtitle in translated_subtitles:
            gen_audio_path = os.path.join(audio_path, f"speech_{subtitle['index']}.wav")
            try:
                audio = model.apply_tts(text=subtitle['text'], sample_rate=sample_rate, speaker=speaker, put_accent=True, put_yo=True)
                torchaudio.save(gen_audio_path, audio.unsqueeze(0), sample_rate, backend="ffmpeg")
                speech_files.append({
                    'file': gen_audio_path,
                    'start': subtitle['start'],
                    'end': subtitle['end'],
                    'text': subtitle['text'],
                    'orig_text': subtitle['orig_text'],
                })
            except Exception as e:
                print(f"Error generating speech for subtitle {subtitle['index']}: {e}")
        return speech_files
    except Exception as e:
        print(f"Error loading TTS model for language '{target_language}': {e}")
        return []


def get_duration(input_media):
    try:
        probe = ffmpeg.probe(input_media)
        return float(probe["format"]["duration"])
    except ffmpeg.Error as e:
        print(f"Error getting duration for {input_media}: {e.stderr.decode('utf8')}")
        return 0.0


def get_frequency(input_media):
    try:
        probe = ffmpeg.probe(input_media)
        for stream in probe.get('streams', []):
            if stream.get('codec_type') == 'audio':
                return float(stream['sample_rate'])
        return None
    except ffmpeg.Error as e:
        print(f"Error getting frequency for {input_media}: {e.stderr.decode('utf8')}")
        return None


def time_to_seconds(time_str: str):
    """Converts a time string (HH:MM:SS, MM:SS, or SS) to seconds, handling commas."""
    time_str = time_str.replace(",", ".")
    parts = time_str.split(':')
    try:
        if len(parts) == 3:
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        elif len(parts) == 1:
            return float(parts[0])
        else:
            return 0
    except ValueError as e:
        print(f"Error converting time string '{time_str}': {e}")
        return 0


def adjust_audio_timing(audio_file, start_time, end_time, speed_factor=1.0):
    """Adjusts the timing and speed of an audio file using FFmpeg."""
    output_file = audio_file.replace(".wav", "_adjusted.wav")
    duration = end_time - start_time

    print(f"Adjusting {audio_file} from {start_time} to {end_time} (duration {duration}), speed factor {speed_factor}")
    print(f"Start time: {start_time}, End time: {end_time}, duration: {duration}")

    if speed_factor != 1.0:
      command = f"ffmpeg -i {audio_file} -filter:a \"atempo={speed_factor}, asetpts=PTS-STARTPTS\" -c:a pcm_s16le {output_file} -y" #attempt to use asetpts
    else:
      command = f"ffmpeg -i {audio_file} -ss {start_time} -t {duration} -c:a pcm_s16le {output_file} -y" #simplified no atempo

    print(f"Executing: {command}")
    output = subprocess.run(command, shell=True)

    if output.returncode != 0:
        print(f"Error adjusting audio: {output.stderr.decode() if output.stderr else 'No error'}")
        return audio_file
    return output_file


def generate_silence(duration, output_path):
    """Generates a silence audio file using FFmpeg."""
    output_file = os.path.join(output_path, f"silence_debug_{int(duration * 1000)}.wav") # create unique output name
    command = f"ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t {duration} {output_file} -y"
    subprocess.run(command, shell=True)
    return output_file


def create_adjusted_audio_video(video_file, speech_files, bg_audio_file, audio_path):
    """Creates a new video with adjusted audio timing using concat."""
    audio_path = "downloads/audio"
    final_audio_parts = []
    last_end_time = 0

    adjusted_speech_clips = []
    for speech_data in speech_files:
        start_time = time_to_seconds(speech_data['start'])
        end_time = time_to_seconds(speech_data['end'])

        file_duration = get_duration(speech_data['file'])

        sub_duration = end_time - start_time
        if sub_duration == 0:
            speed_rate = 1.0
        else:
            speed_rate = file_duration / sub_duration

        adjusted_audio_path = adjust_audio_timing(speech_data['file'], start_time, end_time, speed_rate)
        adjusted_speech_clips.append({
            'file': adjusted_audio_path,
            'start': speech_data['start'],
            'end': speech_data['end'],
            'text': speech_data['text'],
            'orig_text': speech_data['orig_text'],
            'start_seconds': start_time,
            'end_seconds': end_time
        })

    for clip in adjusted_speech_clips:
        if clip['start_seconds'] > last_end_time:
            silence_duration = clip['start_seconds'] - last_end_time
            silence_file = generate_silence(silence_duration, audio_path)
            final_audio_parts.append(silence_file)
        final_audio_parts.append(clip['file'])
        last_end_time = clip['end_seconds']

    final_wav_file = os.path.join(audio_path, "final_uncompressed.wav")

    # Create concat list
    concat_list_file = "concat_list.txt"
    with open(concat_list_file, "w") as f:
        for part in final_audio_parts:
            f.write(f"file '{part}'\n")

    print(f"Concat list file: {concat_list_file}")
    with open(concat_list_file, 'r') as file:
        print(file.read())

    # Use concat filter
    concat_command = f"ffmpeg -f concat -safe 0 -i {concat_list_file} -c copy {final_wav_file} -y"
    print(f"Concat command: {concat_command}")

    with open("concat_output.log", "w") as log_file:
        output_concat = subprocess.run(concat_command, shell=True, stdout=log_file, stderr=log_file)

    if output_concat.returncode != 0:
        print(f"Error in concat (WAV). Check 'concat_output.log' for details.")
        return None

    final_audio_file = os.path.join(audio_path, "final_audio.aac")
    aac_command = f"ffmpeg -i {final_wav_file} -c:a aac -strict experimental {final_audio_file} -y"

    with open("aac_encode.log", "w") as aac_log:
        output_aac = subprocess.run(aac_command, shell=True, stdout=aac_log, stderr=aac_log)

    if output_aac.returncode != 0:
        print(f"Error in AAC encoding. Check 'aac_encode.log' for details.")
        return None

    # Debugging: Examine final_uncompressed.wav
    print("Examining final_uncompressed.wav:")
    subprocess.run(f"ffprobe {final_wav_file}", shell=True)

    # Debugging: Examine final_audio.aac
    print("Examining final_audio.aac:")
    subprocess.run(f"ffprobe {final_audio_file}", shell=True)

    # Debugging: print final_audio_parts
    print("Final audio parts:")
    print(final_audio_parts)

    output_video_file = "translated_video_with_adjusted_audio.mp4"
    command_merge = f"ffmpeg -i {video_file} -i {final_audio_file} -c:v copy -map 0:v -map 1:a {output_video_file} -y"
    print(f"Merge command: {command_merge}")

    # Redirect merge log
    with open("merge_log.log", "w") as merge_log:
        subprocess.run(command_merge, shell=True, stdout=merge_log, stderr=merge_log)

    print(f"Video with adjusted audio created: {output_video_file}")
    return output_video_file

# def time_to_seconds(time_str):
#     h, m, s = time_str.split(':')
#     s, ms = s.split(',')
#     return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

# def adjust_audio_timing(speech_file, start_seconds, end_seconds):
#     output_file = speech_file.replace(".wav", "_adjusted.wav")
#     original_duration = get_duration(speech_file)
#     target_duration = end_seconds - start_seconds

#     if original_duration > 0 and target_duration > 0:
#         speed_rate = original_duration / target_duration
#         command = f"ffmpeg -i {speech_file} -filter:a \"atempo={speed_rate}\" -y {output_file}"
#         subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
#         return output_file
#     else:
#         print(f"Warning: Could not adjust timing for {speech_file}. Original duration: {original_duration}, Target duration: {target_duration}")
#         return speech_file # Return original if adjustment fails

