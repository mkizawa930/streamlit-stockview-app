import mplfinance as mpf
import pandas as pd
import talib as ta
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


def create_canldestick_chart(df: pd.DataFrame, show=False):
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
