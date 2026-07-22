from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_snapshot(
    dialogues: list[dict[str, Any]],
    audio_manifest: list[dict[str, Any]] | None,
    snapshot_id: str,
) -> list[dict[str, Any]]:
    audio_by_id = {str(x.get("sample_id")): x for x in audio_manifest or []}
    rows: list[dict[str, Any]] = []
    for idx, dialogue in enumerate(dialogues):
        sid = str(dialogue["sample_id"])
        audio = audio_by_id.get(sid, {})
        audio_path = audio.get("audio_path")
        checksum = sha256_file(audio_path) if audio_path and Path(audio_path).exists() else None
        rows.append(
            {
                "snapshot_id": snapshot_id,
                "index": idx,
                "sample_id": sid,
                "label": "FRAUD" if dialogue.get("is_fraud") else "NONFRAUD",
                "is_fraud": bool(dialogue.get("is_fraud")),
                "scenario_id": dialogue.get("scenario_id"),
                "tree_id": dialogue.get("tree_id"),
                "branch_status": dialogue.get("branch_status"),
                "turns": dialogue.get("turns", []),
                "higgs_text": dialogue.get("higgs_text", ""),
                "audio_path": audio_path,
                "audio_sha256": checksum,
                "speaker_metadata": audio.get("speaker_metadata", {}),
                "quality": audio.get("quality", {}),
                "generation_metadata": dialogue.get("metadata", {}),
            }
        )
    return rows
