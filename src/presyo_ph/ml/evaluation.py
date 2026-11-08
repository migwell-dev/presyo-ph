import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def evaluate_forecast(
    actual: pd.Series,
    predicted: pd.Series,
) -> dict:

    actual, predicted = actual.align(
        predicted,
        join="inner",
    )

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    denominator = (
        np.abs(actual) + np.abs(predicted)
    )

    smape = np.mean(
        np.where(
            denominator == 0,
            0,
            2 * np.abs(actual - predicted) / denominator,
        )
    ) * 100

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "smape": float(smape),
    }


def compare_models(
    actual: pd.Series,
    forecasts: dict[str, pd.Series],
) -> pd.DataFrame:

    results = []

    for model_name, predicted in forecasts.items():

        metrics = evaluate_forecast(
            actual,
            predicted,
        )

        results.append({
            "model": model_name,
            **metrics,
        })

    return (
        pd.DataFrame(results)
        .sort_values("smape")
        .reset_index(drop=True)
    )
