import pandas as pd


def prepare_time_series(
    df: pd.DataFrame,
    date_col: str = "price_date",
    target_col: str = "price",
    frequency: str = "MS",
    missing: str = "raise",
) -> pd.Series:
    """
    Convert a DataFrame into a regular monthly time series.

    Parameters
    ----------
    df : pd.DataFrame
        Historical price data.
    date_col : str
        Date column.
    target_col : str
        Numeric target column.
    frequency : str
        Pandas frequency, default monthly start.
    missing : str
        How to handle missing months:
        - raise: raise an error.
        - ffill: forward-fill using previous observations only.

    Returns
    -------
    pd.Series
        Monthly price series.
    """

    data = df[[date_col, target_col]].copy()

    data[date_col] = pd.to_datetime(data[date_col])
    data[target_col] = pd.to_numeric(
        data[target_col],
        errors="coerce",
    )

    data = data.dropna(subset=[date_col, target_col])

    data = (
        data.groupby(date_col)[target_col]
        .mean()
        .sort_index()
    )

    data.index = data.index.to_period("M").to_timestamp()

    data = data.groupby(level=0).mean()

    data = data.asfreq(frequency)

    if data.isna().any():

        if missing == "ffill":
            data = data.ffill()

        elif missing == "raise":
            missing_dates = data[data.isna()].index.tolist()

            raise ValueError(
                f"Missing monthly observations: {missing_dates}"
            )

        else:
            raise ValueError(
                "missing must be either 'raise' or 'ffill'."
            )

    if len(data) == 0:
        raise ValueError("No valid observations found.")

    return data.astype(float)
