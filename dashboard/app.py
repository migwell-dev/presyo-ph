import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data import (
    get_commodities,
    get_regions,
    load_forecasts,
    load_gold_pandas,
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Presyo.ph | Food Price Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("Presyo.ph")
st.caption("Philippine Food Price Analytics & Forecasting")


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data(ttl=600)
def load_dashboard_data():
    return {
        "national": load_gold_pandas("national_monthly_prices"),
        "regional": load_gold_pandas("regional_monthly_prices"),
        "market": load_gold_pandas("market_monthly_prices"),
        "growth": load_gold_pandas("national_commodity_growth"),
    }


data = load_dashboard_data()

national = data["national"].copy()
regional = data["regional"].copy()
market = data["market"].copy()
growth = data["growth"].copy()

for df in [national, regional, market]:
    df["price_date"] = pd.to_datetime(df["price_date"])


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Explore",
    [
        "Overview",
        "Regional Analysis",
        "Market Analysis",
        "Price Growth",
        "Forecasting",
    ],
)

commodities = sorted(national["commodity"].dropna().unique())

selected_commodity = st.sidebar.selectbox(
    "Commodity",
    commodities,
    index=commodities.index("rice") if "rice" in commodities else 0,
)

min_date = national["price_date"].min().date()
max_date = national["price_date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = min_date
    end_date = max_date


# --------------------------------------------------
# FILTERED DATA
# --------------------------------------------------

national_filtered = national[
    (national["commodity"] == selected_commodity)
    & (national["price_date"].dt.date >= start_date)
    & (national["price_date"].dt.date <= end_date)
].sort_values("price_date")

regional_filtered = regional[
    (regional["commodity"] == selected_commodity)
    & (regional["price_date"].dt.date >= start_date)
    & (regional["price_date"].dt.date <= end_date)
].copy()

market_filtered = market[
    (market["commodity"] == selected_commodity)
    & (market["price_date"].dt.date >= start_date)
    & (market["price_date"].dt.date <= end_date)
].copy()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_price(value):
    if pd.isna(value):
        return "N/A"

    return f"PHP {value:,.2f}"


def price_trend_chart(df, x, y, title):
    fig = px.line(
        df,
        x=x,
        y=y,
        title=title,
        markers=True,
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (PHP)",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig


# ==================================================
# OVERVIEW
# ==================================================

if page == "Overview":

    st.header("National Overview")

    if national_filtered.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    latest = national_filtered.iloc[-1]

    previous = (
        national_filtered.iloc[-2]
        if len(national_filtered) > 1
        else None
    )

    if previous is not None and previous["avg_price"] != 0:
        monthly_change = (
            (latest["avg_price"] - previous["avg_price"])
            / previous["avg_price"]
        ) * 100
    else:
        monthly_change = None

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Latest Average Price",
        format_price(latest["avg_price"]),
    )

    col2.metric(
        "Monthly Price Change",
        f"{monthly_change:+.2f}%"
        if monthly_change is not None
        else "N/A",
    )

    col3.metric(
        "Markets Reporting",
        f"{int(latest['markets_reporting']):,}",
    )

    st.divider()

    st.subheader(
        f"National {selected_commodity.title()} Price Trend"
    )

    fig = price_trend_chart(
        national_filtered,
        "price_date",
        "avg_price",
        "Monthly Average Price",
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            national_filtered,
            x="price_date",
            y=["min_price", "avg_price", "max_price"],
            title="National Price Range",
            labels={
                "value": "Price (PHP)",
                "price_date": "Date",
                "variable": "Price Metric",
            },
        )

        fig.update_layout(template="plotly_white")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            national_filtered,
            x="price_date",
            y="markets_reporting",
            title="Markets Reporting Over Time",
        )

        fig.update_layout(template="plotly_white")

        st.plotly_chart(fig, use_container_width=True)


# ==================================================
# REGIONAL ANALYSIS
# ==================================================

elif page == "Regional Analysis":

    st.header("Regional Price Analysis")

    if regional_filtered.empty:
        st.warning("No regional data available.")
        st.stop()

    latest_date = regional_filtered["price_date"].max()

    latest_regional = regional_filtered[
        regional_filtered["price_date"] == latest_date
    ].sort_values("avg_price", ascending=False)

    st.caption(
        f"Regional comparison for {latest_date:%B %Y}"
    )

    fig = px.bar(
        latest_regional,
        x="adm1_name",
        y="avg_price",
        color="avg_price",
        title="Average Price by Region",
        labels={
            "adm1_name": "Region",
            "avg_price": "Average Price (PHP)",
        },
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Regional Price Trends")

    selected_regions = st.multiselect(
        "Compare Regions",
        sorted(regional_filtered["adm1_name"].dropna().unique()),
        default=latest_regional["adm1_name"].head(5).tolist(),
    )

    region_trends = regional_filtered[
        regional_filtered["adm1_name"].isin(selected_regions)
    ]

    fig = px.line(
        region_trends,
        x="price_date",
        y="avg_price",
        color="adm1_name",
        title="Monthly Regional Average Prices",
        labels={
            "price_date": "Date",
            "avg_price": "Average Price (PHP)",
            "adm1_name": "Region",
        },
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Regional Statistics")

    st.dataframe(
        latest_regional[
            [
                "adm1_name",
                "avg_price",
                "median_price",
                "min_price",
                "max_price",
                "markets_reporting",
                "imputed_observations",
            ]
        ].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# MARKET ANALYSIS
# ==================================================

elif page == "Market Analysis":

    st.header("Market-Level Analysis")

    if market_filtered.empty:
        st.warning("No market data available.")
        st.stop()

    regions = sorted(
        market_filtered["adm1_name"].dropna().unique()
    )

    selected_region = st.selectbox(
        "Select Region",
        regions,
    )

    regional_markets = market_filtered[
        market_filtered["adm1_name"] == selected_region
    ]

    markets = sorted(
        regional_markets["mkt_name"].dropna().unique()
    )

    selected_market = st.selectbox(
        "Select Market",
        markets,
    )

    selected_data = regional_markets[
        regional_markets["mkt_name"] == selected_market
    ].sort_values("price_date")

    if selected_data.empty:
        st.warning("No data available for this market.")
        st.stop()

    col1, col2, col3 = st.columns(3)

    col1.metric("Market", selected_market)

    col2.metric(
        "Latest Price",
        format_price(selected_data.iloc[-1]["price"]),
    )

    imputed_pct = selected_data["was_imputed"].mean() * 100

    col3.metric(
        "Imputed Observations",
        f"{imputed_pct:.1f}%",
    )

    st.subheader("Market Price Trend")

    fig = price_trend_chart(
        selected_data,
        "price_date",
        "price",
        f"{selected_market} - {selected_commodity.title()}",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Original vs Imputed Prices")

    fig = go.Figure()

    actual = selected_data[
        ~selected_data["was_imputed"].fillna(False)
    ]

    imputed = selected_data[
        selected_data["was_imputed"].fillna(False)
    ]

    fig.add_trace(
        go.Scatter(
            x=actual["price_date"],
            y=actual["price"],
            mode="markers",
            name="Original observations",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=imputed["price_date"],
            y=imputed["price"],
            mode="markers",
            name="Imputed observations",
            marker=dict(symbol="x", size=9),
        )
    )

    fig.update_layout(
        title="Price Observations and Imputation",
        xaxis_title="Date",
        yaxis_title="Price (PHP)",
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Market Data")

    st.dataframe(
        selected_data[
            [
                "price_date",
                "price",
                "original_price",
                "was_imputed",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# PRICE GROWTH
# ==================================================

elif page == "Price Growth":

    st.header("Long-Term Commodity Price Growth")

    growth_sorted = growth.sort_values(
        "price_increase_pct",
        ascending=False,
    )

    col1, col2 = st.columns(2)

    with col1:
        highest = growth_sorted.iloc[0]

        st.metric(
            "Highest Price Increase",
            f"{highest['price_increase_pct']:.2f}%",
            highest["commodity"].title(),
        )

    with col2:
        lowest = growth_sorted.iloc[-1]

        st.metric(
            "Lowest Price Increase",
            f"{lowest['price_increase_pct']:.2f}%",
            lowest["commodity"].title(),
        )

    st.divider()

    fig = px.bar(
        growth_sorted,
        x="commodity",
        y="price_increase_pct",
        color="price_increase_pct",
        title="Commodity Price Increase (%)",
        labels={
            "commodity": "Commodity",
            "price_increase_pct": "Price Increase (%)",
        },
        text_auto=".2f",
    )

    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Price Growth Details")

    display_growth = growth_sorted.copy()

    display_growth["price_increase_pct"] = (
        display_growth["price_increase_pct"].map(
            lambda x: f"{x:.2f}%"
        )
    )

    st.dataframe(
        display_growth,
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# FORECASTING
# ==================================================

elif page == "Forecasting":

    st.header("Food Price Forecasting")

    forecast_commodity = st.selectbox(
        "Forecast Commodity",
        commodities,
        index=commodities.index(selected_commodity),
    )

    try:
        forecasts = load_forecasts(forecast_commodity)

    except Exception as e:
        st.error(f"Unable to load forecasts: {e}")
        st.stop()

    if forecasts.empty:
        st.warning("No forecast data available.")
        st.stop()

    forecasts["forecast_date"] = pd.to_datetime(
        forecasts["forecast_date"]
    )

    forecasts["generated_at"] = pd.to_datetime(
        forecasts["generated_at"],
        errors="coerce",
        utc=True,
    )

    models = sorted(
        forecasts["model_name"].dropna().unique()
    )

    selected_model = st.selectbox(
        "Forecast Model",
        models,
    )

    forecast_data = forecasts[
        forecasts["model_name"] == selected_model
    ].sort_values("forecast_date")

    if forecast_data.empty:
        st.warning("No forecast available for this model.")
        st.stop()

    latest_run = forecast_data["generated_at"].max()

    if pd.notna(latest_run):
        st.caption(
            f"Forecast generated: {latest_run:%Y-%m-%d %H:%M UTC}"
        )

    actual = national[
        national["commodity"] == forecast_commodity
    ].sort_values("price_date")

    forecast_start = forecast_data["forecast_date"].min()

    actual = actual[
        actual["price_date"] < forecast_start
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=actual["price_date"],
            y=actual["avg_price"],
            mode="lines",
            name="Historical Average Price",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_data["forecast_date"],
            y=forecast_data["upper_bound"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_data["forecast_date"],
            y=forecast_data["lower_bound"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(99, 110, 250, 0.20)",
            name="Prediction Interval",
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_data["forecast_date"],
            y=forecast_data["forecast"],
            mode="lines+markers",
            name="Forecast",
        )
    )

    fig.update_layout(
        title=f"{forecast_commodity.title()} Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price (PHP)",
        hovermode="x unified",
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Forecast Values")

    st.dataframe(
        forecast_data[
            [
                "forecast_date",
                "forecast",
                "lower_bound",
                "upper_bound",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
