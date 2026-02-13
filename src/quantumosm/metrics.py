from __future__ import annotations

import numpy as np


def total_variation(p: np.ndarray, q: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(np.asarray(p) - np.asarray(q))))


def linf(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(p) - np.asarray(q))))


def kl_divergence(p: np.ndarray, q: np.ndarray, *, eps: float = 1e-300) -> float:
    """KL(p || q) with safeguards."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    mask = p > 0
    return float(np.sum(p[mask] * (np.log(p[mask] + eps) - np.log(q[mask] + eps))))
