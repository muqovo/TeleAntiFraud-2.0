from __future__ import annotations

import base64
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from .quality import extract_wav_pcm, is_corrupted_pcm
from .schemas import dialogue_to_higgs_text


@dataclass
class HiggsResult:
    sample_id: str
    audio_path: str | None
    ok: bool
    attempts: int
    error: str | None
    quality: dict[str, Any]
    elapsed_s: float


class HiggsTTSClient:
    def __init__(
        self,
        api_url: str,
        output_dir: str | Path,
        timeout_s: int = 120,
        sample_rate: int = 24000,
        max_retries: int = 3,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.output_dir = Path(output_dir)
        self.timeout_s = timeout_s
        self.sample_rate = sample_rate
        self.max_retries = max_retries

    def synthesize_dialogue(self, dialogue: dict[str, Any]) -> HiggsResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sample_id = str(dialogue["sample_id"])
        target = self.output_dir / f"{sample_id}.wav"
        text = dialogue.get("higgs_text") or dialogue_to_higgs_text(dialogue)
        fallback_texts = _fallback_texts(text)
        start = time.time()
        last_error: str | None = None
        last_quality: dict[str, Any] = {}

        for attempt, candidate_text in enumerate(fallback_texts[: self.max_retries], start=1):
            try:
                wav_bytes = self._request(candidate_text, dialogue)
                corrupted, quality = is_corrupted_pcm(extract_wav_pcm(wav_bytes), self.sample_rate)
                last_quality = quality
                if corrupted:
                    last_error = "quality_gate_failed"
                    continue
                target.write_bytes(wav_bytes)
                return HiggsResult(sample_id, str(target), True, attempt, None, quality, time.time() - start)
            except Exception as exc:
                last_error = str(exc)
                time.sleep(min(2**attempt, 8))

        return HiggsResult(sample_id, None, False, min(len(fallback_texts), self.max_retries), last_error, last_quality, time.time() - start)

    def _request(self, text: str, dialogue: dict[str, Any]) -> bytes:
        payload = {
            "input": text,
            "voice": dialogue.get("metadata", {}).get("voice", "default"),
            "response_format": "wav",
        }
        response = requests.post(self.api_url, json=payload, timeout=self.timeout_s)
        response.raise_for_status()
        ctype = response.headers.get("content-type", "")
        if "application/json" in ctype:
            data = response.json()
            if "audio" in data:
                return base64.b64decode(data["audio"])
            if "audio_base64" in data:
                return base64.b64decode(data["audio_base64"])
            raise ValueError(f"Higgs response has no audio field: {sorted(data)}")
        return response.content


def _fallback_texts(text: str) -> list[str]:
    no_emotion = re.sub(r"<\|emotion:[^|]*\|>\s*", "", text).strip()
    compact = re.sub(r"\s+", " ", no_emotion).strip()
    out = [text]
    if no_emotion and no_emotion != text:
        out.append(no_emotion)
    if compact and compact not in out:
        out.append(compact)
    return out
