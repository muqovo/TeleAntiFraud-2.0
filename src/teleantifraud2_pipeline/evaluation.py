from __future__ import annotations

import os
import re
import time
from typing import Any

from openai import OpenAI

from .metrics import binary_metrics


CN_PROMPT = "请判断下面电话对话是否为电信诈骗。只输出 FRAUD 或 NONFRAUD。"
EN_PROMPT = "Decide whether the following call dialogue is telecom fraud. Output only FRAUD or NONFRAUD."


def parse_label(text: str) -> int | None:
    clean = text.strip().upper()
    if re.search(r"\bNON[-_ ]?FRAUD\b", clean):
        return 0
    if re.search(r"\bFRAUD\b", clean):
        return 1
    if "非诈骗" in clean or "不是诈骗" in clean:
        return 0
    if "诈骗" in clean:
        return 1
    return None


def text_from_dialogue(row: dict[str, Any]) -> str:
    if row.get("transcript"):
        return str(row["transcript"])
    if row.get("higgs_text"):
        return str(row["higgs_text"])
    return "\n".join(f"{t.get('role')}: {t.get('text')}" for t in row.get("turns", []))


def evaluate_openai_compatible(
    rows: list[dict[str, Any]],
    model: str,
    base_url: str,
    api_key_env: str,
    prompt_language: str = "cn",
    sleep_s: float = 0.0,
) -> dict[str, Any]:
    client = OpenAI(api_key=os.environ[api_key_env], base_url=base_url)
    prompt = CN_PROMPT if prompt_language.lower() == "cn" else EN_PROMPT
    predictions: list[int] = []
    y_true: list[int] = []
    details: list[dict[str, Any]] = []
    for row in rows:
        content = f"{prompt}\n\n{text_from_dialogue(row)[:4000]}"
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            temperature=0,
            max_tokens=16,
        )
        raw = response.choices[0].message.content or ""
        pred = parse_label(raw)
        y = 1 if row.get("is_fraud") else 0
        y_true.append(y)
        predictions.append(0 if pred is None else pred)
        details.append({"sample_id": row.get("sample_id"), "label": y, "prediction": pred, "raw": raw})
        if sleep_s:
            time.sleep(sleep_s)
    return {"metrics": binary_metrics(y_true, predictions), "details": details}
