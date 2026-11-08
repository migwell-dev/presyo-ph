import numpy as np
import pandas as pd

from presyo_ph.ml.config import ForecastConfig


def create_features(
    series: pd.Series,
    config: ForecastConfig,
) -> pd.DataFrame:

    df = pd.DataFrame({
        "price": series
    })

    for lag in config.lags:
        df[f"lag_{lag}"] = df["price"].shift(lag)

    for window in config.rolling_windows:
        df[f"rolling_mean_{window}"] = (
            df["price"]
            .shift(1)
            .rolling(window=window)
            .mean()
        )

        df[f"rolling_std_{window}"] = (
            df["price"]
            .shift(1)
            .rolling(window=window)
            .std()
        )

    df["month"] = df.index.month

    df["month_sin"] = (
        2 * 3.141592653589793 * df["month"] / 12
    )

    import numpy as np

    df["month_sin"] = np.sin(df["month_sin"])
    df["month_cos"] = np.cos(
        2 * np.pi * df["month"] / 12
    )

    return df.dropna()


def create_future_features(
    history: pd.Series,
    date: pd.Timestamp,
    config: ForecastConfig,
) -> pd.DataFrame:

    features = {}

    for lag in config.lags:
        features[f"lag_{lag}"] = history.iloc[-lag]

    for window in config.rolling_windows:
        values = history.iloc[-window:]

        features[f"rolling_mean_{window}"] = values.mean()
        features[f"rolling_std_{window}"] = values.std()

    month = date.month

    features["month"] = month
    features["month_sin"] = np.sin(2 * np.pi * month / 12)
    features["month_cos"] = np.cos(2 * np.pi * month / 12)

    return pd.DataFrame([features])
