#!/usr/bin/env python3
"""
Agent 表现追踪系统 - 记录和分析各 Agent 的准确率

功能：
1. 记录每次 Agent 分析结果
2. 验证后更新准确率统计
3. 生成 Agent 表现报告
4. 为动态权重调整提供数据支持
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TRACKING_FILE = BASE_DIR / "agent-performance.json"
ANALYSIS_LOG_DIR = BASE_DIR / "analysis-log"
VALIDATION_QUEUE = BASE_DIR / "validation-queue.md"

class AgentPerformanceTracker:
    def __init__(self):
        self.tracking_data = self.load_tracking_data()
    
    def load_tracking_data(self):
        """加载追踪数据"""
        if TRACKING_FILE.exists():
            with open(TRACKING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # 初始化数据结构
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "agents": {
                "基本面": {
                    "total_predictions": 0,
                    "correct": 0,
                    "partial": 0,
                    "wrong": 0,
                    "avg_confidence": 0,
                    "recent_predictions": []
                },
                "技术面": {
                    "total_predictions": 0,
                    "correct": 0,
                    "partial": 0,
                    "wrong": 0,
                    "avg_confidence": 0,
                    "recent_predictions": []
                },
                "情绪": {
                    "total_predictions": 0,
                    "correct": 0,
                    "partial": 0,
                    "wrong": 0,
                    "avg_confidence": 0,
                    "recent_predictions": []
                },
                "主 Agent": {
                    "total_predictions": 0,
                    "correct": 0,
                    "partial": 0,
                    "wrong": 0,
                    "avg_confidence": 0,
                    "recent_predictions": []
                }
            },
            "validations": []
        }
    
    def scan_analysis_logs(self):
        """扫描分析日志，统计 Agent 表现"""
        print("📊 扫描分析日志...")
        
        logs = list(ANALYSIS_LOG_DIR.glob("*.json"))
        if not logs:
            print("   ⚠️  未找到 JSON 日志")
            return
        
        # 字段映射 (JSON 英文 → 追踪中文)
        agent_mapping = {
            "fundamental": "基本面",
            "technical": "技术面",
            "sentiment": "情绪",
            "main": "主 Agent"
        }
        
        for log_file in logs:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                
                # 提取 Agent 分析结果
                agents = log_data.get("agents", {})
                for agent_key, agent_data in agents.items():
                    agent_name = agent_mapping.get(agent_key, agent_key)
                    if agent_name in self.tracking_data["agents"]:
                        agent_tracking = self.tracking_data["agents"][agent_name]
                        agent_tracking["total_predictions"] += 1
                        
                        # 更新平均置信度
                        confidence = agent_data.get("confidence", 0)
                        total = agent_tracking["total_predictions"]
                        avg = agent_tracking["avg_confidence"]
                        agent_tracking["avg_confidence"] = ((avg * (total - 1)) + confidence) / total
                
                # 主 Agent 决策
                decision = log_data.get("decision", {})
                if decision:
                    main_agent = self.tracking_data["agents"]["主 Agent"]
                    main_agent["total_predictions"] += 1
                    # 从评分推算置信度 (50 分=50% 置信度)
                    score = decision.get("score", 50)
                    confidence = score
                    total = main_agent["total_predictions"]
                    avg = main_agent["avg_confidence"]
                    main_agent["avg_confidence"] = ((avg * (total - 1)) + confidence) / total
                
            except Exception as e:
                print(f"   ⚠️  读取 {log_file.name} 失败：{e}")
        
        print(f"   ✅ 扫描完成：{len(logs)} 个日志文件")
    
    def scan_validation_queue(self):
        """扫描验证队列，统计待验证预测"""
        print("\n📋 扫描验证队列...")
        
        if not VALIDATION_QUEUE.exists():
            print("   ⚠️  验证队列不存在")
            return
        
        pending_count = 0
        with open(VALIDATION_QUEUE, "r", encoding="utf-8") as f:
            for line in f:
                if "⏳ 待验证" in line:
                    pending_count += 1
        
        print(f"   ✅ 待验证预测：{pending_count} 项")
        self.tracking_data["pending_validations"] = pending_count
    
    def calculate_accuracy(self):
        """计算各 Agent 准确率"""
        print("\n📈 计算准确率...")
        
        for agent_name, agent_data in self.tracking_data["agents"].items():
            total = agent_data["total_predictions"]
            correct = agent_data["correct"]
            partial = agent_data["partial"]
            
            if total > 0:
                # 准确率 = (完全正确 + 0.5 * 部分正确) / 总数
                accuracy = (correct + 0.5 * partial) / total
                agent_data["accuracy"] = round(accuracy * 100, 2)
            else:
                agent_data["accuracy"] = 0
            
            print(f"   {agent_name}: {agent_data['accuracy']}% "
                  f"(置信度：{agent_data['avg_confidence']:.1f}%)")
    
    def generate_report(self):
        """生成 Agent 表现报告"""
        print("\n📄 生成报告...")
        
        report = {
            "summary": {
                "total_predictions": sum(
                    a["total_predictions"] for a in self.tracking_data["agents"].values()
                ),
                "pending_validations": self.tracking_data.get("pending_validations", 0),
                "top_agent": None,
                "top_accuracy": 0
            },
            "agents": {}
        }
        
        # 找出表现最好的 Agent
        for agent_name, agent_data in self.tracking_data["agents"].items():
            report["agents"][agent_name] = {
                "总预测数": agent_data["total_predictions"],
                "正确": agent_data["correct"],
                "部分正确": agent_data["partial"],
                "错误": agent_data["wrong"],
                "准确率": f"{agent_data.get('accuracy', 0)}%",
                "平均置信度": f"{agent_data['avg_confidence']:.1f}%"
            }
            
            if agent_data.get("accuracy", 0) > report["summary"]["top_accuracy"]:
                report["summary"]["top_agent"] = agent_name
                report["summary"]["top_accuracy"] = agent_data["accuracy"]
        
        # 保存报告
        report_path = BASE_DIR / "reports" / f"agent_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 报告已保存：{report_path.name}")
        return report
    
    def save(self):
        """保存追踪数据"""
        with open(TRACKING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tracking_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 数据已保存：{TRACKING_FILE.name}")
    
    def run(self):
        """执行完整追踪流程"""
        print("=" * 60)
        print("📊 Agent 表现追踪系统")
        print("=" * 60)
        
        self.scan_analysis_logs()
        self.scan_validation_queue()
        self.calculate_accuracy()
        report = self.generate_report()
        self.save()
        
        # 输出总结
        print("\n" + "=" * 60)
        print("📊 总结")
        print("=" * 60)
        print(f"总预测数：{report['summary']['total_predictions']} 次")
        print(f"待验证：{report['summary']['pending_validations']} 项")
        if report['summary']['top_agent']:
            print(f"最佳 Agent: {report['summary']['top_agent']} "
                  f"({report['summary']['top_accuracy']}%)")
        print("=" * 60)


if __name__ == "__main__":
    tracker = AgentPerformanceTracker()
    tracker.run()
