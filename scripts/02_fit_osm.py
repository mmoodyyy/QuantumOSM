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
from quantumosm.pipeline import fit_manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="CSV produced by 01_build_manifest.py")
    ap.add_argument("--out", required=True, help="Output CSV for metrics")
    args = ap.parse_args()

    manifest = pd.read_csv(args.manifest)
    metrics = fit_manifest(manifest)

    out = Path(args.out)
    ensure_dir(out.parent)
    metrics.to_csv(out, index=False)
    print(f"Wrote metrics for {len(metrics)} rows to {out}")


if __name__ == "__main__":
    main()