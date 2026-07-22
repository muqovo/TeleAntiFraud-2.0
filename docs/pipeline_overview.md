# Pipeline Overview

TeleAntiFraud 2.0 is organized as a release pipeline rather than a single monolithic script.

1. `generation`: builds profile-grounded mixed plot trees. Fraud and near-domain non-fraud leaves share the same opening and risk vocabulary before diverging at controlled branch states.
2. `tts_higgs`: converts each dialogue to Higgs V3 input text with speaker and emotion tokens, calls a configurable HTTP endpoint, and retries with weaker conditioning when quality gates fail.
3. `quality`: applies fixed signal-level checks for silence, near-silence, clipping, high zero-crossing rate, and electrical-noise-like artifacts.
4. `snapshot`: freezes sample labels, text, audio paths, checksums, speaker metadata, quality metadata, and generation provenance.
5. `evaluation`: evaluates frozen manifests with a deterministic two-label output contract: `FRAUD` or `NONFRAUD`.

The default demo is intentionally small and offline-friendly through generation and snapshot building. Higgs TTS and model evaluation require external services configured through environment variables.
