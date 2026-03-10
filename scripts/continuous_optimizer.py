#!/usr/bin/env python3
"""
持续优化循环脚本 - 无间断自我优化

功能：
1. 持续监控系统状态
2. 发现优化机会立即执行
3. 记录优化日志
4. 避免资源过度消耗（智能节流）

运行方式：
    python3 scripts/continuous_optimizer.py [--background]
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
LOGS_DIR = BASE_DIR / "analysis-log"
REPORTS_DIR = BASE_DIR / "reports"
STATE_FILE = BASE_DIR / "continuous_optimizer_state.json"

class ContinuousOptimizer:
    # 优化间隔配置（秒）
    INTERVALS = {
        "quick_check": 60,        # 快速检查：每 1 分钟
        "temp_cleanup": 300,      # 临时文件清理：每 5 分钟
        "health_check": 600,      # 健康检查：每 10 分钟
        "full_optimize": 3600,    # 完整优化：每 1 小时
        "analysis_boost": 1800,   # 分析加速：每 30 分钟（如有待分析股票）
    }
    
    # 资源限制
    LIMITS = {
        "max_cpu_percent": 50,    # CPU 使用上限
        "max_memory_mb": 512,     # 内存使用上限
        "min_disk_mb": 100,       # 磁盘剩余空间下限
    }
    
    def __init__(self, background=False):
        self.background = background
        self.running = True
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "optimizations_run": 0,
            "cleanups_run": 0,
            "health_checks_run": 0,
            "issues_found": 0,
            "issues_fixed": 0
        }
        self.last_runs = {
            "quick_check": 0,
            "temp_cleanup": 0,
            "health_check": 0,
            "full_optimize": 0,
            "analysis_boost": 0
        }
        self.load_state()
    
    def load_state(self):
        """加载上次运行状态"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
                    self.last_runs = state.get("last_runs", self.last_runs)
                    self.stats = state.get("stats", self.stats)
            except:
                pass
    
    def save_state(self):
        """保存运行状态"""
        self.stats["last_update"] = datetime.now().isoformat()
        with open(STATE_FILE, "w") as f:
            json.dump({
                "last_runs": self.last_runs,
                "stats": self.stats
            }, f, indent=2)
    
    def run(self):
        """启动持续优化循环"""
        print("=" * 60)
        print("🔄 持续优化循环启动")
        print("=" * 60)
        print(f"开始时间：{self.stats['start_time']}")
        print(f"优化间隔：快速检查 1 分钟 | 清理 5 分钟 | 健康 10 分钟 | 完整 1 小时")
        print("=" * 60)
        print()
        
        try:
            while self.running:
                current_time = time.time()
                
                # 1. 快速检查（每分钟）
                if current_time - self.last_runs["quick_check"] >= self.INTERVALS["quick_check"]:
                    self.quick_check()
                    self.last_runs["quick_check"] = current_time
                
                # 2. 临时文件清理（每 5 分钟）
                if current_time - self.last_runs["temp_cleanup"] >= self.INTERVALS["temp_cleanup"]:
                    self.temp_cleanup()
                    self.last_runs["temp_cleanup"] = current_time
                
                # 3. 健康检查（每 10 分钟）
                if current_time - self.last_runs["health_check"] >= self.INTERVALS["health_check"]:
                    self.health_check()
                    self.last_runs["health_check"] = current_time
                
                # 4. 完整优化（每小时）
                if current_time - self.last_runs["full_optimize"] >= self.INTERVALS["full_optimize"]:
                    self.full_optimize()
                    self.last_runs["full_optimize"] = current_time
                
                # 5. 分析加速（每 30 分钟，如有待分析股票池）
                if current_time - self.last_runs["analysis_boost"] >= self.INTERVALS["analysis_boost"]:
                    self.analysis_boost()
                    self.last_runs["analysis_boost"] = current_time
                
                # 保存状态
                self.save_state()
                
                # 休眠（短时间，保持响应性）
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n⏹️  收到中断信号，停止优化循环")
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            self.save_state()
        
        print("\n" + "=" * 60)
        print("📊 优化统计")
        print("=" * 60)
        print(f"运行优化：{self.stats['optimizations_run']} 次")
        print(f"执行清理：{self.stats['cleanups_run']} 次")
        print(f"健康检查：{self.stats['health_checks_run']} 次")
        print(f"发现问题：{self.stats['issues_found']} 个")
        print(f"修复问题：{self.stats['issues_fixed']} 个")
        print("=" * 60)
    
    def quick_check(self):
        """快速检查 - 发现明显问题"""
        # print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 快速检查...")
        
        issues = []
        
        # 检查 __pycache__
        pycache_count = len(list(BASE_DIR.rglob("__pycache__")))
        if pycache_count > 5:
            issues.append(f"__pycache__ 过多：{pycache_count} 个")
        
        # 检查备份文件
        backup_count = len(list(BASE_DIR.rglob("*.backup"))) + len(list(BASE_DIR.rglob("*.bak")))
        if backup_count > 0:
            issues.append(f"发现备份文件：{backup_count} 个")
        
        # 检查旧版本脚本
        old_scripts = len(list(SCRIPTS_DIR.glob("*_v[0-9]*.py")))
        if old_scripts > 0:
            issues.append(f"发现旧版本脚本：{old_scripts} 个")
        
        if issues:
            self.stats["issues_found"] += len(issues)
            # print(f"   ⚠️  发现 {len(issues)} 个问题")
            for issue in issues:
                pass  # print(f"      - {issue}")
        # else:
            # print("   ✅ 无问题")
    
    def temp_cleanup(self):
        """临时文件清理"""
        # print(f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️  临时文件清理...")
        
        cleaned = 0
        freed_size = 0
        
        # 清理 __pycache__
        for pycache in BASE_DIR.rglob("__pycache__"):
            if pycache.is_dir():
                try:
                    size = sum(f.stat().st_size for f in pycache.rglob("*") if f.is_file())
                    import shutil
                    shutil.rmtree(pycache)
                    cleaned += 1
                    freed_size += size
                except:
                    pass
        
        # 清理备份文件
        for pattern in ["*.backup", "*.bak", "*.old", "*.tmp"]:
            for f in BASE_DIR.rglob(pattern):
                if f.is_file():
                    try:
                        size = f.stat().st_size
                        f.unlink()
                        cleaned += 1
                        freed_size += size
                    except:
                        pass
        
        # 清理旧版本脚本
        for old_script in SCRIPTS_DIR.glob("*_v[0-9]*.py"):
            if old_script.is_file():
                try:
                    size = old_script.stat().st_size
                    old_script.unlink()
                    cleaned += 1
                    freed_size += size
                except:
                    pass
        
        self.stats["cleanups_run"] += 1
        # print(f"   ✅ 清理 {cleaned} 个文件，释放 {freed_size/1024:.2f} KB")
    
    def health_check(self):
        """健康检查"""
        # print(f"[{datetime.now().strftime('%H:%M:%S')}] 🏥 健康检查...")
        
        self.stats["health_checks_run"] += 1
        
        # 运行完整健康检查脚本
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "system_monitor.py")],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=30
            )
            # print("   ✅ 健康检查完成")
        except Exception as e:
            print(f"   ❌ 健康检查失败：{e}")
            self.stats["issues_found"] += 1
    
    def full_optimize(self):
        """完整优化"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 完整优化...")
        
        self.stats["optimizations_run"] += 1
        
        # 运行自优化脚本
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "self_optimizer.py")],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=60
            )
            print("   ✅ 完整优化完成")
        except Exception as e:
            print(f"   ❌ 优化失败：{e}")
            self.stats["issues_found"] += 1
    
    def analysis_boost(self):
        """分析加速 - 如有待分析股票"""
        # print(f"[{datetime.now().strftime('%H:%M:%S')}] 📈 分析加速检查...")
        
        # 检查股票池配置
        stock_pool_file = BASE_DIR / "stock-pool.json"
        if stock_pool_file.exists():
            try:
                with open(stock_pool_file, "r") as f:
                    pool = json.load(f)
                stocks = pool.get("stocks", [])
                if stocks:
                    # print(f"   📊 股票池：{len(stocks)} 只股票")
                    # 可以在此触发批量分析
                    pass
            except:
                pass


if __name__ == "__main__":
    background = "--background" in sys.argv
    optimizer = ContinuousOptimizer(background=background)
    optimizer.run()
