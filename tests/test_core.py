import numpy as np

from information_flow.core import Carrier, InformationFlow2D


def test_quadratic_product_phase_matches():
    f = InformationFlow2D(n=16)
    a = Carrier(3.0, 3.0, 0.4, omega=2.0)
    b = Carrier(3.0, 3.0, 0.4, omega=2.0)
    c = f.quadratic_cross(a, b, time=1.234)
    expected = f.carrier_envelope(a) * f.carrier_envelope(b)
    assert np.allclose(c, expected)


def test_divergence_free_projection_is_nearly_incompressible():
    f = InformationFlow2D(n=24)
    blob = f.gaussian(3.0, 3.2, 0.5)
    u, v = f.divergence_free_projection(np.zeros_like(blob), blob)
    f.slow_u = u
    f.slow_v = v
    assert f.slow_divergence_rms() < 1e-8


def test_mismatched_carriers_write_less_than_matched():
    matched = InformationFlow2D(n=24)
    mismatch = matched.copy()
    a = Carrier(3.1, 3.25, 0.42, omega=2.0)
    b = Carrier(3.1, 3.25, 0.42, omega=2.0)
    b_bad = Carrier(3.1, 3.25, 0.42, omega=10.0)
    matched.train_pair(a, b, steps=400)
    mismatch.train_pair(a, b_bad, steps=400)
    assert matched.slow_norm() > 8.0 * mismatch.slow_norm()


def test_spatial_separation_reduces_write():
    matched = InformationFlow2D(n=24)
    separated = matched.copy()
    a = Carrier(3.1, 3.25, 0.42, omega=2.0)
    b = Carrier(3.1, 3.25, 0.42, omega=2.0)
    b_sep = Carrier(3.1, 4.6, 0.42, omega=2.0)
    matched.train_pair(a, b, steps=300)
    separated.train_pair(a, b_sep, steps=300)
    assert matched.slow_norm() > 8.0 * separated.slow_norm()


def test_phase_can_reverse_or_null_the_write():
    a = Carrier(3.1, 3.25, 0.42, omega=2.0, phase=0.0)

    in_phase = InformationFlow2D(n=24)
    in_phase.train_pair(a, Carrier(3.1, 3.25, 0.42, 2.0, phase=0.0), steps=250)

    quadrature = InformationFlow2D(n=24)
    quadrature.train_pair(
        a, Carrier(3.1, 3.25, 0.42, 2.0, phase=np.pi / 2), steps=250
    )

    anti_phase = InformationFlow2D(n=24)
    anti_phase.train_pair(
        a, Carrier(3.1, 3.25, 0.42, 2.0, phase=np.pi), steps=250
    )

    assert in_phase.slow_norm() > 20.0 * quadrature.slow_norm()
    assert anti_phase.slow_norm() > 20.0 * quadrature.slow_norm()
    assert np.sum(in_phase.slow_v * anti_phase.slow_v) < 0.0
