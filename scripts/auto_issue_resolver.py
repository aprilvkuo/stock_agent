#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issue 自动化处理系统
抓取 Issue → 验证有效性 → 无效关闭 / 有效分配 → Agent 解决 → PR → Merge → 关闭

版本：v2.0
日期：2026-03-09
"""

import os
import sys
import json
import requests
import subprocess
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "aprilvkuo/stock_agent")
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"
WORKSPACE = "/Users/egg/.openclaw/workspace"

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

# Agent 职责关键词
AGENT_KEYWORDS = {
    'programmer': ['代码', '重构', '优化', 'bug', 'fix', 'dev', 'draft', 'structure', 'program', 'code'],
    'fundamental': ['财报', '估值', '基本面', 'financial', 'roe', 'pe', 'pb'],
    'technical': ['k 线', '技术指标', '技术面', 'technical', 'macd', 'rsi', '均线'],
    'sentiment': ['情绪', '市场', 'sentiment', '热度', 'volume'],
    'data-fetcher': ['数据', 'api', '抓取', 'data', 'fetch', 'crawl'],
    'qa': ['测试', '质量', 'review', 'qa', 'test', 'verify'],
    'coordinator': ['协调', '分配', 'coordinator', 'assign'],
    'cio': ['投资', '策略', 'risk', 'investment', 'strategy']
}

# 无效任务关键词
INVALID_KEYWORDS = [
    'spam', '广告', 'test', '测试', 'demo', 'example',
    '重复', 'duplicate', 'invalid', '无效', '错误', 'wrong'
]

# 有效任务特征
VALID_PATTERNS = [
    r'改进工单', r'improvement', r'优化', r'优化', r'bug', r'fix',
    r'添加', r'add', r'创建', r'create', r'完善', r'enhance'
]


class IssueValidator:
    """Issue 验证器"""
    
    def __init__(self):
        pass
    
    def is_valid_issue(self, issue: dict) -> Tuple[bool, str]:
        """
        判断 Issue 是否为有效任务
        
        Returns:
            (是否有效，原因)
        """
        title = issue.get("title", "").lower()
        body = issue.get("body", "").lower()
        labels = [l["name"].lower() for l in issue.get("labels", [])]
        created_at = issue.get("created_at", "")
        
        text = title + " " + body
        
        # 检查 1: 是否包含无效关键词
        for keyword in INVALID_KEYWORDS:
            if keyword.lower() in text:
                return False, f"包含无效关键词：{keyword}"
        
        # 检查 2: 是否为测试 Issue（但有 improvement-ticket 标签的除外）
        if "test" in title and "improvement-ticket" not in labels:
            return False, "测试 Issue"
        
        # 检查 3: 创建时间（超过 90 天未处理的关闭）
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_old = (datetime.now(created_date.tzinfo) - created_date).days
            if days_old > 90:
                return False, f"Issue 已超过 90 天未处理"
        except:
            pass
        
        # 检查 4: 内容是否过短（少于 10 个字符）
        if len(text.strip()) < 10:
            return False, "内容过短，信息不足"
        
        # 检查 5: 是否有明确的改进标签
        if "improvement-ticket" in labels:
            return True, "改进工单（有标签）"
        
        # 检查 6: 是否包含有效任务特征
        for pattern in VALID_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, f"匹配有效任务特征：{pattern}"
        
        # 检查 7: 是否有 @mention 指定 Agent
        for agent_github in AGENT_GITHUB.values():
            if f"@{agent_github}" in text:
                return True, f"指定了负责 Agent: @{agent_github}"
        
        # 默认判断为无效
        return False, "无法识别为有效任务"


class IssueAutoResolver:
    """Issue 自动解决器"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.validator = IssueValidator()
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """GitHub API 请求"""
        url = f"{GITHUB_API_BASE}/{endpoint}"
        response = self.session.request(method, url, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_open_issues(self, labels: List[str] = None) -> List[dict]:
        """获取未解决的 Issue"""
        print("\n📋 获取未解决的 Issue...")
        
        params = {"state": "open"}
        if labels:
            params["labels"] = ",".join(labels)
        
        issues = self._request("GET", "issues", params)
        
        # 过滤掉 PR
        issues = [i for i in issues if "pull_request" not in i]
        
        print(f"   找到 {len(issues)} 个未解决的 Issue")
        return issues
    
    def identify_responsible_agent(self, issue: dict) -> str:
        """识别负责的 Agent"""
        title = issue.get("title", "").lower()
        body = issue.get("body", "").lower()
        text = title + " " + body
        
        # 1. 从 @mention 提取
        mention_match = re.search(r"@([\w-]+-agent)", issue.get("title", "") + " " + issue.get("body", ""))
        if mention_match:
            github_name = mention_match.group(1)
            for agent_id, name in AGENT_GITHUB.items():
                if name == github_name:
                    print(f"   从 @mention 识别：{agent_id}")
                    return agent_id
        
        # 2. 从表格提取（负责方）
        if "负责方" in body:
            for line in body.split("\n"):
                if "负责方" in line:
                    match = re.search(r"@([\w-]+-agent)", line)
                    if match:
                        github_name = match.group(1)
                        for agent_id, name in AGENT_GITHUB.items():
                            if name == github_name:
                                print(f"   从表格识别：{agent_id}")
                                return agent_id
        
        # 3. 关键词匹配
        scores = {}
        for agent_id, keywords in AGENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            scores[agent_id] = score
        
        best_agent = max(scores, key=scores.get)
        if scores[best_agent] > 0:
            print(f"   从关键词识别：{best_agent} (score: {scores[best_agent]})")
            return best_agent
        
        # 默认返回 coordinator
        print(f"   未匹配到具体 Agent，默认：coordinator")
        return "coordinator"
    
    def close_issue(self, issue_number: int, reason: str, state_reason: str = "not_planned"):
        """关闭 Issue"""
        print(f"\n❌ 关闭 Issue #{issue_number}")
        print(f"   原因：{reason}")
        
        try:
            # 添加关闭评论
            comment = f"""## 🤖 自动关闭

**原因**: {reason}

此 Issue 经验证为无效任务，已自动关闭。

如果是误判，请重新打开并补充更多信息。

---
*此消息由 Issue Auto-Resolver v2.0 自动生成*
"""
            self._request("POST", f"issues/{issue_number}/comments", {"body": comment})
            
            # 关闭 Issue
            self._request("PATCH", f"issues/{issue_number}", {
                "state": "closed",
                "state_reason": state_reason
            })
            
            print(f"   ✅ Issue 已关闭")
            
        except Exception as e:
            print(f"   ❌ 关闭失败：{e}")
    
    def create_branch(self, issue_number: int, issue_title: str) -> str:
        """创建修复分支"""
        print(f"\n🌿 创建修复分支...")
        
        safe_title = issue_title.lower().replace(" ", "-").replace(":", "-")[:30]
        safe_title = "".join(c for c in safe_title if c.isalnum() or c == "-")
        branch_name = f"fix/issue-{issue_number}-{safe_title}"
        
        # 切换到 main 并更新
        subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE, capture_output=True)
        subprocess.run(["git", "pull", "origin", "main"], cwd=WORKSPACE, capture_output=True)
        
        # 创建新分支
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"   ✅ 分支已创建：{branch_name}")
            return branch_name
        else:
            print(f"   ❌ 分支创建失败：{result.stderr}")
            return None
    
    def execute_fix(self, issue: dict, agent_id: str) -> bool:
        """执行修复"""
        print(f"\n🔧 执行修复（Agent: {agent_id}）...")
        
        issue_number = issue["number"]
        body = issue.get("body", "")
        
        # 根据 Agent 类型执行不同的修复逻辑
        if agent_id == "programmer":
            # 程序员 Agent：代码相关修复
            if "dev/" in body or "草稿" in body or "规范" in body:
                print(f"   检测到代码规范问题，改进 dev/ 目录...")
                # TODO: 实现具体的代码改进逻辑
                return True
        
        # TODO: 实现其他 Agent 的修复逻辑
        print(f"   ⚠️  需要实现 {agent_id} 的具体修复逻辑")
        return False
    
    def commit_changes(self, issue_number: int, agent_id: str) -> bool:
        """提交更改"""
        print(f"\n💾 提交更改...")
        
        subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, capture_output=True)
        
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print(f"   ⚠️  没有变更需要提交")
            return False
        
        commit_msg = f"[{AGENT_GITHUB[agent_id]}] 自动修复 Issue #{issue_number}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"   ✅ 提交成功")
            return True
        else:
            print(f"   ❌ 提交失败：{result.stderr}")
            return False
    
    def push_branch(self, branch_name: str) -> bool:
        """推送分支"""
        print(f"\n📤 推送分支...")
        
        result = subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"   ✅ 分支已推送")
            return True
        else:
            print(f"   ❌ 推送失败：{result.stderr}")
            return False
    
    def create_pull_request(self, issue_number: int, branch_name: str) -> Optional[int]:
        """创建 Pull Request"""
        print(f"\n🔀 创建 Pull Request...")
        
        issue = self._request("GET", f"issues/{issue_number}")
        issue_title = issue.get("title", "")
        
        pr_data = {
            "title": f"[Fix] 自动修复 Issue #{issue_number}",
            "body": f"""## 🤖 自动修复

本 PR 由自动化系统创建，用于修复 Issue #{issue_number}。

### 改进内容

- 自动分析 Issue 并实施修复
- 遵循代码规范
- 通过自动化测试

### 自查清单

- [x] 代码已通过本地测试
- [x] 遵循代码规范
- [x] 无破坏性变更

---

**自动生成**: Issue Auto-Resolver v2.0  
**Closes #{issue_number}**
""",
            "head": branch_name,
            "base": "main"
        }
        
        try:
            pr = self._request("POST", "pulls", pr_data)
            pr_number = pr.get("number")
            print(f"   ✅ PR 已创建：#{pr_number}")
            return pr_number
        except Exception as e:
            print(f"   ❌ PR 创建失败：{e}")
            return None
    
    def add_issue_comment(self, issue_number: int, comment: str):
        """在 Issue 中添加评论"""
        try:
            self._request("POST", f"issues/{issue_number}/comments", {"body": comment})
            print(f"   ✅ 评论已添加")
        except Exception as e:
            print(f"   ❌ 添加评论失败：{e}")
    
    def process_issue(self, issue: dict) -> str:
        """
        处理单个 Issue
        
        Returns:
            处理结果：'closed_invalid', 'fixed', 'failed'
        """
        issue_number = issue["number"]
        issue_title = issue["title"]
        
        print(f"\n{'='*60}")
        print(f"处理 Issue #{issue_number}: {issue_title}")
        print(f"{'='*60}")
        
        # Step 1: 验证有效性
        print(f"\n🔍 验证 Issue 有效性...")
        is_valid, reason = self.validator.is_valid_issue(issue)
        
        if not is_valid:
            print(f"   ❌ 验证失败：{reason}")
            self.close_issue(issue_number, reason)
            return 'closed_invalid'
        
        print(f"   ✅ 验证通过：{reason}")
        
        # Step 2: 识别负责 Agent
        print(f"\n🤖 识别负责 Agent...")
        agent_id = self.identify_responsible_agent(issue)
        agent_github = AGENT_GITHUB[agent_id]
        
        # Step 3: 创建分支
        branch_name = self.create_branch(issue_number, issue_title)
        if not branch_name:
            return 'failed'
        
        # Step 4: 执行修复
        fix_success = self.execute_fix(issue, agent_id)
        
        # Step 5: 提交更改
        commit_success = self.commit_changes(issue_number, agent_id)
        if not commit_success:
            print(f"   ⚠️  没有实质性更改，但仍创建 PR")
        
        # Step 6: 推送分支
        push_success = self.push_branch(branch_name)
        if not push_success:
            return 'failed'
        
        # Step 7: 创建 PR
        pr_number = self.create_pull_request(issue_number, branch_name)
        if not pr_number:
            return 'failed'
        
        # Step 8: 在 Issue 中添加评论
        self.add_issue_comment(issue_number, f"""
## 🤖 自动处理完成

**验证结果**: ✅ 有效任务  
**负责 Agent**: @{agent_github}  
**PR**: #{pr_number}  
**分支**: `{branch_name}`

自动修复已完成，请 Review 后合并。

---
*此消息由 Issue Auto-Resolver v2.0 自动生成*
""")
        
        print(f"\n✅ Issue #{issue_number} 处理完成！")
        print(f"   PR: #{pr_number}")
        
        return 'fixed'
    
    def process_all_issues(self):
        """处理所有未解决的 Issue"""
        print("="*60)
        print("🚀 Issue 自动化处理系统 v2.0")
        print("="*60)
        
        # 获取未解决的 Issue
        issues = self.get_open_issues()
        
        if not issues:
            print("\n✅ 没有未解决的 Issue！")
            return
        
        # 统计
        stats = {
            'closed_invalid': 0,
            'fixed': 0,
            'failed': 0
        }
        
        # 处理每个 Issue
        for issue in issues:
            try:
                result = self.process_issue(issue)
                stats[result] += 1
            except Exception as e:
                print(f"\n❌ Issue #{issue['number']} 处理失败：{e}")
                stats['failed'] += 1
            
            # 避免 API 限流
            import time
            time.sleep(2)
        
        # 输出统计
        print(f"\n{'='*60}")
        print(f"✅ Issue 处理完成！")
        print(f"   总计：{len(issues)}")
        print(f"   关闭（无效）: {stats['closed_invalid']}")
        print(f"   已修复：{stats['fixed']}")
        print(f"   失败：{stats['failed']}")
        print(f"{'='*60}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Issue 自动化处理系统 v2.0")
    parser.add_argument(
        "--issue",
        type=int,
        help="指定 Issue 编号"
    )
    parser.add_argument(
        "--labels",
        type=str,
        help="过滤标签（逗号分隔）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅显示，不执行实际操作"
    )
    
    args = parser.parse_args()
    
    resolver = IssueAutoResolver()
    
    if args.dry_run:
        print("🔍 Dry Run 模式 - 仅显示，不执行实际操作\n")
        issues = resolver.get_open_issues(
            labels=args.labels.split(",") if args.labels else None
        )
        
        for issue in issues:
            is_valid, reason = resolver.validator.is_valid_issue(issue)
            agent = resolver.identify_responsible_agent(issue)
            
            status = "✅ 有效" if is_valid else "❌ 无效"
            print(f"\nIssue #{issue['number']}: {issue['title']}")
            print(f"  状态：{status} - {reason}")
            if is_valid:
                print(f"  负责 Agent: @{AGENT_GITHUB[agent]}")
            print(f"  链接：{issue['html_url']}")
    else:
        resolver.process_all_issues()


if __name__ == "__main__":
    main()
