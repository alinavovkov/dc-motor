# DC motor with an elastic load

Python implementation for the course report topic: a separately excited DC motor connected to an elastic load through a flexible shaft.

The project covers the analyst/Python part of the assignment:

- nonlinear time-domain simulation with `solve_ivp`;
- RK45 and Radau solver comparison;
- PID speed controller for a 10 rad/s reference;
- 10+ scenarios with shaft stiffness, load torque, supply voltage, and PID variations;
- performance metrics: rise time, overshoot, settling time, RMSE, MAE;
- plots for transients, phase portraits, and Bode/frequency response.

## Model

State vector:

```text
x = [i, theta_1, omega_1, theta_2, omega_2, integral_error, derivative_filter]
```

Equations:

```text
di/dt       = (u - R*i - Ke*omega_1) / L
dtheta_1/dt = omega_1
domega_1/dt = (Km*i - k*(theta_1 - theta_2) - b*(omega_1 - omega_2)) / J1
dtheta_2/dt = omega_2
domega_2/dt = (k*(theta_1 - theta_2) + b*(omega_1 - omega_2) - Mc(t)) / J2
```

The PID controller acts on load speed `omega_2`:

```text
e = omega_ref - omega_2
u = Kp*e + Ki*integral(e) + Kd*filtered_de/dt
```

Voltage is saturated to the configured supply limit.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m dc_motor.run_scenarios --out outputs
python -m dc_motor.frequency_analysis --out outputs
```

Main outputs:

- `outputs/scenario_metrics.csv`
- `outputs/rk45_vs_radau.csv`
- `outputs/scenario_*.png`
- `outputs/bode_response.png`

## Tests

```powershell
python -m unittest
```
