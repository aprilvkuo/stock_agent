#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五步工作法执行监控模块
监控所有 Agent 是否遵循五步工作法
"""

import os
import json
from datetime import datetime
from typing import Dict, List

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
MONITOR_DIR = os.path.join(WORKSPACE, 'shared/stock-system/monitor')
FIVE_STEP_FILE = os.path.join(MONITOR_DIR, 'five_step_log.json')

class FiveStepMonitor:
    """五步工作法执行监控器"""
    
    def __init__(self):
        self.monitor_dir = MONITOR_DIR
        self.log_file = FIVE_STEP_FILE
        self._ensure_monitor_dir()
        self._init_log()
    
    def _ensure_monitor_dir(self):
        """确保监控目录存在"""
        os.makedirs(self.monitor_dir, exist_ok=True)
    
    def _init_log(self):
        """初始化日志"""
        if not os.path.exists(self.log_file):
            self.log = {
                'created_at': datetime.now().isoformat(),
                'executions': [],
                'violations': [],
                'stats': {
                    'total': 0,
                    'compliant': 0,
                    'violations': 0
                }
            }
        else:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.log = json.load(f)
    
    def _save(self):
        """保存日志"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, ensure_ascii=False, indent=2)
    
    def record_execution(self, agent_name: str, task: str, 
                        steps_completed: List[str], duration_seconds: float):
        """
        记录一次任务执行
        
        参数:
            agent_name: Agent 名称
            task: 任务描述
            steps_completed: 完成的步骤列表 (如 ['UPDATE', 'READ', 'DO', 'CHECK', 'REVIEW'])
            duration_seconds: 执行时长（秒）
        """
        execution = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'task': task,
            'steps_completed': steps_completed,
            'duration_seconds': duration_seconds,
            'compliant': self._check_compliance(steps_completed)
        }
        
        self.log['executions'].append(execution)
        self.log['stats']['total'] += 1
        
        if execution['compliant']:
            self.log['stats']['compliant'] += 1
        else:
            self.log['stats']['violations'] += 1
            self.log['violations'].append({
                'timestamp': execution['timestamp'],
                'agent': agent_name,
                'task': task,
                'missing_steps': self._get_missing_steps(steps_completed)
            })
        
        self._save()
        
        # 违规处理
        if not execution['compliant']:
            self._handle_violation(agent_name, task, steps_completed)
    
    def _check_compliance(self, steps_completed: List[str]) -> bool:
        """检查是否遵循五步工作法"""
        required_steps = ['UPDATE', 'READ', 'DO', 'CHECK', 'REVIEW']
        return all(step in steps_completed for step in required_steps)
    
    def _get_missing_steps(self, steps_completed: List[str]) -> List[str]:
        """获取缺失的步骤"""
        required_steps = ['UPDATE', 'READ', 'DO', 'CHECK', 'REVIEW']
        return [step for step in required_steps if step not in steps_completed]
    
    def _handle_violation(self, agent_name: str, task: str, steps_completed: List[str]):
        """处理违规"""
        missing = self._get_missing_steps(steps_completed)
        violation_count = len([v for v in self.log['violations'] if v['agent'] == agent_name])
        
        message = f"⚠️  {agent_name} 未遵循五步工作法\n"
        message += f"   任务：{task}\n"
        message += f"   缺失步骤：{', '.join(missing)}\n"
        
        if violation_count == 1:
            message += "   处理：提醒"
        elif violation_count == 2:
            message += "   处理：警告"
        elif violation_count >= 3:
            message += "   处理：暂停任务，重新培训"
        
        print(message)
        
        # 写入违规日志
        violation_log = os.path.join(self.monitor_dir, 'violations.log')
        with open(violation_log, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_executions': self.log['stats']['total'],
            'compliant': self.log['stats']['compliant'],
            'violations': self.log['stats']['violations'],
            'compliance_rate': (self.log['stats']['compliant'] / self.log['stats']['total'] * 100) 
                              if self.log['stats']['total'] > 0 else 0
        }
    
    def get_recent_executions(self, limit: int = 10) -> List[Dict]:
        """获取最近执行记录"""
        return self.log['executions'][-limit:]
    
    def get_agent_stats(self, agent_name: str) -> Dict:
        """获取指定 Agent 的统计"""
        agent_executions = [e for e in self.log['executions'] if e['agent'] == agent_name]
        
        return {
            'total': len(agent_executions),
            'compliant': sum(1 for e in agent_executions if e['compliant']),
            'violations': sum(1 for e in agent_executions if not e['compliant']),
            'avg_duration': sum(e['duration_seconds'] for e in agent_executions) / len(agent_executions) 
                           if agent_executions else 0
        }


# 全局监控实例
monitor = FiveStepMonitor()


# 便捷函数

def record_task(agent_name: str, task: str, steps: List[str], duration: float):
    """记录任务执行"""
    monitor.record_execution(agent_name, task, steps, duration)

def get_compliance_rate() -> float:
    """获取遵循率"""
    stats = monitor.get_stats()
    return stats['compliance_rate']

def check_agent(agent_name: str) -> Dict:
    """检查 Agent 遵循情况"""
    return monitor.get_agent_stats(agent_name)


# 测试
if __name__ == "__main__":
    print("测试五步工作法监控...")
    
    # 模拟正常执行
    record_task('基本面 Agent', '分析 600519', 
               ['UPDATE', 'READ', 'DO', 'CHECK', 'REVIEW'], 
               120.5)
    
    # 模拟违规执行
    record_task('技术面 Agent', '分析 00700', 
               ['DO', 'CHECK'],  # 缺失 UPDATE, READ, REVIEW
               60.0)
    
    # 获取统计
    stats = get_compliance_rate()
    print(f"\n遵循率：{stats:.1f}%")
    
    # 获取 Agent 统计
    agent_stats = check_agent('基本面 Agent')
    print(f"\n基本面 Agent 统计:")
    print(f"  总任务：{agent_stats['total']}")
    print(f"  遵循：{agent_stats['compliant']}")
    print(f"  违规：{agent_stats['violations']}")
