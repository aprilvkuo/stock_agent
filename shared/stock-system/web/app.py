#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票多 Agent 系统 - Web 监控服务 v4.0
专业级监控面板，实时数据，工作量排行榜

特性:
- 实时数据（直接从日志统计，100% 准确）
- 工作量排行榜（按执行次数排序）
- 健康度仪表盘
- 实时日志流
- 响应式设计（手机/PC 完美适配）
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import os
import re
import json
import sys

app = Flask(__name__)

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
DATA_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator/data')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')
REQUESTS_DIR = os.path.join(DATA_DIR, 'queue/requests')
RESULTS_DIR = os.path.join(DATA_DIR, 'queue/results')
DEAD_LETTER_DIR = os.path.join(DATA_DIR, 'queue/dead-letter')
SYSTEM_DIR = os.path.join(WORKSPACE, 'shared/stock-system')
MONITOR_DIR = os.path.join(SYSTEM_DIR, 'monitor')
TICKETS_DIR = os.path.join(SYSTEM_DIR, 'tickets')

# v2.0 配置 - 股票多 Agent 系统
STOCK_SYSTEM_V2 = os.path.join(WORKSPACE, 'memory/stock-system')
ANALYSIS_LOG_DIR = os.path.join(STOCK_SYSTEM_V2, 'analysis-log')
VALIDATION_QUEUE_PATH = os.path.join(STOCK_SYSTEM_V2, 'validation-queue.md')

# Agent 配置
AGENTS = {
    'fundamental': {'name': '基本面 Agent', 'emoji': '📊', 'color': '#3B82F6'},
    'technical': {'name': '技术面 Agent', 'emoji': '📈', 'color': '#8B5CF6'},
    'sentiment': {'name': '情绪 Agent', 'emoji': '😊', 'color': '#F59E0B'},
    'coordinator': {'name': '主 Agent', 'emoji': '🎯', 'color': '#EF4444'},
    'qa': {'name': '质检 Agent', 'emoji': '🔍', 'color': '#10B981'},
    'programmer': {'name': '程序员 Agent', 'emoji': '💻', 'color': '#6366F1'}
}

def count_agent_executions(agent_pattern, log_file):
    """统计 Agent 执行次数（直接从日志读取，100% 准确）"""
    if not os.path.exists(log_file):
        return 0, None
    
    count = 0
    last_run = None
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            if re.search(agent_pattern, line, re.IGNORECASE):
                if '完成' in line or 'SUCCESS' in line:
                    count += 1
                    
                    # 提取时间戳
                    time_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                    if time_match:
                        try:
                            timestamp = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                            if last_run is None or timestamp > last_run:
                                last_run = timestamp
                        except:
                            pass
    except Exception as e:
        pass
    
    return count, last_run

def get_agent_stats():
    """获取所有 Agent 统计（实时从日志读取）"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOGS_DIR, f'daemon-{today}.log')
    
    stats = {}
    now = datetime.now()
    
    for agent_id, config in AGENTS.items():
        # 根据 Agent 类型选择匹配模式
        if agent_id == 'qa':
            pattern = r'质检 Agent.*完成|✅ 质检 Agent 完成'
        elif agent_id == 'coordinator':
            pattern = r'主 Agent 汇总完成|Coordinator.*完成'
        elif agent_id == 'programmer':
            pattern = r'程序员 Agent.*完成|✅ 程序员 Agent 完成'
        else:
            pattern = rf'{agent_id}.*完成|{config["name"]}.*完成'
        
        count, last_run = count_agent_executions(pattern, log_file)
        
        # 计算状态
        if last_run:
            minutes_ago = (now - last_run).total_seconds() / 60
            if minutes_ago < 15:
                status = 'active'
                status_text = '运行中'
                emoji = '🟢'
            elif minutes_ago < 60:
                status = 'idle'
                status_text = '空闲'
                emoji = '🟡'
            else:
                status = 'idle'
                status_text = f'{int(minutes_ago/60)}小时前'
                emoji = '🟡'
        else:
            status = 'offline'
            status_text = '未活动'
            emoji = '🔴'
        
        stats[agent_id] = {
            'id': agent_id,
            'name': config['name'],
            'emoji': config['emoji'],
            'color': config['color'],
            'status': status,
            'status_emoji': emoji,
            'status_text': status_text,
            'tasks': count,
            'last_run': last_run.strftime('%Y-%m-%d %H:%M:%S') if last_run else None,
            'last_run_timestamp': last_run.isoformat() if last_run else None
        }
    
    return stats

def get_error_stats():
    """获取错误统计"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOGS_DIR, f'daemon-{today}.log')
    
    if not os.path.exists(log_file):
        return {'total': 0, 'rate': 0, 'by_agent': {}}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        error_lines = [l for l in lines if '[ERROR]' in l]
        success_lines = [l for l in lines if '[SUCCESS]' in l and '完成' in l]
        
        total_errors = len(error_lines)
        total_success = len(success_lines)
        total = total_errors + total_success
        
        error_rate = (total_errors * 100 / total) if total > 0 else 0
        
        # 按 Agent 分类错误
        error_by_agent = {}
        for line in error_lines:
            if 'fundamental' in line.lower():
                error_by_agent['fundamental'] = error_by_agent.get('fundamental', 0) + 1
            elif 'technical' in line.lower():
                error_by_agent['technical'] = error_by_agent.get('technical', 0) + 1
            elif 'sentiment' in line.lower():
                error_by_agent['sentiment'] = error_by_agent.get('sentiment', 0) + 1
        
        return {
            'total': total_errors,
            'success': total_success,
            'rate': round(error_rate, 2),
            'by_agent': error_by_agent
        }
    except:
        return {'total': 0, 'rate': 0, 'by_agent': {}}

def get_system_health():
    """获取系统健康度"""
    # 读取质检报告
    report_file = os.path.join(MONITOR_DIR, 'quality_report.json')
    
    if os.path.exists(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            return report.get('summary', {})
        except:
            pass
    
    # 如果没有报告，计算一个
    error_stats = get_error_stats()
    health_score = max(0, 100 - error_stats['rate'] * 2)
    
    return {
        'health_score': round(health_score, 1),
        'critical_issues': 0,
        'warnings': 1 if error_stats['rate'] > 10 else 0
    }

def get_recent_logs(limit=50):
    """获取最近日志"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOGS_DIR, f'daemon-{today}.log')
    
    if not os.path.exists(log_file):
        return []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 返回最后 N 行
        recent = lines[-limit:]
        return [line.strip() for line in recent]
    except:
        return []

def get_pending_requests():
    """获取待处理请求数"""
    if not os.path.exists(REQUESTS_DIR):
        return 0
    
    count = 0
    for f in os.listdir(REQUESTS_DIR):
        if f.endswith('.md'):
            filepath = os.path.join(REQUESTS_DIR, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if '汇总：✅ 已完成' not in content:
                        count += 1
            except:
                pass
    
    return count

def get_rewards_punishments():
    """获取奖惩记录"""
    rp_file = os.path.join(DATA_DIR, 'rewards_punishments.json')
    
    if os.path.exists(rp_file):
        try:
            with open(rp_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # 返回默认数据
    return {
        'rewards': [],
        'punishments': [],
        'agent_scores': {agent: {'name': config['name'], 'score': 100, 'trend': 'stable'} for agent, config in AGENTS.items()},
        'honor_roll': [],
        'last_update': datetime.now().isoformat()
    }

def get_ranking():
    """获取工作量排行榜（按执行次数排序）"""
    stats = get_agent_stats()
    ranking = sorted(stats.values(), key=lambda x: x['tasks'], reverse=True)
    
    # 添加排名
    for i, agent in enumerate(ranking):
        agent['rank'] = i + 1
        if i == 0:
            agent['medal'] = '🥇'
        elif i == 1:
            agent['medal'] = '🥈'
        elif i == 2:
            agent['medal'] = '🥉'
        else:
            agent['medal'] = f'#{i+1}'
    
    return ranking


# ============ v2.0 分析报告 API ============

def get_v2_analysis_logs(limit=20):
    """获取 v2.0 分析日志列表"""
    if not os.path.exists(ANALYSIS_LOG_DIR):
        return []
    
    logs = []
    try:
        # 获取所有 .md 文件
        files = [f for f in os.listdir(ANALYSIS_LOG_DIR) if f.endswith('.md')]
        
        # 按时间排序（最新的在前）
        files.sort(reverse=True)
        
        for filename in files[:limit]:
            filepath = os.path.join(ANALYSIS_LOG_DIR, filename)
            
            # 解析文件名：2026-03-09_600519_贵州茅台.md
            parts = filename.replace('.md', '').split('_')
            if len(parts) >= 3:
                date = parts[0]
                code = parts[1]
                name = '_'.join(parts[2:])
            else:
                date = 'Unknown'
                code = 'Unknown'
                name = filename.replace('.md', '')
            
            # 读取文件内容摘要
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # 读取前 2000 字符
            
            # 提取评级信息
            rating = 'Unknown'
            if '强烈买入' in content:
                rating = 'STRONG_BUY'
            elif '买入' in content:
                rating = 'BUY'
            elif '持有' in content:
                rating = 'HOLD'
            elif '卖出' in content:
                rating = 'SELL'
            
            logs.append({
                'filename': filename,
                'date': date,
                'code': code,
                'name': name,
                'rating': rating,
                'preview': content[:500],
                'filepath': filepath,
            })
    except Exception as e:
        pass
    
    return logs


def get_v2_analysis_detail(filepath):
    """获取单个分析报告详情"""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'content': content,
            'filename': os.path.basename(filepath),
        }
    except Exception as e:
        return None


def get_v2_validation_queue():
    """获取验证队列"""
    if not os.path.exists(VALIDATION_QUEUE_PATH):
        return []
    
    items = []
    try:
        with open(VALIDATION_QUEUE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 跳过表头，解析表格行
        for line in lines[4:]:  # 跳过标题行
            if line.strip().startswith('|') and '待验证' in line:
                parts = line.split('|')
                if len(parts) >= 8:
                    items.append({
                        'date': parts[1].strip(),
                        'code': parts[2].strip(),
                        'name': parts[3].strip(),
                        'action': parts[4].strip(),
                        'target': parts[5].strip(),
                        'stop_loss': parts[6].strip(),
                        'validate_date': parts[7].strip(),
                        'status': parts[8].strip() if len(parts) > 8 else '待验证',
                    })
    except Exception as e:
        pass
    
    return items

@app.route('/')
def index():
    """主页 - 监控大盘"""
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    """API - 完整数据"""
    agent_stats = get_agent_stats()
    error_stats = get_error_stats()
    health = get_system_health()
    
    return jsonify({
        'agents': agent_stats,
        'ranking': get_ranking(),
        'errors': error_stats,
        'health': health,
        'pending_requests': get_pending_requests(),
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/agents')
def api_agents():
    """API - Agent 统计"""
    return jsonify(get_agent_stats())

@app.route('/api/ranking')
def api_ranking():
    """API - 工作量排行榜"""
    return jsonify(get_ranking())

@app.route('/api/errors')
def api_errors():
    """API - 错误统计"""
    return jsonify(get_error_stats())

@app.route('/api/health')
def api_health():
    """API - 系统健康"""
    return jsonify(get_system_health())

@app.route('/api/logs')
def api_logs():
    """API - 最近日志"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(get_recent_logs(limit))

@app.route('/api/rewards')
def api_rewards():
    """API - 奖惩记录"""
    return jsonify(get_rewards_punishments())

@app.route('/api/agent-ratings', methods=['GET', 'POST'])
def api_agent_ratings():
    """API - Agent 评分（获取或提交评分）"""
    # 添加 stock-system 路径
    stock_system_path = os.path.join(WORKSPACE, 'memory/stock-system')
    sys.path.insert(0, stock_system_path)
    
    try:
        from agent_rating import rating_system
    except ImportError:
        return jsonify({'error': '评分系统未初始化'}), 500
    
    if request.method == 'POST':
        # 提交新评分
        data = request.json
        try:
            rating = rating_system.rate_service(
                provider_id=data.get('provider_id'),
                consumer_id=data.get('consumer_id'),
                service_type=data.get('service_type'),
                accuracy=data.get('accuracy', 3),
                timeliness=data.get('timeliness', 3),
                completeness=data.get('completeness', 3),
                usefulness=data.get('usefulness', 3),
                reliability=data.get('reliability', 3),
                feedback=data.get('feedback', ''),
                suggestions=data.get('suggestions', [])
            )
            return jsonify({'success': True, 'rating': rating})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    else:
        # 获取评分数据
        provider_id = request.args.get('provider_id')
        
        if provider_id:
            # 获取指定 Agent 的统计
            stats = rating_system.get_provider_stats(provider_id)
            return jsonify(stats)
        else:
            # 获取所有 Agent 排名
            ranking = rating_system.get_all_providers_ranking()
            recent_ratings = rating_system.get_recent_ratings(limit=20)
            return jsonify({
                'ranking': ranking,
                'recent_ratings': recent_ratings
            })

@app.route('/api/agent-ratings/recent')
def api_agent_ratings_recent():
    """API - 最近评分记录"""
    stock_system_path = os.path.join(WORKSPACE, 'memory/stock-system')
    sys.path.insert(0, stock_system_path)
    
    try:
        from agent_rating import rating_system
        limit = request.args.get('limit', 20, type=int)
        ratings = rating_system.get_recent_ratings(limit)
        return jsonify(ratings)
    except ImportError:
        return jsonify([]), 500

@app.route('/api/improvement-tickets', methods=['GET', 'POST'])
def api_improvement_tickets():
    """API - 改进工单"""
    stock_system_path = os.path.join(WORKSPACE, 'memory/stock-system')
    sys.path.insert(0, stock_system_path)
    
    try:
        from improvement_ticket import ticket_system
    except ImportError:
        return jsonify({'error': '工单系统未初始化'}), 500
    
    if request.method == 'POST':
        # 创建工单（通常由低分自动触发）
        data = request.json
        try:
            ticket = ticket_system.create_ticket(
                provider_id=data.get('provider_id'),
                consumer_id=data.get('consumer_id'),
                service_type=data.get('service_type'),
                rating=data.get('rating', {})
            )
            return jsonify({'success': True, 'ticket': ticket})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    else:
        # 获取工单列表
        status = request.args.get('status')
        provider = request.args.get('provider')
        tickets = ticket_system.get_all_tickets(status_filter=status, provider_filter=provider)
        return jsonify(tickets)

@app.route('/api/improvement-tickets/stats')
def api_improvement_tickets_stats():
    """API - 工单统计"""
    stock_system_path = os.path.join(WORKSPACE, 'memory/stock-system')
    sys.path.insert(0, stock_system_path)
    
    try:
        from improvement_ticket import ticket_system
        stats = ticket_system.get_statistics()
        return jsonify(stats)
    except ImportError:
        return jsonify({}), 500

@app.route('/api/feedback-reports')
def api_feedback_reports():
    """API - 反馈报告"""
    stock_system_path = os.path.join(WORKSPACE, 'memory/stock-system')
    sys.path.insert(0, stock_system_path)
    
    try:
        from feedback_report import report_generator
        agent_id = request.args.get('agent_id')
        reports = report_generator.get_all_reports(agent_id)
        return jsonify(reports)
    except ImportError:
        return jsonify([]), 500

@app.route('/api/feedback-reports/generate', methods=['POST'])
def api_feedback_reports_generate():
    """API - 生成反馈报告"""
    stock_system_path = os.path.join(WORKSPACE, 'memory/stock-system')
    sys.path.insert(0, stock_system_path)
    
    try:
        from feedback_report import report_generator
        data = request.json
        agent_id = data.get('agent_id')
        weeks_ago = data.get('weeks_ago', 0)
        
        report = report_generator.generate_weekly_report(agent_id, weeks_ago)
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/todo-list')
def api_todo_list():
    """API - TODO List（聚合所有来源：主系统 + sub-agents）"""
    result = {
        "main_system": {"P0": [], "P1": [], "P2": [], "P3": []},
        "sub_agents": []
    }
    
    # 1. 解析主系统 TODO.md
    todo_file = os.path.join(WORKSPACE, 'TODO.md')
    if os.path.exists(todo_file):
        try:
            with open(todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_priority = None
            
            for line in content.split('\n'):
                if '### 🔴 P0' in line:
                    current_priority = "P0"
                elif '### 🔴 P1' in line:
                    current_priority = "P1"
                elif '### 🟡 P2' in line:
                    current_priority = "P2"
                elif '### 🟢 P3' in line:
                    current_priority = "P3"
                
                if current_priority and line.strip().startswith('- [ ]'):
                    task = line.strip()[6:].strip()
                    if task and not task.startswith('---'):
                        result["main_system"][current_priority].append(task)
                elif current_priority and line.strip().startswith('- [x]'):
                    task = line.strip()[6:].strip()
                    if task and not task.startswith('---'):
                        result["main_system"][current_priority].append(f"✅ {task}")
        except Exception as e:
            print(f"解析主 TODO.md 失败：{e}")
    
    # 2. 解析 sub-agents 的 HEARTBEAT.md（作为任务来源）
    agents_dir = os.path.join(WORKSPACE, 'agents')
    agent_tasks = {
        'fundamental': {'name': '基本面 Agent', 'tasks': []},
        'technical': {'name': '技术面 Agent', 'tasks': []},
        'sentiment': {'name': '情绪 Agent', 'tasks': []},
        'review': {'name': '复盘 Agent', 'tasks': []},
        'coordinator': {'name': '主 Agent', 'tasks': []}
    }
    
    import re
    
    for agent_id, agent_info in agent_tasks.items():
        agent_dir = os.path.join(agents_dir, f'stock-{agent_id}')
        heartbeat_file = os.path.join(agent_dir, 'HEARTBEAT.md')
        
        if os.path.exists(heartbeat_file):
            try:
                with open(heartbeat_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取所有 "## 每 XXX - 任务描述" 格式
                pattern = r'##\s*(.*?)\s*-\s*(.*?)(?:\n|$)'
                matches = re.findall(pattern, content)
                
                for freq, task in matches:
                    freq_clean = freq.strip()
                    if not freq_clean.startswith('每'):
                        freq_clean = '每' + freq_clean
                    agent_info['tasks'].append(f"{freq_clean} - {task.strip()}")
            except Exception as e:
                print(f"解析 {agent_id} HEARTBEAT.md 失败：{e}")
    
    # 转换为列表格式
    for agent_id, info in agent_tasks.items():
        if info['tasks']:
            result["sub_agents"].append({
                'id': agent_id,
                'name': info['name'],
                'tasks': info['tasks']
            })
    
    return jsonify(result)


# ============ v2.0 分析报告 API ============

@app.route('/api/v2/logs')
def api_v2_logs():
    """API - v2.0 分析日志列表"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify(get_v2_analysis_logs(limit))


@app.route('/api/v2/log/<path:filepath>')
def api_v2_log_detail(filepath):
    """API - v2.0 分析报告详情"""
    # 解码文件路径
    full_path = os.path.join('/', filepath)
    result = get_v2_analysis_detail(full_path)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/v2/validation')
def api_v2_validation():
    """API - v2.0 验证队列"""
    return jsonify(get_v2_validation_queue())


@app.route('/v2-reports')
def v2_reports():
    """v2.0 分析报告页面"""
    return render_template('v2-reports.html')


@app.route('/v2-report/<path:filepath>')
def v2_report_detail(filepath):
    """v2.0 报告详情页"""
    return render_template('report.html', filepath=os.path.join('/', filepath))

@app.route('/agent-transparency')
def agent_transparency():
    """Agent 透明度监控页面"""
    return render_template('agent-transparency.html')

@app.route('/monitor')
def monitor():
    """实时监控页面"""
    return render_template('monitor.html')

@app.route('/agents')
def agents_page():
    """Agent 状态页面"""
    return render_template('agents.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
