TECTONIC ?= tectonic
PYTHON ?= python

.PHONY: all figures class-panel-figures comparisons
all: paper.pdf

paper.pdf: paper.tex $(wildcard figures/*.pdf) figures/historical_time.png figures/first_case_width.png
	$(TECTONIC) paper.tex --keep-logs

figures:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) build_figures.py

class-panel-figures:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) build_class_panel_figures.py

comparisons:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) summarize_model_comparisons.py
