from __future__ import annotations

import argparse
from pathlib import Path

from teleantifraud2_pipeline.io import read_json, write_json
from teleantifraud2_pipeline.metrics import binary_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute all-FRAUD and all-NONFRAUD baseline metrics.")
    parser.add_argument("--snapshot", default="outputs/demo/snapshot_manifest.json")
    parser.add_argument("--output", default="outputs/demo/baseline_metrics.json")
    args = parser.parse_args()

    rows = read_json(args.snapshot)
    y_true = [1 if r.get("is_fraud") else 0 for r in rows]
    result = {
        "all_fraud": binary_metrics(y_true, [1] * len(y_true)),
        "all_nonfraud": binary_metrics(y_true, [0] * len(y_true)),
    }
    write_json(args.output, result)
    print(f"Wrote baselines to {Path(args.output)}")


if __name__ == "__main__":
    main()
