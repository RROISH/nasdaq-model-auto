#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纳指加仓模型 - 数据更新脚本
从Yahoo Finance获取最新数据并生成model_data.json
"""

import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# 配置
CONFIG = {
    'initialDD': -10,      # 首仓回撤阈值
    'stepDD': -5,          # 每批间隔回撤
    'maxBatch': 4,         # 最大批次
    'rsiPeriod': 14,       # RSI周期
    'lookback': 252        # 回望周期（1年）
}

def fetch_data():
    """从Yahoo Finance获取纳斯达克和VIX数据"""
    print("正在获取纳斯达克数据 (^IXIC)...")
    ndx = yf.download("^IXIC", period="1y", interval="1d", progress=False)
    if ndx.empty:
        raise ValueError("无法获取纳斯达克数据")
    
    print("正在获取VIX恐慌指数 (^VIX)...")
    vix = yf.download("^VIX", period="1y", interval="1d", progress=False)
    if vix.empty:
        raise ValueError("无法获取VIX数据")
    
    print(f"纳斯达克: {len(ndx)} 条, VIX: {len(vix)} 条")
    return ndx, vix

def calculate_indicators(ndx_df, vix_df):
    """计算所有技术指标"""
    close = ndx_df['Close'].values.flatten()
    dates = ndx_df.index
    lookback = min(CONFIG['lookback'], len(close))
    
    # 1. 1年高点回撤
    high_252 = pd.Series(close).rolling(window=lookback, min_periods=1).max().values
    drawdown = (close - high_252) / high_252 * 100
    
    # 2. RSI(14)
    s = pd.Series(close)
    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(window=CONFIG['rsiPeriod']).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=CONFIG['rsiPeriod']).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # 3. 20日涨幅
    change_20d = (close / np.roll(close, 20) - 1) * 100
    change_20d[:20] = 0
    
    # 4. 估值百分位（1年价格百分位）
    percentile_list = []
    for i in range(len(close)):
        if i < 30:
            percentile_list.append(50.0)
        else:
            window_start = max(0, i - lookback + 1)
            window = close[window_start:i+1]
            p = (window <= close[i]).sum() / len(window) * 100
            percentile_list.append(round(float(p), 1))
    
    # 5. VIX恐慌指数
    vix_dict = {}
    for idx, row in vix_df.iterrows():
        date_key = idx.date() if hasattr(idx, 'date') else pd.Timestamp(idx).date()
        vix_dict[date_key] = float(row['Close'].values[0]) if hasattr(row['Close'], 'values') else float(row['Close'])
    
    vix_values = []
    for idx in ndx_df.index:
        date_key = idx.date() if hasattr(idx, 'date') else pd.Timestamp(idx).date()
        vix_values.append(vix_dict.get(date_key, np.nan))
    
    vix_series = pd.Series(vix_values)
    vix_filled = vix_series.ffill().bfill()
    # 如果还有NaN，使用默认值20
    vix_filled = vix_filled.fillna(20)
    
    return {
        'close': close,
        'dates': dates,
        'drawdown': drawdown,
        'rsi': rsi.values,
        'change_20d': change_20d,
        'percentile': percentile_list,
        'vix': vix_filled.values,
        'high_252': high_252
    }

def generate_signals(price_data):
    """生成加仓信号历史"""
    signals = []
    in_position = False
    current_signal = None
    
    for i, row in enumerate(price_data):
        dd = row['dd']
        
        if not in_position and dd <= CONFIG['initialDD']:
            # 开始新信号
            in_position = True
            current_signal = {
                'start_date': row['date'],
                'start_price': row['close'],
                'start_dd': dd,
                'batches': [{
                    'batch': 1,
                    'price': row['close'],
                    'dd': dd,
                    'date': row['date']
                }],
                'next_threshold': CONFIG['initialDD'] + CONFIG['stepDD'],
                'lowest_dd': dd
            }
        elif in_position:
            if dd < current_signal['lowest_dd']:
                current_signal['lowest_dd'] = dd
            
            batch_count = len(current_signal['batches'])
            if batch_count < CONFIG['maxBatch'] and dd <= current_signal['next_threshold']:
                current_signal['batches'].append({
                    'batch': batch_count + 1,
                    'price': row['close'],
                    'dd': dd,
                    'date': row['date']
                })
                current_signal['next_threshold'] += CONFIG['stepDD']
            
            # 结束条件：回撤回到-3%以内且持续30天以上
            if dd > -3:
                days_held = (datetime.strptime(row['date'], '%Y-%m-%d') - 
                           datetime.strptime(current_signal['start_date'], '%Y-%m-%d')).days
                if days_held > 30:
                    current_signal['end_date'] = row['date']
                    current_signal['end_price'] = row['close']
                    signals.append(current_signal)
                    in_position = False
                    current_signal = None
    
    # 如果还有未结束的信号
    if in_position and current_signal:
        signals.append(current_signal)
    
    return signals

def generate_model_data():
    """生成完整的模型数据"""
    # 1. 获取数据
    ndx_df, vix_df = fetch_data()
    
    # 2. 计算指标
    ind = calculate_indicators(ndx_df, vix_df)
    
    # 3. 生成价格历史
    price_data = []
    for i in range(len(ind['close'])):
        date_str = ind['dates'][i].strftime('%Y-%m-%d') if hasattr(ind['dates'][i], 'strftime') else str(ind['dates'][i])[:10]
        price_data.append({
            'date': date_str,
            'close': round(float(ind['close'][i]), 2),
            'dd': round(float(ind['drawdown'][i]), 2),
            'rsi': round(float(ind['rsi'][i]), 1) if not pd.isna(ind['rsi'][i]) else 50,
            'vix': round(float(ind['vix'][i]), 2),
            'percentile': ind['percentile'][i]
        })
    
    # 4. 当前指标
    current = {
        'date': price_data[-1]['date'],
        'price': price_data[-1]['close'],
        'prev_price': price_data[-2]['close'] if len(price_data) > 1 else price_data[-1]['close'],
        'change_1d': round((price_data[-1]['close'] / price_data[-2]['close'] - 1) * 100, 2) if len(price_data) > 1 else 0,
        'drawdown': price_data[-1]['dd'],
        'rsi': price_data[-1]['rsi'],
        'change_20d': price_data[-1]['dd'],  # 使用计算好的值
        'percentile': price_data[-1]['percentile'],
        'vix': price_data[-1]['vix'],
        'high_252': round(float(ind['high_252'][-1]), 2)
    }
    
    # 重新计算20日涨幅
    if len(price_data) >= 21:
        current['change_20d'] = round((price_data[-1]['close'] / price_data[-21]['close'] - 1) * 100, 2)
    
    # 5. 加仓信号
    signals = generate_signals(price_data)
    
    # 6. 组装数据
    model_data = {
        'current': current,
        'price_data': price_data,
        'signals': signals,
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return model_data

def main():
    """主函数"""
    try:
        print("=" * 50)
        print("纳指加仓模型 - 数据更新")
        print("=" * 50)
        
        model_data = generate_model_data()
        
        # 保存JSON
        with open('model_data.json', 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 50)
        print("✅ 数据更新成功!")
        print("=" * 50)
        print(f"📅 数据日期: {model_data['current']['date']}")
        print(f"📊 纳斯达克: {model_data['current']['price']:.2f}")
        print(f"📈 1日涨跌: {model_data['current']['change_1d']:+.2f}%")
        print(f"📉 1年回撤: {model_data['current']['drawdown']:.2f}%")
        print(f"📊 RSI(14): {model_data['current']['rsi']:.1f}")
        print(f"📊 20日涨幅: {model_data['current']['change_20d']:+.2f}%")
        print(f"📊 估值百分位: {model_data['current']['percentile']:.1f}%")
        print(f"😰 VIX恐慌指数: {model_data['current']['vix']:.2f}")
        print(f"🎯 加仓信号: {len(model_data['signals'])} 个")
        print(f"💾 数据已保存: model_data.json")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
