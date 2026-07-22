# GitHub Upload Notes

Upload the contents of this directory as the repository root.

Recommended repository name:

```text
teleantifraud2-pipeline
```

Before uploading, confirm these files are present:

```text
README.md
pyproject.toml
requirements.txt
requirements-api.txt
requirements-eval.txt
.env.example
.gitignore
configs/
docs/
examples/
scripts/
src/
```

Do not upload:

```text
outputs/
audio_raw/
data/
checkpoints/
*.wav
*.zip
.env
```

Local Git commands:

```bash
git init
git add .
git commit -m "Release TeleAntiFraud 2.0 pipeline code"
git branch -M main
git remote add origin https://github.com/<owner>/teleantifraud2-pipeline.git
git push -u origin main
```

Paper-aligned pipeline commands are documented in:

```text
docs/paper_pipeline_commands.md
```
