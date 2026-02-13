from quantumosm.parsing import parse_base_name


def test_parse_lr():
    k = parse_base_name("LR_DE_N=14_J=-1.00_h=0.20_alpha=1.60_theta=3_axis=Z")
    assert k.model == "LR"
    assert k.N == 14
    assert abs(k.J + 1.0) < 1e-12
    assert abs(k.h - 0.20) < 1e-12
    assert abs(k.alpha - 1.60) < 1e-12
    assert k.theta == 3
    assert k.axis == "Z"


def test_parse_sr():
    k = parse_base_name("SR_DE_N=14_J=-1.00_h=1.20_theta=0_axis=X")
    assert k.model == "SR"
    assert k.alpha is None
