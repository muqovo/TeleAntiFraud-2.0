# Release Completeness Checklist

## Included

- API-based mixed-tree generation entry point: `scripts/run_generation_api.py`
- Offline template demo for smoke tests: `scripts/run_generation.py`
- OpenAI-compatible six-agent generator: `src/teleantifraud2_pipeline/llm_generation.py`
- Higgs V3-compatible TTS client: `src/teleantifraud2_pipeline/tts_higgs.py`
- Signal-level audio quality gates: `src/teleantifraud2_pipeline/quality.py`
- Snapshot manifest builder: `src/teleantifraud2_pipeline/snapshot.py`
- Binary collapse-aware metrics and baselines: `src/teleantifraud2_pipeline/metrics.py`
- OpenAI-compatible text/ASR evaluation helper: `src/teleantifraud2_pipeline/evaluation.py`
- Config templates for offline and API paths: `configs/`
- Tiny safe scenarios for smoke tests: `examples/`
- Data release safety policy: `docs/data_release_policy.md`

## Deliberately Excluded From Code Release

- Full V1/V2 audio snapshots
- Private reference voice pool audio
- Model checkpoints
- API keys and server-specific paths
- Full provider response logs
- Large generated outputs and zip archives

## Still Requires Local Configuration

- `OPENAI_API_KEY` or another configured OpenAI-compatible provider key for API generation/evaluation
- `HIGGS_TTS_API_URL` for speech synthesis
- External storage location for full benchmark audio and manifests
