from fastapi import APIRouter, File, Form, UploadFile
from services.script_analysis_service import generate_script_feedback
from services.material_analysis_service import generate_material_feedback
from services.Overall_result import overall_result


router = APIRouter()

@router.post("/")
def create_feedback(prompt: str | None = Form(None), file: UploadFile | None = File(None)):
    if prompt is not None and file is not None:
        print("대본과 파일 둘 다 처리합니다")
        result = overall_result(prompt, file.file, mime_type=file.content_type)
    elif prompt is not None:
        print("대본을 처리합니다")
        result = generate_script_feedback(prompt)

    elif file:
        print("파일을 처리합니다")
        result = generate_material_feedback(file.file, mime_type=file.content_type)
    else:
        result = "입력데이터가 없습니다"
        
    return result