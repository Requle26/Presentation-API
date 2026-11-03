import os
import tempfile

from fastapi import APIRouter, File, UploadFile
from services.stt_whisper import transcribe_audio
from services.silence_detect import detect_pauses
from services.speech_rate import get_speech_rate

router = APIRouter()

@router.post("/")
def create_speech_feedback(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "")[1] or ".wav"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
        temp.write(file.file.read())
        temp_path = temp.name

    try:
        result = transcribe_audio(temp_path)
        result["silence"] = detect_pauses(temp_path)
        result["speech_rate"] = get_speech_rate(result["text"], result["silence"])
    finally:
        os.remove(temp_path)

    return result
