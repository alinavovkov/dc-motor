from __future__ import annotations

import os
from pathlib import Path

from .model import SimulationResult


def plot_transients(result: SimulationResult, out_file: Path) -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib"))
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
    axes[0].plot(result.t, result.reference, "k--", label="reference")
    axes[0].plot(result.t, result.omega_rotor, label="rotor speed")
    axes[0].plot(result.t, result.omega_load, label="load speed")
    axes[0].set_ylabel("rad/s")
    axes[0].legend(loc="best")

    axes[1].plot(result.t, result.current)
    axes[1].set_ylabel("current, A")

    axes[2].plot(result.t, result.twist)
    axes[2].set_ylabel("shaft twist, rad")

    axes[3].plot(result.t, result.voltage, label="voltage")
    axes[3].plot(result.t, result.load_torque, label="load torque")
    axes[3].set_xlabel("time, s")
    axes[3].legend(loc="best")

    fig.tight_layout()
    fig.savefig(out_file, dpi=160)
    plt.close(fig)


def plot_phase_portrait(result: SimulationResult, out_file: Path) -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib"))
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(result.twist, result.omega_rotor - result.omega_load)
    ax.set_xlabel("shaft twist, rad")
    ax.set_ylabel("speed difference, rad/s")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_file, dpi=160)
    plt.close(fig)
