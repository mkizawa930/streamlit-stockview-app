from app.exceptions import NotFoundException
import mplfinance as mpf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import talib as ta
import yfinance as yf
from pylab import plt


def analyze(df):
    df["highest"] = df["high"].rolling(14).max().shift(1)
    df["lowest"] = df["low"].rolling(14).min().shift(1)

    atr = ta.ATR(df["high"], df["low"], df["close"], timeperiod=20)
    df["upper"] = df["close"] + 2 * atr.shift(1)
    df["lower"] = df["close"] - 2 * atr.shift(1)

    df["upper_breaks_count"] = (df["high"] >= df["highest"]).rolling(10).sum()
    df["lower_breaks_count"] = (df["low"] <= df["lowest"]).rolling(10).sum()

    bbands_upper, bbands_middle, bbands_lower = ta.BBANDS(
        df["close"], timeperiod=14, nbdevup=2, nbdevdn=2, matype=0
    )
    df["bbands_upper"] = bbands_upper
    df["bbands_lower"] = bbands_lower
    return df


def make_candlestick_figure(df: pd.DataFrame, show=False):
    fig, axes = mpf.plot(
        df,
        type="candle",
        style="yahoo",
        datetime_format="%Y-%m-%d",
        mav=(7, 14, 25),
        volume=True,
        returnfig=True,  # 画像オブジェクトを返す
    )
    return fig, axes


def create_analyzed_chart(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, gridspec_kw={"height_ratios": [2, 1]})
    df[["highest", "close", "lowest"]].plot(ax=axes[0])
    df[["upper_breaks_count", "lower_breaks_count"]].plot(ax=axes[1])
    plt.tight_layout()
    plt.legend(loc="upper left")
    return fig, axes


def fetch(symbol="^GSPC", period="6mo", interval="1d"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(interval=interval, period=period)
    df.rename(columns=str.lower, inplace=True)
    df.index.name = df.index.name.lower()
    return df


@st.cache_data
def get_historical_data(symbol: str, period: str, interval: str = "1d"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    if df.shape[0] == 0:
        raise NotFoundException(
            f"No price data found: symbol={symbol}(period={period}, interval={interval})"
        )
    df.rename(columns=str.lower, inplace=True)
    df.index.name = df.index.name.lower()
    return df


# plotlyでローソク足チャートを作成する
def make_candlestick_chart(df: pd.DataFrame, symbol: str, title: str):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df.open,
                high=df.high,
                low=df.low,
                close=df.close,
                name="OHLCV",
            ),
            go.Scatter(x=df.index, y=df["EMA7"], name="EMA7"),
            go.Scatter(x=df.index, y=df["EMA14"], name="EMA14"),
            # go.Scatter(x=df.index, y=df["close+ATR"], name="close+ATR"),
            # go.Scatter(x=df.index, y=df["close-ATR"], name="close-ATR"),
        ],
        layout={
            "title": title,
        },
    )
    fig.update_layout(yaxis=dict(autorange=True, fixedrange=False))

    return fig
