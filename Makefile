.PHONY: install test lint manifest fit grids summary clean

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .

manifest:
	python scripts/01_build_manifest.py --data-root data/raw/de/Data_michael_DE --out results/metrics/manifest.csv

fit:
	python scripts/02_fit_osm.py --manifest results/metrics/manifest.csv --out results/metrics/osm_metrics.csv

grids:
	python scripts/03_make_grids.py --manifest results/metrics/manifest.csv --metrics results/metrics/osm_metrics.csv --N 14 --outdir results/figures

summary:
	python scripts/04_summary_tables.py --metrics results/metrics/osm_metrics.csv --out results/metrics/summary.csv

clean:
	rm -rf results
