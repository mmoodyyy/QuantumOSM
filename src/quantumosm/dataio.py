from __future__ import annotations

from pathlib import Path
import numpy as np


def load_npy(path: str | Path) -> np.ndarray:
    return np.load(str(path))


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
