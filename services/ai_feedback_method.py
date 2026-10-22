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

client = genai.Client(api_key=api_key)

class feedback(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str
    strengths: list[str]
    improvements: list[str]
    
# 자료 피드백 함수
def generate_material_feedback(input_file, mime_type: str, title: str, perpose: str, detail: str | None = None):
    SYSTEM_PROMPT = """너는 발표 자료 평가 전문 AI인 PresentAI야.
    사용자가 제공한 발표 자료(문서/이미지)를 분석하여 평가 결과를 반환해.

    다음 규칙을 반드시 지켜서 평가해:
    1. score: 발표 자료 전체에 대한 종합 점수를 0~100 사이의 정수로 평가해. 
    2. feedback: 발표 자료 전체에 대한 종합 평가 내용을 작성해.
    3. strengths: 발표 자료의 주요 장점을 2~3개의 문자열로 작성해.
    4. improvements: 발표 자료의 개선할 점을 우선순위 순서로 있는대로 다 적고 문자열로 작성해. 각 문제점은 총점 100점 기준으로 해당 문제 때문에 감점한 점수를 '1. [감점 N점] 개선 내용' 형식으로 명시해. 여기서 N은 해당 문제의 감점 점수이며, improvements에 적은 감점 점수의 합은 100에서 score를 뺀 값과 일치해야 해. 같은 문제를 중복 감점하지 마. (예: score가 85점이면 총 감점은 15점이며, "1. [감점 8점] 3번 슬라이드의 텍스트 가독성이 떨어짐", "2. [감점 7점] 슬라이드 구성이 발표 시간에 비해 많음"처럼 작성해.)
    5. 제공된 발표 자료 내용에만 기반하여 평가하고 없는 정보를 임의로 만들어내지 마.
    6. 언어는 한국어로 작성해.
    """

    uploaded_file = client.files.upload(file=input_file, config=types.UploadFileConfig(mime_type=mime_type))
    if detail is None:
        prompt = f"발표 제목과 목적, 추가 설명등을 참고해서 피드백에 반영해, 발표 제목: {title}, 발표 목적: {perpose}"
    elif detail is not None:
        prompt = f"발표 제목과 목적, 추가 설명등을 참고해서 피드백에 반영해, 발표 제목: {title}, 발표 목적: {perpose}, 추가 설명: {detail}"

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=[prompt, uploaded_file],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=feedback,
        ),
    )

    return response.parsed


# 대본 피드백 함수
def generate_script_feedback(prompt: str, title: str, perpose: str, detail: str | None = None):
    SYSTEM_PROMPT = """너는 발표 평가 AI인 PresentAI야.
    사용자가 제공한 발표 대본을 분석하고, 발표 평가 결과를 JSON 형식으로 반환해.
    반드시 다음 규칙을 지켜.
    score는 0~100 사이의 정수로 평가해.
    feedback에는 발표 전체에 대한 종합 평가를 작성해.
    strengths에는 발표의 장점을 2~3개 문자열로 작성해.
    improvements에는 개선할 점을 우선순위 순서로 있는대로 다 적고 문자열로 작성해. 각 문제점은 총점 100점 기준으로 해당 문제 때문에 감점한 점수를 '1. [감점 N점] 개선 내용' 형식으로 명시해. 여기서 N은 해당 문제의 감점 점수이며, improvements에 적은 감점 점수의 합은 100에서 score를 뺀 값과 일치해야 해. 같은 문제를 중복 감점하지 마. (예: score가 85점이면 총 감점은 15점이며, "1. [감점 8점] 발표의 핵심 주장이 충분히 뒷받침되지 않음", "2. [감점 7점] 결론이 명확하지 않음"처럼 작성해.)
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
    """
    if detail is None:
            TPD = f"발표 제목과 목적, 추가 설명등을 참고해서 피드백에 반영해, 발표 제목: {title}, 발표 목적: {perpose}, 발표 대본: "
    elif detail is not None:
            TPD = f"발표 제목과 목적, 추가 설명등을 참고해서 피드백에 반영해, 발표 제목: {title}, 발표 목적: {perpose}, 추가 설명: {detail}, 발표 대본: "
    
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=[TPD, prompt],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=feedback,
        ),
    )

    return response.parsed


# 대본 / 자료 종합 피드백 함수
def overall_result(prompt: str, input_file, mime_type: str, title: str, perpose: str, detail: str | None = None):
    SYSTEM_PROMPT = """너는 발표 평가 AI인 PresentAI야.
    사용자가 제공한 '발표 대본'과 '발표 자료(문서/이미지)'를 함께 분석하고, 발표 평가 결과를 JSON 형식으로 반환해.
    반드시 다음 규칙을 지켜:
    1. score는 0~100 사이의 정수로 평가해.
    2. feedback에는 대본의 내용과 발표 자료의 시각적/구조적 완성도를 종합한 평가를 작성해.
    3. strengths에는 대본과 발표 자료의 장점을 2~3개 문자열로 작성해.
    4. improvements에는 대본과 발표 자료를 연계하여 개선할 점을 우선순위 순서로 있는대로 다 적고 문자열로 작성해. 각 문제점은 총점 100점 기준으로 해당 문제 때문에 감점한 점수를 '1. [감점 N점] 개선 내용' 형식으로 명시해. 여기서 N은 해당 문제의 감점 점수이며, improvements에 적은 감점 점수의 합은 100에서 score를 뺀 값과 일치해야 해. 같은 문제를 중복 감점하지 마. (예: score가 85점이면 총 감점은 15점이며, "1. [감점 8점] 3번 슬라이드의 시각 자료와 대본 설명이 일치하지 않음", "2. [감점 7점] 대본에서 강조한 핵심 수치가 슬라이드에서 잘 드러나지 않음"처럼 작성해.) 또한 대본과 발표자료의 연관성을 분석해서 적어줘.
    5. 사용자가 제공하지 않은 정보는 임의로 만들어 내지 마.
    6. JSON 이외의 설명이나 마크다운 코드 블록은 출력하지 마.
    7. 모든 필드는 반드시 포함해.
    8. 언어는 한국어로 작성해.
    """
    if detail is None:
        TPD = f"발표 제목과 목적, 추가 설명등을 참고해서 피드백에 반영해, 발표 제목: {title}, 발표 목적: {perpose}, 발표 대본 및 발표 자료: "
    elif detail is not None:
        TPD = f"발표 제목과 목적, 추가 설명등을 참고해서 피드백에 반영해, 발표 제목: {title}, 발표 목적: {perpose}, 추가 설명: {detail}, 발표 대본 및 발표 자료: "

    uploaded_file = client.files.upload(file=input_file, config=types.UploadFileConfig(mime_type=mime_type))
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        contents=[TPD, prompt, uploaded_file],
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
