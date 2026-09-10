# Theory note — an information-flow equation

## 1. Not a fundamental law

"Information Navier–Stokes" is a design analogy, not a proposed replacement for fluid mechanics or quantum mechanics.

The useful abstraction is the separation of roles:

```text
fast coherent state       carries information
quadratic interaction     binds selected states
slow routing field        stores consequences
bounded local detector    converts state into action
```

The code asks whether those roles can live in one continuous field model.

## 2. Fast carrier channels

Let channel `i` be

\[
z_i(x,t)=A_i(x)e^{i(\omega_i t+\phi_i)}.
\]

`A_i(x)` is a localized spatial envelope. Frequency and phase are part of the address.

The pair channel is

\[
q_{ij}(x,t)=\Re[z_i(x,t)z_j(x,t)^*].
\]

For stationary envelopes,

\[
q_{ij}=A_iA_j\cos[(\omega_i-\omega_j)t+(\phi_i-\phi_j)].
\]

So a single quadratic product already tests three conditions:

\[
A_iA_j \neq 0 \quad\text{(spatial overlap)},
\]

\[
|\omega_i-\omega_j| \lesssim 1/T \quad\text{(finite-time frequency match)},
\]

and

\[
\cos(\phi_i-\phi_j) \quad\text{(signed phase channel)}.
\]

## 3. Finite-time carrier orthogonality

For relative phase zero,

\[
\frac1T\int_0^T \cos(\Delta\omega t)dt
=
\frac{\sin(\Delta\omega T)}{\Delta\omega T}.
\]

Thus the integration time itself determines frequency-address resolution. Longer slow integration yields narrower carrier selectivity.

This is the conceptual handoff from wavebit-style time-averaged carrier orthogonality. Here the surviving product is not used to reconstruct a quantum state coefficient; it is used as a **plasticity drive**.

## 4. Slow operator write

Let `U_s=(u_s,v_s)` be a slow routing velocity field. The implemented toy uses

\[
\partial_t U_s
=
\eta\,\Pi_{\mathrm{div}=0}[C_{ij}q_{ij}]
-\lambda U_s
+\nu_s\Delta U_s.
\]

`C_ij` is an explicit coupling direction/tensor. `Pi_div=0` is the Helmholtz projection, keeping the learned velocity perturbation incompressible.

This is deliberately stronger engineering than raw Navier–Stokes: it chooses which quadratic channel couples to the slow field. The earlier carrier-free Gate 6 failure motivates doing so. A large nonlinear state change is not enough; a useful system needs **addressed nonlinear consequence**.

## 5. Recall as transport through a changed operator

A positive scalar cue density `rho` obeys the transport model

\[
\partial_t\rho+(U_0+U_s)\cdot\nabla\rho=D\Delta\rho.
\]

The learned `U_s` therefore changes the propagator experienced by future cues.

This makes memory operational:

\[
\text{past pair interaction}
\rightarrow
\Delta U_s
\rightarrow
\text{different future trajectory}.
\]

The stored object is not a label or lookup-table entry. It is a changed routing field.

## 6. Bounded readout

The machine never reconstructs a full latent state. Two local detectors are enough for the current experiment:

\[
y_a(t)=\int h_a(x)\rho(x,t)dx.
\]

The receipt stores peak detector values and their bias.

This matters when comparing the idea with classical emulation of quantum circuits. Wavebit emulators pay an exponential price when reconstructing a complete `2^N` state. A task-directed information-flow machine need not perform that tomography; it may expose only the low-dimensional consequences required for action. That does **not** prove favorable complexity, but it is a different computational objective.

## 7. Phase as signed plasticity

When `Delta omega = 0`,

\[
q_{ij}=A_iA_j\cos(\Delta\phi).
\]

Therefore:

\[
\Delta\phi=0 \Rightarrow +\text{write},
\]

\[
\Delta\phi=\pi/2 \Rightarrow 0\text{ in the real product channel},
\]

\[
\Delta\phi=\pi \Rightarrow -\text{write}.
\]

The default experiment shows exactly this sign reversal in later routing. A future complex/quadrature slow state could preserve both cosine and sine products instead of discarding the quadrature channel.

## 8. The deeper architecture

The intended machine is not globally nonlinear all the time.

```text
coherent / near-linear propagation
        |
        | spatial + carrier + phase address
        v
selected nonlinear junction
        |
        v
slow operator write
        |
        v
future coherent propagation changes
```

That offers a possible resolution of the long-running tension in the earlier field-computing repos:

- pure linear waves preserve rich phase structure but do not learn by themselves;
- unrestricted nonlinear fields compute, but interference becomes difficult to address;
- carrier-coded nonlinear junctions let us choose **where nonlinearity is allowed to matter**.

Whether that architecture is computationally useful beyond this toy remains open.
