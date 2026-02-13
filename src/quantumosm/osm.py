from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.signal import savgol_filter


@dataclass(frozen=True)
class OSMFit:
    beta: float
    Z: float
    converged: bool
    iters: int
    E_target: float



def stable_eps(P, R, p_floor=1e-12, smooth=True, win=7, poly=2):
    P = np.clip(P, 0.0, None)
    P = P / (P.sum() + 1e-300)

    eps = R / np.maximum(P, p_floor)

    if smooth:
        # fill any infinities/nans conservatively before smoothing
        bad = ~np.isfinite(eps)
        if bad.any():
            idx = np.arange(len(eps))
            good = ~bad
            eps[bad] = np.interp(idx[bad], idx[good], eps[good])

        win = min(win, len(eps) if len(eps) % 2 == 1 else len(eps) - 1)
        win = max(win, 3)  # must be odd >=3
        eps = savgol_filter(eps, window_length=win, polyorder=min(poly, win-1))

    return P, eps

def _softmax_logweights(logw: np.ndarray) -> np.ndarray:
    m = np.max(logw)
    w = np.exp(logw - m)
    return w / np.sum(w)


def predict_p(d: np.ndarray, eps: np.ndarray, beta: float) -> tuple[np.ndarray, float]:
    """Return p_pred and partition function Z(beta)."""
    d = np.asarray(d, dtype=float)
    eps = np.asarray(eps, dtype=float)
    if np.any(d <= 0):
        raise ValueError("Degeneracies must be strictly positive for all outcomes used in prediction.")
    logw = np.log(d) - beta * eps
    p = _softmax_logweights(logw)
    # Stable Z via log-sum-exp style
    m = np.max(logw)
    Z = float(np.sum(np.exp(logw - m)) * np.exp(m))
    return p, Z


def expected_eps(d: np.ndarray, eps: np.ndarray, beta: float) -> float:
    p, _ = predict_p(d, eps, beta)
    return float(np.sum(p * eps))


def solve_beta_energy_constraint(
    d: np.ndarray,
    eps: np.ndarray,
    E_target: float,
    *,
    beta0: float = 0.0,
    max_expand: int = 80,
    max_iter: int = 200,
    tol: float = 1e-12,
) -> OSMFit:
    """
    Solve for beta using the OSM energy constraint:
        sum_j p_beta(j) * eps_j = E_target
    where p_beta(j) ∝ d_j exp(-beta eps_j).
    """
    d = np.asarray(d, dtype=float)
    eps = np.asarray(eps, dtype=float)

    # Remove any zero-degeneracy outcomes (should not happen for magnetization spectrum)
    mask = d > 0
    d = d[mask]
    eps = eps[mask]

    # HUO / degenerate eps: any beta works; choose 0.
    if np.allclose(eps, eps[0]):
        p, Z = predict_p(d, eps, 0.0)
        return OSMFit(beta=0.0, Z=Z, converged=True, iters=0, E_target=E_target)

    def f(beta: float) -> float:
        return expected_eps(d, eps, beta) - E_target

    # Bracket a root by expanding symmetrically around beta0.
    lo = beta0
    hi = beta0
    flo = f(lo)
    step = 1.0
    bracketed = False

    for _ in range(max_expand):
        lo = beta0 - step
        hi = beta0 + step
        flo = f(lo)
        fhi = f(hi)
        if flo == 0.0:
            p, Z = predict_p(d, eps, lo)
            return OSMFit(beta=lo, Z=Z, converged=True, iters=0, E_target=E_target)
        if fhi == 0.0:
            p, Z = predict_p(d, eps, hi)
            return OSMFit(beta=hi, Z=Z, converged=True, iters=0, E_target=E_target)
        if flo * fhi < 0:
            bracketed = True
            break
        step *= 2.0

    if not bracketed:
        # Choose beta minimizing |f| on the explored interval.
        candidates = np.linspace(beta0 - step, beta0 + step, 401)
        vals = np.array([abs(f(b)) for b in candidates])
        beta_best = float(candidates[int(np.argmin(vals))])
        p, Z = predict_p(d, eps, beta_best)
        return OSMFit(beta=beta_best, Z=Z, converged=False, iters=0, E_target=E_target)

    # Bisection
    fhi = f(hi)
    it = 0
    mid = 0.5 * (lo + hi)
    for it in range(1, max_iter + 1):
        mid = 0.5 * (lo + hi)
        fmid = f(mid)
        if abs(fmid) < tol or (hi - lo) < tol:
            p, Z = predict_p(d, eps, mid)
            return OSMFit(beta=mid, Z=Z, converged=True, iters=it, E_target=E_target)
        if flo * fmid < 0:
            hi = mid
            fhi = fmid
        else:
            lo = mid
            flo = fmid

    p, Z = predict_p(d, eps, mid)
    return OSMFit(beta=float(mid), Z=Z, converged=False, iters=it, E_target=E_target)


def epsilon_from_PR(P: np.ndarray, R: np.ndarray, *, floor: float = 0.0) -> np.ndarray:
    """Compute eps_j = R_j / P_j with optional flooring of tiny P_j."""
    P = np.asarray(P, dtype=float)
    R = np.asarray(R, dtype=float)
    if floor > 0:
        P = np.maximum(P, floor)
    return R / P
