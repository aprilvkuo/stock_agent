#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票预测验证脚本 - 复盘 Agent 使用
获取真实股价数据，验证之前的预测
"""

import sys
import json
from datetime import datetime, timedelta
import subprocess
import re

def get_stock_data(stock_code):
    """
    调用 stock-analyzer 技能获取真实股票数据
    返回：股价、涨跌幅、成交量等
    """
    try:
        # 调用 stock-analyzer 脚本
        result = subprocess.run(
            ['python3', 'scripts/analyze_stock.py', stock_code],
            capture_output=True,
            text=True,
            cwd='/Users/egg/.openclaw/workspace/skills/stock-analyzer'
        )
        
        output = result.stdout
        
        # 解析输出数据
        data = {
            'stock_code': stock_code,
            'timestamp': datetime.now().isoformat(),
            'price': None,
            'change_pct': None,
            'pe': None,
            'pb': None,
            'roe': None,
            'revenue': None,
            'revenue_growth': None,
            'profit': None,
            'profit_growth': None,
            'ma5': None,
            'ma20': None,
            'ma60': None,
            'rsi': None,
            'macd': None,
        }
        
        # 解析股价
        price_match = re.search(r'当前股价：¥([\d.]+)', output)
        if price_match:
            data['price'] = float(price_match.group(1))
        
        # 解析涨跌幅
        change_match = re.search(r'涨跌幅：\+?([\d.]+)%', output)
        if change_match:
            data['change_pct'] = float(change_match.group(1))
        
        # 解析 PE
        pe_match = re.search(r'市盈率（PE TTM）：([\d.]+) 倍', output)
        if pe_match:
            data['pe'] = float(pe_match.group(1))
        
        # 解析 PB
        pb_match = re.search(r'市净率（PB）：([\d.]+) 倍', output)
        if pb_match:
            data['pb'] = float(pb_match.group(1))
        
        # 解析 ROE
        roe_match = re.search(r'ROE：([\d.]+)%', output)
        if roe_match:
            data['roe'] = float(roe_match.group(1))
        
        # 解析营收
        revenue_match = re.search(r'营收：¥([\d.]+) 亿元\(\+([\d.]+)%\)', output)
        if revenue_match:
            data['revenue'] = float(revenue_match.group(1))
            data['revenue_growth'] = float(revenue_match.group(2))
        
        # 解析利润
        profit_match = re.search(r'净利润：¥([\d.]+) 亿元\(\+([\d.]+)%\)', output)
        if profit_match:
            data['profit'] = float(profit_match.group(1))
            data['profit_growth'] = float(profit_match.group(2))
        
        # 解析均线
        ma5_match = re.search(r'MA5：¥([\d.]+)', output)
        if ma5_match:
            data['ma5'] = float(ma5_match.group(1))
        
        ma20_match = re.search(r'MA20：¥([\d.]+)', output)
        if ma20_match:
            data['ma20'] = float(ma20_match.group(1))
        
        ma60_match = re.search(r'MA60：¥([\d.]+)', output)
        if ma60_match:
            data['ma60'] = float(ma60_match.group(1))
        
        # 解析 RSI
        rsi_match = re.search(r'RSI：(\d+)', output)
        if rsi_match:
            data['rsi'] = int(rsi_match.group(1))
        
        # 解析 MACD
        macd_match = re.search(r'MACD：(.+)', output)
        if macd_match:
            data['macd'] = macd_match.group(1).strip()
        
        return data
        
    except Exception as e:
        print(f"获取数据失败：{e}")
        return None


def validate_prediction(prediction_type, predicted_value, actual_data, current_price):
    """
    验证单个预测
    
    返回：(是否成功，偏差分析)
    """
    if prediction_type == 'price_breakthrough':
        # 价格突破预测
        target_price = float(predicted_value.replace('元', ''))
        if current_price >= target_price:
            return True, f"当前价{current_price}元已突破目标{target_price}元"
        else:
            gap = (target_price - current_price) / target_price * 100
            return False, f"当前价{current_price}元，距离目标{target_price}元还差{gap:.1f}%"
    
    elif prediction_type == 'growth_rate':
        # 增速预测
        # 需要实际财报数据，暂时标记为待验证
        return None, "需等待财报发布后验证"
    
    elif prediction_type == 'policy':
        # 政策预测
        # 需要人工判断，暂时标记为待验证
        return None, "需人工评估政策面"
    
    elif prediction_type == 'stop_loss':
        # 止损位预测
        stop_price = float(predicted_value.replace('元', ''))
        if current_price >= stop_price:
            safety = (current_price - stop_price) / stop_price * 100
            return True, f"当前价{current_price}元，距离止损位{stop_price}元有{safety:.1f}%安全边际"
        else:
            return False, f"当前价{current_price}元已跌破止损位{stop_price}元"
    
    return None, "未知预测类型"


def parse_prediction_content(content):
    """
    解析预测内容，返回预测类型和值
    """
    if '突破' in content and '元' in content:
        # 提取价格
        match = re.search(r'突破\s*([\d.]+)\s*元', content)
        if match:
            return 'price_breakthrough', match.group(1) + '元'
    
    elif '增速' in content or '增长' in content:
        match = re.search(r'增速.*?(\d+)%', content)
        if match:
            return 'growth_rate', match.group(1) + '%'
    
    elif '政策' in content or '利空' in content:
        return 'policy', ''
    
    elif '跌破' in content and '元' in content:
        match = re.search(r'跌破\s*([\d.]+)\s*元', content)
        if match:
            return 'stop_loss', match.group(1) + '元'
    
    return 'unknown', ''


def update_validation_status(stock_code, prediction_content, status, analysis):
    """
    更新 validation-queue.md 中的验证状态
    
    参数:
        stock_code: 股票代码
        prediction_content: 预测内容（用于匹配行）
        status: 验证状态（✅ 正确 / ❌ 错误 / ⏳ 待人工验证）
        analysis: 偏差分析
    """
    queue_path = '/Users/egg/.openclaw/workspace/memory/stock-system/validation-queue.md'
    
    with open(queue_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        # 匹配股票代码和预测内容，且状态为待验证
        if stock_code in line and '待验证' in line:
            # 进一步检查预测内容是否匹配
            parts = line.split('|')
            if len(parts) >= 4:
                line_prediction = parts[3].strip()
                # 模糊匹配预测内容
                if prediction_content[:10] in line_prediction or line_prediction[:10] in prediction_content:
                    # 更新状态列和实际结果列、偏差分析列
                    # 表格格式：| 日期 | 股票 | 预测内容 | 验证日 | 状态 | 实际结果 | 偏差分析 |
                    parts[5] = f' {status} '
                    parts[6] = f' {analysis} '
                    lines[i] = '|'.join(parts) + '\n'
                    updated = True
                    print(f"   ✅ 已更新验证状态到文件")
                    break
    
    if updated:
        with open(queue_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    else:
        print(f"   ⚠️ 未找到匹配的记录，无法更新")


def main():
    """
    主函数：验证 validation-queue.md 中的到期预测
    """
    if len(sys.argv) > 1:
        # 指定股票代码
        stock_code = sys.argv[1]
        print(f"验证股票：{stock_code}")
    else:
        # 验证所有到期项目
        print("验证所有到期的预测项目")
    
    # 读取 validation-queue.md
    try:
        with open('/Users/egg/.openclaw/workspace/memory/stock-system/validation-queue.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("错误：找不到 validation-queue.md")
        return
    
    # 解析表格行
    lines = content.split('\n')
    today = datetime.now().strftime('%m-%d')
    today_full = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"验证日期：{today_full.strftime('%Y-%m-%d')}")
    print(f"{'='*60}\n")
    
    validated_count = 0
    update_count = 0
    
    for line in lines:
        if not line.strip().startswith('|') or '待验证' not in line:
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 6:
            continue
        
        date = parts[1]  # 03-08
        stock_info = parts[2]  # 600519 茅台
        prediction = parts[3]  # 预测内容
        validate_date = parts[4]  # 04-08
        
        # 解析股票代码
        stock_code_match = re.search(r'(\d{6}|\d{3})', stock_info)
        if not stock_code_match:
            continue
        stock_code = stock_code_match.group(1)
        
        # 检查是否到期
        try:
            validate_date_obj = datetime.strptime(f"2026-{validate_date}", '%Y-%m-%d')
        except:
            continue
        
        if validate_date_obj > today_full:
            # 未到期
            remaining_days = (validate_date_obj - today_full).days
            print(f"⏳ {stock_info} - '{prediction}' 还有{remaining_days}天到期")
            continue
        
        # 到期了，获取真实数据验证
        print(f"\n🔍 验证：{stock_info}")
        print(f"   预测：{prediction}")
        
        # 获取真实数据
        data = get_stock_data(stock_code)
        if not data or not data['price']:
            print(f"   ❌ 获取数据失败")
            continue
        
        print(f"   当前价：¥{data['price']} ({'+' if data['change_pct'] > 0 else ''}{data['change_pct']}%)")
        
        # 解析预测类型并验证
        pred_type, pred_value = parse_prediction_content(prediction)
        success, analysis = validate_prediction(pred_type, pred_value, data, data['price'])
        
        if success is True:
            status = "✅ 正确"
        elif success is False:
            status = "❌ 错误"
        else:
            status = "⏳ 待人工验证"
        
        print(f"   状态：{status}")
        print(f"   分析：{analysis}")
        
        # 更新文件
        update_validation_status(stock_code, prediction, status, analysis)
        update_count += 1
        
        validated_count += 1
    
    print(f"\n{'='*60}")
    if validated_count == 0:
        print("本次无到期需要验证的预测")
    else:
        print(f"完成 {validated_count} 项验证")
        print(f"已更新 {update_count} 项到文件")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
