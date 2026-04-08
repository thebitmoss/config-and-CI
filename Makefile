.PHONY: test lint ci run

PYTHON ?= python3
SAMPLE_CSV ?= data/sample_sales.csv

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

ci: lint test

run:
	$(PYTHON) sales_summary.py $(SAMPLE_CSV)
