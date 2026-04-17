#!/usr/bin/env python3
"""
纳指买卖模型 - V8终极版 (大周期跟随策略)
基于200日均线基础仓位 + 趋势/恐慌/估值微调
"""

import json
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 尝试导入akshare
try:
    import akshare as ak
    print(f"✅ AKShare版本: {ak.__version__}")
except ImportError:
    os.system("pip install akshare --quiet")
    import akshare as ak
    print(f"✅ AKShare已安装，版本: {ak.__version__}")

DATA_FILE = "data/nasdaq_data.json"

def fetch_data():
    """获取纳斯达克和VIX数据"""
    print("\n=== 获取数据 ===")
    
    # 获取纳指数据 (^IXIC)
    try:
        df = ak.index_us_stock_sina(symbol=".IXIC")
        df = df.tail(252 * 10).copy()  # 近10年
        df = df.rename(columns={'date': 'Date', 'close': 'Close'})
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        print(f"✅ 纳指数据: {len(df)} 条，最新 {df['Date'].max().strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"❌ 获取纳指数据失败: {e}")
        raise
    
    # 获取VIX数据
    try:
        vix_df = ak.index_us_stock_sina(symbol=".VIX")
        vix_df = vix_df.tail(252 * 10).copy()
        vix_df = vix_df.rename(columns={'date': 'Date', 'close': 'VIX'})
        vix_df['Date'] = pd.to_datetime(vix_df['Date']).dt.tz_localize(None)
        print(f"✅ VIX数据: {len(vix_df)} 条")
    except Exception as e:
        print(f"⚠️ VIX获取失败: {e}，使用默认值")
        vix_df = pd.DataFrame(columns=['Date', 'VIX'])
    
    # 合并数据
    data = pd.merge(df[['Date', 'Close']], vix_df[['Date', 'VIX']], on='Date', how='left')
    data = data.sort_values('Date').reset_index(drop=True)
    data['VIX'] = data['VIX'].fillna(20)
    
    return data

def calculate_v8_signals(data):
    """V8终极版信号计算"""
    print("\n=== V8模型计算 ===")
    
    prices = data['Close'].values
    vix_values = data['VIX'].values
    n = len(prices)
    
    # 计算技术指标
    data['MA20'] = data['Close'].rolling(20).mean()
    data['MA50'] = data['Close'].rolling(50).mean()
    data['MA200'] = data['Close'].rolling(200).mean()
    data['MA200_Dist'] = (data['Close'] - data['MA200']) / data['MA200'] * 100
    
    # 52周高低点
    data['High_52w'] = data['Close'].rolling(252).max()
    data['Low_52w'] = data['Close'].rolling(252).min()
    data['Position_52w'] = (data['Close'] - data['Low_52w']) / (data['High_52w'] - data['Low_52w'])
    
    # VIX变化率
    data['VIX_Change_5d'] = (data['VIX'] - data['VIX'].shift(5)) / data['VIX'].shift(5) * 100
    
    results = []
    
    for i in range(n):
        if i < 200 or pd.isna(data.loc[i, 'MA200']):
            results.append({
                'score': 50, 'signal': '持有', 'target_pos': 0.5,
                'components': {}, 'details': {}
            })
            continue
        
        row = data.loc[i]
        price = row['Close']
        vix = row['VIX']
        pos = row['Position_52w']
        ma_dist = row['MA200_Dist']
        ma20 = row['MA20']
        ma50 = row['MA50']
        ma200 = row['MA200']
        
        # ========== Step 1: 大周期基础仓位 ==========
        if ma_dist > 10:
            base_pos = 0.90
        elif ma_dist > 0:
            base_pos = 0.80
        elif ma_dist > -10:
            base_pos = 0.60
        elif ma_dist > -20:
            base_pos = 0.40
        else:
            base_pos = 0.20
        
        # ========== Step 2: 中周期调整 ==========
        if ma50 > ma200:  # 金叉
            trend_adj = 0.10 if price > ma50 else 0.0
        else:  # 死叉
            trend_adj = -0.15
        
        # ========== Step 3: 恐慌极端触发 ==========
        vix_change = row['VIX_Change_5d'] if not pd.isna(row['VIX_Change_5d']) else 0
        
        if vix > 45:
            panic_adj = 0.20
        elif vix > 35:
            panic_adj = 0.10
        elif vix < 12 and pos > 0.90:
            panic_adj = -0.15
        elif vix < 15 and pos > 0.85:
            panic_adj = -0.10
        else:
            panic_adj = 0.0
        
        # ========== Step 4: 估值微调 ==========
        if pos > 0.95 and vix < 18:
            val_adj = -0.10
        elif pos < 0.15 and vix > 25:
            val_adj = 0.10
        else:
            val_adj = 0.0
        
        # 计算最终仓位
        target_pos = base_pos + trend_adj + panic_adj + val_adj
        target_pos = max(0.0, min(0.95, target_pos))
        
        # 映射到评分（用于展示）
        if target_pos >= 0.90: score = 90
        elif target_pos >= 0.75: score = 80
        elif target_pos >= 0.60: score = 65
        elif target_pos >= 0.45: score = 50
        elif target_pos >= 0.30: score = 35
        elif target_pos >= 0.15: score = 20
        else: score = 10
        
        # 信号标签
        if score >= 85: signal = '强烈买入'
        elif score >= 70: signal = '买入'
        elif score >= 55: signal = '定投'
        elif score >= 40: signal = '持有'
        elif score >= 25: signal = '减仓'
        elif score >= 10: signal = '卖出'
        else: signal = '强烈卖出'
        
        results.append({
            'score': score,
            'signal': signal,
            'target_pos': round(target_pos, 2),
            'components': {
                'base': base_pos,
                'trend': trend_adj,
                'panic': panic_adj,
                'value': val_adj
            },
            'details': {
                'valuation_level': round((1 - pos) * 40, 1),
                'fear_level': min(35, vix) if vix > 15 else vix / 15 * 20,
                'trend_level': max(0, 25 - max(0, ma_dist)) if ma_dist > 0 else 25 + min(0, ma_dist),
                'position_52w': round(pos * 100, 1)
            }
        })
    
    return results

def main():
    print(f"=== 纳指模型 V8终极版 ===")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 获取数据
        df = fetch_data()
        
        # 计算信号
        signals = calculate_v8_signals(df)
        
        # 加载旧数据
        old_data = {}
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    old_data = json.load(f).get('daily_data', {})
                print(f"✅ 加载现有数据: {len(old_data)} 天")
            except Exception as e:
                print(f"⚠️ 无法读取旧数据: {e}")
        
        # 合并数据
        update_count = 0
        for i, (date, signal) in enumerate(zip(df['Date'], signals)):
            if pd.isna(df.loc[i, 'Close']):
                continue
            
            date_str = date.strftime('%Y-%m-%d')
            
            old_data[date_str] = {
                'price': float(df.loc[i, 'Close']),
                'change': float(df.loc[i, 'Close'] - df.loc[i-1, 'Close']) if i > 0 else 0,
                'change_percent': float((df.loc[i, 'Close'] / df.loc[i-1, 'Close'] - 1) * 100) if i > 0 else 0,
                'vix': float(df.loc[i, 'VIX']),
                'ma200': float(df.loc[i, 'MA200']) if not pd.isna(df.loc[i, 'MA200']) else None,
                'ma200_distance': float(df.loc[i, 'MA200_Dist']) if not pd.isna(df.loc[i, 'MA200_Dist']) else None,
                'score': signal['score'],
                'signal': signal['signal'],
                'target_position': signal['target_pos'],
                'signal_desc': get_signal_desc(signal['score']),
                'details': signal['details'],
                'components': signal['components'],
                'version': '8.0'
            }
            update_count += 1
        
        # 保存
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        output = {
            'last_update': datetime.now().isoformat(),
            'model_version': '8.0',
            'model_name': 'V8终极版（大周期跟随）',
            'daily_data': old_data
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据更新成功: {update_count} 天")
        print(f"📦 总记录数: {len(old_data)} 天")
        
        # 显示最近3天
        recent_dates = sorted(old_data.keys())[-3:]
        print(f"\n📈 最近3天数据:")
        for d in recent_dates:
            data = old_data[d]
            print(f"   {d}: {data['score']}分 | {data['signal']} | 仓位:{data['target_position']:.0%} | 点位:{data['price']:.0f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_signal_desc(score):
    """获取信号描述"""
    if score >= 85: return '🔥 历史级买点，建议重仓'
    elif score >= 70: return '📈 趋势确认，积极布局'
    elif score >= 55: return '💰 可定投或适度加仓'
    elif score >= 40: return '⏸️ 持有观望，暂不操作'
    elif score >= 25: return '⚠️ 考虑减仓，锁定利润'
    elif score >= 10: return '📉 高估区域，建议减仓'
    else: return '🚨 泡沫区域，清仓避险'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
