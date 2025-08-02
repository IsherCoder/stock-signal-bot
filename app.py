import yfinance as yf
import ta
import pandas as pd
import requests

# --- SETTINGS ---
symbol = "AAPL"
BOT_TOKEN = "7957629826:AAG4yUMTw7lzDpFiQOApEyMJfF99sH93E0U"
CHAT_ID = "8419695857"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

# --- FETCH DATA ---
data = yf.download(symbol, period="12mo", interval="1d")
data.dropna(inplace=True)

close_series = data["Close"]
if isinstance(close_series, pd.DataFrame):
    close_series = close_series.iloc[:, 0]

rsi = ta.momentum.RSIIndicator(close=close_series, window=14)
sma50 = ta.trend.SMAIndicator(close=close_series, window=50)
sma200 = ta.trend.SMAIndicator(close=close_series, window=200)

data["RSI"] = rsi.rsi()
data["SMA_50"] = sma50.sma_indicator()
data["SMA_200"] = sma200.sma_indicator()
data.dropna(inplace=True)

latest = data.iloc[-1]

try:
    price = float(latest["Close"])
    latest_rsi = float(latest["RSI"])
    latest_sma50 = float(latest["SMA_50"])
    latest_sma200 = float(latest["SMA_200"])
except (TypeError, ValueError):
    send_telegram_message("❗ Not enough data to generate signal.")
    exit()

# --- BUILD MESSAGE ---
message = f"📈 *Signal for {symbol}*\n"
message += f"Price: £{round(price, 2)}\n"
message += f"RSI: {round(latest_rsi, 2)}\n"
message += f"SMA50: £{round(latest_sma50, 2)}\n"
message += f"SMA200: £{round(latest_sma200, 2)}\n"

if latest_rsi < 30 and latest_sma50 > latest_sma200:
    signal = "✅ *Buy Signal*: Oversold and trending up"
elif latest_rsi > 70:
    signal = "❌ *Sell Signal*: Overbought"
else:
    signal = "📊 *Hold*: No strong signal"

message += f"\n{signal}"
send_telegram_message(message)
