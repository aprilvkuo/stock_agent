#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票多 Agent 系统 - 守护进程 v3.0
完全自动化自我进化版本

核心特性:
- 单实例锁（PID 文件）
- 请求级文件锁（防并发）
- 自动重试机制（3 次）
- 死信队列（连续失败）
- 自我进化触发
"""

import os
import sys
import time
import subprocess
import fcntl
import json
from datetime import datetime
from pathlib import Path

# 配置
SCRIPTS_DIR = '/Users/egg/.openclaw/workspace/shared/stock-system/scripts'
DATA_DIR = '/Users/egg/.openclaw/workspace/agents/stock-coordinator/data'
REQUESTS_DIR = os.path.join(DATA_DIR, 'queue/requests')
RESULTS_DIR = os.path.join(DATA_DIR, 'queue/results')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')
DEAD_LETTER_DIR = os.path.join(DATA_DIR, 'queue/dead-letter')
LOCK_DIR = os.path.join(DATA_DIR, 'queue/locks')

# 导入模块
sys.path.insert(0, SCRIPTS_DIR)
from agent_todo import add_agent_task, complete_agent_task, hold_agent_meeting

# 配置参数
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒
CHECK_INTERVAL = 30  # 检查间隔（秒）

def log(message, level='INFO'):
    """写入日志"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f'daemon-{datetime.now().strftime("%Y-%m-%d")}.log')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{level}] {message}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_line)
    
    print(log_line.strip())

def check_single_instance():
    """检查单实例 - 防止多进程同时运行"""
    pid_file = '/tmp/stock-daemon.pid'
    
    try:
        pid_fd = open(pid_file, 'w')
        fcntl.flock(pid_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        pid_fd.write(str(os.getpid()))
        pid_fd.flush()
        return pid_fd  # 保持文件打开以维持锁
    except BlockingIOError:
        print("❌ 守护进程已在运行中 (检测到 PID 文件锁)")
        sys.exit(1)

def acquire_request_lock(request_id):
    """获取请求锁"""
    os.makedirs(LOCK_DIR, exist_ok=True)
    lock_file = os.path.join(LOCK_DIR, f'{request_id}.lock')
    
    try:
        fd = open(lock_file, 'w')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fd.write(str(os.getpid()))
        fd.flush()
        return fd
    except (BlockingIOError, IOError):
        return None

def release_request_lock(lock_fd, request_id):
    """释放请求锁"""
    if lock_fd:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
            lock_file = os.path.join(LOCK_DIR, f'{request_id}.lock')
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except:
            pass

def get_pending_requests():
    """获取待处理的请求"""
    pending = []
    
    if not os.path.exists(REQUESTS_DIR):
        return pending
    
    for f in sorted(os.listdir(REQUESTS_DIR)):  # 按文件名排序，保证顺序
        if f.endswith('.md') and not f.startswith('.'):
            filepath = os.path.join(REQUESTS_DIR, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # 跳过已完成的（检查汇总状态）
                    if '汇总：✅ 已完成' in content:
                        continue
                    
                    # 检查是否有待处理的任务（检查任务复选框或状态行）
                    has_pending = False
                    if '- [ ] 基本面 Agent' in content or '- [ ] 技术面 Agent' in content or '- [ ] 情绪 Agent' in content:
                        has_pending = True
                    elif '基本面：⏳ 待处理' in content or '技术面：⏳ 待处理' in content or '情绪面：⏳ 待处理' in content:
                        has_pending = True
                    
                    if has_pending:
                        request_id = f.replace('.md', '')
                        
                        # 提取股票信息
                        import re
                        stock_match = re.search(r'股票代码：(\d+)', content)
                        name_match = re.search(r'股票名称：(.+)', content)
                        
                        # 检查重试次数
                        retry_match = re.search(r'重试次数：(\d+)', content)
                        retry_count = int(retry_match.group(1)) if retry_match else 0
                        
                        pending.append({
                            'id': request_id,
                            'code': stock_match.group(1) if stock_match else '',
                            'name': name_match.group(1).strip() if name_match else '',
                            'file': filepath,
                            'content': content,
                            'retry_count': retry_count
                        })
            except Exception as e:
                log(f"读取请求文件失败 {f}: {e}", 'ERROR')
    
    return pending

def run_agent(agent_name, stock_code, stock_name, request_id, max_retries=MAX_RETRIES):
    """运行 Agent 脚本（带重试机制）"""
    agent_scripts = {
        'fundamental': 'agent-fundamental.py',
        'technical': 'agent-technical.py',
        'sentiment': 'agent-sentiment.py'
    }
    
    if agent_name not in agent_scripts:
        return False
    
    script_path = os.path.join(SCRIPTS_DIR, agent_scripts[agent_name])
    
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(
                ['python3', script_path, stock_code, stock_name, request_id],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                log(f"{agent_name} Agent 完成：{stock_code} {stock_name}", 'SUCCESS')
                return True
            else:
                error_msg = result.stderr.strip()[:200] if result.stderr else '未知错误'
                if attempt < max_retries:
                    log(f"{agent_name} Agent 失败 (尝试 {attempt}/{max_retries}): {error_msg}", 'WARNING')
                    time.sleep(RETRY_DELAY)
                else:
                    log(f"{agent_name} Agent 失败 ({max_retries}次尝试后放弃): {error_msg}", 'ERROR')
                    return False
                    
        except subprocess.TimeoutExpired:
            if attempt < max_retries:
                log(f"{agent_name} Agent 超时 (尝试 {attempt}/{max_retries})", 'WARNING')
                time.sleep(RETRY_DELAY)
            else:
                log(f"{agent_name} Agent 超时 ({max_retries}次尝试后放弃)", 'ERROR')
                return False
        except Exception as e:
            error_msg = str(e)[:200]
            if attempt < max_retries:
                log(f"{agent_name} Agent 异常 (尝试 {attempt}/{max_retries}): {error_msg}", 'WARNING')
                time.sleep(RETRY_DELAY)
            else:
                log(f"{agent_name} Agent 异常 ({max_retries}次尝试后放弃): {error_msg}", 'ERROR')
                return False
    
    return False

def mark_task_done(filepath, agent_name):
    """标记任务完成"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新复选框
        content = content.replace(
            f'- [ ] {agent_name.capitalize()} Agent',
            f'- [x] {agent_name.capitalize()} Agent'
        )
        
        # 更新状态
        content = content.replace(
            f'{agent_name.capitalize()}：⏳ 待处理',
            f'{agent_name.capitalize()}：✅ 已完成'
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        log(f"标记任务完成失败：{e}", 'ERROR')

def increment_retry_count(filepath):
    """增加重试计数"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        if '重试次数:' in content:
            content = re.sub(r'重试次数：\d+', lambda m: f'重试次数：{int(m.group().split(":")[1]) + 1}', content)
        else:
            # 在请求信息后添加重试计数
            content = content.replace('## 状态', '## 元数据\n- 重试次数：1\n\n## 状态')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return int(re.search(r'重试次数：(\d+)', content).group(1))
    except:
        return 0

def move_to_dead_letter(filepath, request_id, reason):
    """移动到死信队列"""
    try:
        os.makedirs(DEAD_LETTER_DIR, exist_ok=True)
        dest = os.path.join(DEAD_LETTER_DIR, f'{request_id}.md')
        
        # 添加失败信息
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content += f"\n\n## 失败信息\n- 原因：{reason}\n- 时间：{datetime.now().isoformat()}\n- 状态：已移入死信队列\n"
        
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.remove(filepath)
        log(f"请求 {request_id} 移入死信队列：{reason}", 'WARNING')
    except Exception as e:
        log(f"移入死信队列失败：{e}", 'ERROR')

def process_request(request):
    """处理单个请求（带锁和重试）"""
    request_id = request['id']
    stock_code = request['code']
    stock_name = request['name']
    filepath = request['file']
    content = request['content']
    retry_count = request.get('retry_count', 0)
    
    # 获取请求锁
    lock_fd = acquire_request_lock(request_id)
    if not lock_fd:
        log(f"请求 {request_id} 正在被其他进程处理，跳过", 'DEBUG')
        return
    
    try:
        log(f"开始处理请求：{request_id} - {stock_code} {stock_name} (重试:{retry_count}/{MAX_RETRIES})")
        
        agents = ['fundamental', 'technical', 'sentiment']
        failed_agents = []
        
        for agent in agents:
            # 检查是否已完成
            if f'- [x] {agent.capitalize()}' in content or f'- [x] {agent.title()}' in content:
                log(f"跳过已完成的 {agent} Agent", 'DEBUG')
                continue
            
            # 运行 Agent
            success = run_agent(agent, stock_code, stock_name, request_id)
            
            if success:
                mark_task_done(filepath, agent)
                # 重新读取内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                failed_agents.append(agent)
                log(f"{agent} Agent 执行失败", 'ERROR')
        
        # 检查是否全部失败
        if len(failed_agents) == len(agents):
            new_retry_count = increment_retry_count(filepath)
            if new_retry_count >= MAX_RETRIES:
                move_to_dead_letter(filepath, request_id, f"所有 Agent 连续失败{MAX_RETRIES}次")
            else:
                log(f"请求 {request_id} 等待下次重试 (第{new_retry_count}次)", 'WARNING')
        else:
            log(f"请求 {request_id} 部分完成，等待下次处理")
            
    except Exception as e:
        log(f"处理请求 {request_id} 异常：{e}", 'ERROR')
    finally:
        release_request_lock(lock_fd, request_id)

def run_coordinator():
    """运行主 Agent 汇总"""
    script_path = os.path.join(SCRIPTS_DIR, 'agent-coordinator.py')
    
    try:
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log("主 Agent 汇总完成", 'SUCCESS')
        else:
            log(f"主 Agent 失败：{result.stderr[:200]}", 'ERROR')
            
    except Exception as e:
        log(f"主 Agent 异常：{str(e)}", 'ERROR')

def run_qa_agent(action='daily'):
    """运行质检 Agent"""
    script_path = os.path.join(SCRIPTS_DIR, 'agent-qa.py')
    
    try:
        log(f"🔍 开始质检 Agent ({action})...", 'INFO')
        result = subprocess.run(
            ['python3', script_path, action],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            log("✅ 质检 Agent 完成", 'SUCCESS')
        else:
            log(f"质检 Agent 失败：{result.stderr[:200]}", 'ERROR')
            
    except Exception as e:
        log(f"质检 Agent 异常：{str(e)}", 'ERROR')

def run_stats_collector():
    """运行数据统计系统"""
    script_path = os.path.join(SCRIPTS_DIR, "stats_collector.py")
    try:
        log(f"📊 开始数据统计...", "INFO")
        result = subprocess.run(["python3", script_path], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            log("✅ 数据统计完成", "SUCCESS")
        else:
            log(f"数据统计失败：{result.stderr[:200]}", "ERROR")
    except Exception as e:
        log(f"数据统计异常：{str(e)}", "ERROR")

def run_auto_alert():
    """运行自动告警系统"""
    script_path = os.path.join(SCRIPTS_DIR, "auto_alert.py")
    try:
        log(f"🚨 开始自动告警...", "INFO")
        result = subprocess.run(["python3", script_path], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            log("✅ 自动告警完成", "SUCCESS")
        else:
            log(f"自动告警失败：{result.stderr[:200]}", "ERROR")
    except Exception as e:
        log(f"自动告警异常：{str(e)}", "ERROR")

def run_programmer_agent():
    """运行程序员 Agent（自动修复）"""
    script_path = os.path.join(SCRIPTS_DIR, 'agent-programmer.py')
    
    try:
        log(f"👨‍💻 开始程序员 Agent...", 'INFO')
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            log("✅ 程序员 Agent 完成", 'SUCCESS')
            if result.stdout:
                for line in result.stdout.strip().split('\n')[-5:]:
                    log(f"   {line}")
        else:
            log(f"程序员 Agent 失败：{result.stderr[:200]}", 'ERROR')
            
    except Exception as e:
        log(f"程序员 Agent 异常：{str(e)}", 'ERROR')

def run_task_queue():
    """运行自动任务队列"""
    script_path = os.path.join(SCRIPTS_DIR, 'auto_task_queue.py')
    
    try:
        log(f"📋 开始自动任务队列检查...", 'INFO')
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log("✅ 自动任务队列检查完成", 'SUCCESS')
            # 提取关键信息
            for line in result.stdout.split('\n'):
                if '下一个执行任务' in line or '负责' in line and '截止' in line:
                    log(f"   {line.strip()}")
        else:
            log(f"自动任务队列失败：{result.stderr[:200]}", 'ERROR')
            
    except Exception as e:
        log(f"自动任务队列异常：{str(e)}", 'ERROR')

def main():
    """主循环"""
    # 单实例检查
    pid_fd = check_single_instance()
    
    log("=" * 60)
    log("🚀 股票多 Agent 系统守护进程 v3.0 (完全自动化)")
    log("=" * 60)
    log("📋 五步工作法：已启用")
    log("🔒 单实例锁：已启用")
    log("🔄 自动重试：已启用 (最多 3 次)")
    log("💀 死信队列：已启用")
    log("👨‍💻 程序员 Agent: 已启用")
    log("🤖 自我进化：已启用")
    log("=" * 60)
    
    # 发送启动通知
    try:
        subprocess.run([
            'osascript',
            '-e',
            'display notification "股票多 Agent 系统 v3.0 已启动" with title "📊 系统通知" sound name "Glass"'
        ])
        log("已发送启动通知", 'INFO')
    except:
        pass
    
    # 初始化计时器
    last_coordinator_run = time.time()
    last_qa_run = time.time()
    last_meeting_run = time.time()
    last_programmer_run = time.time()
    last_task_queue_run = time.time()
    last_stats_run = time.time()
    
    coordinator_interval = 300  # 5 分钟
    qa_interval = 900  # 15 分钟（节省 Token）
    meeting_interval = 3600  # 1 小时
    programmer_interval = 600  # 10 分钟（检查工单）
    task_queue_interval = 300  # 5 分钟（检查任务队列）
    
    consecutive_failures = 0
    
    while True:
        try:
            # 检查待处理请求
            pending = get_pending_requests()
            
            if pending:
                log(f"发现 {len(pending)} 个待处理请求", 'INFO')
                
                for request in pending:
                    process_request(request)
                
                consecutive_failures = 0
            else:
                log("没有待处理请求", 'DEBUG')
            
            # 定期运行主 Agent 汇总
            now = time.time()
            if now - last_coordinator_run > coordinator_interval:
                run_coordinator()
                last_coordinator_run = now
            
            # 定期运行质检 Agent（优化版：只运行一次，包含所有检查）
            if now - last_qa_run > qa_interval:
                log("⏰ 定时质检 Agent 时间到（每 15 分钟）", 'INFO')
                run_qa_agent()  # v2.0 包含所有检查
                last_qa_run = now
            
            # Agent 例会（每小时）
            if now - last_meeting_run > meeting_interval:
                log("📋 召开 Agent 例会", 'INFO')
                try:
                    meeting = hold_agent_meeting('hourly')
                    log(f"✅ 例会完成：{meeting.get('summary', '无总结')}", 'SUCCESS')
                except Exception as e:
                    log(f"❌ 例会失败：{str(e)}", 'ERROR')
                last_meeting_run = now
            
            # 程序员 Agent（每 10 分钟检查工单）
            if now - last_programmer_run > programmer_interval:
                log("👨‍💻 程序员 Agent 检查工单", 'INFO')
                run_programmer_agent()
                last_programmer_run = now
            
            # 自动任务队列（每 5 分钟检查）
            if now - last_task_queue_run > task_queue_interval:
                log("📋 自动任务队列检查", 'INFO')
                run_task_queue()
                last_task_queue_run = now
            
            # 等待
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("守护进程停止 (用户中断)")
            break
        except Exception as e:
            error_msg = str(e)
            log(f"守护进程异常：{error_msg}", 'ERROR')
            consecutive_failures += 1
            
            if consecutive_failures >= 3:
                log("连续失败 3 次，等待重启...", 'ERROR')
                consecutive_failures = 0
            
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
