# InformationFlow — from Navier–Stokes to information flow

A small executable attempt to distill one idea that kept reappearing across the field-computing repos:

> **Carry information coherently. Make it nonlinear only when selected things should bind. Let that nonlinear consequence become slow routing structure. Read only what the current task needs.**

This repo is **not** a claim that intelligence literally obeys Navier–Stokes, and it is not a claim of quantum computation. It is an information-flow model inspired by three concrete observations:

1. nonlinear flow can create useful computation, but uncontrolled mixing is not selective memory;
2. classical wave carriers can use frequency/phase orthogonality to decide which products survive time averaging;
3. a persistent slow transport field can make a past interaction alter a later route.

The result is an "information Navier–Stokes" design equation: fast coherent channels are transported, selected quadratic products write a slower divergence-free routing field, and later cues are advected by the field that earlier events changed.

## Why this repo exists now

The immediate predecessor was the carrier-free five-world fluid-synapse attacker in `-mp-ri`. It produced a large collision-specific low-frequency state difference (`||ΔΩ|| ≈ 7.90`) but **failed functionally**:

```text
isolated collision routing M  = -0.004934
separated control M           = +0.076289
```

So "Navier–Stokes is nonlinear" was not enough. The medium changed, but the desired associative route was not isolated from other changes.

At the same time, Padlewski et al. (arXiv:2601.02977v2, *Classical Analog Emulation of Quantum Circuits via Time-Averaged Dynamic States*) introduced **wavebits**: classical oscillatory channels whose correlations are selected by coherent products and time averaging. Their paper is aimed at analog emulation of quantum circuits, not AI or Navier–Stokes. The useful handoff here is narrower: **orthogonal carriers provide an address for quadratic interactions**.

This repo turns that handoff into code.

## The model

Each fast information channel is a localized complex carrier

```text
z_i(x,t) = A_i(x) exp(i(ω_i t + φ_i)).
```

A pair produces the real quadratic channel

```text
q_ij(x,t) = Re[z_i z_j*].
```

The slow routing velocity `U_slow = (u_s, v_s)` is written by that product, then projected onto the incompressible subspace:

```text
∂t U_slow
    = η Π_div-free[C_ij q_ij]
      - λ U_slow
      + ν_s ΔU_slow.
```

A later scalar cue `ρ` is transported by the fixed drift plus the learned slow field:

```text
∂t ρ + (U0 + U_slow) · ∇ρ = D Δρ.
```

Only two localized detector patches are read during recall. There is no global state tomography.

The coupling tensor `C_ij` is explicit in this toy. That is important: the code demonstrates an **algorithmic mechanism**, not spontaneous Reynolds-stress plasticity in an unmodified Navier–Stokes fluid.

## The carrier-addressed worlds

`information-flow` runs six equal-time worlds from the same blank slow field:

| World | Training condition |
| --- | --- |
| `W0` | no pair |
| `WA` | A only |
| `WB` | B only |
| `WAB` | A+B overlap in space and match in carrier frequency |
| `Wsep` | A+B match in carrier but are separated in space |
| `Wfreq` | A+B overlap in space but their carrier frequencies mismatch |

After training, every world receives the **same cue**. The only question is whether the changed slow field now routes it differently.

Default 48×48 receipt:

```text
slow write norm
WAB    0.094714
Wsep   0.007156
Wfreq  0.000725

recall routing bias (upper - lower detector)
WAB    +0.069242
Wsep   +0.009761
Wfreq  +0.000657
```

So the matched pair produces about **7.09×** the isolated routing effect of the spatial-separation control and **105.3×** the frequency-mismatch control. The matched slow-field norm is about **130.6×** the frequency-mismatch norm.

Those numbers are reproducible for the current deterministic toy and live in `results/carrier_addressed.json`.

## What unexpectedly fell out: phase is a signed write address

The simplest sweep is more interesting than the headline ratio.

At equal carrier frequency, the time-averaged quadratic channel is proportional to

```text
cos(Δφ).
```

And the field does exactly that:

```text
relative phase 0        -> routing bias +0.069242
relative phase π/2      -> ~0 write
relative phase π        -> routing bias -0.038144
relative phase 3π/2     -> ~0 write
```

So one physical pair has at least three qualitatively different instructions without changing its location or amplitude:

```text
in phase       write one direction
quadrature     do not write this channel
anti-phase     write the opposite direction
```

That is not quantum magic. It is ordinary coherent multiplication. But it gives the slow operator a **phase-addressed signed plasticity channel**.

## Frequency is another address axis

For a finite training window `T`, a mismatched pair averages approximately like

```text
|sin(Δω T) / (Δω T)|.
```

The measured slow field follows the same qualitative narrowing. In the default run the slow write falls from `0.094714` at `Δω=0` to `0.000725` at `Δω=8` and `9.46e-5` at `Δω=12`.

That means the architecture has three distinct selectors before we introduce any learned attention mechanism:

```text
WHERE   spatial envelope overlap
WHICH   carrier / beat frequency
SIGN    relative phase
```

The old fluid synapse had mostly **where**. Wavebit-style carrier coding gives us **which** and **sign**.

## Run it

```bash
python -m pip install -e .[dev]
information-flow --out results/latest.json
pytest -q
```

Core implementation:

```text
src/information_flow/core.py        field + carriers + slow operator + recall
src/information_flow/experiment.py  six-world write/recall receipt
src/information_flow/sweeps.py      frequency and phase address sweeps
THEORY.md                           equations and claim boundary
RESULTS.md                          deterministic default receipt
```

## Relationship to `-mp-ri`

`-mp-ri` now contains the assembled continuously running field organism: active observation, private receiver history, fast fluid state, slow body, delayed receipts, failure-gated writes and finite structural budget.

`InformationFlow` is not another organism. It is intended to become a **replacement binding layer inside that organism**:

```text
current -mp-ri
fast activity
    -> hand-supplied eligibility/write
    -> slow vortex body

candidate handoff
carrier-coded fast activity
    -> selected quadratic product
    -> slow information-flow write
    -> same slow body / same observer / same delayed consequence machinery
```

The next serious experiment is therefore integration, not another ladder of isolated gates.

## Scientific boundary

What is established here:

- coherent carrier multiplication supplies spatial, frequency and phase selectivity by construction;
- the selected product can write a persistent incompressible routing field;
- after training is over, that slow field changes a later cue's route;
- phase can reverse the sign of the learned route without changing carrier location or power.

What is **not** established:

- that this is a new law of physics;
- that quantum-to-classical transition is "where nonlinearity appears";
- that unmodified Navier–Stokes naturally discovers this addressing scheme;
- that this yields quantum computational advantage;
- that it beats neural networks, reservoirs, state-space models or ordinary signal processing.

The useful question is simpler:

> **Can an adaptive system use coherent wave addresses for cheap transport, invoke nonlinearity only at selected bindings, and store those bindings as a slow operator that routes future information?**

This repo finally gives that question one executable form.
