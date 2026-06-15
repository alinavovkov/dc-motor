from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .config import MotorParameters, PIDGains


LoadTorque = Callable[[float], float]


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    params: MotorParameters
    gains: PIDGains
    load_torque: LoadTorque
    t_final: float = 4.0


def constant_load(value: float = 1.0) -> LoadTorque:
    return lambda _t: value


def step_load(before: float = 0.0, after: float = 1.0, at: float = 1.0) -> LoadTorque:
    return lambda t: before if t < at else after


def ramp_load(start: float = 0.0, slope: float = 0.5, max_value: float = 1.5) -> LoadTorque:
    return lambda t: min(max_value, start + slope * t)


def sine_load(offset: float = 0.8, amplitude: float = 0.3, frequency_hz: float = 1.0) -> LoadTorque:
    return lambda t: offset + amplitude * np.sin(2.0 * np.pi * frequency_hz * t)


def random_load(seed: int = 7, base: float = 0.8, amplitude: float = 0.25, step: float = 0.2) -> LoadTorque:
    rng = np.random.default_rng(seed)
    values = rng.uniform(base - amplitude, base + amplitude, size=200)

    def load(t: float) -> float:
        idx = min(int(t / step), len(values) - 1)
        return float(values[idx])

    return load


def default_scenarios() -> list[Scenario]:
    base = MotorParameters()
    soft = MotorParameters(shaft_stiffness=5.0)
    stiff = MotorParameters(shaft_stiffness=25.0)
    low_voltage = MotorParameters(voltage_limit=24.0)
    high_damping = MotorParameters(shaft_damping=0.35)

    underdamped = PIDGains(kp=1.2, ki=3.5, kd=0.02)
    balanced = PIDGains(kp=0.8, ki=4.0, kd=0.18)
    overdamped = PIDGains(kp=2.5, ki=2.0, kd=0.5)

    return [
        Scenario("baseline_balanced", "Report baseline: k=11, Mc=1, balanced PID.", base, balanced, constant_load(1.0)),
        Scenario("underdamped_pid", "Low derivative gain from report state 1.", base, underdamped, constant_load(1.0)),
        Scenario("overdamped_pid", "High Kp and Kd from report state 3.", base, overdamped, constant_load(1.0)),
        Scenario("soft_shaft", "Reduced shaft stiffness.", soft, balanced, constant_load(1.0)),
        Scenario("stiff_shaft", "Increased shaft stiffness.", stiff, balanced, constant_load(1.0)),
        Scenario("step_load", "Load torque step at t=1 s.", base, balanced, step_load(0.0, 1.0, 1.0)),
        Scenario("late_step_load", "Heavier load torque step at t=2 s.", base, balanced, step_load(0.3, 1.4, 2.0)),
        Scenario("ramp_load", "Slowly increasing load torque.", base, balanced, ramp_load(0.2, 0.45, 1.5)),
        Scenario("sine_load", "Periodic load disturbance.", base, balanced, sine_load(0.8, 0.3, 1.2)),
        Scenario("random_load", "Deterministic random load disturbance.", base, balanced, random_load()),
        Scenario("low_voltage", "Supply voltage saturation at 24 V.", low_voltage, balanced, constant_load(1.0)),
        Scenario("high_damping", "Higher viscous shaft damping.", high_damping, balanced, constant_load(1.0)),
    ]
