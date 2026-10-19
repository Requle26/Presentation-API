from fastapi import APIRouter, File, UploadFile
from services.script_analysis_service import generate_script_feedback
from services.material_analysis_service import generate_material_feedback
from pydantic import BaseModel


router = APIRouter()

class prompt_request(BaseModel):
    prompt: str

@router.post("/script")
def create_script_feedback(request: prompt_request):
    result = generate_script_feedback(request.prompt)
    return result

@router.post("/material")
async def create_material_feedback(file: UploadFile = File(...)):
    result = generate_material_feedback(file.file, mime_type=file.content_type)
    return result