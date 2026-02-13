#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# Allow running from a fresh clone without `pip install -e .`
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from quantumosm.dataio import load_npy, ensure_dir
from quantumosm.degen import magnetization_degeneracies
from quantumosm.osm import epsilon_from_PR, predict_p
from quantumosm.plotting import plot_pdf_comparison, save_figure


AXES = ["X", "Y", "Z"]
THETAS = [0, 1, 2, 3]


def make_grid(manifest: pd.DataFrame, metrics: pd.DataFrame, *, model: str, h: float, N: int, alpha: float | None, outdir: Path) -> None:
    sub = manifest[(manifest["model"] == model) & (manifest["h"] == h) & (manifest["N"] == N)].copy()
    if model == "LR":
        sub = sub[np.isclose(sub["alpha"].astype(float), float(alpha))]

    beta_map = {r["base"]: float(r["beta_A"]) for _, r in metrics.iterrows()}

    fig, axs = plt.subplots(nrows=3, ncols=4, figsize=(12, 7), sharex=False, sharey=False)

    for i, axis in enumerate(AXES):
        for j, theta in enumerate(THETAS):
            ax = axs[i, j]
            row = sub[(sub["axis"] == axis) & (sub["theta"] == theta)]
            if len(row) != 1:
                ax.axis("off")
                continue

            row = row.iloc[0]
            P = load_npy(row["P_path"]).astype(float)
            R = load_npy(row["R_path"]).astype(float)
            eig = load_npy(row["eig_path"]).astype(float)

            d = magnetization_degeneracies(int(row["N"]), eig)
            eps = epsilon_from_PR(P, R)
            beta = beta_map[row["base"]]

            P_pred, _ = predict_p(d, eps, beta)
            title = f"{axis}, θ={theta}"
            plot_pdf_comparison(ax, eig, P, P_pred, title)

            if i == 0 and j == 0:
                ax.legend(fontsize=8, frameon=False)

    grid_title = f"{model}  N={N}  h={h:.2f}" + (f"  α={alpha:.2f}" if alpha is not None else "")
    fig.suptitle(grid_title, fontsize=12)

    fname = f"grid_{model}_N{N}_h{h:.2f}" + (f"_a{alpha:.2f}" if alpha is not None else "") + ".png"
    save_figure(fig, outdir / fname, dpi=300)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="CSV produced by 01_build_manifest.py")
    ap.add_argument("--metrics", required=True, help="CSV produced by 02_fit_osm.py")
    ap.add_argument("--N", type=int, default=14, help="System size for grids")
    ap.add_argument("--alpha", type=float, default=1.60, help="Alpha for LR grids (ignored for SR)")
    ap.add_argument("--outdir", default="results/figures", help="Output folder for figures")
    args = ap.parse_args()

    manifest = pd.read_csv(args.manifest)
    metrics = pd.read_csv(args.metrics)
    outdir = ensure_dir(args.outdir)

    make_grid(manifest, metrics, model="SR", h=0.20, N=args.N, alpha=None, outdir=outdir)
    make_grid(manifest, metrics, model="SR", h=1.20, N=args.N, alpha=None, outdir=outdir)
    make_grid(manifest, metrics, model="LR", h=0.20, N=args.N, alpha=args.alpha, outdir=outdir)
    make_grid(manifest, metrics, model="LR", h=1.20, N=args.N, alpha=args.alpha, outdir=outdir)

    print(f"Wrote grids to: {outdir}")


if __name__ == "__main__":
    main()