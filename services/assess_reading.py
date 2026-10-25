from pathlib import Path
import sys

ASSESSMENT_DIR = Path(__file__).resolve().parent / "korean-reading-assessment"
if str(ASSESSMENT_DIR) not in sys.path:
    sys.path.insert(0, str(ASSESSMENT_DIR))

from g2p_expected import g2p
from pipeline_sentence import expected_eojeol_prons, score_sentence
from phoneme_map import phones_to_hangul

ITEM_TYPES = {"transparent", "phonrule", "nonword"}


def assess_reading(audio_path, expected_text, item_type="transparent"):
    """Recognize and score a recording against a word, phrase, or sentence.

    Args:
        audio_path: Path to a readable audio file.
        expected_text: The text the speaker was asked to read.
        item_type: Scoring rule: ``transparent``, ``phonrule``, or ``nonword``.

    Returns:
        A JSON-friendly dictionary with overall and per-word scores.
    """
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file does not exist: {path}")
    if not isinstance(expected_text, str) or not expected_text.strip():
        raise ValueError("expected_text must be a non-empty string")
    if item_type not in ITEM_TYPES:
        raise ValueError(
            f"item_type must be one of {', '.join(sorted(ITEM_TYPES))}"
        )

    from phoneme_asr import transcribe_phones

    expected_text = expected_text.strip()
    recognized_phonemes = transcribe_phones(str(path))
    scores, heard, eojeols = score_sentence(
        expected_text, recognized_phonemes, item_type=item_type
    )
    expected_pronunciations = expected_eojeol_prons(expected_text)

    total_units = sum(score.n_jamo for score in scores)
    accuracy = (
        sum(score.accuracy * score.n_jamo for score in scores) / total_units
        if total_units
        else 0.0
    )
    items = []
    for word, pronunciation, actual, score in zip(
        eojeols, expected_pronunciations, heard, scores
    ):
        items.append(
            {
                "word": word,
                "expected_pronunciation": pronunciation,
                "recognized_text": actual,
                "correct": score.correct,
                "accuracy": score.accuracy,
                "errors": [
                    {
                        "kind": error.kind,
                        "tag": error.tag,
                        "weight": error.weight,
                        "expected": "".join(token.char for token in error.exp),
                        "actual": "".join(token.char for token in error.act),
                    }
                    for error in score.errors
                ],
            }
        )

    return {
        "expected_text": expected_text,
        "expected_pronunciation": g2p(expected_text),
        "recognized_text": phones_to_hangul(recognized_phonemes),
        "recognized_phonemes": recognized_phonemes,
        "item_type": item_type,
        "correct": bool(scores) and all(score.correct for score in scores),
        "accuracy": round(accuracy, 4),
        "word_count": len(items),
        "items": items,
    }
