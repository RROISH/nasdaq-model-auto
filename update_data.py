#!/usr/bin/env python3
"""
纳指买卖模型数据更新脚本 - 修复版
修复 VIX 数据获取问题
"""

import json
import os
import sys
from datetime import datetime
import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

DATA_FILE = "data/nasdaq_data.json"

def fetch_data(ticker, period="10y"):
    """获取股票数据并处理多索引列问题"""
    print(f"正在获取 {ticker} 数据...")
    
    df = yf.download(ticker, period=period, progress=False, auto_adjust=False)
    
    # 处理多级列名问题（yfinance新版返回MultiIndex）
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 统一列名
    if 'Adj Close' in df.columns:
        df.rename(columns={'Adj Close': 'Close'}, inplace=True)
    
    return df[['Date', 'Close']].copy()

def calculate_signals(ndx_df, vix_df):
    """计算交易信号"""
    print("计算交易信号...")
    
    ndx_df = ndx_df.rename(columns={'Close': 'NDX_Close'})
    vix_df = vix_df.rename(columns={'Close': 'VIX'})
    
    merged = pd.merge(ndx_df, vix_df[['Date', 'VIX']], on='Date', how='left')
    merged['VIX'] = merged['VIX'].ffill().fillna(20)
    
    # 技术指标
    merged['MA200'] = merged['NDX_Close'].rolling(window=200, min_periods=1).mean()
    merged['MA200_Distance'] = (merged['NDX_Close'] - merged['MA200']) / merged['MA200'] * 100
    
    # 估值百分位
    merged['Price_Ratio'] = merged['NDX_Close'] / merged['MA200']
    merged['PE_Percentile'] = merged['Price_Ratio'].rolling(window=252, min_periods=50).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1] if len(x) > 0 else 0.5
    )
    merged['PE_Percentile'] = merged['PE_Percentile'].fillna(0.5)
    
    # 涨跌幅
    merged['Change'] = merged['NDX_Close'].diff()
    merged['Change_Percent'] = merged['NDX_Close'].pct_change() * 100
    
    # 评分系统
    def calculate_score(row):
        try:
            pe_pct = float(row['PE_Percentile']) if pd.notna(row['PE_Percentile']) else 0.5
            ma_dist = float(row['MA200_Distance']) if pd.notna(row['MA200_Distance']) else 0
            vix = float(row['VIX']) if pd.notna(row['VIX']) else 20
            
            pe_score = (1 - pe_pct) * 40
            
            if ma_dist < -20:
                trend_score = 30
            elif ma_dist < -10:
                trend_score = 20 + (ma_dist + 20) / 10 * 10
            elif ma_dist < 0:
                trend_score = 10 + (ma_dist + 10) / 10 * 10
            else:
                trend_score = max(0, 10 - ma_dist)
            
            if vix > 30:
                vix_score = 30
            elif vix > 20:
                vix_score = 15 + (vix - 20) / 10 * 15
            else:
                vix_score = vix / 20 * 15
            
            return int(round(pe_score + trend_score + vix_score))
        except:
            return 50
    
    merged['Score'] = merged.apply(calculate_score, axis=1)
    
    # 交易信号
    def get_signal(row):
        score = row['Score']
        vix = row['VIX'] if pd.notna(row['VIX']) else 20
        ma_dist = row['MA200_Distance'] if pd.notna(row['MA200_Distance']) else 0
        
        if score >= 75 and vix > 20:
            return ('买入', '强烈建议买入（高恐慌+低估值）')
        elif score >= 65:
            return ('买入', '建议买入（估值合理或超跌）')
        elif score <= 25 and ma_dist > 15:
            return ('卖出', '建议卖出（高估+超买）')
        elif score <= 35 and ma_dist > 10:
            return ('卖出', '考虑减仓（相对高估）')
        else:
            return ('持有', '继续持有观望')
    
    signals = merged.apply(get_signal, axis=1, result_type='expand')
    merged['Signal'] = signals[0]
    merged['Signal_Desc'] = signals[1]
    
    return merged

def load_existing_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"last_update": "", "daily_data": {}}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def update_data():
    print(f"=== 开始更新数据: {datetime.now()} ===")
    
    try:
        ndx_df = fetch_data("^IXIC")
        vix_df = fetch_data("^VIX")
        
        print(f"纳指数据: {len(ndx_df)} 条")
        print(f"VIX数据: {len(vix_df)} 条")
        
        result_df = calculate_signals(ndx_df, vix_df)
        
        existing = load_existing_data()
        daily_data = existing.get('daily_data', {})
        
        for _, row in result_df.iterrows():
            if pd.isna(row['NDX_Close']):
                continue
            
            date_str = row['Date'].strftime('%Y-%m-%d')
            
            daily_data[date_str] = {
                'price': float(row['NDX_Close']),
                'change': float(row['Change']) if pd.notna(row['Change']) else 0,
                'change_percent': float(row['Change_Percent']) if pd.notna(row['Change_Percent']) else 0,
                'vix': float(row['VIX']) if pd.notna(row['VIX']) else 20,
                'pe_percentile': float(row['PE_Percentile']) if pd.notna(row['PE_Percentile']) else 0.5,
                'ma200_distance': float(row['MA200_Distance']) if pd.notna(row['MA200_Distance']) else 0,
                'score': int(row['Score']) if pd.notna(row['Score']) else 50,
                'signal': str(row['Signal']),
                'signal_desc': str(row['Signal_Desc'])
            }
        
        output = {
            'last_update': datetime.now().isoformat(),
            'daily_data': daily_data
        }
        save_data(output)
        
        print(f"更新完成，共 {len(daily_data)} 个交易日")
        
        recent_dates = sorted(daily_data.keys())[-5:]
        print("最近5天:")
        for date in recent_dates:
            d = daily_data[date]
            print(f"  {date}: 价格={d['price']:.2f}, 信号={d['signal']}, 评分={d['score']}")
        
        return True
        
    except Exception as e:
        print(f"更新失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_data()
    sys.exit(0 if success else 1)
