from fastapi import APIRouter, File, Form, UploadFile
from services.ai_feedback_method import overall_result, generate_script_feedback, generate_material_feedback


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