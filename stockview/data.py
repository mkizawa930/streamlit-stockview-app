import joblib
import yfinance as yf

memory = joblib.Memory("/tmp/stockview")


@memory.cache
def fetch(symbol="^GSPC", period="6mo", interval="1d"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(interval=interval, period=period)
    df.rename(columns=str.lower, inplace=True)
    df.index.name = df.index.name.lower()
    return df
