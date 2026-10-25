import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from API_server.services.assess_reading import assess_reading


router = APIRouter()


@router.post("/")
def create_audio_feedback(
    expected_text: str = Form(...),
    audio: UploadFile = File(...),
    item_type: str = Form("transparent"),
):
    suffix = Path(audio.filename or "").suffix
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"audio{suffix}"
        with audio_path.open("wb") as destination:
            shutil.copyfileobj(audio.file, destination)

        try:
            return assess_reading(audio_path, expected_text, item_type)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error