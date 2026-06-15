# DC-мотор з пружним навантаженням

Python-реалізація для теми курсового звіту: DC-мотор незалежного збудження, з'єднаний із навантаженням через пружний вал.

Проєкт покриває частину завдання, пов'язану з Python-реалізацією та аналізом:

- нелінійне моделювання у часовій області за допомогою `solve_ivp`;
- порівняння чисельних методів RK45 та Radau;
- PID-регулятор швидкості для заданого значення 10 рад/с;
- 10+ сценаріїв із варіацією жорсткості вала, моменту навантаження, напруги живлення та PID-коефіцієнтів;
- метрики якості регулювання: час наростання, перерегулювання, час встановлення, RMSE, MAE;
- графіки перехідних процесів, фазові портрети та частотний аналіз/діаграма Боде.

## Модель

Вектор стану:

```text
x = [i, theta_1, omega_1, theta_2, omega_2, integral_error, derivative_filter]
```

Рівняння:

```text
di/dt       = (u - R*i - Ke*omega_1) / L
dtheta_1/dt = omega_1
domega_1/dt = (Km*i - k*(theta_1 - theta_2) - b*(omega_1 - omega_2)) / J1
dtheta_2/dt = omega_2
domega_2/dt = (k*(theta_1 - theta_2) + b*(omega_1 - omega_2) - Mc(t)) / J2
```

PID-регулятор діє на швидкість навантаження `omega_2`:

```text
e = omega_ref - omega_2
u = Kp*e + Ki*integral(e) + Kd*filtered_de/dt
```

Напруга обмежується заданою межею живлення.

## Швидкий запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m dc_motor.run_scenarios --out outputs
python -m dc_motor.frequency_analysis --out outputs
```

Основні результати:

- `outputs/scenario_metrics.csv`
- `outputs/rk45_vs_radau.csv`
- `outputs/scenario_*.png`
- `outputs/bode_response.png`

## Тести

```powershell
python -m unittest
```
