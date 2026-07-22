from __future__ import annotations

import argparse
from pathlib import Path

from teleantifraud2_pipeline.io import load_config, read_json, write_json
from teleantifraud2_pipeline.snapshot import build_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze dialogues and audio metadata into a snapshot manifest.")
    parser.add_argument("--config", default="configs/pipeline.demo.yaml")
    parser.add_argument("--dialogues", default=None)
    parser.add_argument("--tts-manifest", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    snapshot_cfg = cfg.get("snapshot", {})
    dialogues_path = args.dialogues or cfg.get("generation", {}).get("output_path", "outputs/demo/dialogues.json")
    tts_manifest_path = args.tts_manifest or cfg.get("tts", {}).get("manifest_path", "outputs/demo/tts_manifest.json")
    output_path = args.output or snapshot_cfg.get("output_path", "outputs/demo/snapshot_manifest.json")
    audio_manifest = read_json(tts_manifest_path) if Path(tts_manifest_path).exists() else []
    rows = build_snapshot(read_json(dialogues_path), audio_manifest, snapshot_cfg.get("snapshot_id", "demo-v0"))
    write_json(output_path, rows)
    print(f"Wrote {len(rows)} snapshot rows to {Path(output_path)}")


if __name__ == "__main__":
    main()
