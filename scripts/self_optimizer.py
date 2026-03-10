#!/usr/bin/env python3
"""
系统自优化脚本 - 持续监控和优化股票多 Agent 系统

功能：
1. 清理临时文件和缓存
2. 检查并合并冗余文件
3. 优化项目结构
4. 生成性能报告
5. 自动提交优化结果

运行方式：
    python3 scripts/self_optimizer.py [--dry-run]
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
LOGS_DIR = BASE_DIR / "analysis-log"
EXEC_LOGS_DIR = BASE_DIR / "execution-logs"
REPORTS_DIR = BASE_DIR / "reports"

class SelfOptimizer:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.stats = {
            "cleaned_files": 0,
            "cleaned_size": 0,
            "optimized_scripts": 0,
            "git_commits": 0
        }
    
    def run(self):
        """执行完整优化流程"""
        print("=" * 60)
        print("🔧 系统自优化启动")
        print("=" * 60)
        
        # 1. 清理临时文件
        self.cleanup_temp_files()
        
        # 2. 检查冗余脚本
        self.check_redundant_scripts()
        
        # 3. 优化分析日志
        self.optimize_logs()
        
        # 4. 生成性能报告
        self.generate_performance_report()
        
        # 5. Git 提交
        self.git_commit()
        
        # 输出统计
        print("\n" + "=" * 60)
        print("✅ 优化完成！")
        print(f"   清理文件：{self.stats['cleaned_files']} 个")
        print(f"   清理空间：{self.stats['cleaned_size'] / 1024:.2f} KB")
        print(f"   优化脚本：{self.stats['optimized_scripts']} 个")
        print(f"   Git 提交：{self.stats['git_commits']} 次")
        print("=" * 60)
    
    def cleanup_temp_files(self):
        """清理临时文件和缓存"""
        print("\n📦 Step 1: 清理临时文件...")
        
        # 清理 __pycache__
        for pycache in BASE_DIR.rglob("__pycache__"):
            if pycache.is_dir():
                size = sum(f.stat().st_size for f in pycache.rglob("*") if f.is_file())
                if not self.dry_run:
                    shutil.rmtree(pycache)
                self.stats["cleaned_files"] += 1
                self.stats["cleaned_size"] += size
                print(f"   🗑️  清理 __pycache__: {pycache.relative_to(BASE_DIR)} ({size/1024:.2f} KB)")
        
        # 清理备份文件
        for pattern in ["*.backup", "*.bak", "*.old"]:
            for backup_file in BASE_DIR.rglob(pattern):
                if backup_file.is_file():
                    size = backup_file.stat().st_size
                    if not self.dry_run:
                        backup_file.unlink()
                    self.stats["cleaned_files"] += 1
                    self.stats["cleaned_size"] += size
                    print(f"   🗑️  清理备份：{backup_file.relative_to(BASE_DIR)} ({size/1024:.2f} KB)")
        
        # 清理旧版本脚本
        for old_script in BASE_DIR.rglob("*_v[0-9]*.py"):
            if old_script.is_file() and "scripts" in str(old_script):
                size = old_script.stat().st_size
                if not self.dry_run:
                    old_script.unlink()
                self.stats["cleaned_files"] += 1
                self.stats["cleaned_size"] += size
                print(f"   🗑️  清理旧版：{old_script.relative_to(BASE_DIR)} ({size/1024:.2f} KB)")
    
    def check_redundant_scripts(self):
        """检查冗余脚本"""
        print("\n🔍 Step 2: 检查冗余脚本...")
        
        # 查找可能冗余的脚本对
        script_names = {}
        for py_file in SCRIPTS_DIR.glob("*.py"):
            base_name = py_file.stem.split("_v")[0].split("_v")[0]
            if base_name not in script_names:
                script_names[base_name] = []
            script_names[base_name].append(py_file)
        
        for base_name, files in script_names.items():
            if len(files) > 1:
                print(f"   ⚠️  发现冗余：{base_name} ({len(files)} 个版本)")
                for f in files:
                    print(f"      - {f.name}")
    
    def optimize_logs(self):
        """优化日志文件"""
        print("\n📝 Step 3: 优化日志...")
        
        # 检查分析日志数量
        log_files = list(LOGS_DIR.glob("*.md"))
        print(f"   📊 分析日志：{len(log_files)} 个")
        
        # 检查执行日志
        exec_logs = list(EXEC_LOGS_DIR.glob("*.json")) if EXEC_LOGS_DIR.exists() else []
        print(f"   📊 执行日志：{len(exec_logs)} 个")
        
        # 如果日志过多，建议归档
        if len(log_files) > 100:
            print(f"   ⚠️  日志过多，建议归档旧日志")
    
    def generate_performance_report(self):
        """生成性能报告"""
        print("\n📈 Step 4: 生成性能报告...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "system_info": {
                "total_size_mb": self.get_dir_size(BASE_DIR) / (1024 * 1024),
                "script_count": len(list(SCRIPTS_DIR.glob("*.py"))),
                "log_count": len(list(LOGS_DIR.glob("*.md")))
            }
        }
        
        report_path = REPORTS_DIR / f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if not self.dry_run:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"   ✅ 报告已保存：{report_path.relative_to(BASE_DIR)}")
        else:
            print(f"   📄 [Dry-run] 报告将保存至：{report_path.relative_to(BASE_DIR)}")
    
    def get_dir_size(self, path):
        """计算目录大小"""
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total
    
    def git_commit(self):
        """Git 提交优化结果"""
        print("\n📦 Step 5: Git 提交...")
        
        if self.dry_run:
            print("   📄 [Dry-run] 跳过 Git 提交")
            return
        
        try:
            # 检查是否有变更
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                # 有变更，提交
                subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, check=True)
                subprocess.run(
                    ["git", "commit", "-m", "🤖 系统自优化 - " + datetime.now().strftime("%Y-%m-%d %H:%M")],
                    cwd=BASE_DIR,
                    check=True,
                    capture_output=True
                )
                self.stats["git_commits"] = 1
                print("   ✅ Git 提交成功")
            else:
                print("   ⏭️  无变更，跳过提交")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Git 操作失败：{e}")
        except Exception as e:
            print(f"   ⚠️  错误：{e}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    optimizer = SelfOptimizer(dry_run=dry_run)
    optimizer.run()
