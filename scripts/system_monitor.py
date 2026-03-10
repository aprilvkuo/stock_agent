#!/usr/bin/env python3
"""
系统监控脚本 - 持续监控股票多 Agent 系统健康状态

功能：
1. 监控系统资源使用（磁盘空间、文件数量）
2. 检查关键脚本是否正常运行
3. 验证 Heartbeat 任务执行状态
4. 自动触发优化（当超过阈值时）
5. 发送告警（当发现异常时）

运行方式：
    python3 scripts/system_monitor.py [--auto-optimize]
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
LOGS_DIR = BASE_DIR / "analysis-log"
REPORTS_DIR = BASE_DIR / "reports"
STATUS_FILE = BASE_DIR / "system-health.json"

class SystemMonitor:
    # 阈值配置
    THRESHOLDS = {
        "max_dir_size_mb": 50,  # 目录最大 50MB
        "max_pycache_count": 10,  # 最多 10 个__pycache__
        "max_log_files": 100,  # 最多 100 个日志文件
        "max_backup_files": 5,  # 最多 5 个备份文件
        "script_error_threshold": 3  # 脚本错误超过 3 次触发告警
    }
    
    def __init__(self, auto_optimize=False):
        self.auto_optimize = auto_optimize
        self.alerts = []
        self.health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
            "alerts": []
        }
    
    def run(self):
        """执行完整监控流程"""
        print("=" * 60)
        print("🏥 系统健康检查")
        print("=" * 60)
        
        # 1. 检查磁盘使用
        self.check_disk_usage()
        
        # 2. 检查临时文件
        self.check_temp_files()
        
        # 3. 检查脚本健康
        self.check_scripts_health()
        
        # 4. 检查日志状态
        self.check_logs_status()
        
        # 5. 检查 Heartbeat 状态
        self.check_heartbeat_status()
        
        # 6. 生成健康报告
        self.generate_health_report()
        
        # 7. 处理告警
        self.process_alerts()
        
        # 输出总结
        print("\n" + "=" * 60)
        if self.alerts:
            print(f"⚠️  发现 {len(self.alerts)} 个告警")
            self.health_status["status"] = "warning"
        else:
            print("✅ 系统健康状态良好")
            self.health_status["status"] = "healthy"
        print("=" * 60)
        
        return len(self.alerts) == 0
    
    def check_disk_usage(self):
        """检查磁盘使用"""
        print("\n💾 Check 1: 磁盘使用...")
        
        total_size = self.get_dir_size(BASE_DIR)
        size_mb = total_size / (1024 * 1024)
        
        self.health_status["checks"]["disk_usage"] = {
            "size_mb": round(size_mb, 2),
            "threshold_mb": self.THRESHOLDS["max_dir_size_mb"],
            "status": "ok" if size_mb < self.THRESHOLDS["max_dir_size_mb"] else "warning"
        }
        
        print(f"   📊 总大小：{size_mb:.2f} MB / {self.THRESHOLDS['max_dir_size_mb']} MB")
        
        if size_mb >= self.THRESHOLDS["max_dir_size_mb"]:
            alert = f"磁盘使用超限：{size_mb:.2f} MB > {self.THRESHOLDS['max_dir_size_mb']} MB"
            self.alerts.append(alert)
            print(f"   ⚠️  {alert}")
            if self.auto_optimize:
                self.trigger_optimization()
    
    def check_temp_files(self):
        """检查临时文件"""
        print("\n🗑️  Check 2: 临时文件...")
        
        # 统计 __pycache__
        pycache_count = len(list(BASE_DIR.rglob("__pycache__")))
        self.health_status["checks"]["pycache_count"] = {
            "count": pycache_count,
            "threshold": self.THRESHOLDS["max_pycache_count"],
            "status": "ok" if pycache_count < self.THRESHOLDS["max_pycache_count"] else "warning"
        }
        print(f"   📦 __pycache__: {pycache_count} 个")
        
        if pycache_count >= self.THRESHOLDS["max_pycache_count"]:
            alert = f"__pycache__ 过多：{pycache_count} >= {self.THRESHOLDS['max_pycache_count']}"
            self.alerts.append(alert)
            print(f"   ⚠️  {alert}")
        
        # 统计备份文件
        backup_count = len(list(BASE_DIR.rglob("*.backup"))) + len(list(BASE_DIR.rglob("*.bak")))
        self.health_status["checks"]["backup_count"] = {
            "count": backup_count,
            "threshold": self.THRESHOLDS["max_backup_files"],
            "status": "ok" if backup_count < self.THRESHOLDS["max_backup_files"] else "warning"
        }
        print(f"   📦 备份文件：{backup_count} 个")
        
        if backup_count >= self.THRESHOLDS["max_backup_files"]:
            alert = f"备份文件过多：{backup_count} >= {self.THRESHOLDS['max_backup_files']}"
            self.alerts.append(alert)
            print(f"   ⚠️  {alert}")
    
    def check_scripts_health(self):
        """检查脚本健康"""
        print("\n🔧 Check 3: 脚本健康...")
        
        critical_scripts = [
            "auto_agent.py",
            "self_optimizer.py",
            "validate_predictions.py"
        ]
        
        missing_scripts = []
        for script in critical_scripts:
            script_path = SCRIPTS_DIR / script
            if not script_path.exists():
                missing_scripts.append(script)
                print(f"   ❌ 缺失：{script}")
            else:
                print(f"   ✅ 存在：{script}")
        
        self.health_status["checks"]["critical_scripts"] = {
            "missing": missing_scripts,
            "status": "ok" if not missing_scripts else "critical"
        }
        
        if missing_scripts:
            alert = f"关键脚本缺失：{', '.join(missing_scripts)}"
            self.alerts.append(alert)
    
    def check_logs_status(self):
        """检查日志状态"""
        print("\n📝 Check 4: 日志状态...")
        
        log_count = len(list(LOGS_DIR.glob("*.md")))
        self.health_status["checks"]["log_count"] = {
            "count": log_count,
            "threshold": self.THRESHOLDS["max_log_files"],
            "status": "ok" if log_count < self.THRESHOLDS["max_log_files"] else "warning"
        }
        print(f"   📊 分析日志：{log_count} 个")
        
        if log_count >= self.THRESHOLDS["max_log_files"]:
            alert = f"日志文件过多：{log_count} >= {self.THRESHOLDS['max_log_files']}"
            self.alerts.append(alert)
            print(f"   ⚠️  {alert}")
    
    def check_heartbeat_status(self):
        """检查 Heartbeat 状态"""
        print("\n💓 Check 5: Heartbeat 状态...")
        
        # 检查最近是否有分析日志
        recent_logs = [
            f for f in LOGS_DIR.glob("*.md")
            if datetime.fromtimestamp(f.stat().st_mtime) > datetime.now() - timedelta(hours=24)
        ]
        
        self.health_status["checks"]["heartbeat"] = {
            "recent_analyses": len(recent_logs),
            "status": "ok" if len(recent_logs) > 0 else "warning"
        }
        
        if len(recent_logs) > 0:
            print(f"   ✅ 24 小时内有 {len(recent_logs)} 次分析")
        else:
            print(f"   ⚠️  24 小时内无分析记录")
            # 这不一定是问题，可能是正常情况
    
    def generate_health_report(self):
        """生成健康报告"""
        print("\n📈 Check 6: 生成报告...")
        
        report_path = REPORTS_DIR / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(self.health_status, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 报告已保存：{report_path.relative_to(BASE_DIR)}")
        
        # 更新状态文件
        with open(STATUS_FILE, "w") as f:
            json.dump(self.health_status, f, indent=2, ensure_ascii=False)
    
    def process_alerts(self):
        """处理告警"""
        if self.alerts:
            print("\n🚨 告警列表:")
            for i, alert in enumerate(self.alerts, 1):
                print(f"   {i}. {alert}")
            
            self.health_status["alerts"] = self.alerts
    
    def trigger_optimization(self):
        """触发优化"""
        print("\n🔧 自动触发优化...")
        try:
            subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "self_optimizer.py")],
                cwd=BASE_DIR,
                check=True,
                capture_output=True,
                timeout=60
            )
            print("   ✅ 优化完成")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 优化失败：{e}")
        except Exception as e:
            print(f"   ❌ 错误：{e}")
    
    def get_dir_size(self, path):
        """计算目录大小"""
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total


if __name__ == "__main__":
    auto_optimize = "--auto-optimize" in sys.argv
    monitor = SystemMonitor(auto_optimize=auto_optimize)
    success = monitor.run()
    sys.exit(0 if success else 1)
