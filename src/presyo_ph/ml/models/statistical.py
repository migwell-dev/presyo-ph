import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX


def sarima_forecast(
    series: pd.Series,
    horizon: int,
    order: tuple = (1, 1, 1),
    seasonal_order: tuple = (1, 1, 1, 12),
) -> pd.Series:

    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    fitted_model = model.fit(disp=False)

    return fitted_model.forecast(steps=horizon)


def holt_winters_forecast(
    series: pd.Series,
    horizon: int,
    seasonal_period: int = 12,
) -> pd.Series:

    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=seasonal_period,
    )

    fitted_model = model.fit()

    return fitted_model.forecast(horizon)
