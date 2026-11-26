PYTHON ?= python3
TABLE ?= chain
PORT ?= 8000

.PHONY: test serve experiment compare
test:
	$(PYTHON) -m unittest discover -s tests -v
serve:
	$(PYTHON) -m src.server --table $(TABLE) --port $(PORT)
experiment:
	$(PYTHON) -m experiments.probe_experiment
compare:
	$(PYTHON) -m experiments.compare_experiment
