.PHONY: setup run test lint seed reset

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	cp -n .env.example .env || true

run:
	flask --app run.py run --debug

seed:
	flask --app run.py seed

reset:
	flask --app run.py reset-db

test:
	pytest -q

lint:
	ruff check .
