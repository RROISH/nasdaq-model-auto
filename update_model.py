import yfinance as yf
import json
import os
from datetime import datetime

# 获取数据
ndx = yf.Ticker("^IXIC")
hist = ndx.history(period="1year")
latest = hist.iloc[-1]

# 计算指标
close = latest['Close']
high_52w = hist['High'].max()
low_52w = hist['Low'].min()
position_52w = ((close - low_52w) / (high_52w - low_52w)) * 100

change_1d = ((close - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100
change_5d = ((close - hist.iloc[-6]['Close']) / hist.iloc[-6]['Close']) * 100 if len(hist) >= 6 else 0

ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
ma50_deviation = ((close - ma_50) / ma_50) * 100

vix = yf.Ticker("^VIX").history(period="5d").iloc[-1]['Close']

data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "close": round(close, 2),
    "change_1d": round(change_1d, 2),
    "change_5d": round(change_5d, 2),
    "position_52w": round(position_52w, 2),
    "ma50_deviation": round(ma50_deviation, 2),
    "vix": round(vix, 2)
}

# 保存到output目录（适配你的工作流）
os.makedirs('output', exist_ok=True)
with open('output/latest.json', 'w') as f:
    json.dump(data, f)

# 同时复制到根目录（备用）
with open('latest.json', 'w') as f:
    json.dump(data, f)

print(f"数据已生成: {data}")
