from __future__ import annotations

import numpy as np

from .core import Carrier, InformationFlow2D


def frequency_sweep(
    deltas=(0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 12.0),
    *,
    n: int = 48,
    train_steps: int = 800,
    omega0: float = 2.0,
) -> list[dict[str, float]]:
    """Measure how finite integration time turns carrier frequency into address."""
    out: list[dict[str, float]] = []
    for delta in deltas:
        field = InformationFlow2D(n=n)
        a = Carrier(3.1, 3.25, 0.42, omega=omega0)
        b = Carrier(3.1, 3.25, 0.42, omega=omega0 + float(delta))
        field.train_pair(a, b, steps=train_steps)
        total_time = train_steps * field.dt
        if abs(delta) < 1e-15:
            window_coherence = 1.0
        else:
            window_coherence = abs(
                np.sin(float(delta) * total_time)
                / (float(delta) * total_time)
            )
        out.append(
            {
                "delta_omega": float(delta),
                "slow_norm": field.slow_norm(),
                "rectangular_window_coherence": float(window_coherence),
            }
        )
    matched = out[0]["slow_norm"] + 1e-15
    for row in out:
        row["slow_norm_relative_to_match"] = row["slow_norm"] / matched
    return out


def phase_sweep(
    phases=(0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi),
    *,
    n: int = 48,
    train_steps: int = 800,
    recall_steps: int = 500,
    omega: float = 2.0,
) -> list[dict[str, float]]:
    """Show that relative phase controls write sign in the real cross channel."""
    out: list[dict[str, float]] = []
    for phase in phases:
        field = InformationFlow2D(n=n)
        a = Carrier(3.1, 3.25, 0.42, omega=omega, phase=0.0)
        b = Carrier(3.1, 3.25, 0.42, omega=omega, phase=float(phase))
        field.train_pair(a, b, steps=train_steps)
        recall = field.recall(steps=recall_steps)
        out.append(
            {
                "phase": float(phase),
                "cos_phase": float(np.cos(phase)),
                "slow_norm": field.slow_norm(),
                "routing_bias": float(recall["routing_bias"]),
            }
        )
    return out
