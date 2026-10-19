import os
from pathlib import Path

from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google.genai import types

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("프로젝트 루트 .env에 GEMINI_API_KEY를 설정해 주세요.")

class presentation_analysis(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str
    strengths: list[str]
    improvements: list[str]

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """너는 발표 평가 AI인 PresentAI야.
사용자가 제공한 발표 대본을 분석하고, 발표 평가 결과를 JSON 형식으로 반환해.
반드시 다음 규칙을 지켜.
score는 0~100 사이의 정수로 평가해.
feedback에는 발표 전체에 대한 종합 평가를 작성해.
strengths에는 발표의 장점을 2~3개 문자열로 작성해.
improvements에는 개선할 점을 2~3개 문자열로 작성해.
사용자가 제공하지 않은 정보는 임의로 만들어 내지 마.
JSON 이외의 설명이나 마크다운 코드 블록은 출력하지 마.
모든 필드는 반드시 포함해.
평가 결과는 아래 JSON 구조를 따라야 해.
반환 형식:
{
"score": 85,
"feedback": "발표에 대한 종합 평가",
"strengths": [
"장점 1",
"장점 2"
],
"improvements": [
"개선점 1",
"개선점 2"
]
}
다음 발표 대본을 평가해.
발표 대본:
"""

def generate_script_feedback(prompt: str):
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=presentation_analysis,
        ),
    )

    result = response.parsed

    if result is None:
        raise ValueError("구조화된 분석결과 반환 실패")

    return result