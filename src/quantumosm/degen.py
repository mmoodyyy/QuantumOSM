from __future__ import annotations

from math import comb
import numpy as np


def magnetization_degeneracies(N: int, eigenvalues: np.ndarray) -> np.ndarray:
    """
    Degeneracies for total magnetization M = sum_i sigma_i^z (or x/y rotated versions),
    where eigenvalues are in steps of 2: -N, -N+2, ..., N.

    For eigenvalue m, degeneracy is C(N, (N+m)/2).
    """
    d = np.zeros_like(eigenvalues, dtype=float)
    for i, m in enumerate(eigenvalues):
        m_int = int(round(float(m)))
        k2 = N + m_int
        if k2 % 2 != 0:
            d[i] = 0.0
            continue
        k = k2 // 2
        if k < 0 or k > N:
            d[i] = 0.0
            continue
        d[i] = float(comb(N, k))
    return d
