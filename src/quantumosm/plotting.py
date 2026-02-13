from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def plot_pdf_comparison(ax, x: np.ndarray, p_data: np.ndarray, p_pred: np.ndarray, title: str) -> None:
    ax.plot(x, p_data, marker="o", linewidth=1.0, label="DE (data)")
    ax.plot(x, p_pred, marker="s", linewidth=1.0, label="OSM pred.")
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("eigenvalue", fontsize=8)
    ax.set_ylabel("probability", fontsize=8)
    ax.tick_params(labelsize=8)
    ax.grid(True, linewidth=0.3, alpha=0.6)


def save_figure(fig, outpath: str | Path, *, dpi: int = 300) -> None:
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outpath, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
