import os
import tempfile

from fastapi import APIRouter, File, UploadFile
from services.stt_whisper import transcribe_audio

router = APIRouter()

@router.post("/")
def create_speech_feedback(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "")[1] or ".wav"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
        temp.write(file.file.read())
        temp_path = temp.name

    try:
        result = transcribe_audio(temp_path)
    finally:
        os.remove(temp_path)

    return result
