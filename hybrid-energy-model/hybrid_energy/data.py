"""Synthetic example profiles and CSV loaders for the hybrid energy model.

All profiles are pandas Series indexed by an hourly DatetimeIndex.
Swap the synthetic generators below for `load_profile_csv()` once you have
real measured data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _hourly_index(n_hours: int, start: str = "2024-01-01") -> pd.DatetimeIndex:
    return pd.date_range(start=start, periods=n_hours, freq="h")


def synthetic_load_profile(
    n_hours: int = 24 * 7,
    base_kw: float = 60.0,
    peak_kw: float = 150.0,
    noise_std: float = 5.0,
    seed: int = 0,
) -> pd.Series:
    """A daily-cycle electricity demand profile (two peaks: morning + evening)."""
    rng = np.random.default_rng(seed)
    idx = _hourly_index(n_hours)
    hour = idx.hour.to_numpy()

    morning_peak = np.exp(-((hour - 8) ** 2) / (2 * 2.5**2))
    evening_peak = np.exp(-((hour - 19) ** 2) / (2 * 3.0**2))
    shape = 0.4 * morning_peak + 1.0 * evening_peak
    shape = shape / shape.max()

    load = base_kw + (peak_kw - base_kw) * shape
    load = load + rng.normal(0, noise_std, size=n_hours)
    load = np.clip(load, base_kw * 0.5, None)
    return pd.Series(load, index=idx, name="load_kw")


def synthetic_solar_cf(
    n_hours: int = 24 * 7,
    cloudiness_std: float = 0.15,
    seed: int = 1,
) -> pd.Series:
    """Solar capacity factor in [0, 1]: a daylight bell curve times daily cloud cover."""
    rng = np.random.default_rng(seed)
    idx = _hourly_index(n_hours)
    hour = idx.hour.to_numpy() + idx.minute.to_numpy() / 60.0

    daylight = np.clip(np.sin(np.pi * (hour - 6) / 12), 0, None)
    daylight[(hour < 6) | (hour > 18)] = 0.0

    n_days = int(np.ceil(n_hours / 24))
    daily_cloud_factor = np.clip(rng.normal(1.0, cloudiness_std, size=n_days), 0.2, 1.0)
    cloud_per_hour = np.repeat(daily_cloud_factor, 24)[:n_hours]

    cf = daylight * cloud_per_hour
    return pd.Series(np.clip(cf, 0, 1), index=idx, name="solar_cf")


def synthetic_wind_cf(
    n_hours: int = 24 * 7,
    mean_cf: float = 0.35,
    persistence: float = 0.9,
    noise_std: float = 0.08,
    seed: int = 2,
) -> pd.Series:
    """Wind capacity factor in [0, 1] as an autocorrelated (AR1) random process."""
    rng = np.random.default_rng(seed)
    idx = _hourly_index(n_hours)

    cf = np.empty(n_hours)
    cf[0] = mean_cf
    for t in range(1, n_hours):
        shock = rng.normal(0, noise_std)
        cf[t] = persistence * cf[t - 1] + (1 - persistence) * mean_cf + shock

    return pd.Series(np.clip(cf, 0, 1), index=idx, name="wind_cf")


def load_profile_csv(path: str, column: str | None = None) -> pd.Series:
    """Load an hourly profile from a CSV with a datetime column as the index.

    The CSV must have a parseable datetime in its first column and one
    numeric value column (name it whatever you like, or pass `column`).
    """
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    if column is None:
        column = df.columns[0]
    series = df[column]
    series.index.freq = pd.infer_freq(series.index)
    return series
