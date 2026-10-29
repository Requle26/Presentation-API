from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from services.ai_feedback_method import overall_result, generate_script_feedback, generate_material_feedback
import openai
from services.file_converter import UnsupportedFileType


router = APIRouter()
@router.post("/")
def create_feedback(title: str, perpose: str, detail: str | None = Form(None), prompt: str | None = Form(None), file: UploadFile | None = File(None)):
    try:
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
            raise HTTPException(status_code=400, detail="대본이나 파일 중 하나 이상을 입력해야 합니다.")

    except UnsupportedFileType as e:
        raise HTTPException(status_code=415, detail=str(e))
    except openai.InternalServerError as e:
        if e.status_code == 503:
            raise HTTPException(status_code=503, detail="모델 사용량이 많습니다. 잠시 후 다시 시도해 주세요.")
        raise HTTPException(status_code=502, detail="AI 서버 오류가 발생했습니다.")

    if result is None:
        raise HTTPException(status_code=502, detail="피드백 결과 반환 실패")
    return result