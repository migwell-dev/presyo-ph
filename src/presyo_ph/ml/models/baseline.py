import numpy as np
import pandas as pd


def naive_forecast(
    series: pd.Series,
    horizon: int,
) -> np.ndarray:

    return np.repeat(series.iloc[-1], horizon)


def seasonal_naive_forecast(
    series: pd.Series,
    horizon: int,
    seasonal_period: int = 12,
) -> np.ndarray:

    seasonal_values = series.iloc[-seasonal_period:].values

    return np.resize(seasonal_values, horizon)


def moving_average_forecast(
    series: pd.Series,
    horizon: int,
    window: int = 3,
) -> np.ndarray:

    average = series.iloc[-window:].mean()

    return np.repeat(average, horizon)
