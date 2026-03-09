#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序员 Agent - AI 工具选择器
根据任务复杂度自动选择最合适的 AI 工具
"""

import os
import json
from enum import Enum
from typing import Optional, Dict, Any


class TaskComplexity(Enum):
    """任务复杂度等级"""
    SIMPLE = "simple"          # 简单：单文件修改
    MEDIUM = "medium"          # 中等：多文件修改
    COMPLEX = "complex"        # 复杂：系统重构
    RESEARCH = "research"      # 研究型：需要调研


class AIToolSelector:
    """AI 工具选择器"""
    
    def __init__(self):
        self.config = {
            'simple': {
                'tool': 'local',
                'timeout': 60,
                'description': '本地执行，快速简单任务'
            },
            'medium': {
                'tool': 'codex',
                'timeout': 600,
                'description': 'Codex，中等复杂度代码任务'
            },
            'complex': {
                'tool': 'claude-code',
                'timeout': 1800,
                'description': 'Claude Code，复杂开发和重构'
            },
            'research': {
                'tool': 'claude-code',
                'timeout': 3600,
                'description': 'Claude Code，研究型任务'
            }
        }
    
    def evaluate_complexity(self, task: str, files_count: int = 1, 
                          code_lines: int = 0) -> TaskComplexity:
        """
        评估任务复杂度
        
        Args:
            task: 任务描述
            files_count: 涉及的文件数量
            code_lines: 代码行数
            
        Returns:
            TaskComplexity 等级
        """
        # 关键词分析
        complex_keywords = ['重构', '架构', '优化', ' redesign', 'refactor']
        medium_keywords = ['修复', '添加', '修改', 'update', 'fix', 'add']
        research_keywords = ['调研', '研究', '分析', 'compare', 'research']
        
        task_lower = task.lower()
        
        # 研究型任务
        if any(kw in task_lower for kw in research_keywords):
            return TaskComplexity.RESEARCH
        
        # 复杂任务
        if any(kw in task_lower for kw in complex_keywords):
            if files_count > 5 or code_lines > 500:
                return TaskComplexity.COMPLEX
        
        # 中等任务
        if any(kw in task_lower for kw in medium_keywords):
            if files_count > 1 or code_lines > 100:
                return TaskComplexity.MEDIUM
        
        # 简单任务
        if files_count == 1 and code_lines < 50:
            return TaskComplexity.SIMPLE
        
        # 默认中等
        return TaskComplexity.MEDIUM
    
    def select_tool(self, complexity: TaskComplexity) -> Dict[str, Any]:
        """
        根据复杂度选择工具
        
        Args:
            complexity: 任务复杂度
            
        Returns:
            工具配置字典
        """
        tool_config = self.config[complexity.value]
        
        return {
            'tool': tool_config['tool'],
            'timeout': tool_config['timeout'],
            'complexity': complexity.value,
            'description': tool_config['description']
        }
    
    def spawn_agent(self, task: str, **kwargs) -> Optional[str]:
        """
        Spawn AI Agent 执行任务
        
        Args:
            task: 任务描述
            **kwargs: 额外参数
            
        Returns:
            Agent 会话 ID 或 None
        """
        # 评估复杂度
        complexity = self.evaluate_complexity(
            task,
            files_count=kwargs.get('files_count', 1),
            code_lines=kwargs.get('code_lines', 0)
        )
        
        # 选择工具
        tool_config = self.select_tool(complexity)
        
        print(f"\n🤖 AI 工具选择")
        print(f"{'='*60}")
        print(f"任务复杂度：{complexity.value}")
        print(f"选择工具：{tool_config['tool']}")
        print(f"超时时间：{tool_config['timeout']}秒")
        print(f"描述：{tool_config['description']}")
        print(f"{'='*60}\n")
        
        # 根据工具类型 spawn
        tool = tool_config['tool']
        timeout = tool_config['timeout']
        
        if tool == 'local':
            # 本地执行
            print("💻 使用本地执行")
            return self._execute_local(task, **kwargs)
        
        elif tool == 'codex':
            # Codex
            print("🔷 使用 Codex")
            return self._spawn_codex(task, timeout, **kwargs)
        
        elif tool == 'claude-code':
            # Claude Code
            print("🟠 使用 Claude Code")
            return self._spawn_claude_code(task, timeout, **kwargs)
        
        else:
            print(f"⚠️  未知工具：{tool}")
            return None
    
    def _execute_local(self, task: str, **kwargs) -> Optional[str]:
        """本地执行任务"""
        print(f"执行本地任务：{task[:100]}...")
        # 这里实现本地执行逻辑
        return "local-executed"
    
    def _spawn_codex(self, task: str, timeout: int, **kwargs) -> Optional[str]:
        """Spawn Codex Agent"""
        try:
            from openclaw import sessions_spawn
            
            result = sessions_spawn(
                runtime="subagent",
                task=task,
                mode="run",
                timeoutSeconds=timeout
            )
            
            print(f"✅ Codex Agent 已启动")
            return result.get('sessionKey')
            
        except Exception as e:
            print(f"❌ Codex 启动失败：{e}")
            return None
    
    def _spawn_claude_code(self, task: str, timeout: int, **kwargs) -> Optional[str]:
        """Spawn Claude Code Agent"""
        try:
            from openclaw import sessions_spawn
            
            result = sessions_spawn(
                runtime="acp",
                agentId="claude-code",
                task=task,
                mode="run",
                timeoutSeconds=timeout
            )
            
            print(f"✅ Claude Code Agent 已启动")
            return result.get('sessionKey')
            
        except Exception as e:
            print(f"❌ Claude Code 启动失败：{e}")
            return None


# 便捷函数
def ai_do(task: str, **kwargs):
    """
    程序员 Agent 的 AI 工具调用接口
    
    Args:
        task: 任务描述
        **kwargs: 额外参数
        
    Returns:
        执行结果
    """
    selector = AIToolSelector()
    return selector.spawn_agent(task, **kwargs)


# 使用示例
if __name__ == '__main__':
    print("🤖 程序员 Agent - AI 工具选择器测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            'task': '修复这个语法错误',
            'files_count': 1,
            'code_lines': 20
        },
        {
            'task': '重构代码结构，优化性能',
            'files_count': 10,
            'code_lines': 1000
        },
        {
            'task': '调研最新的 Python 异步框架',
            'files_count': 0,
            'code_lines': 0
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['task']}")
        result = ai_do(case['task'], 
                      files_count=case['files_count'],
                      code_lines=case['code_lines'])
        print(f"结果：{result}")
