import altair as alt
import plotly.graph_objects as go
import streamlit as st
import talib as ta

from stockview.data import fetch


def gen_candlestick_chart(df):
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
            go.Scatter(x=df.index, y=df["MA7"], name="MA7"),
        ],
        layout={
            "title": f"Candlestick chart {'^GSPC'}",
        },
    )
    fig.update_layout(yaxis=dict(autorange=True, fixedrange=False))

    return fig


if "inputs" not in st.session_state:
    st.session_state.inputs = []

if "period" not in st.session_state:
    st.session_state.period = "6mo"


def add_input():
    st.session_state.inputs.append(len(st.session_state.inputs))


def delete_input(index):
    def on_click():
        st.session_state.inputs.pop(index)

    return on_click


st.title("株価Dashboard")

st.session_state.period = st.selectbox(
    "期間", ["1mo", "3mo", "6mo", "1y"], index=1
)  # 2y, 5y

df = fetch("^GSPC", period=st.session_state.period)

df["MA7"] = ta.SMA(df.close, timeperiod=14)
# st.multiselect("Select Indicators", ["MA"])


fig = gen_candlestick_chart(df)
st.plotly_chart(fig)

st.button("Indicatorを追加", on_click=add_input)

for i in st.session_state.inputs:
    col1, col2, col3 = st.columns(3, vertical_alignment="bottom")

    with col1:
        st.selectbox("Indicator", ["MA", "Bollinger Band"], key=f"indicator_select_{i}")

    with col2:
        st.text_input("Period", key=f"indicator_text_{i}")

    with col3:
        st.button("delete", on_click=delete_input(i), key=f"indicator_del_button_{i}")

c = (
    alt.Chart(df.reset_index())
    .mark_line()
    .encode(
        alt.Y("close").scale(zero=False),
        x="date",
    )
)
st.altair_chart(c, use_container_width=True)

st.subheader("OHLCデータ")
st.write(df)
