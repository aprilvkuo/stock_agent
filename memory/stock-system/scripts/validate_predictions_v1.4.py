#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票预测验证脚本 - 复盘 Agent 使用 v1.4 增强版

支持验证类型:
1. 价格突破预测 ✅
2. 止损位预测 ✅
3. 营收增速预测 ✅ (v1.4 新增)
4. 利润增速预测 ✅ (v1.4 新增)
5. 政策事件预测 ⚠️ (半自动)
"""

import sys
import json
import os
from datetime import datetime, timedelta
import subprocess
import re

# 配置
STOCK_SYSTEM = '/Users/egg/.openclaw/workspace/memory/stock-system'
STOCK_ANALYZER_SCRIPT = '/Users/egg/.openclaw/workspace/skills/stock-analyzer/scripts/analyze_stock.py'


def get_stock_data(stock_code):
    """
    调用 stock-analyzer 获取真实股票数据
    """
    try:
        result = subprocess.run(
            ['python3', STOCK_ANALYZER_SCRIPT, stock_code],
            capture_output=True,
            text=True,
            timeout=60,
            cwd='/Users/egg/.openclaw/workspace/skills/stock-analyzer'
        )
        
        output = result.stdout
        data = parse_stock_output(output, stock_code)
        return data
        
    except Exception as e:
        print(f"获取数据失败：{e}")
        return None


def parse_stock_output(output, stock_code):
    """解析 stock-analyzer 输出"""
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
    }
    
    # 解析股价
    price_match = re.search(r'当前股价：¥([\d.]+)', output)
    if price_match:
        data['price'] = float(price_match.group(1))
    
    # 解析涨跌幅
    change_match = re.search(r'涨跌幅：([+-]?[\d.]+)%', output)
    if change_match:
        data['change_pct'] = float(change_match.group(1))
    
    # 解析 PE
    pe_match = re.search(r'市盈率.*?([\d.]+)\s*倍', output)
    if pe_match:
        data['pe'] = float(pe_match.group(1))
    
    # 解析 PB
    pb_match = re.search(r'市净率.*?([\d.]+)\s*倍', output)
    if pb_match:
        data['pb'] = float(pb_match.group(1))
    
    # 解析 ROE
    roe_match = re.search(r'ROE：([\d.]+)%', output)
    if roe_match:
        data['roe'] = float(roe_match.group(1))
    
    # 解析营收
    revenue_match = re.search(r'营收：¥([\d.]+) 亿元.*?\+([\d.-]+)%', output)
    if revenue_match:
        data['revenue'] = float(revenue_match.group(1))
        data['revenue_growth'] = float(revenue_match.group(2))
    
    # 解析利润
    profit_match = re.search(r'净利润：¥([\d.]+) 亿元.*?\+([\d.-]+)%', output)
    if profit_match:
        data['profit'] = float(profit_match.group(1))
        data['profit_growth'] = float(profit_match.group(2))
    
    return data


def validate_prediction(prediction_type, predicted_value, actual_data, current_price):
    """
    验证单个预测 v1.4 增强版
    
    支持类型:
    - price_breakthrough: 价格突破
    - stop_loss: 止损位
    - growth_rate: 增速预测（营收/利润）
    - policy: 政策事件
    
    返回：(是否成功，偏差分析)
    """
    if prediction_type == 'price_breakthrough':
        return validate_price_breakthrough(predicted_value, current_price)
    
    elif prediction_type == 'stop_loss':
        return validate_stop_loss(predicted_value, current_price)
    
    elif prediction_type == 'revenue_growth':
        return validate_growth_rate('营收', predicted_value, actual_data.get('revenue_growth'))
    
    elif prediction_type == 'profit_growth':
        return validate_growth_rate('利润', predicted_value, actual_data.get('profit_growth'))
    
    elif prediction_type == 'policy':
        return validate_policy_event(predicted_value)
    
    return None, "未知预测类型"


def validate_price_breakthrough(predicted_value, current_price):
    """验证价格突破预测"""
    target_price = float(predicted_value.replace('元', ''))
    if current_price >= target_price:
        return True, f"当前价{current_price}元已突破目标{target_price}元"
    else:
        gap = (target_price - current_price) / target_price * 100
        return False, f"当前价{current_price}元，距离目标{target_price}元还差{gap:.1f}%"


def validate_stop_loss(predicted_value, current_price):
    """验证止损位预测"""
    stop_price = float(predicted_value.replace('元', ''))
    if current_price >= stop_price:
        safety = (current_price - stop_price) / stop_price * 100
        return True, f"当前价{current_price}元，距离止损位{stop_price}元有{safety:.1f}%安全边际"
    else:
        return False, f"当前价{current_price}元已跌破止损位{stop_price}元"


def validate_growth_rate(metric_name, predicted_value, actual_value):
    """
    验证增速预测（营收/利润）v1.4 新增
    
    判断标准:
    - 方向一致且偏差<20%: ✅ 正确
    - 方向一致但偏差 20-50%: ⚠️ 部分正确
    - 方向相反或偏差>50%: ❌ 错误
    """
    if actual_value is None:
        return None, f"需等待财报发布（{metric_name}增速数据缺失）"
    
    # 解析预测值
    predicted_pct = float(predicted_value.replace('%', ''))
    
    # 计算偏差
    direction_match = (predicted_pct > 0) == (actual_value > 0)  # 方向是否一致
    deviation = abs(predicted_pct - actual_value)
    deviation_pct = abs(predicted_pct - actual_value) / max(abs(predicted_pct), 1) * 100
    
    if direction_match and deviation_pct < 20:
        return True, f"预测{predicted_pct}%，实际{actual_value}%，偏差{deviation_pct:.1f}%（✅ 优秀）"
    elif direction_match and deviation_pct < 50:
        return True, f"预测{predicted_pct}%，实际{actual_value}%，偏差{deviation_pct:.1f}%（⚠️ 可接受）"
    elif direction_match:
        return False, f"预测{predicted_pct}%，实际{actual_value}%，偏差{deviation_pct:.1f}%（❌ 偏差较大）"
    else:
        return False, f"预测{predicted_pct}%，实际{actual_value}%，方向相反（❌ 错误）"


def validate_policy_event(predicted_value):
    """
    验证政策事件预测 v1.4 新增
    
    当前实现：半自动
    - 需要人工确认政策事件
    - 提供新闻搜索链接辅助判断
    """
    # 生成辅助判断信息
    news_search_url = f"https://www.baidu.com/s?wd={predicted_value}"
    
    return None, f"需人工验证政策事件\n   请搜索确认：{predicted_value}\n   搜索链接：{news_search_url}"


def parse_prediction_content(content):
    """
    解析预测内容，返回预测类型和值 v1.4 增强
    
    支持的预测类型:
    - 突破 XXX 元 → price_breakthrough
    - 跌破 XXX 元 → stop_loss
    - 增速 XX% → revenue_growth 或 profit_growth
    - 政策/版号/利空 → policy
    """
    content = content.strip()
    
    # 价格突破
    if '突破' in content and '元' in content:
        match = re.search(r'突破\s*¥?([\d.]+)\s*元', content)
        if match:
            return 'price_breakthrough', match.group(1) + '元'
    
    # 止损位（跌破/不跌破）
    if ('跌破' in content or '不跌破' in content) and '元' in content:
        match = re.search(r'跌破\s*¥?([\d.]+)\s*元', content)
        if match:
            return 'stop_loss', match.group(1) + '元'
    
    # 营收增速
    if '营收' in content and ('增速' in content or '增长' in content) and '%' in content:
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', content)
        if match:
            return 'revenue_growth', match.group(1) + '%'
    
    # 利润增速
    if ('利润' in content or '净利' in content) and ('增速' in content or '增长' in content) and '%' in content:
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', content)
        if match:
            return 'profit_growth', match.group(1) + '%'
    
    # 政策事件
    if any(keyword in content for keyword in ['政策', '版号', '利空', '利好', '监管']):
        return 'policy', content
    
    return 'unknown', ''


def update_validation_status(stock_code, prediction_content, status, analysis):
    """
    更新 validation-queue.md 中的验证状态
    """
    queue_path = os.path.join(STOCK_SYSTEM, 'validation-queue.md')
    
    with open(queue_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        if stock_code in line and '待验证' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                line_prediction = parts[3].strip()
                if prediction_content[:10] in line_prediction or line_prediction[:10] in prediction_content:
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


def generate_validation_report(results):
    """
    生成验证报告 v1.4 新增
    
    参数:
        results: 验证结果列表
    """
    report_path = os.path.join(STOCK_SYSTEM, 'reports', f'validation_{datetime.now().strftime("%Y%m%d_%H%M")}.md')
    
    total = len(results)
    correct = sum(1 for r in results if r['status'] == '✅ 正确')
    partial = sum(1 for r in results if r['status'] == '⚠️ 部分正确')
    error = sum(1 for r in results if r['status'] == '❌ 错误')
    pending = sum(1 for r in results if r['status'] == '⏳ 待人工验证')
    
    accuracy = (correct + partial * 0.5) / total * 100 if total > 0 else 0
    
    content = f"""# 预测验证报告

**验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**验证范围**: 所有到期预测

---

## 📊 核心指标

| 指标 | 数值 |
|------|------|
| 验证总数 | {total} |
| ✅ 正确 | {correct} |
| ⚠️ 部分正确 | {partial} |
| ❌ 错误 | {error} |
| ⏳ 待人工验证 | {pending} |
| **准确率** | **{accuracy:.1f}%** |

---

## 📋 详细结果

| 股票 | 预测内容 | 验证结果 | 偏差分析 |
|------|----------|----------|----------|
"""
    
    for r in results:
        content += f"| {r['stock']} | {r['prediction']} | {r['status']} | {r['analysis']} |\n"
    
    content += f"""
---

## 📝 总结

本次验证共 {total} 项预测，准确率 {accuracy:.1f}%。

"""
    
    if correct > 0:
        content += f"✅ {correct} 项预测正确，表现优秀。\n\n"
    if error > 0:
        content += f"❌ {error} 项预测错误，需分析原因。\n\n"
    if pending > 0:
        content += f"⏳ {pending} 项需人工验证，请及时处理。\n\n"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return report_path


def main():
    """
    主函数：验证 validation-queue.md 中的到期预测
    """
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
        print(f"验证股票：{stock_code}")
    else:
        print("验证所有到期的预测项目")
    
    # 读取 validation-queue.md
    try:
        with open(os.path.join(STOCK_SYSTEM, 'validation-queue.md'), 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("错误：找不到 validation-queue.md")
        return
    
    lines = content.split('\n')
    today_full = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"验证日期：{today_full.strftime('%Y-%m-%d')}")
    print(f"{'='*60}\n")
    
    validated_count = 0
    update_count = 0
    results = []  # 用于生成报告
    
    for line in lines:
        if not line.strip().startswith('|') or '待验证' not in line:
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 6:
            continue
        
        stock_info = parts[2]
        prediction = parts[3]
        validate_date = parts[4]
        
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
            remaining_days = (validate_date_obj - today_full).days
            print(f"⏳ {stock_info} - '{prediction}' 还有{remaining_days}天到期")
            continue
        
        # 到期了，验证
        print(f"\n🔍 验证：{stock_info}")
        print(f"   预测：{prediction}")
        
        # 解析预测类型
        pred_type, pred_value = parse_prediction_content(prediction)
        
        # 根据预测类型获取数据并验证
        if pred_type in ['price_breakthrough', 'stop_loss']:
            # 价格类预测，获取股价
            data = get_stock_data(stock_code)
            if not data or not data['price']:
                print(f"   ❌ 获取数据失败")
                continue
            
            print(f"   当前价：¥{data['price']} ({'+' if data['change_pct'] > 0 else ''}{data['change_pct']}%)")
            success, analysis = validate_prediction(pred_type, pred_value, data, data['price'])
            
        elif pred_type in ['revenue_growth', 'profit_growth']:
            # 增速预测，获取财报数据
            data = get_stock_data(stock_code)
            if not data:
                print(f"   ❌ 获取数据失败")
                continue
            
            print(f"   实际增速：{data.get('revenue_growth') or data.get('profit_growth')}%")
            success, analysis = validate_prediction(pred_type, pred_value, data, None)
            
        elif pred_type == 'policy':
            # 政策预测，半自动验证
            success, analysis = validate_prediction(pred_type, pred_value, None, None)
            
        else:
            success = None
            analysis = f"未知预测类型：{pred_type}"
        
        # 确定状态
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
        
        # 记录结果
        results.append({
            'stock': stock_info,
            'prediction': prediction,
            'status': status,
            'analysis': analysis,
        })
        
        validated_count += 1
    
    # 生成验证报告
    if results:
        report_path = generate_validation_report(results)
        print(f"\n📄 验证报告已生成：{report_path}")
    
    print(f"\n{'='*60}")
    if validated_count == 0:
        print("本次无到期需要验证的预测")
    else:
        print(f"完成 {validated_count} 项验证")
        print(f"已更新 {update_count} 项到文件")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
