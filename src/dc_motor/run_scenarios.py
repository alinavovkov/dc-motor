from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .metrics import mae, rmse, step_info
from .model import simulate, step_reference
from .plotting import plot_phase_portrait, plot_transients
from .scenarios import default_scenarios


def run(out: Path, make_plots: bool = True) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    comparison_rows = []
    reference = step_reference(10.0)

    for scenario in default_scenarios():
        result = simulate(
            params=scenario.params,
            gains=scenario.gains,
            reference=reference,
            load_torque=scenario.load_torque,
            t_final=scenario.t_final,
            method="RK45",
        )
        info = step_info(result.t, result.omega_load, result.reference)
        rows.append(
            {
                "scenario": scenario.name,
                "description": scenario.description,
                "kp": scenario.gains.kp,
                "ki": scenario.gains.ki,
                "kd": scenario.gains.kd,
                "shaft_stiffness": scenario.params.shaft_stiffness,
                "shaft_damping": scenario.params.shaft_damping,
                "voltage_limit": scenario.params.voltage_limit,
                **info,
                "speed_rmse_to_reference": rmse(result.omega_load, result.reference),
                "speed_mae_to_reference": mae(result.omega_load, result.reference),
            }
        )

        radau = simulate(
            params=scenario.params,
            gains=scenario.gains,
            reference=reference,
            load_torque=scenario.load_torque,
            t_final=scenario.t_final,
            method="Radau",
        )
        comparison_rows.append(
            {
                "scenario": scenario.name,
                "rmse_rk45_radau_load_speed": rmse(result.omega_load, radau.omega_load),
                "mae_rk45_radau_load_speed": mae(result.omega_load, radau.omega_load),
            }
        )

        if make_plots:
            plot_transients(result, out / f"scenario_{scenario.name}.png")
            plot_phase_portrait(result, out / f"phase_{scenario.name}.png")

    pd.DataFrame(rows).to_csv(out / "scenario_metrics.csv", index=False)
    pd.DataFrame(comparison_rows).to_csv(out / "rk45_vs_radau.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    run(args.out, make_plots=not args.no_plots)


if __name__ == "__main__":
    main()

