#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# Allow running from a fresh clone without `pip install -e .`
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import argparse
from pathlib import Path

from quantumosm.dataio import ensure_dir
from quantumosm.pipeline import build_manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True, help="Path containing Pj_DE/ and Rj_DE/")
    ap.add_argument("--out", required=True, help="Output CSV path for manifest")
    args = ap.parse_args()

    df = build_manifest(Path(args.data_root))
    out = Path(args.out)
    ensure_dir(out.parent)
    df.to_csv(out, index=False)
    print(f"Wrote manifest with {len(df)} rows to {out}")


if __name__ == "__main__":
    main()