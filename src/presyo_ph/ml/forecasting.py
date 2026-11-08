import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DateType,
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.arima.model import ARIMA

from presyo_ph.medallion.gold import save_gold_tables
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

FORECAST_SCHEMA = StructType([
    StructField("forecast_date", DateType(), nullable=False),
    StructField("commodity", StringType(), nullable=False),
    StructField("model_name", StringType(), nullable=False),
    StructField("forecast", DoubleType(), nullable=False),
    StructField("lower_bound", DoubleType(), nullable=False),
    StructField("upper_bound", DoubleType(), nullable=False),
    StructField("generated_at", TimestampType(), nullable=False),
])


def _future_index(
    series: pd.Series,
    horizon: int,
    config: ForecastConfig,
) -> pd.DatetimeIndex:
    """Return the next `horizon` periods after the last observation."""
    return pd.date_range(
        start=series.index[-1],
        periods=horizon + 1,
        freq=config.frequency,
    )[1:]


def _as_series(values, index: pd.DatetimeIndex) -> pd.Series:
    """Coerce model output to a float Series on the shared forecast index."""
    arr = (
        values.to_numpy()
        if hasattr(values, "to_numpy")
        else np.asarray(values)
    )

    if len(arr) != len(index):
        raise ValueError(
            f"Forecast length {len(arr)} does not match "
            f"horizon {len(index)}."
        )

    return pd.Series(arr.astype(float), index=index)


def save_forecasts(
    spark: SparkSession,
    forecast_df: pd.DataFrame,
    commodity_name: str
) -> None:
    """Convert pandas forecast output to Spark and save it to Gold."""

    rows = [
        (
            row.forecast_date.date(),
            row.commodity,
            row.model_name,
            float(row.forecast),
            float(row.lower_bound),
            float(row.upper_bound),
            row.generated_at.to_pydatetime(),
        )
        for row in forecast_df.itertuples(index=False)
    ]

    spark_df = spark.createDataFrame(
        rows,
        schema=FORECAST_SCHEMA,
    )

    save_gold_tables({
        f"{commodity_name}_forecasts": spark_df,
    })


def prepare_series(
    df: pd.DataFrame,
    config: ForecastConfig,
) -> pd.Series:
    """
    Prepare a monthly time series from a pandas DataFrame.

    Expects one observation per month, with no missing target values.
    Dates are normalized to the start of their month.
    """

    required_columns = [
        config.date_col,
        config.target_col,
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = df[required_columns].copy()

    data[config.date_col] = (
        pd.to_datetime(data[config.date_col])
        .dt.to_period("M")
        .dt.to_timestamp()  # month start
    )

    data[config.target_col] = pd.to_numeric(
        data[config.target_col],
        errors="coerce",
    )

    data = data.dropna(
        subset=[config.date_col, config.target_col]
    )

    data = data.sort_values(config.date_col)

    if data[config.date_col].duplicated().any():
        raise ValueError(
            "Duplicate dates found. Aggregate the data to one "
            "observation per month before forecasting."
        )

    series = (
        data
        .set_index(config.date_col)[config.target_col]
        .astype(float)
        .asfreq(config.frequency)
    )

    if series.isna().any():
        raise ValueError(
            "Missing monthly observations found. Resolve missing "
            "months before fitting the forecasting model."
        )

    if len(series) < 3:
        raise ValueError(
            "At least three observations are required."
        )

    return series


def fit_forecaster(
    series: pd.Series,
    config: ForecastConfig,
):
    """Fit the configured ARIMA model."""

    model = ARIMA(
        series,
        order=config.arima_order,
    )

    return model.fit()


def generate_forecast(
    series: pd.Series,
    config: ForecastConfig,
    commodity: str = "rice",
) -> pd.DataFrame:
    """
    Fit ARIMA and generate future forecasts with prediction intervals.
    """

    fitted_model = fit_forecaster(series, config)

    alpha = 1 - config.confidence_level

    forecast_result = fitted_model.get_forecast(
        steps=config.horizon
    )

    forecast_summary = forecast_result.summary_frame(
        alpha=alpha
    )

    future_dates = _future_index(series, config.horizon, config)

    forecast_df = pd.DataFrame({
        "forecast_date": future_dates,
        "commodity": commodity,
        "model_name": f"ARIMA{config.arima_order}",
        "forecast": forecast_summary["mean"].to_numpy(),
        "lower_bound": forecast_summary["mean_ci_lower"].to_numpy(),
        "upper_bound": forecast_summary["mean_ci_upper"].to_numpy(),
        "generated_at": pd.Timestamp.now(tz="UTC").tz_localize(None),
    })

    return forecast_df


def generate_forecasts(
    series: pd.Series,
    horizon: int,
    config: ForecastConfig,
) -> dict[str, pd.Series]:
    """Run all candidate models; return forecasts on a shared index."""

    idx = _future_index(series, horizon, config)

    raw = {
        "naive": naive_forecast(series, horizon),
        "seasonal_naive": seasonal_naive_forecast(
            series,
            horizon,
            config.seasonal_period,
        ),
        "moving_average": moving_average_forecast(series, horizon),
        "sarima": sarima_forecast(series, horizon),
        "holt_winters": holt_winters_forecast(
            series,
            horizon,
            config.seasonal_period,
        ),
        "random_forest": random_forest_forecast(series, horizon, config),
        "xgboost": xgboost_forecast(series, horizon, config),
    }

    return {name: _as_series(vals, idx) for name, vals in raw.items()}


def evaluate_forecasts(
    series: pd.Series,
    config: ForecastConfig,
) -> pd.DataFrame:
    """Evaluate all models on a single holdout split."""

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
    """Evaluate all models with expanding-window cross-validation."""

    min_train = max(2 * config.seasonal_period, 24)
    needed = min_train + n_splits * config.test_size

    if len(series) < needed:
        raise ValueError(
            f"Need at least {needed} observations for {n_splits} folds; "
            f"got {len(series)}."
        )

    splitter = TimeSeriesSplit(
        n_splits=n_splits,
        test_size=config.test_size,
    )

    results = []

    for fold, (train_idx, test_idx) in enumerate(
        splitter.split(series),
        start=1,
    ):

        # iloc with an index array drops the freq; restore it.
        train = series.iloc[train_idx].asfreq(config.frequency)
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
