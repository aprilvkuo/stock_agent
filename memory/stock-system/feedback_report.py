#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 互相指导系统 - 反馈报告模块
每周自动生成 Agent 服务反馈报告（v1.7 新增 Git 自动提交）
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List

# 导入 Git 版本控制
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from git_version_control import GitVersionControl

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
RATING_DIR = os.path.join(STOCK_SYSTEM, 'agent-ratings')
REPORTS_DIR = os.path.join(STOCK_SYSTEM, 'feedback-reports')

# 确保目录存在
os.makedirs(REPORTS_DIR, exist_ok=True)

# Git 控制器实例
_git = GitVersionControl()

class FeedbackReportGenerator:
    """反馈报告生成器"""
    
    def __init__(self):
        self.agent_names = {
            'fundamental': '基本面 Agent',
            'technical': '技术面 Agent',
            'sentiment': '情绪 Agent',
            'coordinator': '主 Agent',
            'qa': '质检 Agent',
            'programmer': '程序员 Agent',
            'risk': '风险评估师',
            'cio': '首席投资官',
            'data-fetcher': '数据抓取 Agent'
        }
    
    def generate_weekly_report(self, agent_id: str, weeks_ago: int = 0) -> Dict:
        """
        生成指定 Agent 的周度反馈报告
        
        Args:
            agent_id: Agent ID
            weeks_ago: 几周前（0=本周，1=上周）
            
        Returns:
            报告字典
        """
        # 计算日期范围
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday(), weeks=weeks_ago)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # 收集该周所有评分
        ratings = self._collect_ratings(agent_id, week_start, week_end)
        
        if not ratings:
            return self._empty_report(agent_id, week_start, week_end)
        
        # 生成报告
        report = {
            'agent_id': agent_id,
            'agent_name': self.agent_names.get(agent_id, agent_id),
            'report_type': 'weekly',
            'period': {
                'start': week_start.strftime('%Y-%m-%d'),
                'end': week_end.strftime('%Y-%m-%d'),
                'week_number': week_start.isocalendar()[1]
            },
            'generated_at': datetime.now().isoformat(),
            
            # 总体表现
            'summary': {
                'total_services': len(ratings),
                'average_score': round(sum(r['overall_score'] for r in ratings) / len(ratings), 2),
                'trend': self._calculate_trend(ratings),
                'best_service': self._find_best_service(ratings),
                'worst_service': self._find_worst_service(ratings)
            },
            
            # 按服务类型分组
            'feedback_by_service_type': self._group_by_service_type(ratings),
            
            # 按甲方分组
            'feedback_by_consumer': self._group_by_consumer(ratings),
            
            # 评分维度分析
            'dimension_analysis': self._analyze_dimensions(ratings),
            
            # 甲方评价摘录
            'consumer_comments': self._extract_comments(ratings),
            
            # 改进建议汇总
            'improvement_suggestions': self._aggregate_suggestions(ratings),
            
            # 低分记录
            'low_ratings': [r for r in ratings if r['overall_score'] < 3.0],
            
            # 下周行动计划
            'action_plan': []
        }
        
        # 生成行动计划
        report['action_plan'] = self._generate_action_plan(report)
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _collect_ratings(self, agent_id: str, start: datetime, end: datetime) -> List[Dict]:
        """收集指定日期范围内的评分"""
        ratings = []
        
        # 遍历评分文件
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            rating_file = os.path.join(RATING_DIR, f'rating-{date_str}.json')
            
            if os.path.exists(rating_file):
                try:
                    with open(rating_file, 'r', encoding='utf-8') as f:
                        day_ratings = json.load(f)
                    
                    # 筛选出该 Agent 作为提供者的评分
                    for rating in day_ratings:
                        if rating.get('provider') == agent_id:
                            ratings.append(rating)
                except:
                    pass
            
            current += timedelta(days=1)
        
        return ratings
    
    def _calculate_trend(self, ratings: List[Dict]) -> str:
        """计算趋势"""
        if len(ratings) < 2:
            return 'stable'
        
        # 按时间排序
        sorted_ratings = sorted(ratings, key=lambda x: x['timestamp'])
        
        # 前半段 vs 后半段
        mid = len(sorted_ratings) // 2
        first_half_avg = sum(r['overall_score'] for r in sorted_ratings[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(r['overall_score'] for r in sorted_ratings[mid:]) / (len(sorted_ratings) - mid)
        
        if second_half_avg > first_half_avg + 0.3:
            return 'up'
        elif second_half_avg < first_half_avg - 0.3:
            return 'down'
        else:
            return 'stable'
    
    def _find_best_service(self, ratings: List[Dict]) -> Dict:
        """找出最佳服务"""
        if not ratings:
            return {}
        
        best = max(ratings, key=lambda x: x['overall_score'])
        return {
            'service_type': best.get('service_type', ''),
            'consumer': best.get('consumer', ''),
            'score': best.get('overall_score', 0),
            'date': best.get('date', '')
        }
    
    def _find_worst_service(self, ratings: List[Dict]) -> Dict:
        """找出最差服务"""
        if not ratings:
            return {}
        
        worst = min(ratings, key=lambda x: x['overall_score'])
        return {
            'service_type': worst.get('service_type', ''),
            'consumer': worst.get('consumer', ''),
            'score': worst.get('overall_score', 0),
            'date': worst.get('date', '')
        }
    
    def _group_by_service_type(self, ratings: List[Dict]) -> Dict:
        """按服务类型分组"""
        groups = {}
        
        for rating in ratings:
            service_type = rating.get('service_type', 'unknown')
            
            if service_type not in groups:
                groups[service_type] = {
                    'count': 0,
                    'total_score': 0,
                    'average_score': 0,
                    'ratings': []
                }
            
            groups[service_type]['count'] += 1
            groups[service_type]['total_score'] += rating['overall_score']
            groups[service_type]['ratings'].append(rating)
        
        # 计算平均分
        for service_type in groups:
            count = groups[service_type]['count']
            groups[service_type]['average_score'] = round(groups[service_type]['total_score'] / count, 2)
            groups[service_type]['ratings'] = groups[service_type]['ratings'][:5]  # 只保留最近 5 条
        
        return groups
    
    def _group_by_consumer(self, ratings: List[Dict]) -> Dict:
        """按甲方分组"""
        groups = {}
        
        for rating in ratings:
            consumer = rating.get('consumer', 'unknown')
            
            if consumer not in groups:
                groups[consumer] = {
                    'count': 0,
                    'average_score': 0,
                    'total_score': 0
                }
            
            groups[consumer]['count'] += 1
            groups[consumer]['total_score'] += rating['overall_score']
        
        # 计算平均分
        for consumer in groups:
            count = groups[consumer]['count']
            groups[consumer]['average_score'] = round(groups[consumer]['total_score'] / count, 2)
        
        return groups
    
    def _analyze_dimensions(self, ratings: List[Dict]) -> Dict:
        """分析评分维度"""
        dimensions = {
            'accuracy': {'name': '准确性', 'total': 0, 'count': 0},
            'timeliness': {'name': '及时性', 'total': 0, 'count': 0},
            'completeness': {'name': '完整性', 'total': 0, 'count': 0},
            'usefulness': {'name': '有用性', 'total': 0, 'count': 0},
            'reliability': {'name': '可靠性', 'total': 0, 'count': 0}
        }
        
        for rating in ratings:
            scores = rating.get('scores', {})
            for dim, score in scores.items():
                if dim in dimensions:
                    dimensions[dim]['total'] += score
                    dimensions[dim]['count'] += 1
        
        # 计算平均分
        for dim in dimensions:
            count = dimensions[dim]['count']
            dimensions[dim]['average'] = round(dimensions[dim]['total'] / count, 2) if count > 0 else 0
            del dimensions[dim]['total']
            del dimensions[dim]['count']
        
        return dimensions
    
    def _extract_comments(self, ratings: List[Dict]) -> List[Dict]:
        """提取甲方评价"""
        comments = []
        
        for rating in ratings:
            feedback = rating.get('feedback', '')
            if feedback:
                comments.append({
                    'consumer': rating.get('consumer', ''),
                    'service_type': rating.get('service_type', ''),
                    'score': rating.get('overall_score', 0),
                    'comment': feedback,
                    'date': rating.get('date', '')
                })
        
        # 按评分排序，低分优先
        comments.sort(key=lambda x: x['score'])
        
        return comments[:10]  # 只保留 10 条
    
    def _aggregate_suggestions(self, ratings: List[Dict]) -> List[Dict]:
        """汇总改进建议"""
        suggestion_count = {}
        
        for rating in ratings:
            suggestions = rating.get('suggestions', [])
            for suggestion in suggestions:
                suggestion_count[suggestion] = suggestion_count.get(suggestion, 0) + 1
        
        # 按提及次数排序
        aggregated = [
            {'suggestion': s, 'count': c}
            for s, c in suggestion_count.items()
        ]
        aggregated.sort(key=lambda x: x['count'], reverse=True)
        
        return aggregated
    
    def _generate_action_plan(self, report: Dict) -> List[Dict]:
        """生成行动计划"""
        actions = []
        
        # 基于低分记录
        if report['low_ratings']:
            actions.append({
                'priority': 'high',
                'action': '分析低分原因并制定改进措施',
                'details': f"本周有{len(report['low_ratings'])}次低分评价（<3 分）"
            })
        
        # 基于改进建议
        if report['improvement_suggestions']:
            top_suggestions = report['improvement_suggestions'][:3]
            for i, sugg in enumerate(top_suggestions, 1):
                actions.append({
                    'priority': 'medium' if sugg['count'] <= 2 else 'high',
                    'action': f"改进建议 #{i}",
                    'details': f"{sugg['suggestion']}（被提及{sugg['count']}次）"
                })
        
        # 基于维度分析
        dim_analysis = report['dimension_analysis']
        weak_dimensions = [
            (k, v['average']) for k, v in dim_analysis.items()
            if v['average'] < 3.5
        ]
        weak_dimensions.sort(key=lambda x: x[1])
        
        for dim, avg in weak_dimensions[:2]:
            actions.append({
                'priority': 'medium',
                'action': f"提升{dim_analysis[dim]['name']}",
                'details': f"当前得分{avg}/5.0，需要改进"
            })
        
        return actions
    
    def _empty_report(self, agent_id: str, start: datetime, end: datetime) -> Dict:
        """生成空报告"""
        return {
            'agent_id': agent_id,
            'agent_name': self.agent_names.get(agent_id, agent_id),
            'report_type': 'weekly',
            'period': {
                'start': start.strftime('%Y-%m-%d'),
                'end': end.strftime('%Y-%m-%d')
            },
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_services': 0,
                'average_score': 0,
                'trend': 'no_data',
                'message': '本周暂无服务记录'
            }
        }
    
    def _save_report(self, report: Dict):
        """保存报告（v1.7 新增 Git 自动提交）"""
        agent_id = report['agent_id']
        period_start = report['period']['start']
        
        report_file = os.path.join(
            REPORTS_DIR,
            f"feedback-{agent_id}-{period_start}.json"
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 同时生成 Markdown 版本
        self._save_markdown_report(report)
        
        # Git 自动提交（v1.7 新增）
        agent_name = report.get('agent_name', agent_id)
        week_num = report['period']['week_number']
        score = report['summary'].get('average_score', 0)
        commit_msg = f"生成 {agent_name} 周度反馈报告 (第{week_num}周) - 得分：{score}/5.0"
        git_record = _git.commit("系统 Agent", commit_msg, auto_push=True)
        if git_record:
            print(f"✅ Git 提交：{git_record['hash'][:8]}")
    
    def _save_markdown_report(self, report: Dict):
        """保存 Markdown 格式报告"""
        agent_id = report['agent_id']
        period_start = report['period']['start']
        
        md_file = os.path.join(
            REPORTS_DIR,
            f"feedback-{agent_id}-{period_start}.md"
        )
        
        md_content = self._format_markdown(report)
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _format_markdown(self, report: Dict) -> str:
        """格式化为 Markdown"""
        summary = report.get('summary', {})
        
        md = f"""# {report['agent_name']} - 周度反馈报告

**报告周期**: {report['period']['start']} 至 {report['period']['end']}  
**生成时间**: {report['generated_at'][:10]}

---

## 📊 总体表现

| 指标 | 数值 |
|------|------|
| 服务次数 | {summary.get('total_services', 0)} |
| 平均得分 | {summary.get('average_score', 0)}/5.0 |
| 趋势 | {self._trend_emoji(summary.get('trend', 'stable'))} |

"""
        
        # 按服务类型
        if report.get('feedback_by_service_type'):
            md += "## 🔧 按服务类型\n\n"
            md += "| 服务类型 | 次数 | 平均分 |\n"
            md += "|----------|------|--------|\n"
            
            for service_type, data in report['feedback_by_service_type'].items():
                md += f"| {service_type} | {data['count']} | {data['average_score']}/5.0 |\n"
            
            md += "\n"
        
        # 甲方评价
        if report.get('consumer_comments'):
            md += "## 💬 甲方评价摘录\n\n"
            for comment in report['consumer_comments'][:5]:
                stars = '⭐' * int(comment['score'])
                md += f"> \"{comment['comment']}\"  \n"
                md += f"> —— {comment['consumer']} ({stars} {comment['score']}/5.0)\n\n"
        
        # 改进建议
        if report.get('improvement_suggestions'):
            md += "## 💡 改进建议汇总\n\n"
            for i, sugg in enumerate(report['improvement_suggestions'][:5], 1):
                md += f"{i}. **{sugg['suggestion']}**（被提及{sugg['count']}次）\n"
            md += "\n"
        
        # 行动计划
        if report.get('action_plan'):
            md += "## 📋 下周行动计划\n\n"
            for action in report['action_plan']:
                priority_emoji = '🔴' if action['priority'] == 'high' else '🟡'
                md += f"- {priority_emoji} **{action['action']}**: {action['details']}\n"
            md += "\n"
        
        return md
    
    def _trend_emoji(self, trend: str) -> str:
        """趋势表情"""
        if trend == 'up':
            return '📈 上升'
        elif trend == 'down':
            return '📉 下降'
        else:
            return '➡️ 稳定'
    
    def get_all_reports(self, agent_id: str = None) -> List[Dict]:
        """获取所有报告"""
        reports = []
        
        if not os.path.exists(REPORTS_DIR):
            return reports
        
        for filename in os.listdir(REPORTS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(REPORTS_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    
                    if agent_id is None or report.get('agent_id') == agent_id:
                        reports.append(report)
                except:
                    pass
        
        # 按生成时间倒序
        reports.sort(key=lambda x: x.get('generated_at', ''), reverse=True)
        
        return reports


# 全局实例
report_generator = FeedbackReportGenerator()


# 便捷函数
def generate_weekly_report(agent_id, weeks_ago=0):
    """便捷函数：生成周度报告"""
    return report_generator.generate_weekly_report(agent_id, weeks_ago)

def get_all_reports(agent_id=None):
    """便捷函数：获取所有报告"""
    return report_generator.get_all_reports(agent_id)


# 测试
if __name__ == '__main__':
    print("🧪 测试反馈报告生成器...")
    
    # 生成基本面 Agent 的本周报告
    report = generate_weekly_report('fundamental', weeks_ago=0)
    
    print(f"✅ 报告生成成功")
    print(f"   Agent: {report['agent_name']}")
    print(f"   周期：{report['period']['start']} 至 {report['period']['end']}")
    print(f"   服务次数：{report['summary']['total_services']}")
    print(f"   平均得分：{report['summary']['average_score']}/5.0")
    print(f"   趋势：{report['summary']['trend']}")
    
    # 获取所有报告
    all_reports = get_all_reports()
    print(f"\n📊 共有 {len(all_reports)} 份报告")
    
    print("\n✅ 测试完成！")
