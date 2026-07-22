from __future__ import annotations

import array
import math
from pathlib import Path


def extract_wav_pcm(wav_bytes: bytes) -> bytes:
    idx = wav_bytes.find(b"data")
    if idx >= 0 and idx + 8 < len(wav_bytes):
        return wav_bytes[idx + 8 :]
    return wav_bytes[44:] if len(wav_bytes) > 44 else b""


def is_corrupted_pcm(pcm: bytes, sample_rate: int = 24000) -> tuple[bool, dict[str, float]]:
    if len(pcm) < 1000:
        return True, {"reason": "too_short", "bytes": float(len(pcm))}

    samples = array.array("h")
    samples.frombytes(pcm[: len(pcm) - (len(pcm) % 2)])
    if not samples:
        return True, {"reason": "empty"}

    n = len(samples)
    peak = max(abs(s) for s in samples)
    rms = math.sqrt(sum(s * s for s in samples) / n)
    near_zero_ratio = sum(1 for s in samples if abs(s) < 100) / n
    clipping_ratio = sum(1 for s in samples if abs(s) >= 32700) / n
    zcr = sum(1 for i in range(1, n) if (samples[i] >= 0) != (samples[i - 1] >= 0))
    zcr_ratio = zcr / n
    total_abs = sum(abs(s) for s in samples) + 1
    hf_ratio = sum(abs(samples[i] - samples[i - 1]) for i in range(1, n)) / total_abs
    crest = peak / (rms + 1)
    duration_s = n / sample_rate

    metrics = {
        "duration_s": round(duration_s, 4),
        "peak": float(peak),
        "rms": round(rms, 4),
        "near_zero_ratio": round(near_zero_ratio, 6),
        "clipping_ratio": round(clipping_ratio, 6),
        "zcr_ratio": round(zcr_ratio, 6),
        "hf_ratio": round(hf_ratio, 6),
        "crest": round(crest, 6),
    }

    corrupted = (
        (rms < 30 and peak < 200)
        or rms > 18000
        or near_zero_ratio > 0.75
        or rms < 300
        or clipping_ratio > 0.08
        or zcr_ratio > 0.48
        or hf_ratio > 1.8
        or (crest < 5.0 and rms > 300)
        or (zcr_ratio > 0.2 and rms < 800)
        or (zcr_ratio > 0.15 and hf_ratio > 1.0 and crest < 8.0)
    )
    return corrupted, metrics


def inspect_wav(path: str | Path, sample_rate: int = 24000) -> tuple[bool, dict[str, float]]:
    wav_bytes = Path(path).read_bytes()
    return is_corrupted_pcm(extract_wav_pcm(wav_bytes), sample_rate=sample_rate)
