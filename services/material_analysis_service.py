import os
from pathlib import Path

from google import genai
from dotenv import load_dotenv
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("프로젝트 루트 .env에 GEMINI_API_KEY를 설정해 주세요.")

class material_feedback(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str
    strengths: list[str]
    improvements: list[str]

client = genai.Client(api_key=api_key)


SYSTEM_PROMPT = """너는 발표 자료 평가 전문 AI인 PresentAI야.
사용자가 제공한 발표 자료(문서/이미지)를 분석하여 평가 결과를 반환해.

다음 규칙을 반드시 지켜서 평가해:
1. score: 발표 자료 전체에 대한 종합 점수를 0~100 사이의 정수로 평가해.
2. feedback: 발표 자료 전체에 대한 종합 평가 내용을 작성해.
3. strengths: 발표 자료의 주요 장점을 2~3개의 문자열로 작성해.
4. improvements: 발표 자료의 개선 포인트를 작성하되, 반드시 각 문제점마다 '1. [N점] 개선 내용' 형식으로 번호와 감점/인정 점수를 명시하여 작성해. (예: "1. [75점] 3번 슬라이드의 텍스트 가독성이 떨어짐")
5. 제공된 발표 자료 내용에만 기반하여 평가하고 없는 정보를 임의로 만들어내지 마.
6. 언어는 한국어로 작성해.
"""


def generate_material_feedback(input_file, mime_type: str):
    uploaded_file = client.files.upload(file=input_file, config=types.UploadFileConfig(mime_type=mime_type))

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=[uploaded_file, "이 문서의 핵심 내용을 요약해줘"],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=material_feedback,
        ),
    )

    return response.parsed