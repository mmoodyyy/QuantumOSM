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

from quantumosm.dataio import ensure_dir


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", required=True, help="CSV produced by 02_fit_osm.py")
    ap.add_argument("--out", default="results/metrics/summary.csv", help="Output CSV for grouped summary")
    args = ap.parse_args()

    df = pd.read_csv(args.metrics)
    grp_cols = ["model", "N", "h", "alpha"]
    out = (
        df.groupby(grp_cols, dropna=False)
        .agg(
            TV_mean=("TV", "mean"),
            TV_median=("TV", "median"),
            KL_mean=("KL", "mean"),
            Linf_mean=("Linf", "mean"),
            n=("base", "count"),
            converged_frac=("converged", "mean"),
        )
        .reset_index()
        .sort_values(grp_cols)
    )

    outpath = Path(args.out)
    ensure_dir(outpath.parent)
    out.to_csv(outpath, index=False)
    print(f"Wrote summary to {outpath}")


if __name__ == "__main__":
    main()