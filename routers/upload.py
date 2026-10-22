from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from services.ai_feedback_method import overall_result, generate_script_feedback, generate_material_feedback


router = APIRouter()

@router.post("/")
def create_feedback(title: str, perpose: str, detail: str | None = Form(None), prompt: str | None = Form(None), file: UploadFile | None = File(None)):
    if prompt is not None and file is not None:
        print("대본과 파일 둘 다 처리합니다")
        result = overall_result(
            prompt = prompt,
            input_file = file.file,
            mime_type=file.content_type,
            title = title,
            perpose = perpose,
            detail = detail
            )

    elif prompt is not None and file is None:
        print("대본을 처리합니다")
        result = generate_script_feedback(
            prompt,
            title, 
            perpose,
            detail
            )

    elif file is not None and prompt is None:
        print("파일을 처리합니다")
        result = generate_material_feedback(
            input_file = file.file,
            mime_type = file.content_type,
            title = title,
            perpose = perpose,
            detail = detail
            )

    else:
        raise HTTPException (status_code=400, detail="대본이나 파일 중 하나 이상을 입력해야 합니다.")
        
    return result