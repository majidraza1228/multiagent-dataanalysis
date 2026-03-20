---
name: project-scaffold
description: ML image classifier project structure, requirements.txt, .gitignore, and Makefile
---

```bash
# create full project structure
mkdir -p ml-image-classifier/{app,model,ui,tests,data,checkpoints,logs,samples,.claude/skills}
```

```
# requirements.txt
torch==2.2.2
torchvision==0.17.2
fastapi==0.111.0
uvicorn[standard]==0.29.0
gradio==4.31.0
mlflow==2.13.0
httpx==0.27.0
pydantic==2.7.1
python-multipart==0.0.9
Pillow==10.3.0
matplotlib==3.9.0
tabulate==0.9.0
```

```
# .gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
*.egg

# ML artifacts
checkpoints/
*.pt
*.pth
*.ckpt
mlruns/
mlflow.db

# Logs & data
logs/
*.jsonl
data/

# Environment
.env
.venv/
venv/
*.env

# IDE
.vscode/
.idea/
*.swp

# macOS
.DS_Store
```

```makefile
# Makefile
.PHONY: install train serve ui monitor test

install:
	pip install -r requirements.txt

train:
	python model/train.py

serve:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

ui:
	python ui/app.py

monitor:
	python monitor_dashboard.py

test:
	python tests/test_api.py
```
