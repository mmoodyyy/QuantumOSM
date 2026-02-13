# QuantumOSM

Publishable, reproducible analysis pipeline for **Observable Statistical Mechanics (OSM)** tests on
exact-diagonalization (DE) data from spin chains.

This repository:
- ingests `*.npy` datasets containing P^DE_j and R^DE_j for a chosen observable,
- reconstructs the **observable-specific energies** ε_j = R^DE_j / P^DE_j,
- solves for β_A using the OSM energy constraint,
- produces OSM-predicted stationary PDFs and quantitative error metrics,
- generates paper-ready grid plots (3 rows = axis, 4 columns = initial state / θ).

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### 1) Put the data in the expected location

Unzip your dataset to:

```
data/raw/de/Data_michael_DE/
  Pj_DE/*.npy
  Rj_DE/*.npy
```

### 2) Build a manifest (one row per configuration)

```bash
python scripts/01_build_manifest.py \
  --data-root data/raw/de/Data_michael_DE \
  --out results/metrics/manifest.csv
```

### 3) Fit OSM and compute metrics

```bash
python scripts/02_fit_osm.py \
  --manifest results/metrics/manifest.csv \
  --out results/metrics/osm_metrics.csv
```

### 4) Make paper-ready 3×4 grids (default: N=14)

```bash
python scripts/03_make_grids.py \
  --manifest results/metrics/manifest.csv \
  --metrics results/metrics/osm_metrics.csv \
  --N 14 \
  --outdir results/figures
```

## Data format (what the scripts expect)

For each configuration there are three files sharing the same **base name**:

- `..._P_DE.npy` : the diagonal-ensemble outcome distribution P^DE_j over unique eigenvalues
- `..._R_DE.npy` : R^DE_j (used to reconstruct ε_j via Eq. (8) of the OSM paper)
- `..._unique_eigenvalues.npy` : unique eigenvalues of the measured observable (e.g. global magnetization)

Example base name:
`LR_DE_N=14_J=-1.00_h=0.20_alpha=1.60_theta=3_axis=Z`

## Notes on committing data

If `*.npy` files become large, use **Git LFS** (recommended):
```bash
git lfs install
git lfs track "*.npy"
git add .gitattributes
```

## License

MIT. See `LICENSE`.
