import altair as alt
import streamlit as st
import talib as ta

from app.functions import (
    get_historical_data,
    make_candlestick_chart,
)


def add_input():
    st.session_state.inputs.append(len(st.session_state.inputs))


def delete_input(index):
    def on_click():
        st.session_state.inputs.pop(index)

    return on_click


def on_change_symbol():
    value = st.session_state.symbol_input
    if value:
        st.session_state.symbol = value


@st.dialog("error")
def show_error_dialog(message):
    st.error("エラーが発生しました。\n" + message)


# session stateの初期化
if "inputs" not in st.session_state:
    st.session_state.inputs = []

if "period" not in st.session_state:
    st.session_state.period = "6mo"

if "interval" not in st.session_state:
    st.session_state.interval = "1d"

if "symbol" not in st.session_state:
    st.session_state.symbol = "^GSPC"

if "symbol_input" not in st.session_state:
    st.session_state.symbol_input = "^GSPC"

st.title("株価チャート")

with st.sidebar:
    st.header("検索条件")
    # 銘柄: テキスト入力
    symbol_input = st.text_input(
        "銘柄(Symbol)",
        key="symbol_input",
        on_change=on_change_symbol,
        placeholder="銘柄名を入力: ^GSPC",
    )

    st.session_state.period = st.selectbox(
        "期間(Period)", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=1
    )  # 2y, 5y

    st.session_state.interval = st.selectbox(
        "間隔(Interval)",
        ["1m", "5m", "15m", "30m", "1h", "1d"],
        index=5,
    )
    st.write("")
    st.button("検索", use_container_width=True)

df = None
try:
    df = get_historical_data(st.session_state.symbol, period=st.session_state.period)

    df["MA7"] = ta.SMA(df.close, timeperiod=7)
    df["MA14"] = ta.SMA(df.close, timeperiod=14)
    df["EMA7"] = ta.SMA(df.close, timeperiod=7)
    df["EMA14"] = ta.SMA(df.close, timeperiod=14)
    # df["ATR"] = ta.ATR(df.high, df.low, df.close, timeperiod=14)
    # df["close+ATR"] = df.close + df.ATR
    # df["close-ATR"] = df.close - df.ATR
    # st.multiselect("Select Indicators", ["MA"])
except Exception as e:
    show_error_dialog(str(e))

if df is not None:
    if st.checkbox("データを表示する"):
        st.write(df)

    fig = make_candlestick_chart(
        df, symbol=st.session_state.symbol, title=f"symbol={st.session_state.symbol}"
    )
    st.plotly_chart(fig)
    # TODO

    # ## Indicator
    # st.button("テクニカル指標を追加", on_click=add_input)

    # for i in st.session_state.inputs:
    #     col1, col2, col3 = st.columns(3, vertical_alignment="bottom")

    #     with col1:
    #         st.selectbox(
    #             "テクニカル指標", ["MA", "Bollinger Band"], key=f"indicator_select_{i}"
    #         )

    #     with col2:
    #         st.text_input("期間", key=f"indicator_text_{i}")

    #     with col3:
    #         st.button("削除", on_click=delete_input(i), key=f"indicator_del_button_{i}")


else:
    st.error("データがありません。")


# 終値 + 特徴量をプロット
# df = analyze(df)

# base = (
#     alt.Chart(df.reset_index(), title="終値+その他")
#     .encode(
#         alt.X("date", axis=alt.Axis(title=None)),
#     )
#     .properties(title="close price")
# )

# line1 = base.mark_line().encode(
#     x=alt.X("date:T"),
#     y=alt.Y("close:Q").scale(zero=False),
# )

# line2 = (
#     base.mark_line()
#     .transform_fold(
#         fold=["upper_breaks_count", "lower_breaks_count"],
#         as_=["variable", "value"],
#     )
#     .encode(alt.Y("value:Q"), color="variable:N")
# )


# chart = alt.layer(line1, line2).resolve_scale(y="independent")

# st.altair_chart(
#     chart,
#     use_container_width=True,
# )
