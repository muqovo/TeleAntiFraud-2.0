from __future__ import annotations

import argparse
from pathlib import Path

from teleantifraud2_pipeline.evaluation import evaluate_openai_compatible
from teleantifraud2_pipeline.io import load_config, read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ASR/transcript + LLM fraud classification.")
    parser.add_argument("--config", default="configs/pipeline.demo.yaml")
    parser.add_argument("--snapshot", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    eval_cfg = cfg.get("evaluation", {})
    snapshot_path = args.snapshot or cfg.get("snapshot", {}).get("output_path", "outputs/demo/snapshot_manifest.json")
    output_path = args.output or eval_cfg.get("output_path", "outputs/demo/text_eval_results.json")
    rows = read_json(snapshot_path)
    result = evaluate_openai_compatible(
        rows,
        model=eval_cfg["model"],
        base_url=eval_cfg["base_url"],
        api_key_env=eval_cfg.get("api_key_env", "OPENAI_API_KEY"),
        prompt_language=eval_cfg.get("prompt_language", "cn"),
        sleep_s=float(eval_cfg.get("sleep_s", 0)),
    )
    write_json(output_path, result)
    print(f"Wrote evaluation results to {Path(output_path)}")


if __name__ == "__main__":
    main()
