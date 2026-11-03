from fastapi import HTTPException
import re

def get_text_length(text: str):
    cleaned_text = re.sub(r'[^a-zA-Z0-9가-힣]', '', text)
    return len(cleaned_text)

def get_total_pauses(duration_info):
    total_pauses = 0
    for p in duration_info["pauses"]:
        total_pauses += p["duration"]
    return total_pauses

def get_speech_rate(text, duration_info):
    if duration_info["pauses"] == []:
        result = round(60 * (get_text_length(text) / duration_info["duration"]), 1)
        return result
    result = round(60 * (get_text_length(text) / (duration_info["duration"] - get_total_pauses(duration_info))), 1)
    return result