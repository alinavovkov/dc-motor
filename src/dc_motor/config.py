from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MotorParameters:
    resistance: float = 2.5
    inductance: float = 0.01
    torque_constant: float = 0.5
    back_emf_constant: float = 0.5
    rotor_inertia: float = 0.01
    load_inertia: float = 0.02
    shaft_stiffness: float = 11.0
    shaft_damping: float = 0.15
    voltage_limit: float = 48.0


@dataclass(frozen=True)
class PIDGains:
    kp: float = 0.8
    ki: float = 4.0
    kd: float = 0.18
    derivative_time_constant: float = 0.02

