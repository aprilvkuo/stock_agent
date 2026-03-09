#!/usr/bin/env python3
"""
Git 版本控制模块 - 记录每个 Agent 的重大更新
标准流程：add -> config user -> commit -> push
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

# Agent Git User 映射
AGENT_GIT_USERS = {
    "技术 Agent": ("技术 Agent", "tech-agent@stock-system.local"),
    "情绪 Agent": ("情绪 Agent", "emotion-agent@stock-system.local"),
    "资金 Agent": ("fund-agent@stock-system.local"),
    "估值 Agent": ("valuation-agent@stock-system.local"),
    "协调 Agent": ("coordinator@stock-system.local"),
    "系统 Agent": ("系统 Agent", "system-agent@stock-system.local"),
    "auto_agent.py": ("系统 Agent", "system-agent@stock-system.local"),
    "task_assigner.py": ("协调 Agent", "coordinator@stock-system.local"),
    "feedback_report.py": ("系统 Agent", "system-agent@stock-system.local"),
    "improvement_ticket.py": ("系统 Agent", "system-agent@stock-system.local"),
    "agent_rating.py": ("系统 Agent", "system-agent@stock-system.local"),
}

class GitVersionControl:
    """Git 版本控制器"""
    
    def __init__(self, repo_path: str = None):
        """初始化 Git 控制器"""
        if repo_path is None:
            repo_path = Path(__file__).parent
        self.repo_path = Path(repo_path)
        self.log_file = self.repo_path / ".git-commits.json"
        self.commits_log = self._load_commits_log()
    
    def _load_commits_log(self) -> list:
        """加载提交历史记录"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_commits_log(self):
        """保存提交历史记录"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.commits_log, f, ensure_ascii=False, indent=2)
    
    def _run_git(self, *args, check=True):
        """运行 Git 命令"""
        result = subprocess.run(
            ['git'] + list(args),
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    
    def commit(self, agent_name: str, message: str, files: list = None, auto_push: bool = True):
        """
        提交重大更新
        
        Args:
            agent_name: Agent 名称（用于设置 Git user）
            message: 提交信息
            files: 指定文件列表（None 表示 add -A）
            auto_push: 是否自动 push
        """
        try:
            # 1. 获取 Agent Git User
            git_user = AGENT_GIT_USERS.get(agent_name, (agent_name, f"{agent_name.lower()}@stock-system.local"))
            
            # 2. 添加文件
            if files:
                self._run_git('add', *files)
            else:
                self._run_git('add', '-A')
            
            # 3. 配置 Git User
            self._run_git('config', 'user.name', git_user[0])
            self._run_git('config', 'user.email', git_user[1])
            
            # 4. 检查是否有变更
            status = self._run_git('status', '--porcelain')
            if not status.stdout.strip():
                print(f"[Git] 无变更，跳过提交")
                return None
            
            # 5. 提交
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"[{agent_name}] {timestamp} - {message}"
            commit_result = self._run_git('commit', '-m', commit_msg)
            
            # 6. 获取 commit hash
            commit_hash = self._run_git('rev-parse', 'HEAD').stdout.strip()
            
            # 7. Push（可选）
            push_result = None
            if auto_push:
                try:
                    push_result = self._run_git('push', 'origin', 'main', check=False)
                except Exception as e:
                    print(f"[Git] Push 失败：{e}")
                    push_result = None
            
            # 8. 记录提交历史
            commit_record = {
                "hash": commit_hash,
                "agent": agent_name,
                "message": message,
                "timestamp": timestamp,
                "files": files,
                "pushed": push_result is not None and push_result.returncode == 0
            }
            self.commits_log.append(commit_record)
            self._save_commits_log()
            
            print(f"[Git] ✅ 提交成功：{commit_hash[:8]} by {agent_name}")
            if push_result and push_result.returncode == 0:
                print(f"[Git] 📤 Push 成功")
            
            return commit_record
            
        except subprocess.CalledProcessError as e:
            print(f"[Git] ❌ 提交失败：{e}")
            print(f"stderr: {e.stderr}")
            return None
        except Exception as e:
            print(f"[Git] ❌ 异常：{e}")
            return None
    
    def get_history(self, limit: int = 10, agent: str = None):
        """
        获取提交历史
        
        Args:
            limit: 返回数量
            agent: 过滤特定 Agent
        """
        history = self.commits_log
        if agent:
            history = [h for h in history if h.get('agent') == agent]
        return history[-limit:]
    
    def show_history(self, limit: int = 10, agent: str = None):
        """显示提交历史"""
        history = self.get_history(limit, agent)
        if not history:
            print("📭 暂无提交记录")
            return
        
        print(f"\n📜 最近 {len(history)} 条提交记录:\n")
        print("=" * 80)
        for record in reversed(history):
            agent = record.get('agent', 'Unknown')
            msg = record.get('message', '')
            ts = record.get('timestamp', '')
            hash_val = record.get('hash', '')[:8]
            pushed = "📤" if record.get('pushed') else "💾"
            
            print(f"{pushed} [{ts}] {agent}")
            print(f"   {hash_val}: {msg}")
            print("-" * 80)


# 便捷函数
def git_commit(agent_name: str, message: str, files: list = None, auto_push: bool = True):
    """便捷提交函数"""
    git = GitVersionControl()
    return git.commit(agent_name, message, files, auto_push)

def git_history(limit: int = 10, agent: str = None):
    """查看提交历史"""
    git = GitVersionControl()
    git.show_history(limit, agent)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 git_version_control.py <command> [args]")
        print("命令:")
        print("  history [limit] [agent]  - 查看提交历史")
        print("  test                     - 测试提交")
        sys.exit(1)
    
    cmd = sys.argv[1]
    git = GitVersionControl()
    
    if cmd == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        agent = sys.argv[3] if len(sys.argv) > 3 else None
        git.show_history(limit, agent)
    
    elif cmd == "test":
        # 测试提交
        record = git.commit("系统 Agent", "测试 Git 版本控制功能", auto_push=False)
        if record:
            print(f"\n测试成功！Commit: {record['hash'][:8]}")
    
    else:
        print(f"未知命令：{cmd}")
        sys.exit(1)
