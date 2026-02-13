from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

from .parsing import parse_base_name
from .dataio import load_npy
from .degen import magnetization_degeneracies
from .osm import epsilon_from_PR, solve_beta_energy_constraint, predict_p
from .metrics import total_variation, kl_divergence, linf


def build_manifest(data_root: str | Path) -> pd.DataFrame:
    """Scan data_root for matching P/R/eigenvalues triples and return a manifest dataframe."""
    data_root = Path(data_root)
    pj_dir = data_root / "Pj_DE"
    rj_dir = data_root / "Rj_DE"
    if not pj_dir.exists() or not rj_dir.exists():
        raise FileNotFoundError(f"Expected Pj_DE/ and Rj_DE/ under {data_root}")

    p_files = list(pj_dir.glob("*_P_DE.npy"))
    rows: list[dict] = []
    for pf in p_files:
        base = pf.name.replace("_P_DE.npy", "")
        rf = rj_dir / f"{base}_R_DE.npy"
        ev_pf = pj_dir / f"{base}_unique_eigenvalues.npy"
        ev_rf = rj_dir / f"{base}_unique_eigenvalues.npy"
        if not rf.exists() or not ev_pf.exists() or not ev_rf.exists():
            continue

        key = parse_base_name(base)
        rows.append(
            dict(
                base=base,
                model=key.model,
                N=key.N,
                J=key.J,
                h=key.h,
                alpha=key.alpha,
                theta=key.theta,
                axis=key.axis,
                P_path=str(pf),
                R_path=str(rf),
                eig_path=str(ev_pf),
            )
        )

    df = pd.DataFrame(rows)
    if len(df) == 0:
        raise RuntimeError(f"No complete P/R/eigenvalues triples found under {data_root}")
    df = df.sort_values(["model", "N", "h", "alpha", "theta", "axis"]).reset_index(drop=True)
    return df


def fit_one_row(row: pd.Series) -> dict:
    P = load_npy(row["P_path"]).astype(float)
    R = load_npy(row["R_path"]).astype(float)
    eig = load_npy(row["eig_path"]).astype(float)

    d = magnetization_degeneracies(int(row["N"]), eig)
    eps = epsilon_from_PR(P, R, floor=0.0)

    E_target = float(np.sum(R))  # from Eq. (8): sum_j p_j eps_j = sum_j R_j

    fit = solve_beta_energy_constraint(d, eps, E_target)
    p_pred, Z = predict_p(d[d > 0], eps[d > 0], fit.beta) if np.any(d<=0) else predict_p(d, eps, fit.beta)

    # Metrics against the original P: ensure matching shapes if d had zeros (unlikely)
    if len(p_pred) != len(P):
        # Reconstruct p_pred into full length with zeros where d==0
        full = np.zeros_like(P, dtype=float)
        full[d > 0] = p_pred
        p_pred = full

    return dict(
        base=row["base"],
        model=row["model"],
        N=int(row["N"]),
        J=float(row["J"]),
        h=float(row["h"]),
        alpha=(None if pd.isna(row["alpha"]) else float(row["alpha"])),
        theta=int(row["theta"]),
        axis=row["axis"],
        beta_A=float(fit.beta),
        Z_A=float(Z),
        Ebar_DE=float(E_target),
        TV=total_variation(P, p_pred),
        KL=kl_divergence(P, p_pred),
        Linf=linf(P, p_pred),
        converged=bool(fit.converged),
        iters=int(fit.iters),
        n_outcomes=int(len(P)),
    )


def fit_manifest(manifest: pd.DataFrame) -> pd.DataFrame:
    rows = [fit_one_row(manifest.iloc[i]) for i in range(len(manifest))]
    return pd.DataFrame(rows)
