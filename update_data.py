#!/usr/bin/env python3
"""
纳指买卖模型 - 终极修复版
"""

import json
import os
import sys
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

DATA_FILE = "data/nasdaq_data.json"

def fetch_data(ticker, period="10y"):
    """获取数据 - 强制转为一维"""
    print(f"获取 {ticker} ...")
    
    df = yf.download(ticker, period=period, progress=False, auto_adjust=False)
    df = df.reset_index()
    
    # 处理多级列名
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 找到收盘价列
    close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    
    # 强制转为一维 numpy 数组，避免 DataFrame 问题
    prices = np.array(df[close_col]).flatten()
    dates = pd.to_datetime(df['Date']).values
    
    # 创建简单的 DataFrame
    result = pd.DataFrame({
        'Date': dates,
        'Close': prices.astype(float)
    }).dropna()
    
    print(f"  成功: {len(result)} 条")
    return result

def calculate_signals(ndx_df, vix_df):
    """计算信号 - 使用 numpy 避免 pandas 多列问题"""
    print("计算指标...")
    
    # 合并
    merged = pd.merge(ndx_df, vix_df.rename(columns={'Close': 'VIX'}), on='Date', how='left')
    merged['VIX'] = merged['VIX'].ffill().fillna(20)
    
    # 转为 numpy 数组处理（彻底解决 DataFrame 多列问题）
    prices = merged['Close'].values.astype(float)
    n = len(prices)
    
    # 计算 MA200 和 MA50
    ma200 = np.array([np.mean(prices[max(0, i-199):i+1]) for i in range(n)])
    ma50 = np.array([np.mean(prices[max(0, i-49):i+1]) for i in range(n)])
    
    # 计算距离200日均线的百分比
    ma200_dist = (prices - ma200) / ma200 * 100
    
    # 计算估值百分位（252日滚动）
    pe_pct = np.zeros(n)
    for i in range(n):
        start = max(0, i - 251)
        if i - start >= 50:
            window = prices[start:i+1] / ma200[start:i+1]
            pe_pct[i] = np.mean(window <= prices[i]/ma200[i])
        else:
            pe_pct[i] = 0.5
    
    # 计算涨跌幅
    changes = np.diff(prices, prepend=prices[0])
    changes_pct = changes / np.where(prices != 0, prices, 1) * 100
    
    # 评分计算
    scores = np.zeros(n, dtype=int)
    vix_values = merged['VIX'].values
    
    for i in range(n):
        # 估值分 (40)
        val_score = (1 - pe_pct[i]) * 40
        
        # 趋势分 (30)
        dist = ma200_dist[i]
        if dist < -20:
            trend_score = 30
        elif dist < -10:
            trend_score = 20 + (dist + 20)
        elif dist < 0:
            trend_score = 10 + (dist + 10)
        else:
            trend_score = max(0, 10 - dist)
        
        # VIX分 (30)
        vix = vix_values[i]
        if vix > 30:
            vix_score = 30
        elif vix > 20:
            vix_score = 15 + (vix - 20) * 1.5
        else:
            vix_score = vix / 20 * 15
        
        scores[i] = int(max(0, min(100, round(val_score + trend_score + vix_score))))
    
    # 生成信号
    signals = []
    for i in range(n):
        score = scores[i]
        vix = vix_values[i]
        dist = ma200_dist[i]
        
        if score >= 75 and vix > 20:
            signals.append(('买入', '强烈建议买入（高恐慌+低估值）'))
        elif score >= 65:
            signals.append(('买入', '建议买入（估值合理或超跌）'))
        elif score <= 25 and dist > 15:
            signals.append(('卖出', '建议卖出（高估+超买）'))
        elif score <= 35 and dist > 10:
            signals.append(('卖出', '考虑减仓（相对高估）'))
        else:
            signals.append(('持有', '继续持有观望'))
    
    # 组装结果
    result = pd.DataFrame({
        'Date': merged['Date'],
        'Price': prices,
        'Change': changes,
        'Change_Percent': changes_pct,
        'VIX': vix_values,
        'PE_Percentile': pe_pct,
        'MA200_Distance': ma200_dist,
        'Score': scores,
        'Signal': [s[0] for s in signals],
        'Signal_Desc': [s[1] for s in signals]
    })
    
    return result

def main():
    print(f"=== 开始: {datetime.now()} ===")
    
    try:
        # 获取数据
        ndx = fetch_data("^IXIC")
        vix = fetch_data("^VIX")
        
        # 计算
        result = calculate_signals(ndx, vix)
        
        # 加载旧数据
        old_data = {}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE) as f:
                old_data = json.load(f).get('daily_data', {})
        
        # 更新
        for _, row in result.iterrows():
            date = pd.Timestamp(row['Date']).strftime('%Y-%m-%d')
            old_data[date] = {
                'price': float(row['Price']),
                'change': float(row['Change']),
                'change_percent': float(row['Change_Percent']),
                'vix': float(row['VIX']),
                'pe_percentile': float(row['PE_Percentile']),
                'ma200_distance': float(row['MA200_Distance']),
                'score': int(row['Score']),
                'signal': str(row['Signal']),
                'signal_desc': str(row['Signal_Desc'])
            }
        
        # 保存
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'last_update': datetime.now().isoformat(),
                'daily_data': old_data
            }, f, ensure_ascii=False, indent=2)
        
        print(f"完成! 共 {len(old_data)} 天")
        
        # 显示最近3天
        for date in sorted(old_data.keys())[-3:]:
            d = old_data[date]
            print(f"  {date}: {d['price']:.0f}分 {d['signal']}")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
