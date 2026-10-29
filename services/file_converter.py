import base64
import shutil
import subprocess
import tempfile
from pathlib import Path

import pymupdf as fitz

IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
PDF_TYPE = "application/pdf"
OFFICE_TYPES = {
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
    "application/vnd.ms-powerpoint",  # ppt
}
PDF_RENDER_ZOOM = 1.5


class UnsupportedFileType(Exception):
    pass


def _pdf_to_images(pdf_bytes: bytes) -> list[tuple[bytes, str]]:
    images = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(PDF_RENDER_ZOOM, PDF_RENDER_ZOOM))
            images.append((pix.tobytes("png"), "image/png"))
    return images


def _office_to_pdf(data: bytes, suffix: str) -> bytes:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        raise UnsupportedFileType("서버에 LibreOffice가 없어 PPT 파일을 변환할 수 없습니다.")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"input{suffix}"
        src.write_bytes(data)
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(src)],
            check=True, capture_output=True, timeout=120,
        )
        return (Path(tmp) / "input.pdf").read_bytes()


def file_to_images(file, mime_type: str) -> list[str]:
    """업로드 파일을 페이지/슬라이드 순서의 이미지 data URL 리스트로 변환한다."""
    data = file.read()

    if mime_type in IMAGE_TYPES:
        images = [(data, mime_type)]
    elif mime_type == PDF_TYPE:
        images = _pdf_to_images(data)
    elif mime_type in OFFICE_TYPES:
        suffix = ".pptx" if mime_type.endswith("presentation") else ".ppt"
        images = _pdf_to_images(_office_to_pdf(data, suffix))
    else:
        raise UnsupportedFileType(f"지원하지 않는 파일 형식입니다: {mime_type}")

    return [f"data:{mime};base64,{base64.b64encode(raw).decode()}" for raw, mime in images]
