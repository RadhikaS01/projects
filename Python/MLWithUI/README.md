---
title: "Laptop Price Predictor"
sdk: gradio
language: en
license: mit
tags:
  - machine-learning
  - regression
  - gradio
emoji: "💻"
---

# Laptop Price Predictor (MLWithUI)

Step-by-step:

1. Create virtual environment and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Train the model (this reads `resources/laptop_data.csv` and saves the pipeline to `models/pipeline.joblib`):

```bash
python src/train_model.py
```

3. Start the Gradio app locally:

```bash
python app.py
```

To deploy to your Hugging Face Space, set `HF_TOKEN` and run:

```bash
python deploy_to_hf.py --repo_id RadhikaS01/MLSpace
```

Notes:
- The `sdk: gradio` frontmatter is required by Hugging Face Spaces to detect the app type.
- Do not commit your `HF_TOKEN`; use environment variables or `huggingface-cli login`.
