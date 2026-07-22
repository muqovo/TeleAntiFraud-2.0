# Paper Pipeline Commands

The paper-aligned path uses API generation first. The offline generator is only a smoke-test fallback.

## 1. API Mixed-Tree Generation

```powershell
$env:OPENAI_API_KEY="your-key"
$env:PYTHONPATH="src"
python scripts/run_generation_api.py --config configs/pipeline.api.example.yaml
```

For another OpenAI-compatible provider, edit `configs/pipeline.api.example.yaml`:

```yaml
generation:
  llm:
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key_env: DASHSCOPE_API_KEY
    model: qwen-plus
```

## 2. Higgs V3 Synthesis

```powershell
$env:HIGGS_TTS_API_URL="http://HOST:PORT/v1/audio/speech"
$env:PYTHONPATH="src"
python scripts/run_higgs_tts.py --config configs/pipeline.api.example.yaml
```

## 3. Freeze Snapshot

```powershell
$env:PYTHONPATH="src"
python scripts/build_snapshot.py --config configs/pipeline.api.example.yaml
```

## 4. Baseline Audit

```powershell
$env:PYTHONPATH="src"
python scripts/run_baseline_eval.py `
  --snapshot outputs/api_demo/snapshot_manifest.json `
  --output outputs/api_demo/baseline_metrics.json
```

## 5. OpenAI-Compatible Text Evaluation

```powershell
$env:OPENAI_API_KEY="your-key"
$env:PYTHONPATH="src"
python scripts/run_text_eval.py --config configs/pipeline.api.example.yaml
```
