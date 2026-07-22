from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Turn:
    role: str
    text: str
    emotion: str = "neutral"
    speaker: str | None = None


@dataclass
class Dialogue:
    sample_id: str
    is_fraud: bool
    scenario_id: str
    tree_id: str
    branch_status: str
    turns: list[Turn]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["higgs_text"] = dialogue_to_higgs_text(payload)
        return payload


def dialogue_to_higgs_text(dialogue: dict[str, Any]) -> str:
    lines: list[str] = []
    for turn in dialogue.get("turns", []):
        speaker = turn.get("speaker")
        if not speaker:
            speaker = "SPEAKER0" if turn.get("role") in {"assistant", "caller", "scammer"} else "SPEAKER1"
        emotion = normalize_higgs_emotion(str(turn.get("emotion") or "neutral"))
        token = f"<|emotion:{emotion}|>" if emotion else ""
        lines.append(f"[{speaker}]{token}{turn.get('text', '').strip()}")
    return "\n".join(x for x in lines if x.strip())


def normalize_higgs_emotion(label: str) -> str:
    mapping = {
        "neutral": "",
        "calm": "relief",
        "professional": "",
        "authoritative": "",
        "persuasive": "",
        "urgent": "fear",
        "fearful": "fear",
        "confused": "confusion",
        "suspicious": "disgust",
        "angry": "anger",
        "relieved": "relief",
        "sad": "sadness",
        "sadness": "sadness",
        "surprised": "surprise",
        "surprise": "surprise",
        "helpless": "helplessness",
    }
    clean = label.strip().lower()
    return mapping.get(clean, clean if clean in {"anger", "fear", "sadness", "surprise", "disgust", "confusion", "helplessness", "relief", "contentment"} else "")
