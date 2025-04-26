import os
import subprocess
import ffmpeg

def get_duration(input_media):
    """Get duration of audio/video file"""
    try:
        probe = ffmpeg.probe(input_media)
        return float(probe["format"]["duration"])
    except ffmpeg.Error as e:
        print(f"Error getting duration for {input_media}: {e.stderr.decode('utf8')}")
        return 0.0

def get_frequency(input_media):
    """Get sample rate of audio file"""
    try:
        probe = ffmpeg.probe(input_media)
        for stream in probe.get('streams', []):
            if stream.get('codec_type') == 'audio':
                return float(stream['sample_rate'])
        return None
    except ffmpeg.Error as e:
        print(f"Error getting frequency for {input_media}: {e.stderr.decode('utf8')}")
        return None

def adjust_audio_timing(audio_file, start_time, end_time, speed_factor=1.0):
    """Adjusts timing and speed of audio file"""
    output_file = audio_file.replace(".wav", "_adjusted.wav")
    duration = end_time - start_time

    if speed_factor != 1.0:
        command = f"ffmpeg -i {audio_file} -filter:a \"atempo={speed_factor}, asetpts=PTS-STARTPTS\" -c:a pcm_s16le {output_file} -y"
    else:
        command = f"ffmpeg -i {audio_file} -ss {start_time} -t {duration} -c:a pcm_s16le {output_file} -y"

    with open("adjust_output.log", "w") as log_file:
        output = subprocess.run(command, shell=True, stdout=log_file, stderr=log_file)
        if output.returncode != 0:
            print(f"Error adjusting audio: {output.stderr.decode() if output.stderr else 'No error'}")
            return audio_file
    return output_file

def generate_silence(duration, output_path):
    """Generate silent audio of specified duration"""
    output_file = os.path.join(output_path, f"silence_{int(duration * 1000)}.wav")
    command = f"ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t {duration} {output_file} -y"
    with open("silence_output.log", "w") as log_file:
        output = subprocess.run(command, shell=True, stdout=log_file, stderr=log_file)
        if output.returncode != 0:
            print(f"Error silence file generating: {output.stderr.decode() if output.stderr else 'No error'}")
            return None
    return output_file

def create_adjusted_audio_video(config, speech_files):
    """Create final video with adjusted audio timing"""
    video_file = config.video_file
    bg_audio_file = config.bg_file
    audio_path = config.audio_path
    
    final_audio_parts = []
    last_end_time = 0

    adjusted_speech_clips = []
    for speech_data in speech_files:
        start_time = time_to_seconds(speech_data['start'])
        end_time = time_to_seconds(speech_data['end'])

        # Get original audio duration and calculate speed adjustment
        file_duration = get_duration(speech_data['file'])
        
        sub_duration = end_time - start_time
        
        # Instead of slowing down audio too much, add silence if needed
        use_silence = False
        if file_duration < sub_duration * 0.7:  # If TTS is much shorter than subtitle duration
            speed_rate = 0.9  # Slow down slightly but not too much
            remaining_silence = sub_duration - (file_duration / speed_rate)
            use_silence = remaining_silence > 0.3  # Only use silence if it's significant
        else:
            speed_rate = file_duration / sub_duration if sub_duration > 0 else 1.0
        
        adjusted_audio_path = adjust_audio_timing(speech_data['file'], start_time, end_time, speed_rate)
        
        adjusted_speech_clips.append({
            'file': adjusted_audio_path,
            'start': speech_data['start'],
            'end': speech_data['end'],
            'text': speech_data['text'],
            'orig_text': speech_data['orig_text'],
            'start_seconds': start_time,
            'end_seconds': end_time,
            'use_silence': use_silence,
            'original_duration': file_duration
        })
    
    # Build final audio with proper timing
    for i, clip in enumerate(adjusted_speech_clips):
        # Add silence gap between clips if needed
        if clip['start_seconds'] > last_end_time:
            silence_duration = clip['start_seconds'] - last_end_time
            silence_file = generate_silence(silence_duration, audio_path)
            final_audio_parts.append(silence_file)
        
        final_audio_parts.append(clip['file'])
        
        # Add trailing silence if the audio was sped up to prevent sounding rushed
        if clip['use_silence']:
            adjusted_duration = get_duration(clip['file'])
            expected_duration = clip['end_seconds'] - clip['start_seconds']
            silence_needed = expected_duration - adjusted_duration
            if silence_needed > 0.2:  # Only add if silence is noticeable
                silence_file = generate_silence(silence_needed, audio_path)
                final_audio_parts.append(silence_file)
                last_end_time = clip['end_seconds']
            else:
                last_end_time = clip['start_seconds'] + adjusted_duration
        else:
            last_end_time = clip['end_seconds']

    # Create uncompressed final audio
    final_wav_file = os.path.join(audio_path, "final_uncompressed.wav")

    # Create concat list
    concat_list_file = "concat_list.txt"
    with open(concat_list_file, "w") as f:
        for part in final_audio_parts:
            f.write(f"file '{part}'\n")

    # Use concat filter
    concat_command = f"ffmpeg -f concat -safe 0 -i {concat_list_file} -c copy {final_wav_file} -y"
    
    with open("concat_output.log", "w") as log_file:
        output_concat = subprocess.run(concat_command, shell=True, stdout=log_file, stderr=log_file)

    if output_concat.returncode != 0:
        print(f"Error in concat (WAV). Check 'concat_output.log' for details.")
        return None

    # Mix with background audio
    final_audio_file = os.path.join(audio_path, "final_audio.aac")
    if bg_audio_file and os.path.exists(bg_audio_file):
        mixed_audio_file = os.path.join(audio_path, "mixed_audio.wav")
        amix_command = f"ffmpeg -i {final_wav_file} -i {bg_audio_file} -filter_complex [0:a][1:a]amix=inputs=2:duration=longest {mixed_audio_file} -y"

        with open("amix_output.log", "w") as amix_log:
            output_amix = subprocess.run(amix_command, shell=True, stdout=amix_log, stderr=amix_log)
        
        if output_amix.returncode != 0:
            print("Error mixing audio with background. Using only adjusted speech.")
            final_audio_file = final_wav_file
        else:
            final_audio_file = mixed_audio_file
    else:
        aac_command = f"ffmpeg -i {final_wav_file} -c:a aac -strict experimental {final_audio_file} -y"
        with open("aac_encode.log", "w") as aac_log:
            output_aac = subprocess.run(aac_command, shell=True, stdout=aac_log, stderr=aac_log)
        
        if output_aac.returncode != 0:
            print(f"Error in AAC encoding. Check 'aac_encode.log' for details.")
            return None

    # Merge audio with video
    output_video_file = config.final_output
    command_merge = f"ffmpeg -i {video_file} -i {final_audio_file} -c:v copy -map 0:v -map 1:a {output_video_file} -y"

    with open("merge_log.log", "w") as merge_log:
        subprocess.run(command_merge, shell=True, stdout=merge_log, stderr=merge_log)

    print(f"Video with adjusted audio created: {output_video_file}")
    return output_video_file
