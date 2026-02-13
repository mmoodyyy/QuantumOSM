import numpy as np
from quantumosm.osm import solve_beta_energy_constraint, predict_p


def test_solve_beta_simple():
    d = np.array([1.0, 1.0])
    eps = np.array([0.0, 1.0])
    E_target = 0.25
    fit = solve_beta_energy_constraint(d, eps, E_target)
    assert fit.converged
    p, _ = predict_p(d, eps, fit.beta)
    assert abs(float(np.sum(p * eps)) - E_target) < 1e-9
    assert abs(float(np.sum(p)) - 1.0) < 1e-12
