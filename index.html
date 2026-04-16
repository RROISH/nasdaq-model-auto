<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>纳指模型 - 今日信号</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 15px;
        }
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .date {
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }
        .live {
            display: inline-block;
            background: #00d084;
            color: #fff;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            margin-left: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        
        .signal-box {
            background: rgba(0,0,0,0.25);
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
        }
        .signal-label { font-size: 13px; opacity: 0.8; margin-bottom: 8px; }
        .signal-value {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .signal-value.strong-buy { color: #00ff88; }
        .signal-value.buy { color: #26de81; }
        .signal-value.hold { color: #fed330; }
        .signal-value.sell { color: #ff6b6b; }
        .signal-value.strong-sell { color: #ff4757; }
        
        .score-bar {
            background: rgba(255,255,255,0.1);
            height: 6px;
            border-radius: 3px;
            margin: 15px 0;
            position: relative;
        }
        .score-fill {
            height: 100%;
            border-radius: 3px;
            background: linear-gradient(90deg, #ff4757 0%, #fed330 50%, #00ff88 100%);
            transition: width 0.5s ease;
        }
        .score-num {
            font-size: 20px;
            font-weight: bold;
            margin-top: 5px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin: 15px 0;
        }
        .card {
            background: rgba(255,255,255,0.08);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        .card-label { font-size: 12px; opacity: 0.7; margin-bottom: 6px; }
        .card-value { font-size: 22px; font-weight: bold; }
        .card-sub { font-size: 11px; margin-top: 4px; opacity: 0.8; }
        .up { color: #26de81; }
        .down { color: #ff6b6b; }
        
        .details {
            background: rgba(0,0,0,0.15);
            border-radius: 12px;
            padding: 15px;
            margin: 15px 0;
        }
        .detail-title { font-size: 14px; margin-bottom: 12px; font-weight: 600; }
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            font-size: 13px;
        }
        .detail-row:last-child { border-bottom: none; }
        .detail-score { font-weight: bold; min-width: 30px; text-align: right; }
        .detail-score.pos { color: #26de81; }
        .detail-score.neg { color: #ff6b6b; }
        .detail-score.zero { color: #74b9ff; }
        
        .suggest {
            background: rgba(255,215,0,0.15);
            border-left: 3px solid #ffd700;
            padding: 15px;
            border-radius: 0 12px 12px 0;
            margin-top: 15px;
        }
        .suggest-title { color: #ffd700; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
        .suggest-text { font-size: 14px; line-height: 1.6; opacity: 0.95; }
        .position { margin-top: 10px; font-size: 13px; opacity: 0.9; }
        
        .footer {
            text-align: center;
            font-size: 11px;
            opacity: 0.5;
            padding: 20px 0;
        }
        
        .loading {
            text-align: center;
            padding: 60px 20px;
        }
        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .error {
            background: rgba(255,71,87,0.2);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            font-size: 14px;
        }
        .refresh {
            background: rgba(255,255,255,0.2);
            border: none;
            color: #fff;
            padding: 10px 20px;
            border-radius: 20px;
            margin-top: 15px;
            cursor: pointer;
            font-size: 13px;
        }
        
        @media (max-width: 480px) {
            .grid { grid-template-columns: 1fr; gap: 10px; }
            .signal-value { font-size: 36px; }
            .container { padding: 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📈 纳指交易模型</h2>
            <div class="date" id="todayDate">--<span class="live">LIVE</span></div>
        </div>
        
        <div id="mainContent">
            <div class="loading">
                <div class="spinner"></div>
                <p style="margin-top:15px; opacity:0.8">加载今日数据中...</p>
            </div>
        </div>
        
        <div class="footer">
            <p>数据每日自动更新 | 仅供参考不构成投资建议</p>
            <p id="updateTime">最后更新: --</p>
        </div>
    </div>

    <script>
        const DATA_FILE = './latest.json';
        
        async function init() {
            const now = new Date();
            document.getElementById('todayDate').innerHTML = 
                `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日 ` +
                `<span class="live">LIVE</span>`;
            
            try {
                const data = await fetch(DATA_FILE + '?_=' + Date.now()).then(r => r.json());
                render(data);
            } catch(e) {
                document.getElementById('mainContent').innerHTML = `
                    <div class="error">
                        <p>⚠️ 数据加载失败</p>
                        <p style="font-size:12px; margin-top:5px; opacity:0.7">
                            等待每日22:30自动更新，或检查网络连接
                        </p>
                        <button class="refresh" onclick="init()">重新加载</button>
                    </div>
                `;
            }
        }
        
        function calculateScore(d) {
            let score = 0;
            const details = [];
            
            let vixScore = 0;
            if (d.vix > 30) vixScore = 2;
            else if (d.vix > 25) vixScore = 1;
            else if (d.vix < 15) vixScore = -1;
            score += vixScore;
            details.push({ name: 'VIX恐慌指数', val: d.vix.toFixed(2), score: vixScore });
            
            let posScore = 0;
            if (d.position_52w > 95) posScore = -2;
            else if (d.position_52w > 85) posScore = -1;
            else if (d.position_52w < 20) posScore = 2;
            else if (d.position_52w < 30) posScore = 1;
            score += posScore;
            details.push({ name: '52周位置', val: d.position_52w.toFixed(1)+'%', score: posScore });
            
            let maScore = 0;
            const dev = d.ma50_deviation || 0;
            if (dev > 20) maScore = -2;
            else if (dev > 15) maScore = -1;
            else if (dev < -20) maScore = 2;
            else if (dev < -15) maScore = 1;
            score += maScore;
            details.push({ name: '50日均线偏离', val: dev.toFixed(2)+'%', score: maScore });
            
            let momScore = 0;
            const mom5 = d.change_5d || 0;
            if (mom5 > 10) momScore = -1;
            else if (mom5 < -10) momScore = 1;
            score += momScore;
            details.push({ name: '5日涨跌幅', val: mom5.toFixed(2)+'%', score: momScore });
            
            score = Math.max(-5, Math.min(5, score));
            return { score, details, raw: d };
        }
        
        function render(data) {
            const calc = calculateScore(data);
            const s = calc.score;
            
            let signalClass, signalText, action, position;
            if (s >= 3) {
                signalClass = 'strong-buy'; signalText = '强烈买入';
                action = '市场极度恐慌或超跌，是难得的抄底机会';
                position = '建议仓位：80-100%';
            } else if (s >= 1) {
                signalClass = 'buy'; signalText = '买入';
                action = '市场出现买入信号，建议分批建仓';
                position = '建议仓位：60-80%';
            } else if (s > -1) {
                signalClass = 'hold'; signalText = '持有';
                action = '市场震荡，维持现有仓位，等待明确信号';
                position = '建议仓位：维持现状';
            } else if (s > -3) {
                signalClass = 'sell'; signalText = '减仓';
                action = '市场偏高或过热，建议分批减仓锁定利润';
                position = '建议仓位：40-60%';
            } else {
                signalClass = 'strong-sell'; signalText = '强烈卖出';
                action = '市场极度贪婪或泡沫严重，建议大幅减仓或清仓';
                position = '建议仓位：0-20%';
            }
            
            const pct = ((s + 5) / 10) * 100;
            
            document.getElementById('mainContent').innerHTML = `
                <div class="signal-box">
                    <div class="signal-label">今日信号 (${s}/±5)</div>
                    <div class="signal-value ${signalClass}">${signalText}</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width:${pct}%"></div>
                    </div>
                    <div class="score-num" style="${s>0?'color:#26de81':s<0?'color:#ff6b6b':'color:#fed330'}">
                        ${s>0?'+':''}${s}
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <div class="card-label">纳指收盘</div>
                        <div class="card-value">${Math.round(data.close).toLocaleString()}</div>
                        <div class="card-sub ${data.change_1d>=0?'up':'down'}">
                            ${data.change_1d>=0?'+':''}${data.change_1d.toFixed(2)}%
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-label">VIX指数</div>
                        <div class="card-value">${data.vix.toFixed(2)}</div>
                        <div class="card-sub">${data.vix>25?'恐慌':data.vix<15?'贪婪':'正常'}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">52周位置</div>
                        <div class="card-value">${data.position_52w.toFixed(1)}%</div>
                        <div class="card-sub">${data.position_52w>95?'高位':data.position_52w<20?'低位':'中位'}</div>
                    </div>
                    <div class="card">
                        <div class="card-label">50日均线偏离</div>
                        <div class="card-value ${(data.ma50_deviation||0)>=0?'up':'down'}">
                            ${(data.ma50_deviation||0)>=0?'+':''}${(data.ma50_deviation||0).toFixed(1)}%
                        </div>
                        <div class="card-sub">${Math.abs(data.ma50_deviation||0)>15?'极端':'正常'}</div>
                    </div>
                </div>
                
                <div class="details">
                    <div class="detail-title">📋 评分明细</div>
                    ${calc.details.map(item => `
                        <div class="detail-row">
                            <span>${item.name} <span style="opacity:0.7;font-size:11px">(${item.val})</span></span>
                            <span class="detail-score ${item.score>0?'pos':item.score<0?'neg':'zero'}">
                                ${item.score>0?'+':''}${item.score}
                            </span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="suggest">
                    <div class="suggest-title">💡 操作建议</div>
                    <div class="suggest-text">${action}</div>
                    <div class="position">📍 ${position}</div>
                </div>
            `;
            
            document.getElementById('updateTime').textContent = `数据日期: ${data.date || '未知'}`;
        }
        
        init();
        setInterval(init, 60000);
    </script>
</body>
</html>
