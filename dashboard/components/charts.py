"""Reusable Plotly chart factories for the Streamlit dashboard."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def create_candlestick_chart(
    prices: pd.DataFrame,
    indicators: pd.DataFrame = None,
    signals: pd.DataFrame = None,
    title: str = "",
    show_emas: bool = True,
    show_smas: bool = True,
    show_vwap: bool = True,
    show_bb: bool = False,
    height: int = 600,
) -> go.Figure:
    """Create a candlestick chart with optional MA overlays and signal markers."""
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=prices["date"],
        open=prices["open"],
        high=prices["high"],
        low=prices["low"],
        close=prices["close"],
        name="Price",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ))

    if indicators is not None and not indicators.empty:
        ma_colors = {
            "ema_5": "#ff9800", "ema_10": "#2196f3", "ema_20": "#9c27b0",
            "ema_50": "#f44336", "ema_200": "#4caf50",
            "sma_50": "#ff5722", "sma_200": "#00bcd4",
            "vwap_20": "#795548",
        }

        if show_emas:
            for col in ["ema_5", "ema_10", "ema_20", "ema_50", "ema_200"]:
                if col in indicators.columns:
                    fig.add_trace(go.Scatter(
                        x=indicators["date"], y=indicators[col],
                        name=col.upper().replace("_", " "),
                        line=dict(width=1, color=ma_colors.get(col, "#888")),
                        visible="legendonly" if col in ("ema_5", "ema_10") else True,
                    ))

        if show_smas:
            for col in ["sma_50", "sma_200"]:
                if col in indicators.columns:
                    fig.add_trace(go.Scatter(
                        x=indicators["date"], y=indicators[col],
                        name=col.upper().replace("_", " "),
                        line=dict(width=1.5, dash="dash", color=ma_colors.get(col, "#888")),
                    ))

        if show_vwap and "vwap_20" in indicators.columns:
            fig.add_trace(go.Scatter(
                x=indicators["date"], y=indicators["vwap_20"],
                name="VWAP 20",
                line=dict(width=1.5, dash="dot", color=ma_colors["vwap_20"]),
            ))

        if show_bb and "bb_upper" in indicators.columns and "bb_lower" in indicators.columns:
            fig.add_trace(go.Scatter(
                x=indicators["date"], y=indicators["bb_upper"],
                name="BB Upper",
                line=dict(width=1, color="rgba(174,213,129,0.6)"),
            ))
            fig.add_trace(go.Scatter(
                x=indicators["date"], y=indicators["bb_lower"],
                name="BB Lower",
                line=dict(width=1, color="rgba(174,213,129,0.6)"),
                fill="tonexty", fillcolor="rgba(174,213,129,0.08)",
            ))
            if "bb_middle" in indicators.columns:
                fig.add_trace(go.Scatter(
                    x=indicators["date"], y=indicators["bb_middle"],
                    name="BB Middle",
                    line=dict(width=1, dash="dot", color="rgba(174,213,129,0.4)"),
                ))

    if signals is not None and not signals.empty:
        bull = signals[signals["direction"] == "bullish"]
        bear = signals[signals["direction"] == "bearish"]

        if not bull.empty:
            fig.add_trace(go.Scatter(
                x=bull["date"], y=bull["price"],
                mode="markers", name="Bullish Signal",
                marker=dict(symbol="triangle-up", size=10, color="#26a69a", line=dict(width=1, color="white")),
                text=bull["signal_type"], hoverinfo="text+x+y",
            ))

        if not bear.empty:
            fig.add_trace(go.Scatter(
                x=bear["date"], y=bear["price"],
                mode="markers", name="Bearish Signal",
                marker=dict(symbol="triangle-down", size=10, color="#ef5350", line=dict(width=1, color="white")),
                text=bear["signal_type"], hoverinfo="text+x+y",
            ))

    fig.update_layout(
        title=title, height=height, xaxis_rangeslider_visible=False,
        template="plotly_white", margin=dict(l=50, r=20, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_rsi_chart(indicators: pd.DataFrame, height: int = 200) -> go.Figure:
    """Create RSI subplot chart with overbought/oversold zones."""
    fig = go.Figure()

    if "rsi_14" in indicators.columns:
        fig.add_trace(go.Scatter(
            x=indicators["date"], y=indicators["rsi_14"],
            name="RSI(14)", line=dict(color="#2196f3", width=1.5),
        ))

    if "rsi_21" in indicators.columns:
        fig.add_trace(go.Scatter(
            x=indicators["date"], y=indicators["rsi_21"],
            name="RSI(21)", line=dict(color="#ff9800", width=1),
            visible="legendonly",
        ))

    # Overbought/oversold bands
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3)

    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.05)
    fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.05)

    fig.update_layout(
        title="RSI", height=height, template="plotly_white",
        margin=dict(l=50, r=20, t=30, b=20),
        yaxis=dict(range=[0, 100]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_macd_chart(indicators: pd.DataFrame, height: int = 200) -> go.Figure:
    """Create MACD subplot chart with histogram."""
    fig = go.Figure()

    if "macd" in indicators.columns:
        fig.add_trace(go.Scatter(
            x=indicators["date"], y=indicators["macd"],
            name="MACD", line=dict(color="#2196f3", width=1.5),
        ))

    if "macd_signal" in indicators.columns:
        fig.add_trace(go.Scatter(
            x=indicators["date"], y=indicators["macd_signal"],
            name="Signal", line=dict(color="#ff9800", width=1),
        ))

    if "macd_histogram" in indicators.columns:
        colors = ["#26a69a" if v >= 0 else "#ef5350" for v in indicators["macd_histogram"]]
        fig.add_trace(go.Bar(
            x=indicators["date"], y=indicators["macd_histogram"],
            name="Histogram", marker_color=colors, opacity=0.6,
        ))

    fig.add_hline(y=0, line_color="gray", opacity=0.3)

    fig.update_layout(
        title="MACD", height=height, template="plotly_white",
        margin=dict(l=50, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_equity_curve(trades_df: pd.DataFrame, initial_capital: float = 10000, height: int = 350) -> go.Figure:
    """Create equity curve from trades DataFrame."""
    fig = go.Figure()

    if trades_df.empty or "return_pct" not in trades_df.columns:
        fig.update_layout(title="Equity Curve (No trades)", height=height, template="plotly_white",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    equity = [initial_capital]
    dates = [trades_df["entry_date"].iloc[0]]

    for _, trade in trades_df.iterrows():
        if pd.notna(trade["return_pct"]):
            equity.append(equity[-1] * (1 + trade["return_pct"] / 100))
            dates.append(trade["exit_date"])

    fig.add_trace(go.Scatter(
        x=dates, y=equity,
        name="Equity", line=dict(color="#2196f3", width=2),
        fill="tozeroy", fillcolor="rgba(33,150,243,0.1)",
    ))

    fig.add_hline(y=initial_capital, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title="Equity Curve", height=height, template="plotly_white",
        margin=dict(l=50, r=20, t=40, b=30),
        yaxis_title="Capital ($)",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_sector_comparison(perf_df: pd.DataFrame, metric: str = "total_return", height: int = 400) -> go.Figure:
    """Create bar chart comparing a metric across sectors."""
    fig = go.Figure()

    if perf_df.empty:
        fig.update_layout(title="Sector Comparison (No data)", height=height, template="plotly_white",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    from config import SECTORS

    perf_df = perf_df.copy()
    perf_df["sector"] = perf_df["ticker"].map(SECTORS)

    sector_avg = perf_df.groupby("sector")[metric].mean().sort_values(ascending=False)

    colors = {
        "Banks": "#2196f3", "Oil & Gas": "#ff9800", "Pipelines": "#ff5722",
        "Utilities": "#4caf50", "Tech": "#9c27b0", "Rails": "#795548",
        "Telecom": "#00bcd4", "Mining": "#ffc107",
    }

    fig.add_trace(go.Bar(
        x=sector_avg.index,
        y=sector_avg.values,
        marker_color=[colors.get(s, "#888") for s in sector_avg.index],
        text=[f"{v:.1f}%" for v in sector_avg.values],
        textposition="auto",
    ))

    label = metric.replace("_", " ").title()
    fig.update_layout(
        title=f"Average {label} by Sector", height=height, template="plotly_white",
        margin=dict(l=50, r=20, t=50, b=30),
        yaxis_title=label,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_correlation_heatmap(prices_dict: dict[str, pd.Series], height: int = 500) -> go.Figure:
    """Create price correlation matrix heatmap from dict of ticker -> close price series."""
    if not prices_dict:
        fig = go.Figure()
        fig.update_layout(title="Correlation (No data)", height=height, template="plotly_white",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig

    df = pd.DataFrame(prices_dict)
    # Use returns for correlation
    returns = df.pct_change().dropna()
    corr = returns.corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=9),
    ))

    fig.update_layout(
        title="Return Correlation Matrix", height=height, template="plotly_white",
        margin=dict(l=80, r=20, t=50, b=80),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
