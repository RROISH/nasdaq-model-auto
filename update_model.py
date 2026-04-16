<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#f44336">
    <title>纳指模型 - 抄底信号</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            color: #333;
            padding-bottom: 30px;
        }
        .container { max-width: 420px; margin: 0 auto; padding: 15px; }
        .header { text-align: center; padding: 20px 0; }
        .header h1 { font-size: 1.5em; color: #333; margin-bottom: 5px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .header .update-time { font-size: 0.85em; color: #888; }
        .card { 
            background: white; 
            border-radius: 16px; 
            padding: 20px; 
            margin-bottom: 15px; 
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        .date-nav { 
            display: flex; 
            align-items: center; 
            justify-content: center;
            gap: 15px;
            margin-bottom: 5px;
        }
        .nav-btn { 
            width: 44px; 
            height: 44px; 
            border: none; 
            background: #f0f0f0; 
            color: #666; 
            border-radius: 50%; 
            font-size: 1.1em; 
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        .nav-btn:active { background: #e0e0e0; transform: scale(0.95); }
        .nav-btn:disabled { opacity: 0.3; cursor: not-allowed; }
        .date-display { 
            flex: 1; 
            max-width: 160px;
            text-align: center; 
            font-size: 1.1em; 
            font-weight: 600;
            color: #333;
            padding: 12px;
            background: #f8f8f8;
            border-radius: 12px;
            cursor: pointer;
        }
        .date-input-hidden { position: absolute; opacity: 0; width: 0; height: 0; }
        .signal-box { 
            padding: 25px; 
            border-radius: 16px; 
            text-align: center; 
            font-weight: 700; 
            margin: 15px 0;
            font-size: 1.8em;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .signal-buy { background: linear-gradient(135deg, #4CAF50, #45a049); }
        .signal-sell { background: linear-gradient(135deg, #f44336, #d32f2f); }
        .signal-neutral { background: linear-gradient(135deg, #FF9800, #f57c00); }
        .score-text { 
            text-align: center; 
            font-size: 0.9em; 
            color: #666; 
            margin-top: -10px;
            margin-bottom: 15px;
        }
        .data-list { margin-top: 10px; }
        .data-item { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            padding: 14px 0; 
            border-bottom: 1px solid #f0f0f0;
        }
        .data-item:last-child { border-bottom: none; }
        .data-label { font-size: 0.95em; color: #666; }
        .data-value { font-size: 1.1em; font-weight: 600; color: #333; }
        .data-value.up { color: #4CAF50; }
        .data-value.down { color: #f44336; }
        .score-section { margin: 15px 0; }
        .score-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.85em; color: #666; }
        .score-bar { height: 8px; background: #e8e8e8; border-radius: 4px; overflow: hidden; }
        .score-fill { height: 100%; border-radius: 4px; transition: width 0.3s ease; }
        .score-fill.buy { background: linear-gradient(90deg, #4CAF50, #66BB6A); }
        .score-fill.sell { background: linear-gradient(90deg, #f44336, #ef5350); }
        .signal-list { max-height: 320px; overflow-y: auto; margin-top: 10px; }
        .signal-item { 
            display: flex; 
            justify-content: space-between;
            align-items: center;
            padding: 12px; 
            margin: 8px 0; 
            background: #f8f9fa; 
            border-radius: 10px; 
            border-left: 4px solid #4CAF50;
            cursor: pointer;
            transition: background 0.2s;
        }
        .signal-item:active { background: #e8e8e8; }
        .signal-item.sell { border-left-color: #f44336; }
        .signal-item .left { text-align: left; }
        .signal-item .date { font-weight: 600; font-size: 0.95em; color: #333; }
        .signal-item .detail { font-size: 0.8em; color: #888; margin-top: 3px; }
        .signal-item .score { font-weight: 700; font-size: 1em; }
        .signal-item .score.buy { color: #4CAF50; }
        .signal-item .score.sell { color: #f44336; }
        .advice-box { 
            background: #FFF8E1; 
            border-radius: 12px; 
            padding: 15px; 
            margin-top: 15px;
        }
        .advice-title { font-weight: 600; color: #F57C00; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
        .advice-text { color: #666; font-size: 0.95em; line-height: 1.5; }
        footer { text-align: center; padding: 20px; color: #999; font-size: 0.75em; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #ccc; border-radius: 2px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 纳指抄底模型</h1>
            <div class="update-time">2026-04-16 更新</div>
        </div>

        <div class="card">
            <div class="date-nav">
                <button class="nav-btn" id="prevBtn" onclick="prevDay()">◀</button>
                <div class="date-display" id="dateDisplay" onclick="openDatePicker()">--</div>
                <input type="date" id="dateInput" class="date-input-hidden" onchange="onDateChange()">
                <button class="nav-btn" id="nextBtn" onclick="nextDay()">▶</button>
            </div>
        </div>

        <div class="card">
            <div id="signalBox"></div>
            <div class="score-text" id="scoreText"></div>
            <div class="score-section">
                <div class="score-header">
                    <span>买入评分 (≥60触发)</span>
                    <span id="buyScoreVal">0/100</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill buy" id="buyScoreBar" style="width: 0%"></div>
                </div>
            </div>
            <div class="score-section">
                <div class="score-header">
                    <span>卖出评分 (≥50触发)</span>
                    <span id="sellScoreVal">0/100</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill sell" id="sellScoreBar" style="width: 0%"></div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="data-list" id="dataList"></div>
            <div class="advice-box" id="adviceBox">
                <div class="advice-title">💡 操作建议</div>
                <div class="advice-text" id="adviceText">加载中...</div>
            </div>
        </div>

        <div class="card">
            <div style="font-weight: 600; color: #333; margin-bottom: 10px;">📜 历史买卖信号 (点击查询)</div>
            <div class="signal-list" id="signalList"></div>
        </div>

        <footer>
            <p>数据来自 Yahoo Finance | 延迟15分钟 | 仅供参考</p>
        </footer>
    </div>

    <script>
        // 历史数据（这里需要嵌入完整的数据）
        const historyData = [/* 数据将在这里 */];
        let currentIndex = historyData.length - 1;
        
        function init() {
            const dateInput = document.getElementById('dateInput');
            dateInput.min = historyData[0].date;
            dateInput.max = historyData[historyData.length - 1].date;
            updateDisplay();
            showSignals();
        }
        
        function updateDisplay() {
            const data = historyData[currentIndex];
            document.getElementById('dateDisplay').textContent = data.date;
            document.getElementById('dateInput').value = data.date;
            document.getElementById('prevBtn').disabled = (currentIndex <= 0);
            document.getElementById('nextBtn').disabled = (currentIndex >= historyData.length - 1);
            updateSignal(data);
            updateDataList(data);
            updateScoreBars(data);
            updateAdvice(data);
        }
        
        function updateSignal(data) {
            const box = document.getElementById('signalBox');
            const text = document.getElementById('scoreText');
            if (data.buy_signal) {
                box.className = 'signal-box signal-buy';
                box.textContent = '买入';
                text.textContent = `买入评分: ${data.buy_score} / 触发线: 60`;
            } else if (data.sell_signal) {
                box.className = 'signal-box signal-sell';
                box.textContent = '卖出';
                text.textContent = `卖出评分: ${data.sell_score} / 触发线: 50`;
            } else {
                box.className = 'signal-box signal-neutral';
                box.textContent = '观望';
                text.textContent = `买${data.buy_score} / 卖${data.sell_score}`;
            }
        }
        
        function updateDataList(data) {
            const change = data.daily_return || 0;
            const changeClass = change >= 0 ? 'up' : 'down';
            const changeSign = change >= 0 ? '+' : '';
            const html = `
                <div class="data-item">
                    <span class="data-label">纳指收盘</span>
                    <span class="data-value">${data.close ? data.close.toFixed(2) : '--'}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">涨跌幅</span>
                    <span class="data-value ${changeClass}">${changeSign}${change.toFixed(2)}%</span>
                </div>
                <div class="data-item">
                    <span class="data-label">VIX恐慌指数</span>
                    <span class="data-value">${data.vix ? data.vix.toFixed(2) : '--'}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">vs 50日均线</span>
                    <span class="data-value ${data.price_deviation >= 0 ? 'up' : 'down'}">${(data.price_deviation * 100).toFixed(2)}%</span>
                </div>
                <div class="data-item">
                    <span class="data-label">RSI指标</span>
                    <span class="data-value">${data.rsi ? data.rsi.toFixed(0) : '--'} ${getRsiStatus(data.rsi)}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">估值分位</span>
                    <span class="data-value">${data.valuation ? data.valuation.toFixed(2) : '--'} ${getValStatus(data.valuation)}</span>
                </div>
            `;
            document.getElementById('dataList').innerHTML = html;
        }
        
        function updateScoreBars(data) {
            document.getElementById('buyScoreVal').textContent = `${data.buy_score}/100`;
            document.getElementById('buyScoreBar').style.width = `${Math.min(data.buy_score, 100)}%`;
            document.getElementById('sellScoreVal').textContent = `${data.sell_score}/100`;
            document.getElementById('sellScoreBar').style.width = `${Math.min(data.sell_score, 100)}%`;
        }
        
        function updateAdvice(data) {
            const text = document.getElementById('adviceText');
            if (data.buy_signal) {
                text.textContent = data.buy_score >= 75 ? '强烈买入信号！市场恐慌情绪严重，建议积极建仓。' : '中等买入信号，可关注建仓机会。';
            } else if (data.sell_signal) {
                text.textContent = data.sell_score >= 65 ? '强烈卖出信号！市场高位，建议分批减仓。' : '市场处于相对高位，可考虑适当减仓。';
            } else {
                text.textContent = data.buy_score >= 45 ? '接近买入区域，可密切关注。' : data.sell_score >= 35 ? '接近卖出区域，注意风险。' : '市场处于中性区间，建议观望。';
            }
        }
        
        function getRsiStatus(rsi) {
            if (!rsi) return '';
            if (rsi > 70) return '(超买)';
            if (rsi < 30) return '(超卖)';
            return '';
        }
        
        function getValStatus(val) {
            if (!val) return '';
            if (val > 1.15) return '(高估)';
            if (val < 0.93) return '(低估)';
            return '';
        }
        
        function prevDay() {
            if (currentIndex > 0) {
                currentIndex--;
                updateDisplay();
            }
        }
        
        function nextDay() {
            if (currentIndex < historyData.length - 1) {
                currentIndex++;
                updateDisplay();
            }
        }
        
        function openDatePicker() {
            const input = document.getElementById('dateInput');
            if (input.showPicker) input.showPicker();
            else input.click();
        }
        
        function onDateChange() {
            const date = document.getElementById('dateInput').value;
            const index = historyData.findIndex(d => d.date === date);
            if (index !== -1) {
                currentIndex = index;
                updateDisplay();
            }
        }
        
        function showSignals() {
            const buySignals = historyData.filter(d => d.buy_signal).reverse().slice(0, 8);
            const sellSignals = historyData.filter(d => d.sell_signal).reverse().slice(0, 4);
            const allSignals = [...buySignals, ...sellSignals].sort((a, b) => 
                new Date(b.date) - new Date(a.date)
            ).slice(0, 10);
            
            let html = '';
            allSignals.forEach(s => {
                const isBuy = s.buy_signal;
                const score = isBuy ? s.buy_score : s.sell_score;
                html += `
                    <div class="signal-item ${isBuy ? '' : 'sell'}" onclick="goToDate('${s.date}')">
                        <div class="left">
                            <div class="date">${isBuy ? '📥' : '📤'} ${s.date}</div>
                            <div class="detail">纳指${s.close.toFixed(0)} | VIX ${s.vix.toFixed(1)}</div>
                        </div>
                        <div class="score ${isBuy ? 'buy' : 'sell'}">${score}分</div>
                    </div>
                `;
            });
            document.getElementById('signalList').innerHTML = html || '<div style="color:#999;padding:10px;text-align:center;">暂无信号</div>';
        }
        
        function goToDate(date) {
            const index = historyData.findIndex(d => d.date === date);
            if (index !== -1) {
                currentIndex = index;
                updateDisplay();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
        
        init();
    </script>
</body>
</html>
