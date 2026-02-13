# Reproducibility

## Recommended workflow

1. Create a clean virtual environment.
2. Install in editable mode:
   `pip install -e ".[dev]"`.
3. Generate outputs into a separate folder (default: `results/`), which is gitignored.
4. When figures/metrics are final, copy them to `figures/` or `paper/` and commit those.

## Determinism

The numerical parts here are deterministic given the input data (no RNG). The only potential variability is
Matplotlib rendering (minor, backend-dependent). For strict determinism, set:

```bash
export MPLBACKEND=Agg
```
