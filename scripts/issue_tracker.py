#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issue 自动跟踪和分配脚本
获取未解决的 Issue → 分配给负责 Agent → 跟踪解决 → 创建 PR → 合并关闭

版本：v1.0
日期：2026-03-09
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "aprilvkuo/stock_agent")
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"

# Agent GitHub 映射
AGENT_GITHUB = {
    'fundamental': 'fundamental-agent',
    'technical': 'technical-agent',
    'sentiment': 'sentiment-agent',
    'coordinator': 'coordinator-agent',
    'programmer': 'programmer-agent',
    'data-fetcher': 'data-fetcher-agent',
    'qa': 'qa-agent',
    'cio': 'cio-agent'
}

# Agent 职责映射
AGENT_RESPONSIBILITIES = {
    'fundamental': ['财报分析', '估值判断', '基本面'],
    'technical': ['K 线分析', '技术指标', '技术面'],
    'sentiment': ['情绪分析', '市场热度', '情绪面'],
    'coordinator': ['任务协调', '汇总决策', '资源分配'],
    'programmer': ['代码开发', 'Bug 修复', '功能实现', '重构'],
    'data-fetcher': ['数据获取', 'API 调用', '数据抓取'],
    'qa': ['质量检查', '测试验证', '代码审查'],
    'cio': ['投资决策', '风险评估', '策略制定']
}


class IssueTracker:
    """Issue 自动跟踪器"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """发送 GitHub API 请求"""
        url = f"{GITHUB_API_BASE}/{endpoint}"
        response = self.session.request(method, url, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_open_issues(self, labels: List[str] = None) -> List[dict]:
        """
        获取未解决的 Issue
        
        Args:
            labels: 过滤标签（如 ['improvement-ticket']）
            
        Returns:
            Issue 列表
        """
        params = {"state": "open"}
        
        if labels:
            params["labels"] = ",".join(labels)
        
        issues = self._request("GET", "issues", params)
        
        # 过滤掉 PR（GitHub API 返回的 issues 包含 PR）
        issues = [i for i in issues if "pull_request" not in i]
        
        print(f"\n📋 获取到 {len(issues)} 个未解决的 Issue")
        return issues
    
    def parse_issue_info(self, issue: dict) -> dict:
        """
        解析 Issue 信息，提取负责方
        
        Args:
            issue: Issue 数据
            
        Returns:
            解析后的信息
        """
        body = issue.get("body", "")
        title = issue.get("title", "")
        
        # 提取负责方
        provider = None
        
        # 尝试从表格中提取
        if "负责方" in body:
            for line in body.split("\n"):
                if "负责方" in line and "@" in line:
                    # 提取 @xxx-agent
                    import re
                    match = re.search(r"@([\w-]+-agent)", line)
                    if match:
                        provider = match.group(1)
                        break
        
        # 尝试从标题中提取
        if not provider:
            import re
            match = re.search(r"@([\w-]+-agent)", title)
            if match:
                provider = match.group(1)
        
        # 反向查找 Agent ID
        agent_id = None
        if provider:
            for aid, github_name in AGENT_GITHUB.items():
                if github_name == provider:
                    agent_id = aid
                    break
        
        return {
            "issue_number": issue["number"],
            "title": title,
            "created_at": issue["created_at"],
            "labels": [l["name"] for l in issue.get("labels", [])],
            "provider_github": provider,
            "provider_id": agent_id,
            "url": issue["html_url"]
        }
    
    def determine_responsible_agent(self, issue_info: dict) -> Optional[str]:
        """
        根据 Issue 内容确定负责的 Agent
        
        Args:
            issue_info: Issue 信息
            
        Returns:
            Agent ID
        """
        # 如果已经提取到负责方，直接使用
        if issue_info["provider_id"]:
            return issue_info["provider_id"]
        
        # 否则根据关键词匹配
        title = issue_info["title"].lower()
        labels = " ".join(issue_info["labels"]).lower()
        
        for agent_id, keywords in AGENT_RESPONSIBILITIES.items():
            for keyword in keywords:
                if keyword.lower() in title or keyword.lower() in labels:
                    print(f"  匹配到负责 Agent: {agent_id} (关键词：{keyword})")
                    return agent_id
        
        # 默认返回 coordinator
        print(f"  未匹配到具体 Agent，默认分配给 coordinator")
        return "coordinator"
    
    def notify_agent(self, agent_id: str, issue_info: dict):
        """
        通知负责 Agent
        
        Args:
            agent_id: Agent ID
            issue_info: Issue 信息
        """
        github_name = AGENT_GITHUB.get(agent_id, agent_id)
        
        print(f"\n🔔 通知 {github_name}:")
        print(f"   Issue: #{issue_info['issue_number']}")
        print(f"   标题：{issue_info['title']}")
        print(f"   链接：{issue_info['url']}")
        
        # 实际应用中，这里可以：
        # 1. 在 Issue 中添加评论 @agent
        # 2. 发送消息到聊天工具
        # 3. 调用 Agent 的任务系统
        
        # 示例：在 Issue 中添加评论
        comment = f"""
## 🤖 自动通知

@{github_name} 你好！

这个改进工单已分配给你，请处理：

### 📋 处理流程
1. 确认接收任务
2. 创建 Branch: `fix/issue-{issue_info['issue_number']}`
3. 解决问题
4. 创建 PR: 关联此 Issue (`Closes #{issue_info['issue_number']}`)
5. Code Review
6. Merge 关闭

---
*此消息由自动化系统发送*
"""
        
        try:
            self._request(
                "POST",
                f"issues/{issue_info['issue_number']}/comments",
                {"body": comment}
            )
            print(f"   ✅ 评论已添加")
        except Exception as e:
            print(f"   ❌ 添加评论失败：{e}")
    
    def track_pr_status(self, issue_number: int) -> Optional[dict]:
        """
        跟踪关联的 PR 状态
        
        Args:
            issue_number: Issue 编号
            
        Returns:
            PR 信息或 None
        """
        try:
            # 获取关联的 PR
            prs = self._request("GET", f"issues/{issue_number}/pull_requests")
            
            if prs:
                pr = prs[0]
                print(f"\n🔀 关联 PR 状态:")
                print(f"   PR: #{pr['number']}")
                print(f"   状态：{pr['state']}")
                print(f"   链接：{pr['html_url']}")
                return pr
        except Exception as e:
            print(f"   ❌ 获取 PR 状态失败：{e}")
        
        return None
    
    def auto_merge_pr(self, pr_number: int):
        """
        自动合并 PR（如果满足条件）
        
        Args:
            pr_number: PR 编号
        """
        try:
            # 检查 PR 状态
            pr = self._request("GET", f"pulls/{pr_number}")
            
            if pr["state"] != "open":
                print(f"   PR 已关闭，跳过")
                return
            
            # 检查是否可合并
            if pr["mergeable"] is None:
                print(f"   PR 还在检查中，稍后重试")
                return
            
            if not pr["mergeable"]:
                print(f"   PR 有冲突，需要手动解决")
                return
            
            # 检查 CI 状态
            # TODO: 添加 CI 状态检查
            
            # 合并 PR
            print(f"   正在合并 PR...")
            self._request("PUT", f"pulls/{pr_number}/merge", {
                "merge_method": "squash",
                "commit_title": f"Merge PR #{pr_number}"
            })
            
            print(f"   ✅ PR 已合并")
            
        except Exception as e:
            print(f"   ❌ 合并失败：{e}")
    
    def process_issues(self, auto_merge: bool = False):
        """
        处理所有未解决的 Issue
        
        Args:
            auto_merge: 是否自动合并 PR
        """
        print("=" * 60)
        print("🚀 Issue 自动跟踪和分配")
        print("=" * 60)
        
        # 获取未解决的改进工单
        issues = self.get_open_issues(labels=["improvement-ticket"])
        
        if not issues:
            print("\n✅ 没有未解决的改进工单！")
            return
        
        # 处理每个 Issue
        for issue in issues:
            print(f"\n{'='*60}")
            print(f"处理 Issue #{issue['number']}: {issue['title']}")
            print(f"{'='*60}")
            
            # 解析 Issue 信息
            issue_info = self.parse_issue_info(issue)
            
            # 确定负责 Agent
            agent_id = self.determine_responsible_agent(issue_info)
            
            # 通知 Agent
            self.notify_agent(agent_id, issue_info)
            
            # 跟踪 PR 状态
            pr = self.track_pr_status(issue_info["issue_number"])
            
            # 如果 PR 已就绪，自动合并
            if pr and auto_merge:
                if pr["state"] == "open" and pr.get("mergeable"):
                    # 检查是否有 Review 批准
                    # TODO: 添加 Review 检查
                    self.auto_merge_pr(pr["number"])
            
            # 等待一下，避免 API 限流
            import time
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print("✅ Issue 处理完成！")
        print(f"{'='*60}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Issue 自动跟踪和分配脚本")
    parser.add_argument(
        "--auto-merge",
        action="store_true",
        help="自动合并满足条件的 PR"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅显示，不执行实际操作"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 Dry Run 模式 - 仅显示，不执行实际操作\n")
    
    tracker = IssueTracker()
    
    if not args.dry_run:
        tracker.process_issues(auto_merge=args.auto_merge)
    else:
        # Dry run: 只显示信息
        issues = tracker.get_open_issues(labels=["improvement-ticket"])
        for issue in issues:
            issue_info = tracker.parse_issue_info(issue)
            agent_id = tracker.determine_responsible_agent(issue_info)
            print(f"\nIssue #{issue['number']}: {issue['title']}")
            print(f"  负责 Agent: {AGENT_GITHUB.get(agent_id, agent_id)}")
            print(f"  链接：{issue['html_url']}")


if __name__ == "__main__":
    main()
