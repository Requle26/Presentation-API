import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from API_server.services.assess_reading import assess_reading  # noqa: E402


def test_assess_reading_returns_json_friendly_scores(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"placeholder")
    monkeypatch.setitem(
        sys.modules,
        "phoneme_asr",
        SimpleNamespace(transcribe_phones=lambda _path: "B A D A"),
    )

    result = assess_reading(audio_path, "바다")

    assert result["expected_text"] == "바다"
    assert result["recognized_text"] == "바다"
    assert result["correct"] is True
    assert result["accuracy"] == 1.0
    assert result["items"][0]["word"] == "바다"
    assert result["items"][0]["errors"] == []


def test_assess_reading_rejects_missing_audio():
    with pytest.raises(FileNotFoundError):
        assess_reading("missing.wav", "바다")


def test_assess_reading_rejects_empty_text(tmp_path):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"placeholder")

    with pytest.raises(ValueError, match="expected_text"):
        assess_reading(audio_path, " ")
