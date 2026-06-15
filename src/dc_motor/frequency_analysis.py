from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
from scipy import signal

from .config import MotorParameters


def plant_state_space(params: MotorParameters | None = None) -> signal.StateSpace:
    params = params or MotorParameters()
    a = np.zeros((5, 5), dtype=float)
    b = np.zeros((5, 1), dtype=float)
    c = np.zeros((1, 5), dtype=float)
    d = np.zeros((1, 1), dtype=float)

    a[0, 0] = -params.resistance / params.inductance
    a[0, 2] = -params.back_emf_constant / params.inductance
    b[0, 0] = 1.0 / params.inductance

    a[1, 2] = 1.0
    a[2, 0] = params.torque_constant / params.rotor_inertia
    a[2, 1] = -params.shaft_stiffness / params.rotor_inertia
    a[2, 2] = -params.shaft_damping / params.rotor_inertia
    a[2, 3] = params.shaft_stiffness / params.rotor_inertia
    a[2, 4] = params.shaft_damping / params.rotor_inertia

    a[3, 4] = 1.0
    a[4, 1] = params.shaft_stiffness / params.load_inertia
    a[4, 2] = params.shaft_damping / params.load_inertia
    a[4, 3] = -params.shaft_stiffness / params.load_inertia
    a[4, 4] = -params.shaft_damping / params.load_inertia

    c[0, 4] = 1.0
    return signal.StateSpace(a, b, c, d)


def bode_data(params: MotorParameters | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    system = plant_state_space(params)
    w = np.logspace(-1, 3, 600)
    w, magnitude, phase = signal.bode(system, w=w)
    return w, magnitude, phase


def save_bode_plot(out: Path) -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib"))
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    w, magnitude, phase = bode_data()
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].semilogx(w, magnitude)
    axes[0].set_ylabel("magnitude, dB")
    axes[0].grid(True, which="both", alpha=0.3)
    axes[1].semilogx(w, phase)
    axes[1].set_ylabel("phase, deg")
    axes[1].set_xlabel("frequency, rad/s")
    axes[1].grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "bode_response.png", dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    save_bode_plot(args.out)


if __name__ == "__main__":
    main()
