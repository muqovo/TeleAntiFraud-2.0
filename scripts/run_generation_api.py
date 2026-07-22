from __future__ import annotations

import argparse
from pathlib import Path

from teleantifraud2_pipeline.io import load_config, read_jsonl, write_json
from teleantifraud2_pipeline.llm_generation import OpenAICompatibleGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate mixed-tree dialogues with an OpenAI-compatible API.")
    parser.add_argument("--config", default="configs/pipeline.api.example.yaml")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    generation = cfg.get("generation", {})
    llm = generation.get("llm", {})
    input_path = generation.get("scenario_path", "examples/mini_scenarios.jsonl")
    output_path = args.output or generation.get("output_path", "outputs/api_demo/dialogues.json")

    generator = OpenAICompatibleGenerator(
        base_url=llm["base_url"],
        api_key_env=llm.get("api_key_env", "OPENAI_API_KEY"),
        model=llm["model"],
        temperature=float(llm.get("temperature", 0.7)),
        max_retries=int(llm.get("max_retries", 3)),
        sleep_s=float(llm.get("sleep_s", 0)),
    )
    rows = generator.generate(
        read_jsonl(input_path),
        depth=int(generation.get("tree_depth", 4)),
        branch_factor=int(generation.get("branch_factor", 3)),
        seed=int(generation.get("seed", 13)),
    )
    write_json(output_path, rows)
    print(f"Wrote {len(rows)} API-generated dialogues to {Path(output_path)}")


if __name__ == "__main__":
    main()
