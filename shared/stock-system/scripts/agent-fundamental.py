#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本面 Agent - 独立执行脚本

遵循五步工作法:
1️⃣ UPDATE → 2️⃣ READ → 3️⃣ DO → 4️⃣ CHECK → 5️⃣ REVIEW
"""

import os
import sys
import json
import time
from datetime import datetime
import subprocess
import re

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
COORDINATOR_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator')
DATA_DIR = os.path.join(COORDINATOR_DIR, 'data')
QUEUE_DIR = os.path.join(DATA_DIR, 'queue')
REQUESTS_DIR = os.path.join(QUEUE_DIR, 'requests')
RESULTS_DIR = os.path.join(QUEUE_DIR, 'results')
STOCK_DATA_SCRIPT = os.path.join(WORKSPACE, 'shared/stock-system/scripts/stock_data.py')

def get_stock_data(stock_code, max_retries=3):
    """获取股票数据 - 带重试机制"""
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                ['python3', STOCK_DATA_SCRIPT, stock_code],
                capture_output=True,
                text=True,
                timeout=60
            )
            # 解析 JSON 输出
            output = result.stdout
            if '{' in output:
                json_start = output.index('{')
                json_str = output[json_start:]
                data = json.loads(json_str)
                if data.get('success'):
                    return data
                elif attempt < max_retries:
                    print(f"  ⚠️  API 返回失败，重试 {attempt}/{max_retries}")
                    time.sleep(2)
                else:
                    print(f"  ⚠️  API 连续失败{max_retries}次，使用降级数据")
                    return data
            elif attempt < max_retries:
                print(f"  ⚠️  无 JSON 输出，重试 {attempt}/{max_retries}")
                time.sleep(2)
            else:
                print(f"  ❌  无法解析数据")
                return None
        except subprocess.TimeoutExpired:
            if attempt < max_retries:
                print(f"  ⚠️  获取超时，重试 {attempt}/{max_retries}")
                time.sleep(2)
            else:
                print(f"  ❌  获取超时 ({max_retries}次)")
                return None
        except Exception as e:
            if attempt < max_retries:
                print(f"  ⚠️  异常：{e}，重试 {attempt}/{max_retries}")
                time.sleep(2)
            else:
                print(f"  ❌  获取失败：{e}")
                return None
    
    return None

def parse_output(output, stock_code):
    """解析 stock-analyzer 输出"""
    data = {'stock_code': stock_code}
    
    patterns = {
        'stock_name': r'股票名称：(.+)',
        'price': r'当前股价：¥([\d.]+)',
        'change_pct': r'涨跌幅：([+-]?[\d.]+)%',
        'pe': r'市盈率.*?：([\d.]+)',
        'pb': r'市净率.*?：([\d.]+)',
        'roe': r'ROE：([\d.]+)%',
        'revenue_growth': r'营收.*?\+([\d.]+)%',
        'profit_growth': r'净利润.*?\+([\d.]+)%',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            if key in ['price', 'pe', 'pb', 'roe']:
                data[key] = float(match.group(1))
            elif key in ['change_pct', 'revenue_growth', 'profit_growth']:
                data[key] = float(match.group(1))
            else:
                data[key] = match.group(1).strip()
    
    return data

def analyze_fundamental(data):
    """基本面分析"""
    rating = '持有'
    confidence = 60
    reasons = []
    risks = []
    data_sources = []
    analysis_details = {}
    
    # 记录数据来源
    if data.get('source'):
        data_sources.append(f"数据源：{data['source']}")
    if data.get('pe'):
        data_sources.append("PE 数据")
    if data.get('roe'):
        data_sources.append("ROE 数据")
    if data.get('revenue'):
        data_sources.append("财报数据")
    
    # 记录分析的指标
    analysis_details = {
        '估值指标': {
            'PE': data.get('pe', 'N/A'),
            'PB': data.get('pb', 'N/A'),
        },
        '盈利能力': {
            'ROE': f"{data.get('roe', 'N/A')}%" if data.get('roe') else 'N/A',
            '毛利率': f"{data.get('gross_margin', 'N/A')}%" if data.get('gross_margin') else 'N/A',
            '净利率': f"{data.get('net_margin', 'N/A')}%" if data.get('net_margin') else 'N/A',
        },
        '增长能力': {
            '营收增速': f"{data.get('revenue_growth', 'N/A')}%" if data.get('revenue_growth') else 'N/A',
            '利润增速': f"{data.get('profit_growth', 'N/A')}%" if data.get('profit_growth') else 'N/A',
        }
    }
    
    # ROE 分析
    if data.get('roe'):
        if data['roe'] >= 25:
            reasons.append(f"ROE {data['roe']}% 优秀")
            confidence += 15
        elif data['roe'] >= 20:
            reasons.append(f"ROE {data['roe']}% 良好")
            confidence += 10
        elif data['roe'] < 15:
            risks.append(f"ROE {data['roe']}% 偏低")
            confidence -= 10
    
    # 增长分析
    if data.get('revenue_growth'):
        if data['revenue_growth'] >= 20:
            reasons.append(f"营收增速 {data['revenue_growth']}% 优秀")
            confidence += 10
        elif data['revenue_growth'] >= 15:
            reasons.append(f"营收增速 {data['revenue_growth']}% 良好")
            confidence += 5
        elif data['revenue_growth'] < 0:
            risks.append(f"营收负增长 {data['revenue_growth']}%")
            confidence -= 15
    
    if data.get('profit_growth'):
        if data['profit_growth'] >= 20:
            reasons.append(f"利润增速 {data['profit_growth']}% 优秀")
            confidence += 10
        elif data['profit_growth'] >= 15:
            reasons.append(f"利润增速 {data['profit_growth']}% 良好")
            confidence += 5
    
    # 估值分析
    if data.get('pe'):
        if data['pe'] < 15:
            reasons.append(f"PE {data['pe']}倍 低估")
            confidence += 10
            rating = '买入'
        elif data['pe'] < 25:
            reasons.append(f"PE {data['pe']}倍 合理")
            confidence += 5
        elif data['pe'] > 40:
            risks.append(f"PE {data['pe']}倍 偏高")
            confidence -= 10
    
    if data.get('pb') and data['pb'] > 8:
        risks.append(f"PB {data['pb']}倍 偏高")
        confidence -= 5
    
    # 确定评级
    if confidence >= 80:
        rating = '买入'
    elif confidence >= 70:
        rating = '买入'
    elif confidence < 50:
        rating = '卖出'
    
    confidence = max(50, min(95, confidence))
    
    return {
        'rating': rating,
        'confidence': confidence,
        'reasons': reasons,
        'risks': risks,
        'data_sources': data_sources if data_sources else ['东方财富 API', '财报数据'],
        'analysis_details': analysis_details,
        'agent_version': '基本面 Agent v1.0',
    }

def process_requests():
    """处理请求队列"""
    if not os.path.exists(REQUESTS_DIR):
        os.makedirs(REQUESTS_DIR, exist_ok=True)
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 查找待处理的请求
    pending = []
    for f in os.listdir(REQUESTS_DIR):
        if f.endswith('.md'):
            filepath = os.path.join(REQUESTS_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                if '基本面：⏳ 待处理' in content:
                    # 提取股票代码
                    match = re.search(r'股票代码：(\d+)', content)
                    if match:
                        pending.append({
                            'file': f,
                            'filepath': filepath,
                            'stock_code': match.group(1),
                            'content': content
                        })
    
    if not pending:
        print("✅ 无待处理请求")
        return
    
    print(f"📋 发现 {len(pending)} 个待处理请求")
    
    for req in pending:
        print(f"\n处理请求：{req['file']}")
        stock_code = req['stock_code']
        
        # 获取数据
        print(f"  获取 {stock_code} 数据...")
        data = get_stock_data(stock_code)
        if not data:
            print(f"  ❌ 获取数据失败")
            continue
        
        print(f"  ✅ {data.get('stock_name', stock_code)} 当前价：¥{data.get('price', 'N/A')}")
        
        # 执行分析
        print(f"  执行基本面分析...")
        result = analyze_fundamental(data)
        print(f"  评级：{result['rating']} ({result['confidence']}%)")
        
        # 写入结果
        result_file = f"result-{datetime.now().strftime('%Y%m%d%H%M%S')}-fundamental.md"
        result_path = os.path.join(RESULTS_DIR, result_file)
        
        # 构建详细数据表格
        details_table = []
        if 'analysis_details' in result:
            for category, metrics in result['analysis_details'].items():
                for metric, value in metrics.items():
                    details_table.append(f"- {metric}: {value}")
        
        result_content = f"""# 分析结果 - 基本面

## 请求 ID
{req['file'].replace('.md', '')}

## Agent
{result.get('agent_version', '基本面 Agent-v1.0')}

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据来源
{chr(10).join(['- ' + src for src in result.get('data_sources', ['东方财富 API', '财报数据'])])}

## 股票信息
- 代码：{stock_code}
- 名称：{data.get('stock_name', 'N/A')}
- 当前价：¥{data.get('price', 'N/A')}

## 分析结果
| 项目 | 内容 |
|------|------|
| 评级 | {result['rating']} |
| 置信度 | {result['confidence']}% |
| 关键依据 | {'; '.join(result['reasons'][:3])} |
| 风险点 | {'; '.join(result['risks'][:2]) if result['risks'] else '无明显风险'} |

## 详细数据
{chr(10).join(details_table) if details_table else '- PE: N/A' + chr(10) + '- PB: N/A' + chr(10) + '- ROE: N/A%'}

## 分析过程
1. 获取股票实时数据和财务指标
2. 分析 ROE 盈利能力
3. 分析营收和利润增长趋势
4. 评估 PE/PB 估值水平
5. 综合判断给出评级

## 判断标准
- ROE > 25%: 优秀
- PE < 15: 低估
- 营收增速 > 20%: 高增长
- PB > 8: 偏高
"""
        
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(result_content)
        
        print(f"  ✅ 结果写入：{result_file}")
        
        # 更新请求状态（同时更新复选框和状态行）
        new_content = req['content']
        new_content = new_content.replace('- [ ] 基本面 Agent', '- [x] 基本面 Agent')
        new_content = new_content.replace('基本面：⏳ 待处理', '基本面：✅ 已完成')
        with open(req['filepath'], 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ 请求状态已更新")

def main():
    print(f"\n{'='*50}")
    print(f"📊 基本面 Agent - 检查请求")
    print(f"{'='*50}\n")
    
    process_requests()
    
    print(f"\n{'='*50}")
    print(f"✅ 基本面 Agent 执行完成")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
