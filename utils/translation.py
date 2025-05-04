import json
import os
from googletrans import Translator

from utils.subtitles import convert_num_to_words

class GoogleTranslator:
    def __init__(self, config):
        self.config = config
        self.translator = Translator()
        
    def translate(self, subtitles):
        """Translate subtitles using Google Translate"""
        translated_subtitles = []
        
        for subtitle in subtitles:
            orig_text = convert_num_to_words(subtitle['text'])
            translated_text = self.translator.translate(orig_text, dest=self.config.target_language).text
            translated_subtitles.append({
                'index': subtitle['index'],
                'start': subtitle['start'],
                'end': subtitle['end'],
                'text': translated_text,
                'orig_text': orig_text,
            })
        
        # Save translations
        output_file = os.path.join(self.config.translations_path, f"google_{self.config.target_language}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_subtitles, f, ensure_ascii=False, indent=2)
            
        return translated_subtitles


from google import genai
from google.genai import Client
from typing import List, Dict

class GoogleGeminiTranslator:
    def __init__(self, config):
        """
        Initialize the Google Gemini Translator.
        """
        self.config = config

    def translate(self, subtitles: List[Dict]) -> List[Dict]:
        """
        Translate subtitles using Google Gemini LLM.
        :param subtitles: List of subtitle dictionaries with 'start', 'end', and 'text'.
        :return: Translated subtitles in the same format as input.
        """
        # Merge subtitles into a single text with timecodes
        merged_text = self._merge_subtitles(subtitles)

        # Prepare the prompt for the LLM
        prompt = self._build_prompt(merged_text, self.config.target_language)

        # Call the Gemini API
        client = Client(api_key=self.config.google_api_key)
        response = client.models.generate_content(
            model=self.config.google_model_name,
            contents=prompt
        )

        # Parse the response back into subtitle format
        translated_subtitles = self._parse_translated_vtt(self._clean_webvtt_content(response.text), subtitles)

        # Save the translated subtitles to a file
        output_file = os.path.join(
            self.config.translations_path,
            f"google_gemini_{self.config.target_language}.json"
        )
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_subtitles, f, ensure_ascii=False, indent=2)

        return translated_subtitles

    def _merge_subtitles(self, subtitles: List[Dict]) -> str:
        """
        Merge subtitles into a single VTT-formatted string.
        :param subtitles: List of subtitle dictionaries.
        :return: Merged subtitles as a string.
        """
        return "\n".join(
            f"{subtitle['start']} --> {subtitle['end']}\n{subtitle['text']}"
            for subtitle in subtitles
        )

    def _build_prompt(self, subtitle_content: str, target_language: str) -> str:
        """
        Build the prompt for the LLM.
        :param subtitle_content: Merged subtitle content.
        :param target_language: Target language for translation.
        :return: Prompt string.
        """
        prompt = f"""
        You are a professional subtitle translator and editor working on dubbing videos from English to {target_language}. You will be provided with subtitles in WEBVTT format.
        Your task:
        1. Translate each subtitle line from English to {target_language}.
        2. Preserve the original WEBVTT timestamp structure.
        3. If a sentence is split across multiple fragments, merge them into a larger fragment if it improves the flow and keeps the spoken {target_language} translation within a similar duration.
        4. Ensure the {target_language} translation would take approximately the same time to speak as the original English fragment to keep it in sync with the video.

        Translate this content:
        {subtitle_content}
        """
        return prompt

    def _parse_translated_vtt(self, vtt_text: str, original_subtitles: List[Dict]) -> List[Dict]:
        """
        Parse the translated VTT text into the required subtitle format.
        :param vtt_text: Translated VTT text.
        :param original_subtitles: Original subtitles for reference.
        :return: List of translated subtitles in the required format.
        """
        output_file = os.path.join(
            self.config.translations_path,
            f"google_gemini_{self.config.target_language}_raw.txt"
        )
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(vtt_text)

        lines = vtt_text.strip().split("\n")
        translated_subtitles = []
        current_text = ""
        current_start = None
        current_end = None
        current_orig_text = ""

        for line in lines[2:]:
            if line.strip() == "WEBVTT":  # Skip the WEBVTT header
                continue
            if " --> " in line:  # Timecode line
                if current_text:  # Save the previous subtitle
                    translated_subtitles.append({
                        "index": len(translated_subtitles) + 1,
                        "start": current_start,
                        "end": current_end,
                        "text": current_text.strip(),
                        "orig_text": current_orig_text.strip()
                    })
                current_start, current_end = line.split(" --> ")
                current_text = ""
                current_orig_text = ""
            else:  # Text line
                current_text += line + " "
                if original_subtitles and len(translated_subtitles) < len(original_subtitles):
                    current_orig_text += original_subtitles[len(translated_subtitles)].get("text", "") + " "

        # Add the last subtitle
        if current_text and current_start and current_end:
            translated_subtitles.append({
                "index": len(translated_subtitles) + 1,
                "start": current_start,
                "end": current_end,
                "text": current_text.strip(),
                "orig_text": current_orig_text.strip()
            })

        return translated_subtitles

    def _build_prompt(self, subtitle_content, target_language):
        prompt = f"""
    You are a professional subtitle translator and editor working on dubbing videos from English to Tatar. You will be provided with subtitles in WEBVTT format.

    Your task:
    1. Translate each subtitle line from English to Tatar.
    2. Preserve the original WEBVTT timestamp structure.
    3. If a sentence is split across multiple fragments, merge them into a larger fragment if it improves the flow and keeps the spoken Tatar translation within a similar duration.
    4. Ensure the Tatar translation would take approximately the same time to speak as the original English fragment to keep it in sync with the video.
    5. Do not use English words, abbreviations, or symbols in the Tatar translation.
        - Translate or explain abbreviations and acronyms clearly for a Tatar-speaking audience unfamiliar with them.
        - Example: "UK" should be translated as "Бөекбритания".
    6. Write all numbers and symbols (like %, $, €, etc.) as fully written Tatar words.
        - Example: "10%" becomes "ун процент"
        - Example: "$5" becomes "биш доллар"
    7. Use formal, clear, and natural-sounding Tatar phrasing.
    8. Return the result in WEBVTT format, maintaining timestamps unchanged or adjusting them if merging fragments, and replacing only the subtitle text with its Tatar translation.

    Important:
    If merging fragments, adjust timestamps correctly and preserve WEBVTT syntax.

    Translate this content:
    {subtitle_content}
    """
        return prompt

    def _clean_webvtt_content(self, content):
        """Remove everything before the 'WEBVTT' header."""
        last_webvtt_index = content.lower().rfind("webvtt")

        if last_webvtt_index == -1:
            raise ValueError("Invalid WEBVTT file: 'WEBVTT' header not found.")
        return content[last_webvtt_index:]

def get_translator(service_name, config):
    """Factory function to get translator based on service name"""
    if service_name == "google":
        return GoogleTranslator(config)
    # Add more translation services here as they're implemented
    elif service_name == "google_gemini":
        return GoogleGeminiTranslator(config)
    else:
        raise ValueError(f"Unknown translation service: {service_name}")
