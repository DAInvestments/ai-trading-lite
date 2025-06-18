dashboard.py
# AI Trading Lite - Clean Streamlit Version

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="AI Trading Lite", layout="wide")
st.title("📈 AI Trading Lite Dashboard")
st.markdown(f"Date: **{datetime.now().strftime('%A, %d %B %Y')}**")

# --- WATCHLIST INPUT ---
st.subheader("🔧 Your ASX Watchlist")
def_watchlist = "CSL.AX, BHP.AX, NAB.AX, RIO.AX, WBC.AX, NCK.AX, VSCO, MGR.AX"
user_input = st.text_input("Enter ASX tickers (comma separated):", def_watchlist)
watchlist = [ticker.strip().upper() for ticker in user_input.split(",") if ticker.strip()]

# --- FETCH DATA ---
def fetch_price_data(tickers):
    try:
        df = yf.download(tickers=tickers, period="7d", interval="1d", group_by='ticker', auto_adjust=True, threads=True)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_price_data(watchlist)

# --- BASIC SIGNALS ---
def generate_signals(data):
    signals = []
    for ticker in watchlist:
        try:
            df = data[ticker].copy()
            df["SMA_3"] = df["Close"].rolling(3).mean()
            df["SMA_5"] = df["Close"].rolling(5).mean()
            latest = df.iloc[-1]
            signal = "HOLD"
            if latest["SMA_3"] > latest["SMA_5"]:
                signal = "BUY"
            elif latest["SMA_3"] < latest["SMA_5"]:
                signal = "SELL"
            signals.append({
                "Ticker": ticker,
                "Price": round(latest["Close"], 2),
                "SMA_3": round(latest["SMA_3"], 2),
                "SMA_5": round(latest["SMA_5"], 2),
                "Signal": signal
            })
        except Exception as e:
            signals.append({"Ticker": ticker, "Error": str(e)})
    return pd.DataFrame(signals)

if data is not None and not data.empty:
    st.subheader("📋 Trading Signals")
    results = generate_signals(data)
    st.dataframe(results)
else:
    st.warning("No data returned. Check tickers or connection.")
