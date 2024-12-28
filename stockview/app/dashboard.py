from datetime import datetime

import altair as alt
import plotly.graph_objects as go
import streamlit as st
import talib as ta
import yfinance as yf
from analysis import analyze

today = datetime.now().date()


def fetch(symbol="^GSPC", period="6mo", interval="1d"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(interval=interval, period=period)
    df.rename(columns=str.lower, inplace=True)
    df.index.name = df.index.name.lower()
    return df


@st.cache_data
def get_historical_data(symbol: str, period: str, interval: str = "1d", today=today):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    df.rename(columns=str.lower, inplace=True)
    df.index.name = df.index.name.lower()
    return df


# plotlyでローソク足チャートを作成する
def gen_candlestick_chart(df, symbol):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df.open,
                high=df.high,
                low=df.low,
                close=df.close,
                name="candlestick",
            ),
            go.Scatter(x=df.index, y=df["EMA7"], name="EMA7"),
            go.Scatter(x=df.index, y=df["EMA14"], name="EMA14"),
            # go.Scatter(x=df.index, y=df["close+ATR"], name="close+ATR"),
            # go.Scatter(x=df.index, y=df["close-ATR"], name="close-ATR"),
        ],
        layout={
            "title": f"Candlestick chart {symbol}",
        },
    )
    fig.update_layout(yaxis=dict(autorange=True, fixedrange=False))

    return fig


def add_input():
    st.session_state.inputs.append(len(st.session_state.inputs))


def delete_input(index):
    def on_click():
        st.session_state.inputs.pop(index)

    return on_click


# def on_change_symbol_input():
#     st.session_state.symbol_input =


def on_change_symbol():
    print(st.session_state.symbol_input)
    st.session_state.symbol = st.session_state.symbol_input


st.sidebar.title("Chart Viewer")

st.sidebar.subheader("Chart Options")

# session stateの初期化
if "inputs" not in st.session_state:
    st.session_state.inputs = []

if "period" not in st.session_state:
    st.session_state.period = "6mo"

if "symbol" not in st.session_state:
    st.session_state.symbol = "^GSPC"

if "symbol_input" not in st.session_state:
    st.session_state.symbol_input = "^GSPC"


st.title("株価Dashboard")

# Sidebar
col1, col2 = st.columns(2, vertical_alignment="bottom")

with col1:
    value = st.session_state.symbol_input = st.sidebar.selectbox(
        "シンボルを選択",
        ["^GSPC", "^IXIC", "^N225"],
    )

# with col2:
#     st.sidebar.button("Change", on_click=on_change_symbol)

st.session_state.period = st.selectbox(
    "期間", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=1
)  # 2y, 5y


df = get_historical_data(st.session_state.symbol, period=st.session_state.period)

df["MA7"] = ta.SMA(df.close, timeperiod=7)
df["MA14"] = ta.SMA(df.close, timeperiod=14)
df["EMA7"] = ta.SMA(df.close, timeperiod=7)
df["EMA14"] = ta.SMA(df.close, timeperiod=14)
df["ATR"] = ta.ATR(df.high, df.low, df.close, timeperiod=14)
df["close+ATR"] = df.close + df.ATR
df["close-ATR"] = df.close - df.ATR
# st.multiselect("Select Indicators", ["MA"])

fig = gen_candlestick_chart(df, symbol=st.session_state.symbol)
st.plotly_chart(fig)

# Indicator
st.button("Indicatorを追加", on_click=add_input)

for i in st.session_state.inputs:
    col1, col2, col3 = st.columns(3, vertical_alignment="bottom")

    with col1:
        st.selectbox("Indicator", ["MA", "Bollinger Band"], key=f"indicator_select_{i}")

    with col2:
        st.text_input("Period", key=f"indicator_text_{i}")

    with col3:
        st.button("delete", on_click=delete_input(i), key=f"indicator_del_button_{i}")


# 終値 + 特徴量をプロット
df = analyze(df)

base = (
    alt.Chart(df.reset_index(), title="終値+その他")
    .encode(
        alt.X("date", axis=alt.Axis(title=None)),
    )
    .properties(title="close price")
)

line1 = base.mark_line().encode(
    x=alt.X("date:T"),
    y=alt.Y("close:Q").scale(zero=False),
)

line2 = (
    base.mark_line()
    .transform_fold(
        fold=["upper_breaks_count", "lower_breaks_count"],
        as_=["variable", "value"],
    )
    .encode(alt.Y("value:Q"), color="variable:N")
)


# line2 = base.mark_line(color="#ebb134").encode(
#     alt.Y(
#         "upper_breaks_count",
#     ),
# )

# line3 = base.mark_line(color="#eb3434").encode(
#     alt.Y(
#         "lower_breaks_count",
#         axis=alt.Axis(title="count"),
#     ),
# )


chart = alt.layer(line1, line2).resolve_scale(y="independent")

st.altair_chart(
    chart,
    use_container_width=True,
)

if st.checkbox("データを表示する"):
    st.subheader("OHLCデータ")
    st.write(df)
