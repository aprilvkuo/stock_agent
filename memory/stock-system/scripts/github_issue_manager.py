#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Issues + PR 自动化管理模块
低分自动创建 Issue → Agent 解决 → 创建 PR → Merge 关闭 Issue
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 加载配置（优先级：系统环境变量 > .env 文件）
import os
from dotenv import load_dotenv

# 先尝试从系统环境变量读取 Bot Token
GITHUB_TOKEN = os.getenv('GITHUB_BOT_TOKEN', '') or os.getenv('GITHUB_TOKEN', '')
GITHUB_BOT_USERNAME = os.getenv('GITHUB_BOT_USERNAME', 'stock-agent-bot')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'aprilvkuo/stock_agent')

# 如果系统变量没有，再尝试从 .env 文件读取
if not GITHUB_TOKEN:
    env_path = os.path.join(os.path.dirname(__file__), '../../.env.github')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        GITHUB_TOKEN = os.getenv('GITHUB_BOT_TOKEN', '') or os.getenv('GITHUB_TOKEN', '')
        GITHUB_REPO = os.getenv('GITHUB_REPO', 'aprilvkuo/stock_agent')

GITHUB_API_BASE = f'https://api.github.com/repos/{GITHUB_REPO}'

# Agent GitHub 身份映射
AGENT_GITHUB_USERS = {
    'fundamental': os.getenv('AGENT_GITHUB_fundamental', 'fundamental-agent'),
    'technical': os.getenv('AGENT_GITHUB_technical', 'technical-agent'),
    'sentiment': os.getenv('AGENT_GITHUB_sentiment', 'sentiment-agent'),
    'coordinator': os.getenv('AGENT_GITHUB_coordinator', 'coordinator-agent'),
    'programmer': os.getenv('AGENT_GITHUB_programmer', 'programmer-agent'),
    'data-fetcher': os.getenv('AGENT_GITHUB_data-fetcher', 'data-fetcher-agent'),
    'qa': os.getenv('AGENT_GITHUB_qa', 'qa-agent'),
    'cio': os.getenv('AGENT_GITHUB_cio', 'cio-agent'),
}

# 优先级映射
PRIORITY_TO_LABEL = {
    'low': '🟡 low-priority',
    'medium': '🟠 medium-priority',
    'high': '🔴 high-priority',
    'critical': '🚨 critical',
}


class GitHubIssueManager:
    """GitHub Issue 管理器"""
    
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """发送 GitHub API 请求"""
        url = f'{GITHUB_API_BASE}/{endpoint}'
        response = self.session.request(method, url, json=data)
        response.raise_for_status()
        return response.json()
    
    def create_issue(
        self,
        title: str,
        body: str,
        assignees: List[str] = None,
        labels: List[str] = None,
        milestone: int = None
    ) -> dict:
        """
        创建 GitHub Issue
        
        Args:
            title: Issue 标题
            body: Issue 内容（Markdown）
            assignees: 指派给谁（GitHub 用户名列表）
            labels: Label 列表
            milestone: Milestone 编号
            
        Returns:
            Issue 信息（包含 number, html_url 等）
        """
        data = {
            'title': title,
            'body': body,
        }
        
        if assignees:
            data['assignees'] = assignees
        
        if labels:
            data['labels'] = labels
        
        if milestone:
            data['milestone'] = milestone
        
        result = self._request('POST', 'issues', data)
        
        print(f"✅ Issue 已创建：#{result['number']}")
        print(f"   标题：{result['title']}")
        print(f"   链接：{result['html_url']}")
        if assignees:
            print(f"   指派给：{', '.join(assignees)}")
        
        return result
    
    def create_improvement_issue(
        self,
        provider_id: str,
        consumer_id: str,
        service_type: str,
        rating: Dict,
        improvement_plan: List[str] = None
    ) -> dict:
        """
        创建改进工单 Issue（低分自动触发）
        
        Args:
            provider_id: 乙方 Agent ID
            consumer_id: 甲方 Agent ID
            service_type: 服务类型
            rating: 评分数据
            improvement_plan: 改进建议列表
            
        Returns:
            Issue 信息
        """
        # 生成 Issue 编号
        issue_id = f"IMPROVE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 获取优先级
        score = rating.get('overall_score', 0)
        if score <= 1:
            priority = 'critical'
        elif score <= 2:
            priority = 'high'
        elif score <= 3:
            priority = 'medium'
        else:
            priority = 'low'
        
        # 获取乙方 GitHub 账号
        provider_github = AGENT_GITHUB_USERS.get(provider_id, provider_id)
        
        # 生成 Issue 内容
        title = f"[{priority.upper()}] {provider_github} 需要改进：{service_type}"
        
        body = self._generate_issue_body(
            issue_id=issue_id,
            provider_id=provider_id,
            consumer_id=consumer_id,
            service_type=service_type,
            rating=rating,
            improvement_plan=improvement_plan,
            priority=priority
        )
        
        # 准备 Label
        labels = [PRIORITY_TO_LABEL.get(priority, '🟡 low-priority')]
        
        # 添加服务类型 Label
        service_labels = {
            'financial_analysis': '📊 基本面分析',
            'technical_analysis': '📈 技术面分析',
            'sentiment_analysis': '😊 情绪分析',
            'data_fetching': '🤖 数据抓取',
            'code_implementation': '💻 代码实现',
        }
        if service_type in service_labels:
            labels.append(service_labels[service_type])
        
        # 指派给乙方 Agent
        assignees = [provider_github]
        
        # 创建 Issue
        issue = self.create_issue(
            title=title,
            body=body,
            assignees=assignees,
            labels=labels
        )
        
        # 添加 Issue 编号到 body
        issue['improve_id'] = issue_id
        
        return issue
    
    def _generate_issue_body(
        self,
        issue_id: str,
        provider_id: str,
        consumer_id: str,
        service_type: str,
        rating: Dict,
        improvement_plan: List[str],
        priority: str
    ) -> str:
        """生成 Issue 内容（Markdown）"""
        
        # 评分详情
        scores = rating.get('scores', {})
        scores_md = ""
        if scores:
            scores_md = "\n### 📊 评分详情\n\n"
            scores_md += "| 维度 | 得分 |\n"
            scores_md += "|------|------|\n"
            for dim, score in scores.items():
                dim_name = {
                    'accuracy': '准确性',
                    'timeliness': '及时性',
                    'completeness': '完整性',
                    'usefulness': '有用性',
                    'reliability': '可靠性'
                }.get(dim, dim)
                scores_md += f"| {dim_name} | {'⭐' * score}{'☆' * (5-score)} ({score}/5) |\n"
        
        # 改进计划
        plan_md = ""
        if improvement_plan:
            plan_md = "\n### 📋 改进计划\n\n"
            for i, item in enumerate(improvement_plan, 1):
                plan_md += f"- [ ] {item}\n"
        
        # 截止日期（默认 3 天）
        deadline = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        body = f"""# 🎫 改进工单：{issue_id}

**优先级**: {priority.upper()}  
**乙方**: @{AGENT_GITHUB_USERS.get(provider_id, provider_id)}  
**甲方**: @{AGENT_GITHUB_USERS.get(consumer_id, consumer_id)}  
**服务类型**: `{service_type}`  
**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**截止日期**: {deadline}

---

## ⭐ 总体评分

**得分**: {rating.get('overall_score', 0)}/5.0 {'⭐' * int(rating.get('overall_score', 0))}{'☆' * (5-int(rating.get('overall_score', 0)))}

{scores_md}
## 📝 问题描述

{rating.get('feedback', '暂无详细描述')}

## 💡 改进建议

{rating.get('suggestions', ['暂无具体建议']) if isinstance(rating.get('suggestions'), list) else rating.get('suggestions', '暂无具体建议')}

{plan_md}
## 🔗 关联信息

- **触发评分**: {rating.get('id', 'N/A')}
- **服务时间**: {rating.get('date', 'N/A')}
- **影响评估**: {rating.get('impact', '待评估')}

---

## 📌 处理流程

1. **接收任务** - @乙方 确认接收
2. **创建 Branch** - `fix/{issue_id.lower()}`
3. **解决问题** - 实施改进
4. **创建 PR** - 关联此 Issue (`Closes #{{issue_number}}`)
5. **Code Review** - 等待审核
6. **Merge** - 合并后自动关闭

---

**标签**: `improvement-ticket` `agent-feedback`

> 💡 提示：完成改进后，请在 PR 描述中使用 `Closes #{{issue_number}}` 关联此 Issue
"""
        
        return body
    
    def close_issue(self, issue_number: int, reason: str = 'completed') -> dict:
        """
        关闭 Issue
        
        Args:
            issue_number: Issue 编号
            reason: 关闭原因（completed/not_planned）
            
        Returns:
            Issue 信息
        """
        data = {
            'state': 'closed',
            'state_reason': reason
        }
        
        result = self._request('PATCH', f'issues/{issue_number}', data)
        print(f"✅ Issue #{issue_number} 已关闭")
        return result
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = 'main',
        issue_number: int = None
    ) -> dict:
        """
        创建 Pull Request
        
        Args:
            title: PR 标题
            body: PR 内容
            head: 源分支
            base: 目标分支（默认 main）
            issue_number: 关联的 Issue 编号
            
        Returns:
            PR 信息
        """
        data = {
            'title': title,
            'body': body,
            'head': head,
            'base': base,
        }
        
        # 关联 Issue
        if issue_number:
            data['body'] += f"\n\nCloses #{issue_number}"
        
        result = self._request('POST', 'pulls', data)
        
        print(f"✅ PR 已创建：#{result['number']}")
        print(f"   标题：{result['title']}")
        print(f"   链接：{result['html_url']}")
        print(f"   分支：{head} → {base}")
        
        return result
    
    def get_issue(self, issue_number: int) -> dict:
        """获取 Issue 详情"""
        return self._request('GET', f'issues/{issue_number}')
    
    def list_issues(
        self,
        state: str = 'open',
        labels: List[str] = None,
        assignee: str = None
    ) -> List[dict]:
        """
        列出 Issues
        
        Args:
            state: open/closed/all
            labels: Label 过滤
            assignee: 指派给谁
            
        Returns:
            Issues 列表
        """
        params = {'state': state}
        
        if labels:
            params['labels'] = ','.join(labels)
        
        if assignee:
            params['assignee'] = assignee
        
        result = self._request('GET', 'issues', params)
        return result if isinstance(result, list) else []


# 全局实例
issue_manager = GitHubIssueManager()


# 便捷函数
def create_improvement_issue(provider, consumer, service_type, rating, plan=None):
    """便捷函数：创建改进工单 Issue"""
    return issue_manager.create_improvement_issue(
        provider, consumer, service_type, rating, plan
    )

def create_pr(title, body, head, base='main', issue_number=None):
    """便捷函数：创建 PR"""
    return issue_manager.create_pull_request(title, body, head, base, issue_number)

def close_issue(number, reason='completed'):
    """便捷函数：关闭 Issue"""
    return issue_manager.close_issue(number, reason)


# 测试
if __name__ == '__main__':
    print("🧪 测试 GitHub Issue 管理器...")
    
    if not GITHUB_TOKEN or GITHUB_TOKEN == 'your_github_token_here':
        print("⚠️  请先配置 .env.github 中的 GITHUB_TOKEN")
        print("   生成方式：https://github.com/settings/tokens")
    else:
        # 测试创建 Issue
        test_rating = {
            'overall_score': 2,
            'scores': {
                'accuracy': 2,
                'timeliness': 3,
                'completeness': 1,
                'usefulness': 2,
                'reliability': 3
            },
            'feedback': '数据缺少关键指标，需要补充 ROE、毛利率等',
            'suggestions': ['添加 ROE 指标', '添加毛利率指标', '提升数据完整性'],
            'date': datetime.now().isoformat()
        }
        
        issue = issue_manager.create_improvement_issue(
            provider_id="data-fetcher",
            consumer_id="fundamental",
            service_type="financial_data",
            rating=test_rating,
            improvement_plan=[
                "添加 ROE 指标",
                "添加毛利率指标",
                "添加净利率指标",
                "提升数据完整性至 95%+"
            ]
        )
        
        print(f"\n✅ 测试完成！Issue: #{issue.get('number', 'N/A')}")
