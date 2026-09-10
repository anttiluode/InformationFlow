from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import Carrier, InformationFlow2D
from .sweeps import frequency_sweep, phase_sweep


def build_worlds(n: int = 48) -> dict[str, InformationFlow2D]:
    base = InformationFlow2D(n=n)
    return {
        "W0": base.copy(),
        "WA": base.copy(),
        "WB": base.copy(),
        "WAB": base.copy(),
        "Wsep": base.copy(),
        "Wfreq": base.copy(),
    }


def run_carrier_addressed_test(
    *,
    n: int = 48,
    train_steps: int = 800,
    recall_steps: int = 500,
    matched_omega: float = 2.0,
    mismatch_delta_omega: float = 8.0,
) -> dict:
    """Six equal-time worlds: pair-specific write plus two strong controls."""
    worlds = build_worlds(n=n)
    center_x = 3.1
    center_y = 3.25
    a = Carrier(center_x, center_y, 0.42, matched_omega)
    b_match = Carrier(center_x, center_y, 0.42, matched_omega)
    b_sep = Carrier(center_x, 4.60, 0.42, matched_omega)
    b_freq = Carrier(
        center_x,
        center_y,
        0.42,
        matched_omega + mismatch_delta_omega,
    )

    worlds["W0"].train_pair(None, None, steps=train_steps)
    worlds["WA"].train_pair(a, None, steps=train_steps)
    worlds["WB"].train_pair(None, b_match, steps=train_steps)
    worlds["WAB"].train_pair(a, b_match, steps=train_steps)
    worlds["Wsep"].train_pair(a, b_sep, steps=train_steps)
    worlds["Wfreq"].train_pair(a, b_freq, steps=train_steps)

    recall = {
        name: world.recall(steps=recall_steps) for name, world in worlds.items()
    }
    slow = {
        name: {
            "norm": world.slow_norm(),
            "divergence_rms": world.slow_divergence_rms(),
        }
        for name, world in worlds.items()
    }

    def isolated(metric: str, pair: str) -> float:
        return float(
            recall[pair][metric]
            - recall["WA"][metric]
            - recall["WB"][metric]
            + recall["W0"][metric]
        )

    m_match = isolated("routing_bias", "WAB")
    m_sep = isolated("routing_bias", "Wsep")
    m_freq = isolated("routing_bias", "Wfreq")
    selectivity_spatial = float(abs(m_match) / (abs(m_sep) + 1e-12))
    selectivity_frequency = float(abs(m_match) / (abs(m_freq) + 1e-12))

    return {
        "claim_boundary": (
            "This experiment demonstrates carrier- and overlap-addressed quadratic "
            "writing in an engineered information-flow field. It does not establish "
            "that Navier-Stokes spontaneously implements the same synapse."
        ),
        "config": {
            "grid": n,
            "train_steps": train_steps,
            "recall_steps": recall_steps,
            "matched_omega": matched_omega,
            "mismatch_delta_omega": mismatch_delta_omega,
        },
        "slow_fields": slow,
        "recall": recall,
        "metrics": {
            "matched_isolated_routing": m_match,
            "spatial_separation_control": m_sep,
            "frequency_mismatch_control": m_freq,
            "matched_over_spatial_control": selectivity_spatial,
            "matched_over_frequency_control": selectivity_frequency,
            "matched_slow_norm_over_frequency": float(
                slow["WAB"]["norm"] / (slow["Wfreq"]["norm"] + 1e-12)
            ),
        },
        "frequency_sweep": frequency_sweep(
            n=n, train_steps=train_steps, omega0=matched_omega
        ),
        "phase_sweep": phase_sweep(
            n=n, train_steps=train_steps, recall_steps=recall_steps, omega=matched_omega
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Carrier-addressed information-flow write/recall experiment"
    )
    parser.add_argument("--grid", type=int, default=48)
    parser.add_argument("--train-steps", type=int, default=800)
    parser.add_argument("--recall-steps", type=int, default=500)
    parser.add_argument(
        "--out", type=Path, default=Path("results/carrier_addressed.json")
    )
    args = parser.parse_args()
    result = run_carrier_addressed_test(
        n=args.grid,
        train_steps=args.train_steps,
        recall_steps=args.recall_steps,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
