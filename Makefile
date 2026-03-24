.PHONY: install train serve ui monitor test grade eval eval-compare eval-generate

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
	pytest tests/

eval:
	python3 evals/run_eval.py

eval-compare:
	python3 evals/compare_adapters.py

eval-generate:
	python3 evals/generate_cases.py

grade:
	python grader.py
