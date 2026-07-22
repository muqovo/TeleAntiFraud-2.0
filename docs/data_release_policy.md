# Data Release Policy

This repository is intended for code release. Do not commit full audio snapshots, model checkpoints, API keys, private speaker-reference audio, or raw provider responses containing secrets.

Recommended public contents:

- source code under `src/`
- scripts under `scripts/`
- reproducible configuration templates under `configs/`
- tiny non-sensitive examples under `examples/`
- documentation under `docs/`

Recommended external artifacts:

- frozen V1/V2 benchmark audio
- complete snapshot manifests
- full ASR transcripts and model responses
- human-evaluation packets

When publishing external artifacts, keep fraud-context labels and usage restrictions attached. Synthetic scam calls should not be redistributed as ordinary speech data.
