from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.integrate import solve_ivp

from .config import MotorParameters, PIDGains


LoadTorque = Callable[[float], float]
Reference = Callable[[float], float]


@dataclass(frozen=True)
class SimulationResult:
    t: np.ndarray
    current: np.ndarray
    theta_rotor: np.ndarray
    omega_rotor: np.ndarray
    theta_load: np.ndarray
    omega_load: np.ndarray
    voltage: np.ndarray
    reference: np.ndarray
    load_torque: np.ndarray
    method: str

    @property
    def twist(self) -> np.ndarray:
        return self.theta_rotor - self.theta_load


def step_reference(value: float = 10.0, start: float = 0.0) -> Reference:
    return lambda t: value if t >= start else 0.0


def _pid_voltage(
    t: float,
    state: np.ndarray,
    gains: PIDGains,
    reference: Reference,
    limit: float,
) -> float:
    omega_load = state[4]
    integral_error = state[5]
    derivative_filter = state[6]
    error = reference(t) - omega_load
    derivative_estimate = (error - derivative_filter) / gains.derivative_time_constant
    raw_voltage = (
        gains.kp * error
        + gains.ki * integral_error
        + gains.kd * derivative_estimate
    )
    return float(np.clip(raw_voltage, -limit, limit))


def motor_rhs(
    t: float,
    state: np.ndarray,
    params: MotorParameters,
    gains: PIDGains,
    reference: Reference,
    load_torque: LoadTorque,
) -> np.ndarray:
    current, theta_1, omega_1, theta_2, omega_2, _, derivative_filter = state
    voltage = _pid_voltage(t, state, gains, reference, params.voltage_limit)
    twist = theta_1 - theta_2
    speed_delta = omega_1 - omega_2
    shaft_torque = params.shaft_stiffness * twist + params.shaft_damping * speed_delta
    error = reference(t) - omega_2

    di_dt = (
        voltage
        - params.resistance * current
        - params.back_emf_constant * omega_1
    ) / params.inductance
    dtheta_1_dt = omega_1
    domega_1_dt = (
        params.torque_constant * current
        - shaft_torque
    ) / params.rotor_inertia
    dtheta_2_dt = omega_2
    domega_2_dt = (shaft_torque - load_torque(t)) / params.load_inertia
    dintegral_dt = error
    dfilter_dt = (error - derivative_filter) / gains.derivative_time_constant

    return np.array(
        [
            di_dt,
            dtheta_1_dt,
            domega_1_dt,
            dtheta_2_dt,
            domega_2_dt,
            dintegral_dt,
            dfilter_dt,
        ],
        dtype=float,
    )


def simulate(
    *,
    params: MotorParameters | None = None,
    gains: PIDGains | None = None,
    reference: Reference | None = None,
    load_torque: LoadTorque | None = None,
    t_final: float = 4.0,
    sample_count: int = 1000,
    method: str = "RK45",
    initial_state: np.ndarray | None = None,
) -> SimulationResult:
    params = params or MotorParameters()
    gains = gains or PIDGains()
    reference = reference or step_reference()
    load_torque = load_torque or (lambda _t: 1.0)
    initial_state = (
        np.zeros(7, dtype=float)
        if initial_state is None
        else np.asarray(initial_state, dtype=float)
    )
    t_eval = np.linspace(0.0, t_final, sample_count)

    solution = solve_ivp(
        motor_rhs,
        (0.0, t_final),
        initial_state,
        args=(params, gains, reference, load_torque),
        t_eval=t_eval,
        method=method,
        rtol=1e-7,
        atol=1e-9,
    )
    if not solution.success:
        raise RuntimeError(f"Simulation failed with {method}: {solution.message}")

    states = solution.y
    voltages = np.array(
        [_pid_voltage(t, states[:, idx], gains, reference, params.voltage_limit) for idx, t in enumerate(solution.t)]
    )
    references = np.array([reference(t) for t in solution.t])
    loads = np.array([load_torque(t) for t in solution.t])

    return SimulationResult(
        t=solution.t,
        current=states[0],
        theta_rotor=states[1],
        omega_rotor=states[2],
        theta_load=states[3],
        omega_load=states[4],
        voltage=voltages,
        reference=references,
        load_torque=loads,
        method=method,
    )
