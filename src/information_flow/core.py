from __future__ import annotations

from dataclasses import dataclass
import numpy as np

Array = np.ndarray


def _periodic_delta(x: Array, center: float, length: float) -> Array:
    d = x - center
    return (d + 0.5 * length) % length - 0.5 * length


def _periodic_bilinear(field: Array, xq: Array, yq: Array, length: float) -> Array:
    """Periodic bilinear interpolation on a square grid."""
    n = field.shape[0]
    gx = (xq % length) / length * n
    gy = (yq % length) / length * n
    fx = np.floor(gx)
    fy = np.floor(gy)
    i0 = fx.astype(int) % n
    j0 = fy.astype(int) % n
    i1 = (i0 + 1) % n
    j1 = (j0 + 1) % n
    ax = gx - fx
    ay = gy - fy
    return (
        (1.0 - ax) * (1.0 - ay) * field[i0, j0]
        + ax * (1.0 - ay) * field[i1, j0]
        + (1.0 - ax) * ay * field[i0, j1]
        + ax * ay * field[i1, j1]
    )


@dataclass(frozen=True)
class Carrier:
    """A localized oscillatory information channel."""

    x: float
    y: float
    sigma: float
    omega: float
    phase: float = 0.0
    amplitude: float = 1.0


@dataclass(frozen=True)
class Detector:
    x: float
    y: float
    sigma: float = 0.32


class InformationFlow2D:
    r"""Minimal information-flow field with coherent carriers and a slow operator.

    The model is intentionally not presented as a fundamental physical law.
    It is an executable abstraction of four mechanisms:

      1. coherent carrier-coded state;
      2. selective quadratic interaction Re(z_i z_j*);
      3. a slow routing field written by the selected interaction;
      4. bounded local readout of a transported cue.

    The slow field is an incompressible velocity perturbation. A local
    interaction produces a vector forcing which is projected onto the
    divergence-free subspace in Fourier space. Later scalar cues are advected
    by the sum of a fixed rightward drift and the learned slow velocity field.
    """

    def __init__(
        self,
        n: int = 48,
        length: float = 2.0 * np.pi,
        dt: float = 0.02,
        base_speed: float = 0.55,
        cue_diffusion: float = 0.002,
        slow_decay: float = 0.002,
        slow_diffusion: float = 0.002,
    ) -> None:
        if n < 16 or n % 2:
            raise ValueError("n must be an even integer >= 16")
        self.n = int(n)
        self.length = float(length)
        self.dt = float(dt)
        self.base_speed = float(base_speed)
        self.cue_diffusion = float(cue_diffusion)
        self.slow_decay = float(slow_decay)
        self.slow_diffusion = float(slow_diffusion)

        axis = np.linspace(0.0, self.length, self.n, endpoint=False)
        self.x, self.y = np.meshgrid(axis, axis, indexing="ij")
        k = np.fft.fftfreq(self.n, d=self.length / self.n) * 2.0 * np.pi
        self.kx, self.ky = np.meshgrid(k, k, indexing="ij")
        self.k2 = self.kx**2 + self.ky**2
        self.k2_safe = self.k2.copy()
        self.k2_safe[0, 0] = 1.0

        self.slow_u = np.zeros((self.n, self.n), dtype=np.float64)
        self.slow_v = np.zeros((self.n, self.n), dtype=np.float64)

    def copy(self) -> "InformationFlow2D":
        other = InformationFlow2D(
            n=self.n,
            length=self.length,
            dt=self.dt,
            base_speed=self.base_speed,
            cue_diffusion=self.cue_diffusion,
            slow_decay=self.slow_decay,
            slow_diffusion=self.slow_diffusion,
        )
        other.slow_u = self.slow_u.copy()
        other.slow_v = self.slow_v.copy()
        return other

    def gaussian(self, x: float, y: float, sigma: float) -> Array:
        dx = _periodic_delta(self.x, x, self.length)
        dy = _periodic_delta(self.y, y, self.length)
        return np.exp(-0.5 * (dx * dx + dy * dy) / (sigma * sigma))

    def carrier_envelope(self, carrier: Carrier) -> Array:
        return carrier.amplitude * self.gaussian(carrier.x, carrier.y, carrier.sigma)

    def carrier_state(self, carrier: Carrier, time: float) -> Array:
        """Complex narrowband signal z(x,t) = A(x) exp(i(omega t + phase))."""
        return self.carrier_envelope(carrier) * np.exp(
            1j * (carrier.omega * time + carrier.phase)
        )

    def quadratic_cross(self, a: Carrier, b: Carrier, time: float) -> Array:
        """Physical-style coherent product Re(z_a z_b*)."""
        za = self.carrier_state(a, time)
        zb = self.carrier_state(b, time)
        return np.real(za * np.conj(zb))

    def _laplacian(self, field: Array) -> Array:
        return np.fft.ifft2(-self.k2 * np.fft.fft2(field)).real

    def divergence_free_projection(self, fx: Array, fy: Array) -> tuple[Array, Array]:
        """Helmholtz-project a vector field onto its incompressible part."""
        fxh = np.fft.fft2(fx)
        fyh = np.fft.fft2(fy)
        dot = self.kx * fxh + self.ky * fyh
        ux = fxh - self.kx * dot / self.k2_safe
        uy = fyh - self.ky * dot / self.k2_safe
        ux[0, 0] = 0.0
        uy[0, 0] = 0.0
        return np.fft.ifft2(ux).real, np.fft.ifft2(uy).real

    def slow_divergence_rms(self) -> float:
        uh = np.fft.fft2(self.slow_u)
        vh = np.fft.fft2(self.slow_v)
        div = np.fft.ifft2(1j * self.kx * uh + 1j * self.ky * vh).real
        return float(np.sqrt(np.mean(div * div)))

    def write_step(
        self,
        interaction: Array,
        *,
        direction: tuple[float, float] = (0.0, 1.0),
        write_rate: float = 0.12,
    ) -> None:
        """Let a selected quadratic product deform the slow routing field.

        The direction is an explicit coupling tensor of this toy model. It is
        analogous to choosing which stress component couples into the slow
        transport operator. The projection prevents us from smuggling in a
        compressible sink/source field.
        """
        fx = float(direction[0]) * interaction
        fy = float(direction[1]) * interaction
        px, py = self.divergence_free_projection(fx, fy)
        self.slow_u += self.dt * (
            write_rate * px
            - self.slow_decay * self.slow_u
            + self.slow_diffusion * self._laplacian(self.slow_u)
        )
        self.slow_v += self.dt * (
            write_rate * py
            - self.slow_decay * self.slow_v
            + self.slow_diffusion * self._laplacian(self.slow_v)
        )

    def train_pair(
        self,
        a: Carrier | None,
        b: Carrier | None,
        *,
        steps: int,
        direction: tuple[float, float] = (0.0, 1.0),
        write_rate: float = 0.12,
    ) -> None:
        """Integrate one carrier pair for equal physical time.

        A-only and B-only worlds deliberately have no cross write here. They
        are controls for the pair-specific term rather than a model of every
        possible self-interaction in a fluid.
        """
        for step in range(int(steps)):
            if a is None or b is None:
                interaction = np.zeros_like(self.slow_u)
            else:
                interaction = self.quadratic_cross(a, b, step * self.dt)
            self.write_step(
                interaction, direction=direction, write_rate=write_rate
            )

    def slow_norm(self) -> float:
        return float(np.sqrt(np.mean(self.slow_u**2 + self.slow_v**2)))

    def slow_difference_norm(self, other: "InformationFlow2D") -> float:
        return float(
            np.sqrt(
                np.mean(
                    (self.slow_u - other.slow_u) ** 2
                    + (self.slow_v - other.slow_v) ** 2
                )
            )
        )

    def _advect_cue_once(self, rho: Array) -> Array:
        u = self.base_speed + self.slow_u
        v = self.slow_v
        x_back = self.x - self.dt * u
        y_back = self.y - self.dt * v
        nxt = _periodic_bilinear(rho, x_back, y_back, self.length)

        if self.cue_diffusion > 0.0:
            epsilon = min(
                0.20,
                self.cue_diffusion * self.dt * (self.n / self.length) ** 2,
            )
            neighbor_mean = (
                np.roll(nxt, 1, axis=0)
                + np.roll(nxt, -1, axis=0)
                + np.roll(nxt, 1, axis=1)
                + np.roll(nxt, -1, axis=1)
            ) / 4.0
            nxt = (1.0 - epsilon) * nxt + epsilon * neighbor_mean

        mass = float(nxt.sum())
        if mass > 0.0:
            nxt /= mass
        return nxt

    def recall(
        self,
        *,
        cue_x: float = 0.8,
        cue_y: float = np.pi,
        cue_sigma: float = 0.22,
        upper: Detector | None = None,
        lower: Detector | None = None,
        steps: int = 500,
    ) -> dict[str, float]:
        """Inject one positive cue and expose only two local detector values."""
        if upper is None:
            upper = Detector(5.4, np.pi + 0.7, 0.32)
        if lower is None:
            lower = Detector(5.4, np.pi - 0.7, 0.32)

        rho = self.gaussian(cue_x, cue_y, cue_sigma)
        rho /= rho.sum()
        up_mask = self.gaussian(upper.x, upper.y, upper.sigma)
        down_mask = self.gaussian(lower.x, lower.y, lower.sigma)
        up_mask /= up_mask.max()
        down_mask /= down_mask.max()

        peak_upper = 0.0
        peak_lower = 0.0
        for _ in range(int(steps)):
            rho = self._advect_cue_once(rho)
            peak_upper = max(peak_upper, float(np.sum(rho * up_mask)))
            peak_lower = max(peak_lower, float(np.sum(rho * down_mask)))

        return {
            "upper": peak_upper,
            "lower": peak_lower,
            "routing_bias": peak_upper - peak_lower,
        }
