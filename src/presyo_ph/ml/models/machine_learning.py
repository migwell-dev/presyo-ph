import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from presyo_ph.ml.config import ForecastConfig
from presyo_ph.ml.features import (
    create_features,
    create_future_features,
)


def recursive_forecast(
    model,
    series: pd.Series,
    horizon: int,
    config: ForecastConfig,
) -> pd.Series:
    """
    Generate multi-step forecasts recursively.

    Each prediction becomes part of the history
    used to generate the next prediction.
    """

    history = series.copy()
    predictions = []

    for _ in range(horizon):

        next_date = (
            history.index[-1] + pd.offsets.MonthBegin(1)
        )

        X_future = create_future_features(
            history,
            next_date,
            config,
        )

        prediction = float(model.predict(X_future)[0])

        predictions.append(prediction)

        history.loc[next_date] = prediction

    future_dates = pd.date_range(
        start=series.index[-1] + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq=config.frequency,
    )

    return pd.Series(
        predictions,
        index=future_dates,
        name="forecast",
    )


def random_forest_forecast(
    series: pd.Series,
    horizon: int,
    config: ForecastConfig,
) -> pd.Series:

    df = create_features(series, config)

    X = df.drop(columns=["price"])
    y = df["price"]

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        random_state=config.random_state,
        n_jobs=-1,
    )

    model.fit(X, y)

    return recursive_forecast(
        model,
        series,
        horizon,
        config,
    )


def xgboost_forecast(
    series: pd.Series,
    horizon: int,
    config: ForecastConfig,
) -> pd.Series:

    df = create_features(series, config)

    X = df.drop(columns=["price"])
    y = df["price"]

    model = XGBRegressor(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=config.random_state,
    )

    model.fit(X, y)

    return recursive_forecast(
        model,
        series,
        horizon,
        config,
    )
