from fastapi import APIRouter
from services.analysis_service import generate_at_response
from pydantic import BaseModel

router = APIRouter()

class prompt_request(BaseModel):
    prompt: str

@router.post("/")
def create_ai_response(request: prompt_request):
    result = generate_at_response(request.prompt)
    return result