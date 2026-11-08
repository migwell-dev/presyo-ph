import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from presyo_ph.ml.config import ForecastConfig
from presyo_ph.ml.evaluation import compare_models
from presyo_ph.ml.models.baseline import (
    moving_average_forecast,
    naive_forecast,
    seasonal_naive_forecast,
)
from presyo_ph.ml.models.machine_learning import (
    random_forest_forecast,
    xgboost_forecast,
)
from presyo_ph.ml.models.statistical import (
    holt_winters_forecast,
    sarima_forecast,
)


def generate_forecasts(
    series: pd.Series,
    horizon: int,
    config: ForecastConfig,
) -> dict[str, pd.Series]:

    future_dates = pd.date_range(
        start=series.index[-1] + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq=config.frequency,
    )

    forecasts = {
        "naive": pd.Series(
            naive_forecast(series, horizon),
            index=future_dates,
        ),

        "seasonal_naive": pd.Series(
            seasonal_naive_forecast(
                series,
                horizon,
                config.seasonal_period,
            ),
            index=future_dates,
        ),

        "moving_average": pd.Series(
            moving_average_forecast(series, horizon),
            index=future_dates,
        ),

        "sarima": sarima_forecast(
            series,
            horizon,
        ),

        "holt_winters": holt_winters_forecast(
            series,
            horizon,
            config.seasonal_period,
        ),

        "random_forest": random_forest_forecast(
            series,
            horizon,
            config,
        ),

        "xgboost": xgboost_forecast(
            series,
            horizon,
            config,
        ),
    }

    return forecasts


def evaluate_forecasts(
    series: pd.Series,
    config: ForecastConfig,
) -> pd.DataFrame:

    train = series.iloc[:-config.test_size]
    test = series.iloc[-config.test_size:]

    forecasts = generate_forecasts(
        train,
        len(test),
        config,
    )

    return compare_models(
        test,
        forecasts,
    )

def walk_forward_evaluate(
    series: pd.Series,
    config: ForecastConfig,
    n_splits: int = 3,
) -> pd.DataFrame:

    splitter = TimeSeriesSplit(
        n_splits=n_splits,
        test_size=config.test_size,
    )

    results = []

    for fold, (train_idx, test_idx) in enumerate(
        splitter.split(series),
        start=1,
    ):

        train = series.iloc[train_idx]
        test = series.iloc[test_idx]

        forecasts = generate_forecasts(
            train,
            len(test),
            config,
        )

        metrics = compare_models(
            test,
            forecasts,
        )

        metrics["fold"] = fold

        results.append(metrics)

    results_df = pd.concat(
        results,
        ignore_index=True,
    )

    return (
        results_df
        .groupby("model")
        .agg({
            "mae": "mean",
            "rmse": "mean",
            "smape": "mean",
        })
        .sort_values("smape")
        .reset_index()
    )

