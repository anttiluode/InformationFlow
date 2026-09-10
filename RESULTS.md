# Results

Deterministic default run:

```bash
PYTHONPATH=src python -m information_flow.experiment \
  --grid 48 --train-steps 800 --recall-steps 500 \
  --out results/carrier_addressed.json
```

## Six-world receipt

| world | slow-field norm | recall routing bias |
| --- | ---: | ---: |
| W0 | 0 | ~0 |
| WA | 0 | ~0 |
| WB | 0 | ~0 |
| WAB matched | 0.0947143 | +0.0692423 |
| Wsep spatial control | 0.00715604 | +0.00976131 |
| Wfreq carrier control | 0.000725247 | +0.000657468 |

Derived selectivity:

```text
matched / spatial-control routing    7.0935x
matched / frequency-control routing  105.3166x
matched / frequency slow norm        130.5960x
```

The slow vector field remains numerically incompressible; the default WAB divergence RMS is approximately `8.1e-14`.

## Frequency-address sweep

```text
Delta omega    slow norm    relative to match
0.00           0.094714     1.0000
0.25           0.024085     0.2543
0.50           0.013395     0.1414
1.00           0.002174     0.0230
2.00           0.001937     0.0204
4.00           0.001632     0.0172
8.00           0.000725     0.00766
12.00          0.0000946    0.000998
```

The exact curve is modified by slow decay and diffusion, but the narrowing is the expected finite-window coherence effect.

## Phase-address sweep

```text
Delta phase    slow norm    later routing bias
0              0.094714     +0.069242
pi/2           ~0           ~0
pi             0.094714     -0.038144
3pi/2          ~0           ~0
```

This is the most interesting qualitative result of the first implementation: **relative phase changes the sign of the persistent route written by an otherwise identical pair**.

## Interpretation boundary

The experiment is intentionally engineered so carrier coherence controls a quadratic slow write. The positive result therefore establishes the mechanism and its selectivity, not a spontaneous discovery by fluid dynamics.

The scientific next step is to replace the explicit coupling channel with a physically generated nonlinear transfer while preserving the same attacker suite: matched carrier, spatially separated, carrier-mismatched, phase-scrambled, equal time, equal power, full fast washout, identical recall.
