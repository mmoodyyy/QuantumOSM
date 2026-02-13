# OSM equations implemented here

This repository implements the core equilibrium solution used in **Observable Statistical Mechanics (OSM)**.

Given a (coarse-grained) observable \(A\) with eigenvalues \(a_j\) and degeneracies \(d_j\), OSM predicts
an equilibrium distribution over outcomes

\[
p^{DE}_j = \frac{d_j e^{-\beta_A \varepsilon_j}}{Z_A}, \qquad
Z_A = \sum_j d_j e^{-\beta_A \varepsilon_j}.
\]

The observable-specific energies \(\varepsilon_j\) are obtained from diagonal-ensemble data via

\[
\varepsilon_j = \frac{R^{DE}_j}{p^{DE}_j},
\]

where \(R^{DE}_j\) is the (data-provided) quantity defined in the OSM paper.

The Lagrange multiplier \(\beta_A\) is fixed by the constraint

\[
\sum_j p^{DE}_j \varepsilon_j = E,
\]

which is solved numerically (bisection) using the predicted distribution
\(p_{\beta}(j) \propto d_j e^{-\beta \varepsilon_j}\).

## What is in the DE dataset

For each configuration, the dataset provides:
- `*_P_DE.npy` : the empirical stationary distribution \(P^{DE}_j\),
- `*_R_DE.npy` : \(R^{DE}_j\),
- `*_unique_eigenvalues.npy` : the unique eigenvalues \(a_j\) of the measured observable.

This code assumes these observables are **total magnetizations** along X/Y/Z, so the degeneracies are
computed analytically as \(d_j = \binom{N}{(N+a_j)/2}\).
