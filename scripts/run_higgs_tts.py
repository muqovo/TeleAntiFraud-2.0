from __future__ import annotations

import argparse
import os
from pathlib import Path

from teleantifraud2_pipeline.io import load_config, read_json, write_json
from teleantifraud2_pipeline.tts_higgs import HiggsTTSClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize dialogues with a Higgs V3-compatible TTS endpoint.")
    parser.add_argument("--config", default="configs/pipeline.demo.yaml")
    parser.add_argument("--input", default=None)
    parser.add_argument("--output-manifest", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    tts_cfg = cfg.get("tts", {})
    api_url = os.environ.get(tts_cfg.get("api_url_env", "HIGGS_TTS_API_URL"), tts_cfg.get("api_url", ""))
    if not api_url:
        raise SystemExit("Set HIGGS_TTS_API_URL or tts.api_url before running synthesis.")

    input_path = args.input or cfg.get("generation", {}).get("output_path", "outputs/demo/dialogues.json")
    manifest_path = args.output_manifest or tts_cfg.get("manifest_path", "outputs/demo/tts_manifest.json")
    dialogues = read_json(input_path)
    if args.limit is not None:
        dialogues = dialogues[: args.limit]

    client = HiggsTTSClient(
        api_url=api_url,
        output_dir=tts_cfg.get("audio_dir", "outputs/demo/audio_raw"),
        timeout_s=int(tts_cfg.get("timeout_s", 120)),
        max_retries=int(tts_cfg.get("max_retries", 3)),
    )
    manifest = [result.__dict__ for result in (client.synthesize_dialogue(d) for d in dialogues)]
    write_json(manifest_path, manifest)
    ok = sum(1 for row in manifest if row.get("ok"))
    print(f"Synthesized {ok}/{len(manifest)} files; manifest: {Path(manifest_path)}")


if __name__ == "__main__":
    main()
