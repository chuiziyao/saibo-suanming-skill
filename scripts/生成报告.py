# -*- coding: utf-8 -*-
"""
赛博算命 - 完整算命脚本
为1983年1月26日早上5点左右（寅时/卯时）男性生成完整命理报告
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, 'scripts')
from 八字排盘 import (
    calc_bazi, calc_dayun, get_shensha, get_geju, 
    analyze_xiyongshen, predict_liunian, get_shishen,
    TIANGAN_WUXING, DIZHI_WUXING, TIANGAN, DIZHI,
    WUXING_SHENG, WUXING_KE
)

def get_favorable_industries(xiyong):
    """根据喜用神推荐行业"""
    wx_to_industry = {
        '金': '金融、钢铁、机械制造、珠宝、汽车',
        '木': '教育、文化、出版、林业、园艺、纺织',
        '水': '贸易、物流、旅游、水产、饮料、进出口',
        '火': '能源、电子、餐饮、影视、广告、互联网',
        '土': '房地产、建筑、农业、陶瓷、石材、仓储'
    }
    return '、'.join([wx_to_industry.get(wx, '') for wx in xiyong if wx in wx_to_industry])

def get_favorable_directions(xiyong):
    """根据喜用神推荐方位"""
    wx_to_direction = {
        '金': '西方',
        '木': '东方',
        '水': '北方',
        '火': '南方',
        '土': '本地/中央'
    }
    return '、'.join([wx_to_direction.get(wx, '') for wx in xiyong if wx in wx_to_direction])

def get_favorable_colors(xiyong):
    """根据喜用神推荐颜色"""
    wx_to_color = {
        '金': '白色、金色、银色',
        '木': '绿色、青色、碧色',
        '水': '黑色、蓝色、灰色',
        '火': '红色、紫色、粉色',
        '土': '黄色、棕色、咖啡色'
    }
    return '、'.join([wx_to_color.get(wx, '') for wx in xiyong if wx in wx_to_color])

def get_favorable_numbers(xiyong):
    """根据喜用神推荐数字"""
    wx_to_number = {
        '金': '4、9、7、8',
        '木': '3、8、1、2',
        '水': '1、6、0',
        '火': '2、7、3、9',
        '土': '5、0、2、7'
    }
    return '、'.join([wx_to_number.get(wx, '') for wx in xiyong if wx in wx_to_number])

def format_bazi_report(bazi, dayun, shensha, geju, xiyong, gender, shichen_label):
    """格式化命理报告为HTML"""
    
    # 五行分布
    wx = bazi['wuxing_count']
    
    # 日主信息
    day_master = bazi['day_master']
    day_master_wx = TIANGAN_WUXING[day_master]
    day_master_yy = "阳" if day_master in ["甲", "丙", "戊", "庚", "壬"] else "阴"
    
    # 十神关系
    shishen_map = {
        '年干': get_shishen(day_master, bazi['year_pillar'][0]),
        '月干': get_shishen(day_master, bazi['month_pillar'][0]),
        '时干': get_shishen(day_master, bazi['hour_pillar'][0]),
    }
    
    # 大运表格
    dayun_rows = ""
    current_year = datetime.now().year
    birth_year = bazi['birth_year']
    for d in dayun['dayuns']:
        age_range = f"{d['start_age']}-{d['end_age']}岁"
        start_year = birth_year + d['start_age']
        end_year = birth_year + d['end_age']
        year_range = f"{start_year}-{end_year}"
        
        # 标记当前大运
        is_current = d['start_age'] <= (current_year - birth_year) < d['end_age']
        marker = " ← 当前" if is_current else ""
        
        dayun_rows += f"""
        <tr class="{'current-dayun' if is_current else ''}">
            <td>第{d['step']}步</td>
            <td><strong>{d['ganzhi']}</strong></td>
            <td>{age_range}</td>
            <td>{year_range}</td>
            <td>{d['gan_wuxing']} {d['zhi_wuxing']}</td>
            <td>{marker}</td>
        </tr>"""
    
    # 未来流年预测（2026-2035）
    liunian_list = []
    for year in range(2026, 2036):
        ly = predict_liunian(bazi, dayun, year, gender)
        liunian_list.append(ly)
    
    liunian_rows = ""
    for ly in liunian_list:
        year = ly['year']
        ganzhi = ly['liunian_ganzhi']
        shishen = ly['analysis']['流年十神']
        
        # 运势评级
        rating = "☆☆☆☆☆"
        if shishen in ['正财', '偏财']:
            rating = "★★★★★ 财运佳"
        elif shishen in ['正官', '七杀']:
            rating = "★★★★☆ 事业旺"
        elif shishen in ['食神', '伤官']:
            rating = "★★★☆☆ 才华展"
        elif shishen in ['比肩', '劫财']:
            rating = "★★☆☆☆ 防竞争"
        elif shishen in ['正印', '偏印']:
            rating = "★★★★☆ 智慧增"
        
        liunian_rows += f"""
        <tr>
            <td>{year}年</td>
            <td>{ganzhi}</td>
            <td>{shishen}</td>
            <td>{rating}</td>
        </tr>"""
    
    # 生成HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>赛博算命 · {shichen_label}命盘</title>
    <style>
        * {{ margin:0; padding:0; box-sizing: border-box; }}
        body {{
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        h1 {{
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #ffd700, #ffed4e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            text-align: center;
            color: #999;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        .bazi-plot {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
            padding: 30px;
            background: rgba(255, 215, 0, 0.05);
            border: 2px solid rgba(255, 215, 0, 0.3);
            border-radius: 15px;
        }}
        .pillar {{
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            transition: all 0.3s;
        }}
        .pillar:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.2);
        }}
        .pillar-label {{
            font-size: 0.8em;
            color: #999;
            margin-bottom: 10px;
        }}
        .ganzhi {{
            font-size: 2em;
            font-weight: bold;
            color: #ffd700;
            margin: 10px 0;
        }}
        .wuxing-tag {{
            display: inline-block;
            padding: 5px 10px;
            margin: 3px;
            border-radius: 5px;
            font-size: 0.85em;
            background: rgba(255, 255, 255, 0.1);
        }}
        .wuxing-金 {{ color: #ffd700; border: 1px solid #ffd700; }}
        .wuxing-木 {{ color: #4caf50; border: 1px solid #4caf50; }}
        .wuxing-水 {{ color: #2196f3; border: 1px solid #2196f3; }}
        .wuxing-火 {{ color: #f44336; border: 1px solid #f44336; }}
        .wuxing-土 {{ color: #ff9800; border: 1px solid #ff9800; }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 30px 0;
        }}
        .info-card {{
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border-left: 4px solid #ffd700;
        }}
        .info-card h3 {{
            color: #ffd700;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        th {{
            background: rgba(255, 215, 0, 0.2);
            color: #ffd700;
            font-weight: bold;
        }}
        .current-dayun {{
            background: rgba(255, 215, 0, 0.1);
            font-weight: bold;
        }}
        .wuxing-bar {{
            display: flex;
            gap: 10px;
            margin: 15px 0;
        }}
        .wuxing-item {{
            flex: 1;
            text-align: center;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }}
        .wuxing-count {{
            font-size: 1.5em;
            font-weight: bold;
            color: #ffd700;
        }}
        .advice-section {{
            margin: 30px 0;
            padding: 20px;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 10px;
            border-left: 4px solid #4caf50;
        }}
        .advice-section h3 {{
            color: #4caf50;
            margin-bottom: 15px;
        }}
        .disclaimer {{
            margin-top: 40px;
            padding: 20px;
            background: rgba(244, 67, 54, 0.1);
            border-radius: 10px;
            border-left: 4px solid #f44336;
            font-size: 0.9em;
            color: #999;
        }}
        .print-btn {{
            display: block;
            margin: 20px auto;
            padding: 15px 40px;
            background: linear-gradient(90deg, #ffd700, #ffed4e);
            color: #1a1a2e;
            border: none;
            border-radius: 30px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .print-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
        }}
        @media print {{
            body {{ background: white; color: black; }}
            .container {{ background: white; }}
            .print-btn {{ display: none; }}
        }}
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ 打印/保存PDF</button>
    
    <div class="container">
        <h1>🔮 赛博算命</h1>
        <div class="subtitle">
            基于中国传统命理学 · 作者：锤无双<br>
            出生时间：1983年1月26日 {shichen_label} · 男 · 湖州市吴兴区妙西镇
        </div>
        
        <!-- 四柱八字 -->
        <div class="bazi-plot">
            <div class="pillar">
                <div class="pillar-label">年柱（祖先）</div>
                <div class="ganzhi">{bazi['year_pillar']}</div>
                <div class="wuxing-tag wuxing-{TIANGAN_WUXING[bazi['year_pillar'][0]]}">{TIANGAN_WUXING[bazi['year_pillar'][0]]}</div>
                <div class="wuxing-tag wuxing-{DIZHI_WUXING[bazi['year_pillar'][1]]}">{DIZHI_WUXING[bazi['year_pillar'][1]]}</div>
            </div>
            <div class="pillar">
                <div class="pillar-label">月柱（父母/青年）</div>
                <div class="ganzhi">{bazi['month_pillar']}</div>
                <div class="wuxing-tag wuxing-{TIANGAN_WUXING[bazi['month_pillar'][0]]}">{TIANGAN_WUXING[bazi['month_pillar'][0]]}</div>
                <div class="wuxing-tag wuxing-{DIZHI_WUXING[bazi['month_pillar'][1]]}">{DIZHI_WUXING[bazi['month_pillar'][1]]}</div>
            </div>
            <div class="pillar" style="border: 2px solid #ffd700;">
                <div class="pillar-label">日柱（自己）</div>
                <div class="ganzhi">{bazi['day_pillar']}</div>
                <div class="wuxing-tag wuxing-{TIANGAN_WUXING[bazi['day_pillar'][0]]}">{TIANGAN_WUXING[bazi['day_pillar'][0]]}（日主）</div>
                <div class="wuxing-tag wuxing-{DIZHI_WUXING[bazi['day_pillar'][1]]}">{DIZHI_WUXING[bazi['day_pillar'][1]]}</div>
            </div>
            <div class="pillar">
                <div class="pillar-label">时柱（子女/晚年）</div>
                <div class="ganzhi">{bazi['hour_pillar']}</div>
                <div class="wuxing-tag wuxing-{TIANGAN_WUXING[bazi['hour_pillar'][0]]}">{TIANGAN_WUXING[bazi['hour_pillar'][0]]}</div>
                <div class="wuxing-tag wuxing-{DIZHI_WUXING[bazi['hour_pillar'][1]]}">{DIZHI_WUXING[bazi['hour_pillar'][1]]}</div>
            </div>
        </div>
        
        <!-- 命局分析 -->
        <div class="info-grid">
            <div class="info-card">
                <h3>🎯 命局核心</h3>
                <p><strong>日主：</strong>{day_master}（{day_master_wx}，{day_master_yy}）</p>
                <p><strong>格局：</strong>{geju}</p>
                <p><strong>喜用神：</strong>{', '.join(xiyong['xiyongshen'])}</p>
                <p><strong>忌神：</strong>{', '.join(xiyong['jishen'])}</p>
            </div>
            
            <div class="info-card">
                <h3>✨ 神煞</h3>
                <p>{'<br>'.join([f"• {s}" for s in shensha]) if shensha else "无明显神煞"}</p>
            </div>
            
            <div class="info-card" style="grid-column: 1 / -1;">
                <h3>📊 五行分布</h3>
                <div class="wuxing-bar">
                    <div class="wuxing-item">
                        <div class="wuxing-count">{wx['金']}</div>
                        <div>金</div>
                    </div>
                    <div class="wuxing-item">
                        <div class="wuxing-count">{wx['木']}</div>
                        <div>木</div>
                    </div>
                    <div class="wuxing-item">
                        <div class="wuxing-count">{wx['水']}</div>
                        <div>水</div>
                    </div>
                    <div class="wuxing-item">
                        <div class="wuxing-count">{wx['火']}</div>
                        <div>火</div>
                    </div>
                    <div class="wuxing-item">
                        <div class="wuxing-count">{wx['土']}</div>
                        <div>土</div>
                    </div>
                </div>
                <p><strong>分析：</strong>{'五行齐全' if all(wx[k] > 0 for k in wx) else '五行缺' + '、'.join([k for k in wx if wx[k] == 0])}，
                日主{day_master_wx}{'偏旺' if wx[day_master_wx] >= 3 else '中和' if wx[day_master_wx] == 2 else '偏弱'}</p>
            </div>
        </div>
        
        <!-- 大运 -->
        <h2 style="color: #ffd700; margin: 30px 0 20px;">📈 大运走势</h2>
        <p>起运：{dayun['qiyun_age']}岁 · 方向：{dayun['direction']}</p>
        <table>
            <tr>
                <th>步序</th>
                <th>大运干支</th>
                <th>年龄</th>
                <th>对应年份</th>
                <th>五行</th>
                <th>备注</th>
            </tr>
            {dayun_rows}
        </table>
        
        <!-- 流年预测 -->
        <h2 style="color: #ffd700; margin: 30px 0 20px;">🔮 未来流年预测（2026-2035）</h2>
        <table>
            <tr>
                <th>年份</th>
                <th>干支</th>
                <th>十神</th>
                <th>运势</th>
            </tr>
            {liunian_rows}
        </table>
        
        <!-- 综合建议 -->
        <div class="advice-section">
            <h3>💡 综合建议</h3>
            <p><strong>喜用五行：</strong>{', '.join(xiyong['xiyongshen'])}</p>
            <p><strong>有利行业：</strong>{get_favorable_industries(xiyong['xiyongshen'])}</p>
            <p><strong>有利方位：</strong>{get_favorable_directions(xiyong['xiyongshen'])}</p>
            <p><strong>有利颜色：</strong>{get_favorable_colors(xiyong['xiyongshen'])}</p>
            <p><strong>幸运数字：</strong>{get_favorable_numbers(xiyong['xiyongshen'])}</p>
        </div>
        
        <!-- 免责声明 -->
        <div class="disclaimer">
            <h3>⚠️ 免责声明</h3>
            <p>本分析基于传统命理学推演，仅供参考与娱乐。</p>
            <p>命由天定，运在人为；积极心态、不断努力才是改变命运的根本。</p>
            <p>重大决策请咨询专业人士，不建议将命理作为唯一依据。</p>
            <p style="margin-top: 15px; color: #666;">— 赛博算命 v1.0 · 锤无双 出品 · 详细使用说明请关注 B站同名「锤无双」</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

if __name__ == '__main__':
    # 计算寅时（5点不到，按4:30算）
    print("正在计算寅时命盘...")
    bazi_yin = calc_bazi(1983, 1, 26, 4, '男')
    dayun_yin = calc_dayun(bazi_yin, '男')
    shensha_yin = get_shensha(bazi_yin['day_pillar'], bazi_yin['hour_pillar'], bazi_yin['year_pillar'])
    geju_yin = get_geju(bazi_yin)
    xiyong_yin = analyze_xiyongshen(bazi_yin)
    
    html_yin = format_bazi_report(bazi_yin, dayun_yin, shensha_yin, geju_yin, xiyong_yin, '男', '寅时（03:00-05:00）')
    with open('report_寅时.html', 'w', encoding='utf-8') as f:
        f.write(html_yin)
    print("✅ 寅时报告已生成：report_寅时.html")
    
    # 计算卯时（5点多，按5:30算）
    print("正在计算卯时命盘...")
    bazi_mao = calc_bazi(1983, 1, 26, 5, '男')
    dayun_mao = calc_dayun(bazi_mao, '男')
    shensha_mao = get_shensha(bazi_mao['day_pillar'], bazi_mao['hour_pillar'], bazi_mao['year_pillar'])
    geju_mao = get_geju(bazi_mao)
    xiyong_mao = analyze_xiyongshen(bazi_mao)
    
    html_mao = format_bazi_report(bazi_mao, dayun_mao, shensha_mao, geju_mao, xiyong_mao, '男', '卯时（05:00-07:00）')
    with open('report_卯时.html', 'w', encoding='utf-8') as f:
        f.write(html_mao)
    print("✅ 卯时报告已生成：report_卯时.html")
    
    print("\n🎉 两份报告已全部生成！")
    print("请打开以下文件查看：")
    print("  1. report_寅时.html")
    print("  2. report_卯时.html")
