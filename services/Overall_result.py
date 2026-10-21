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

class feedback(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str
    strengths: list[str]
    improvements: list[str]

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """너는 발표 평가 AI인 PresentAI야.
사용자가 제공한 '발표 대본'과 '발표 자료(문서/이미지)'를 함께 분석하고, 발표 평가 결과를 JSON 형식으로 반환해.
반드시 다음 규칙을 지켜:
1. score는 0~100 사이의 정수로 평가해.
2. feedback에는 대본의 내용과 발표 자료의 시각적/구조적 완성도를 종합한 평가를 작성해.
3. strengths에는 대본과 발표 자료의 장점을 2~3개 문자열로 작성해.
4. improvements에는 대본과 발표 자료를 연계하여 개선할 점을 2~3개 문자열로 작성하되, 각 문제점마다 '1. [N점] 개선 내용' 형식으로 번호와 점수를 명시해. (예: "1. [75점] 3번 슬라이드의 시각 자료 내용과 대본의 설명이 일치하지 않음") 또한 대본과 발표자료의 연관성을 분석해서 적어줘
5. 사용자가 제공하지 않은 정보는 임의로 만들어 내지 마.
6. JSON 이외의 설명이나 마크다운 코드 블록은 출력하지 마.
7. 모든 필드는 반드시 포함해.
8. 언어는 한국어로 작성해.
"""

def overall_result(prompt: str, input_file, mime_type: str):
    uploaded_file = client.files.upload(file=input_file, config=types.UploadFileConfig(mime_type=mime_type))
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=[prompt, uploaded_file],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=feedback,
        ),
    )
    result = response.parsed

    if result is None:
        raise ValueError("구조화된 분석결과 반환 실패")

    return result
# ------------------