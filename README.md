# TeleAntiFraud 2.0 Pipeline

This repository contains the code-focused release pipeline for TeleAntiFraud 2.0: mixed-tree dialogue generation, Higgs V3 speech synthesis, audio quality gates, frozen snapshot manifests, and evaluation utilities.

The repo intentionally excludes large audio files, model checkpoints, private reference voices, API keys, and full benchmark artifacts. Put those in an external release or data repository.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Install `openai` separately if you want to run `scripts/run_text_eval.py`.

## Demo

Generate a tiny mixed-tree dialogue set:

```bash
python scripts/run_generation.py --config configs/pipeline.demo.yaml
```

Build a snapshot manifest without audio:

```bash
python scripts/build_snapshot.py --config configs/pipeline.demo.yaml
python scripts/run_baseline_eval.py --snapshot outputs/demo/snapshot_manifest.json
```

Run Higgs V3 synthesis when a compatible endpoint is available:

```bash
export HIGGS_TTS_API_URL="http://HOST:PORT/v1/audio/speech"
python scripts/run_higgs_tts.py --config configs/pipeline.demo.yaml
python scripts/build_snapshot.py --config configs/pipeline.demo.yaml
```

Run an OpenAI-compatible text evaluation:

```bash
export OPENAI_API_KEY="..."
python scripts/run_text_eval.py --config configs/pipeline.demo.yaml
```

## Repository Layout

```text
configs/      reproducible config templates
docs/         release notes and data policy
examples/     tiny safe examples
scripts/      command-line entry points
src/          installable Python package
```

## Paper Alignment

- Profile-grounded mixed plot tree: `teleantifraud2_pipeline.generation`
- Higgs V3 role/emotion speech: `teleantifraud2_pipeline.tts_higgs`
- Fixed audio corruption gates: `teleantifraud2_pipeline.quality`
- Versioned pure-test manifest: `teleantifraud2_pipeline.snapshot`
- Collapse-aware binary metrics: `teleantifraud2_pipeline.metrics`

## Safety

This code is for research evaluation. Keep generated fraud dialogues labeled as synthetic anti-fraud benchmark data, and do not publish private voice references or unlabeled scam-style audio.
