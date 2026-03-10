#!/usr/bin/env python3
"""
主协调 Agent - 使用多 Agent 并发分析

架构:
1. 调用 stock-analyzer 获取真实数据
2. 并发调用 3 个专业 Agent (基本面/技术面/情绪)
3. 汇总结果，计算综合评分
4. 给出最终投资建议

调用方式:
python3 main_coordinator.py <股票代码>
"""

import sys
import json
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

AGENTS_DIR = '/Users/egg/.openclaw/workspace/memory/stock-system/agents'

def call_agent(agent_name, stock_code):
    """调用专业 Agent"""
    script = f'{AGENTS_DIR}/{agent_name}_agent.py'
    result = subprocess.run(
        ['python3', script, stock_code],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {
            'agent': agent_name,
            'error': result.stderr,
            'rating': '持有',
            'confidence': 50,
            'score': 50
        }

def make_decision(fundamental, technical, sentiment):
    """
    综合决策
    
    权重配置:
    - 基本面：50% (长期价值)
    - 技术面：30% (中期趋势)
    - 情绪面：20% (短期波动)
    """
    # 获取各 Agent 评分
    f_score = fundamental.get('score', 50)
    t_score = technical.get('score', 50)
    s_score = sentiment.get('score', 50)
    
    # 加权计算
    weights = {
        'fundamental': 0.5,
        'technical': 0.3,
        'sentiment': 0.2
    }
    
    total_score = (
        f_score * weights['fundamental'] +
        t_score * weights['technical'] +
        s_score * weights['sentiment']
    )
    
    # 计算综合置信度
    f_conf = fundamental.get('confidence', 50)
    t_conf = technical.get('confidence', 50)
    s_conf = sentiment.get('confidence', 50)
    
    avg_confidence = (
        f_conf * weights['fundamental'] +
        t_conf * weights['technical'] +
        s_conf * weights['sentiment']
    )
    
    # 综合评级
    if total_score >= 80:
        rating = '🟢 推荐'
        position = '20-30%'
    elif total_score >= 60:
        rating = '🟡 中性'
        position = '5-10%'
    elif total_score >= 40:
        rating = '🟡 中性'
        position = '0-5%'
    else:
        rating = '🔴 回避'
        position = '0%'
    
    return {
        'score': round(total_score, 1),
        'rating': rating,
        'position': position,
        'confidence': round(avg_confidence, 1),
        'weights': weights
    }

def analyze_stock(stock_code):
    """主分析流程"""
    print("=" * 60)
    print(f"📊 多 Agent 并发分析：{stock_code}")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 并发调用 3 个 Agent
    agents = ['fundamental', 'technical', 'sentiment']
    results = {}
    
    print("\n⚡ 并发调用 Agent...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_agent = {
            executor.submit(call_agent, agent, stock_code): agent
            for agent in agents
        }
        
        for future in as_completed(future_to_agent):
            agent_name = future_to_agent[future]
            try:
                result = future.result()
                results[agent_name] = result
                print(f"   ✅ {result.get('agent', agent_name)}: {result.get('rating', 'N/A')} ({result.get('confidence', 0)}%)")
            except Exception as e:
                print(f"   ❌ {agent_name} 失败：{e}")
                results[agent_name] = {
                    'agent': agent_name,
                    'rating': '持有',
                    'confidence': 50,
                    'score': 50,
                    'error': str(e)
                }
    
    # 综合决策
    print("\n🤔 综合决策...")
    decision = make_decision(
        results.get('fundamental', {}),
        results.get('technical', {}),
        results.get('sentiment', {})
    )
    
    print(f"   综合评分：{decision['score']}")
    print(f"   评级：{decision['rating']}")
    print(f"   建议仓位：{decision['position']}")
    
    # 计算耗时
    duration = (datetime.now() - start_time).total_seconds()
    
    # 输出完整结果
    output = {
        'stock_code': stock_code,
        'timestamp': datetime.now().isoformat(),
        'duration': f"{duration:.2f}秒",
        'agents': results,
        'decision': decision
    }
    
    print("\n" + "=" * 60)
    print(f"✅ 分析完成！耗时：{duration:.2f}秒")
    print("=" * 60)
    
    # 输出 JSON 结果
    print("\n📄 JSON 结果:")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    
    return output

def main():
    if len(sys.argv) < 2:
        print("用法：python3 main_coordinator.py <股票代码>")
        print("示例：python3 main_coordinator.py 600519")
        return
    
    stock_code = sys.argv[1]
    analyze_stock(stock_code)

if __name__ == '__main__':
    main()
