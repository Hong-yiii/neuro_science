TECTONIC ?= tectonic
PYTHON ?= python

.PHONY: all figures
all: paper.pdf

paper.pdf: paper.tex $(wildcard figures/*.pdf) figures/historical_time.png figures/first_case_width.png
	$(TECTONIC) paper.tex --keep-logs

figures:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) build_figures.py
