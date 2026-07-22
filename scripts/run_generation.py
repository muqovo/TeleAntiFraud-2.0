from __future__ import annotations

import argparse
from pathlib import Path

from teleantifraud2_pipeline.generation import generate_from_scenarios
from teleantifraud2_pipeline.io import load_config, read_jsonl, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TeleAntiFraud 2.0 mixed-tree dialogues.")
    parser.add_argument("--config", default="configs/pipeline.demo.yaml")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    generation = cfg.get("generation", {})
    input_path = generation.get("scenario_path", "examples/mini_scenarios.jsonl")
    output_path = args.output or generation.get("output_path", "outputs/demo/dialogues.json")
    scenarios = read_jsonl(input_path)
    rows = generate_from_scenarios(
        scenarios,
        depth=int(generation.get("tree_depth", 4)),
        branch_factor=int(generation.get("branch_factor", 3)),
        seed=int(generation.get("seed", 13)),
    )
    write_json(output_path, rows)
    print(f"Wrote {len(rows)} dialogues to {Path(output_path)}")


if __name__ == "__main__":
    main()
