import time
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import requests

# Telegram credentials
BOT_TOKEN = '7957629826:AAG4yUMTw7lzDpFiQOApEyMJfF99sH93E0U'
CHAT_ID = '8419695857'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def run_bot():
    symbol = "AAPL"
    data = yf.download(symbol, period="12mo", interval="1d")

    close = data["Close"]

    rsi = RSIIndicator(close=close, window=14).rsi()
    sma_50 = SMAIndicator(close=close, window=50).sma_indicator()
    sma_200 = SMAIndicator(close=close, window=200).sma_indicator()

    latest_price = close.iloc[-1]
    latest_rsi = rsi.iloc[-1]
    latest_sma_50 = sma_50.iloc[-1]
    latest_sma_200 = sma_200.iloc[-1]

    signal = "📊 Hold: No strong signal"
    if pd.isna(latest_rsi) or pd.isna(latest_sma_50) or pd.isna(latest_sma_200):
        signal = "⚠️ Not enough data for indicators."
    elif latest_rsi < 30 and latest_sma_50 > latest_sma_200:
        signal = "📈 BUY signal: RSI < 30 and SMA50 > SMA200"
    elif latest_rsi > 70 and latest_sma_50 < latest_sma_200:
        signal = "📉 SELL signal: RSI > 70 and SMA50 < SMA200"

    msg = (
        f"--- Signal for {symbol} ---\n"
        f"Price: £{latest_price:.2f}\n"
        f"RSI: {latest_rsi:.2f}\n"
        f"50-day SMA: £{latest_sma_50:.2f}\n"
        f"200-day SMA: £{latest_sma_200:.2f}\n"
        f"{signal}"
    )
    print(msg)
    send_telegram_message(msg)

# Main loop: run every 5 minutes
while True:
    try:
        run_bot()
    except Exception as e:
        send_telegram_message(f"❌ Bot error: {e}")
    time.sleep(300)  # 5 minutes
