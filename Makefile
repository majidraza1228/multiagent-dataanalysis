.PHONY: install train serve ui monitor test grade

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

grade:
	python grader.py
