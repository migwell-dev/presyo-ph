from dataclasses import dataclass


@dataclass(frozen=True)
class ForecastConfig:
    date_col: str = "price_date"
    target_col: str = "price"

    frequency: str = "MS"
    horizon: int = 12
    test_size: int = 12

    seasonal_period: int = 12

    lags: tuple[int, ...] = (1, 2, 3, 6, 12)
    rolling_windows: tuple[int, ...] = (3, 6, 12)

    random_state: int = 42
