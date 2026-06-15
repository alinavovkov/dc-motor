from __future__ import annotations

import numpy as np


def rmse(actual: np.ndarray, expected: np.ndarray) -> float:
    actual = np.asarray(actual, dtype=float)
    expected = np.asarray(expected, dtype=float)
    return float(np.sqrt(np.mean((actual - expected) ** 2)))


def mae(actual: np.ndarray, expected: np.ndarray) -> float:
    actual = np.asarray(actual, dtype=float)
    expected = np.asarray(expected, dtype=float)
    return float(np.mean(np.abs(actual - expected)))


def step_info(t: np.ndarray, y: np.ndarray, reference: np.ndarray, tolerance: float = 0.02) -> dict[str, float]:
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    reference = np.asarray(reference, dtype=float)
    final_value = float(reference[-1])
    if abs(final_value) < 1e-12:
        return {"rise_time": np.nan, "overshoot_percent": np.nan, "settling_time": np.nan}

    y_norm = y / final_value
    above_10 = np.flatnonzero(y_norm >= 0.1)
    above_90 = np.flatnonzero(y_norm >= 0.9)
    rise_time = np.nan
    if len(above_10) and len(above_90):
        rise_time = float(t[above_90[0]] - t[above_10[0]])

    peak = float(np.max(y))
    overshoot = max(0.0, (peak - final_value) / abs(final_value) * 100.0)
    band = tolerance * abs(final_value)
    outside = np.flatnonzero(np.abs(y - final_value) > band)
    settling_time = 0.0 if len(outside) == 0 else float(t[min(outside[-1] + 1, len(t) - 1)])

    return {
        "rise_time": rise_time,
        "overshoot_percent": overshoot,
        "settling_time": settling_time,
    }

