import re
from num2words import num2words

def parse_vtt(subtitle_file):
    """Parse VTT subtitle file into structured format"""
    with open(subtitle_file, "r", encoding="utf-8") as f:
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
    """Convert numeric values to words for better TTS"""
    return ' '.join([num2words(i) if i.isdigit() else i for i in utterance.split()])

def time_to_seconds(time_str):
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

def is_sentence_end(text):
    """Check if text likely ends a sentence"""
    return bool(re.search(r'[.!?]$', text.strip()))

def is_sentence_start(text):
    """Check if text likely starts a sentence"""
    return bool(re.match(r'^[A-Z]', text.strip()))

def merge_subtitle_segments(subtitles, config):
    """Merge subtitle segments that are part of the same sentence or connected thoughts"""
    if not subtitles:
        return subtitles
    
    merged = []
    current_group = [subtitles[0]]
    
    for i in range(1, len(subtitles)):
        prev = subtitles[i-1]
        current = subtitles[i]
        
        # Calculate time gap between segments
        prev_end = time_to_seconds(prev['end'])
        current_start = time_to_seconds(current['start'])
        time_gap = current_start - prev_end
        
        # Check if segments should be merged based on:
        # 1. Previous segment doesn't end a sentence
        # 2. Current segment doesn't start with capital letter
        # 3. Gap between segments is small
        if (not is_sentence_end(prev['text']) or 
            not is_sentence_start(current['text']) or 
            time_gap < config.segment_merge_threshold):
            
            # Check if merging would exceed max duration
            group_start = time_to_seconds(current_group[0]['start'])
            group_end = time_to_seconds(current['end'])
            
            if (group_end - group_start) <= config.max_segment_merge_duration:
                current_group.append(current)
            else:
                # Create merged segment and start new group
                merged_segment = {
                    'index': current_group[0]['index'],
                    'start': current_group[0]['start'],
                    'end': current_group[-1]['end'],
                    'text': ' '.join(item['text'] for item in current_group)
                }
                merged.append(merged_segment)
                current_group = [current]
        else:
            # Create merged segment and start new group
            merged_segment = {
                'index': current_group[0]['index'],
                'start': current_group[0]['start'],
                'end': current_group[-1]['end'],
                'text': ' '.join(item['text'] for item in current_group)
            }
            merged.append(merged_segment)
            current_group = [current]
    
    # Add the last group
    if current_group:
        merged_segment = {
            'index': current_group[0]['index'],
            'start': current_group[0]['start'],
            'end': current_group[-1]['end'],
            'text': ' '.join(item['text'] for item in current_group)
        }
        merged.append(merged_segment)
    
    # Reindex the merged subtitles
    for i, subtitle in enumerate(merged):
        subtitle['index'] = i + 1
    
    return merged