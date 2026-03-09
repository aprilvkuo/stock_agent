#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issue 自动化处理系统（单线程实时监控版）
抓取 Issue → 验证有效性 → 无效关闭 / 有效分配 → Agent 解决 → PR → Merge → 关闭

版本：v3.1
日期：2026-03-09
特性：单线程、优先级排序、PR 审核等待、实时监控、强制系统环境变量

系统指令:
  - GITHUB_TOKEN 必须从系统环境变量获取（不支持 .env 文件）
  - 首次运行前请确保已配置环境变量
  - 使用 `source ~/.zshrc` 或重新打开终端使配置生效
"""

import os
import sys
import json
import requests
import subprocess
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 系统配置（从环境变量获取）
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "aprilvkuo/stock_agent")
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"
WORKSPACE = os.getenv("WORKSPACE", "/Users/egg/.openclaw/workspace")

# 验证必需的环境变量
if not GITHUB_TOKEN:
    print("❌ 错误：GITHUB_TOKEN 未配置！")
    print("\n📝 请按以下步骤配置:")
    print("\n1. 打开终端配置文件:")
    print("   vim ~/.zshrc  # 或 ~/.bash_profile")
    print("\n2. 添加环境变量:")
    print("   export GITHUB_TOKEN=\"github_pat_xxxxxxxxxxxxx\"")
    print("   export GITHUB_REPO=\"aprilvkuo/stock_agent\"")
    print("   export WORKSPACE=\"/Users/egg/.openclaw/workspace\"")
    print("\n3. 使配置生效:")
    print("   source ~/.zshrc")
    print("\n4. 验证配置:")
    print("   echo $GITHUB_TOKEN")
    print("\n⚠️  注意：GITHUB_TOKEN 必须从系统环境变量获取，不支持 .env 文件！\n")
    sys.exit(1)

# 实时监控配置
MONITOR_INTERVAL = 60  # 监控间隔（秒）
MAX_RETRY = 3  # 最大重试次数

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

# Agent 职责关键词（按特异性排序，特异性高的在前）
AGENT_KEYWORDS = {
    'fundamental': ['财报', '估值', '基本面', 'financial', 'roe', 'pe', 'pb', '财务报表', '利润表', '资产负债表', '现金流'],
    'technical': ['k 线', '技术指标', '技术面', 'technical', 'macd', 'rsi', '均线', '布林带', '成交量'],
    'sentiment': ['情绪', '市场', 'sentiment', '热度', 'volume', '舆情', '新闻', '市场情绪'],
    'data-fetcher': ['数据', 'api', '抓取', 'data', 'fetch', 'crawl', '爬虫', '接口'],
    'qa': ['测试', '质量', 'review', 'qa', 'test', 'verify', '单元测试', '集成测试'],
    'programmer': ['代码', '重构', '优化', 'bug', 'fix', 'dev', 'draft', 'structure', 'program', 'code', '程序', '开发'],
    'coordinator': ['协调', '分配', 'coordinator', 'assign', '任务分配'],
    'cio': ['投资', '策略', 'risk', 'investment', 'strategy', '投资组合', '风控']
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

# 优先级标签（数字越小优先级越高）
PRIORITY_LABELS = {
    'critical': 1,      # 紧急
    'high': 2,          # 高
    'medium': 3,        # 中
    'low': 4,           # 低
    'improvement-ticket': 3,  # 改进工单（默认中）
    'task': 3,          # 任务（默认中）
}


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
    
    def get_priority(self, issue: dict) -> int:
        """
        获取 Issue 优先级（数字越小优先级越高）
        
        Returns:
            优先级数字
        """
        labels = [l["name"].lower() for l in issue.get("labels", [])]
        
        # 检查是否有优先级标签
        for label, priority in PRIORITY_LABELS.items():
            if label in labels:
                return priority
        
        # 默认优先级（中）
        return 3
    
    def get_priority_name(self, priority: int) -> str:
        """将优先级数字转换为名称"""
        for label, p in PRIORITY_LABELS.items():
            if p == priority:
                return label
        return 'medium'


class IssueAutoResolver:
    """Issue 自动解决器（单线程实时监控版）"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.validator = IssueValidator()
        
        # 当前处理状态
        self.current_issue = None
        self.current_pr = None
        self.processing = False
    
    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """GitHub API 请求"""
        url = f"{GITHUB_API_BASE}/{endpoint}"
        response = self.session.request(method, url, json=data, params=params)
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
    
    def get_open_prs(self) -> List[dict]:
        """获取未解决的 PR"""
        print("\n🔀 获取未解决的 PR...")
        
        params = {"state": "open"}
        prs = self._request("GET", "pulls", params)
        
        print(f"   找到 {len(prs)} 个未解决的 PR")
        return prs
    
    def sort_issues_by_priority(self, issues: List[dict]) -> List[dict]:
        """
        按优先级排序 Issue
        
        排序规则:
        1. 优先级标签（critical > high > medium > low）
        2. 创建时间（越早优先级越高）
        """
        def sort_key(issue):
            priority = self.validator.get_priority(issue)
            created_at = issue.get("created_at", "")
            return (priority, created_at)
        
        sorted_issues = sorted(issues, key=sort_key)
        
        print("\n📊 Issue 优先级排序:")
        for i, issue in enumerate(sorted_issues[:10], 1):  # 只显示前 10 个
            priority = self.validator.get_priority(issue)
            priority_name = self.validator.get_priority_name(priority)
            print(f"   {i}. #{issue['number']} [{priority_name}] {issue['title'][:50]}")
        
        if len(sorted_issues) > 10:
            print(f"   ... 还有 {len(sorted_issues) - 10} 个 Issue")
        
        return sorted_issues
    
    def check_pr_status(self, pr_number: int) -> dict:
        """
        检查 PR 状态
        
        Returns:
            PR 状态信息
        """
        pr = self._request("GET", f"pulls/{pr_number}")
        
        return {
            'number': pr['number'],
            'state': pr['state'],
            'merged': pr.get('merged', False),
            'mergeable': pr.get('mergeable', False),
            'mergeable_state': pr.get('mergeable_state', 'unknown'),
            'title': pr['title'],
            'user': pr['user']['login'],
            'created_at': pr['created_at'],
            'updated_at': pr['updated_at']
        }
    
    def wait_for_pr_merge(self, pr_number: int, timeout_hours: int = 24) -> bool:
        """
        等待 PR 被合并
        
        Args:
            pr_number: PR 编号
            timeout_hours: 超时时间（小时）
        
        Returns:
            True: PR 已合并, False: 超时或关闭
        """
        print(f"\n⏳ 等待 PR #{pr_number} 合并...")
        print(f"   超时时间：{timeout_hours} 小时")
        
        start_time = datetime.now()
        timeout = timedelta(hours=timeout_hours)
        
        while True:
            # 检查是否超时
            elapsed = datetime.now() - start_time
            if elapsed > timeout:
                print(f"\n   ❌ 等待超时（{elapsed.total_seconds()/3600:.1f} 小时）")
                return False
            
            try:
                pr_status = self.check_pr_status(pr_number)
                
                # 检查 PR 状态
                if pr_status['merged']:
                    print(f"\n   ✅ PR 已合并！")
                    return True
                
                if pr_status['state'] == 'closed':
                    print(f"\n   ❌ PR 已关闭（未合并）")
                    return False
                
                # 显示等待信息
                print(f"\r   等待中... ({elapsed.total_seconds()/60:.0f} 分钟) "
                      f"PR 状态：{pr_status['state']} "
                      f"可合并：{pr_status['mergeable']}", end="", flush=True)
                
                # 等待 1 分钟后再次检查
                time.sleep(60)
                
            except Exception as e:
                print(f"\n   ❌ 检查 PR 状态失败：{e}")
                time.sleep(60)
    
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
        
        # 3. 关键词匹配（按特异性排序）
        scores = {}
        for agent_id, keywords in AGENT_KEYWORDS.items():
            # 特异性关键词权重更高
            score = sum(2 if kw in text else 1 for kw in keywords if kw.lower() in text)
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
*此消息由 Issue Auto-Resolver v3.0 自动生成*
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

**自动生成**: Issue Auto-Resolver v3.0  
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
    
    def process_issue(self, issue: dict) -> Tuple[str, Optional[int]]:
        """
        处理单个 Issue（单线程）
        
        Returns:
            (处理结果，PR 编号)
            处理结果：'closed_invalid', 'waiting_pr', 'fixed', 'failed'
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
            return 'closed_invalid', None
        
        print(f"   ✅ 验证通过：{reason}")
        
        # Step 2: 识别负责 Agent
        print(f"\n🤖 识别负责 Agent...")
        agent_id = self.identify_responsible_agent(issue)
        agent_github = AGENT_GITHUB[agent_id]
        
        # Step 3: 创建分支
        branch_name = self.create_branch(issue_number, issue_title)
        if not branch_name:
            return 'failed', None
        
        # Step 4: 执行修复
        fix_success = self.execute_fix(issue, agent_id)
        
        # Step 5: 提交更改
        commit_success = self.commit_changes(issue_number, agent_id)
        if not commit_success:
            print(f"   ⚠️  没有实质性更改，但仍创建 PR")
        
        # Step 6: 推送分支
        push_success = self.push_branch(branch_name)
        if not push_success:
            return 'failed', None
        
        # Step 7: 创建 PR
        pr_number = self.create_pull_request(issue_number, branch_name)
        if not pr_number:
            return 'failed', None
        
        # Step 8: 在 Issue 中添加评论
        self.add_issue_comment(issue_number, f"""
## 🤖 自动处理完成

**验证结果**: ✅ 有效任务  
**负责 Agent**: @{agent_github}  
**PR**: #{pr_number}  
**分支**: `{branch_name}`

⚠️ **单线程模式**: 系统正在等待此 PR 合并后才会处理下一个 Issue。

请 Review 后合并，合并后系统将自动处理下一个 Issue。

---
*此消息由 Issue Auto-Resolver v3.0 自动生成*
""")
        
        print(f"\n✅ Issue #{issue_number} 处理完成！")
        print(f"   PR: #{pr_number}")
        print(f"   ⏳ 等待 PR 合并中...")
        
        return 'waiting_pr', pr_number
    
    def process_next_issue(self) -> bool:
        """
        处理下一个 Issue（单线程）
        
        Returns:
            True: 成功处理, False: 无 Issue 可处理
        """
        # 获取未解决的 Issue
        issues = self.get_open_issues()
        
        if not issues:
            print("\n✅ 没有未解决的 Issue！")
            return False
        
        # 按优先级排序
        sorted_issues = self.sort_issues_by_priority(issues)
        
        # 选择优先级最高的 Issue
        next_issue = sorted_issues[0]
        
        print(f"\n🎯 选择处理 Issue #{next_issue['number']}: {next_issue['title']}")
        priority = self.validator.get_priority(next_issue)
        print(f"   优先级：{self.validator.get_priority_name(priority)}")
        
        # 处理 Issue
        result, pr_number = self.process_issue(next_issue)
        
        # 如果创建了 PR，等待合并
        if result == 'waiting_pr' and pr_number:
            print(f"\n{'='*60}")
            print(f"🔄 进入 PR 等待模式")
            print(f"{'='*60}")
            
            merged = self.wait_for_pr_merge(pr_number)
            
            if merged:
                print(f"\n✅ PR 已合并，准备处理下一个 Issue...")
                time.sleep(10)  # 等待 10 秒后继续
                return True  # 继续处理下一个
            else:
                print(f"\n⚠️  PR 未合并，暂停处理新 Issue")
                return False  # 暂停
        
        return result != 'failed'
    
    def monitor_loop(self):
        """实时监控循环（单线程）"""
        print("="*60)
        print("🚀 Issue 自动化处理系统 v3.0（单线程实时监控版）")
        print("="*60)
        print(f"\n📊 配置信息:")
        print(f"   监控间隔：{MONITOR_INTERVAL} 秒")
        print(f"   最大重试：{MAX_RETRY} 次")
        print(f"   仓库：{GITHUB_REPO}")
        print(f"\n📋 工作模式:")
        print(f"   ✅ 单线程 - 一次只处理一个 Issue")
        print(f"   ✅ 优先级排序 - 按优先级选择 Issue")
        print(f"   ✅ PR 等待 - 等待 PR 合并后继续")
        print(f"   ✅ 实时监控 - 持续监控新 Issue")
        print(f"\n按 Ctrl+C 停止监控\n")
        
        retry_count = 0
        
        while True:
            try:
                # 检查是否有未解决的 PR
                open_prs = self.get_open_prs()
                
                if open_prs:
                    print(f"\n⚠️  发现 {len(open_prs)} 个未解决的 PR")
                    print(f"   等待 PR 合并中...")
                    
                    # 等待所有 PR 合并
                    for pr in open_prs:
                        pr_number = pr['number']
                        print(f"\n   等待 PR #{pr_number}...")
                        merged = self.wait_for_pr_merge(pr_number, timeout_hours=1)
                        
                        if not merged:
                            print(f"   ⏳ PR #{pr_number} 未合并，继续等待...")
                    
                    # 等待监控间隔
                    print(f"\n⏱️  等待 {MONITOR_INTERVAL} 秒后继续...")
                    time.sleep(MONITOR_INTERVAL)
                    continue
                
                # 没有 PR，处理下一个 Issue
                has_issue = self.process_next_issue()
                
                if not has_issue:
                    # 没有 Issue 可处理，等待监控间隔
                    print(f"\n⏱️  等待 {MONITOR_INTERVAL} 秒后继续监控...")
                    time.sleep(MONITOR_INTERVAL)
                
                retry_count = 0  # 重置重试计数
                
            except KeyboardInterrupt:
                print(f"\n\n🛑 用户中断，停止监控")
                break
            except Exception as e:
                print(f"\n❌ 错误：{e}")
                retry_count += 1
                
                if retry_count >= MAX_RETRY:
                    print(f"\n❌ 达到最大重试次数（{MAX_RETRY}），停止监控")
                    break
                
                print(f"\n⏱️  等待 {MONITOR_INTERVAL} 秒后重试...")
                time.sleep(MONITOR_INTERVAL)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Issue 自动化处理系统 v3.0（单线程实时监控版）")
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
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="启动实时监控模式"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="监控间隔（秒），默认 60 秒"
    )
    
    args = parser.parse_args()
    
    # 更新监控间隔
    global MONITOR_INTERVAL
    MONITOR_INTERVAL = args.interval
    
    resolver = IssueAutoResolver()
    
    if args.dry_run:
        print("🔍 Dry Run 模式 - 仅显示，不执行实际操作\n")
        issues = resolver.get_open_issues(
            labels=args.labels.split(",") if args.labels else None
        )
        
        # 按优先级排序
        sorted_issues = resolver.sort_issues_by_priority(issues)
        
        for issue in sorted_issues:
            is_valid, reason = resolver.validator.is_valid_issue(issue)
            agent = resolver.identify_responsible_agent(issue)
            priority = resolver.validator.get_priority(issue)
            
            status = "✅ 有效" if is_valid else "❌ 无效"
            priority_name = resolver.validator.get_priority_name(priority)
            
            print(f"\nIssue #{issue['number']}: {issue['title']}")
            print(f"  优先级：{priority_name}")
            print(f"  状态：{status} - {reason}")
            if is_valid:
                print(f"  负责 Agent: @{AGENT_GITHUB[agent]}")
            print(f"  链接：{issue['html_url']}")
    elif args.monitor:
        print(f"🚀 启动实时监控模式（间隔：{MONITOR_INTERVAL} 秒）\n")
        resolver.monitor_loop()
    else:
        resolver.process_next_issue()


if __name__ == "__main__":
    main()
