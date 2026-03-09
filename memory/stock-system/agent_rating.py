#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 互相指导系统 - 服务质量评分模块
每个 Agent 既是服务提供者（乙方），也是服务使用者（甲方）（v1.7 新增 Git 自动提交）
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# 导入 Git 版本控制
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from git_version_control import GitVersionControl

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
STOCK_SYSTEM = os.path.join(WORKSPACE, 'memory/stock-system')
RATING_DIR = os.path.join(STOCK_SYSTEM, 'agent-ratings')
STATS_FILE = os.path.join(STOCK_SYSTEM, 'agent-rating-stats.json')

# 确保目录存在
os.makedirs(RATING_DIR, exist_ok=True)

# Git 控制器实例
_git = GitVersionControl()

class AgentServiceRating:
    """Agent 服务质量评分系统"""
    
    def __init__(self):
        self.rating_file_template = 'rating-{date}.json'
    
    def rate_service(
        self,
        provider_id: str,
        consumer_id: str,
        service_type: str,
        accuracy: int = 3,
        timeliness: int = 3,
        completeness: int = 3,
        usefulness: int = 3,
        reliability: int = 3,
        feedback: str = '',
        suggestions: List[str] = None
    ) -> Dict:
        """
        甲方给乙方服务打分
        
        Args:
            provider_id: 服务提供者（乙方）- 如 'fundamental'
            consumer_id: 服务使用者（甲方）- 如 'coordinator'
            service_type: 服务类型 - 如 'financial_analysis'
            accuracy: 准确性 (1-5)
            timeliness: 及时性 (1-5)
            completeness: 完整性 (1-5)
            usefulness: 有用性 (1-5)
            reliability: 可靠性 (1-5)
            feedback: 文字反馈
            suggestions: 改进建议列表
            
        Returns:
            评分记录字典
        """
        if suggestions is None:
            suggestions = []
        
        # 验证分数范围
        scores = {
            'accuracy': max(1, min(5, accuracy)),
            'timeliness': max(1, min(5, timeliness)),
            'completeness': max(1, min(5, completeness)),
            'usefulness': max(1, min(5, usefulness)),
            'reliability': max(1, min(5, reliability))
        }
        
        # 计算综合得分
        overall_score = sum(scores.values()) / len(scores)
        
        # 创建评分记录
        rating = {
            'id': self._generate_rating_id(),
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'provider': provider_id,
            'consumer': consumer_id,
            'service_type': service_type,
            'scores': scores,
            'overall_score': round(overall_score, 2),
            'feedback': feedback,
            'suggestions': suggestions
        }
        
        # 保存评分
        self._save_rating(rating)
        
        # 更新统计
        self._update_stats(rating)
        
        # 检查是否需要触发改进
        if overall_score < 3.0:
            self._trigger_improvement(provider_id, rating)
        
        return rating
    
    def _generate_rating_id(self) -> str:
        """生成评分 ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"RATING-{timestamp}"
    
    def _save_rating(self, rating: Dict):
        """保存评分到文件"""
        date = rating['date']
        rating_file = os.path.join(RATING_DIR, f'rating-{date}.json')
        
        # 读取现有评分
        ratings = []
        if os.path.exists(rating_file):
            try:
                with open(rating_file, 'r', encoding='utf-8') as f:
                    ratings = json.load(f)
            except:
                ratings = []
        
        # 添加新评分
        ratings.append(rating)
        
        # 保存
        with open(rating_file, 'w', encoding='utf-8') as f:
            json.dump(ratings, f, ensure_ascii=False, indent=2)
        
        # Git 自动提交（v1.7 新增）
        provider = rating.get('provider', 'Unknown')
        consumer = rating.get('consumer', 'Unknown')
        score = rating.get('overall_score', 0)
        service_type = rating.get('service_type', 'unknown')
        commit_msg = f"更新服务评分：{consumer} 评价 {provider} - {service_type} - 得分：{score}/5.0"
        git_record = _git.commit("系统 Agent", commit_msg, files=[rating_file], auto_push=True)
        if git_record:
            print(f"✅ Git 提交：{git_record['hash'][:8]}")
    
    def _update_stats(self, rating: Dict):
        """更新统计数据"""
        stats = self._load_stats()
        
        provider = rating['provider']
        if provider not in stats:
            stats[provider] = {
                'total_ratings': 0,
                'total_score': 0,
                'average_score': 0,
                'by_service_type': {},
                'by_consumer': {},
                'recent_ratings': []  # 最近 10 次评分
            }
        
        provider_stats = stats[provider]
        
        # 更新总体统计
        provider_stats['total_ratings'] += 1
        provider_stats['total_score'] += rating['overall_score']
        provider_stats['average_score'] = round(
            provider_stats['total_score'] / provider_stats['total_ratings'], 2
        )
        
        # 按服务类型统计
        service_type = rating['service_type']
        if service_type not in provider_stats['by_service_type']:
            provider_stats['by_service_type'][service_type] = {
                'count': 0,
                'total_score': 0,
                'average_score': 0
            }
        
        service_stats = provider_stats['by_service_type'][service_type]
        service_stats['count'] += 1
        service_stats['total_score'] += rating['overall_score']
        service_stats['average_score'] = round(
            service_stats['total_score'] / service_stats['count'], 2
        )
        
        # 按甲方统计
        consumer = rating['consumer']
        if consumer not in provider_stats['by_consumer']:
            provider_stats['by_consumer'][consumer] = {
                'count': 0,
                'average_score': 0,
                'total_score': 0
            }
        
        consumer_stats = provider_stats['by_consumer'][consumer]
        consumer_stats['count'] += 1
        consumer_stats['total_score'] += rating['overall_score']
        consumer_stats['average_score'] = round(
            consumer_stats['total_score'] / consumer_stats['count'], 2
        )
        
        # 更新最近评分（保留最近 10 次）
        provider_stats['recent_ratings'].append({
            'date': rating['date'],
            'score': rating['overall_score'],
            'service_type': service_type,
            'consumer': consumer
        })
        provider_stats['recent_ratings'] = provider_stats['recent_ratings'][-10:]
        
        # 计算趋势
        recent = provider_stats['recent_ratings']
        if len(recent) >= 5:
            recent_5_avg = sum(r['score'] for r in recent[-5:]) / 5
            if recent_5_avg > provider_stats['average_score'] + 0.2:
                provider_stats['trend'] = 'up'
            elif recent_5_avg < provider_stats['average_score'] - 0.2:
                provider_stats['trend'] = 'down'
            else:
                provider_stats['trend'] = 'stable'
        else:
            provider_stats['trend'] = 'stable'
        
        # 保存统计
        self._save_stats(stats)
    
    def _load_stats(self) -> Dict:
        """加载统计数据"""
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_stats(self, stats: Dict):
        """保存统计数据"""
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def _trigger_improvement(self, provider_id: str, rating: Dict):
        """触发改进流程（低分自动创建改进工单）"""
        # 这里可以集成到改进工单系统
        # 目前先记录日志
        improvement_log = os.path.join(STOCK_SYSTEM, 'improvement-triggers.md')
        
        log_entry = f"""
## {rating['id']} - {rating['date']}

**乙方**: {provider_id}  
**甲方**: {rating['consumer']}  
**服务类型**: {rating['service_type']}  
**评分**: {rating['overall_score']}/5.0 ⭐

**问题**:
{rating['feedback']}

**改进建议**:
{chr(10).join('- ' + s for s in rating['suggestions'])}

---
"""
        
        with open(improvement_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_provider_stats(self, provider_id: str) -> Dict:
        """获取指定服务提供者的统计数据"""
        stats = self._load_stats()
        return stats.get(provider_id, {})
    
    def get_all_providers_ranking(self) -> List[Dict]:
        """获取所有服务提供者的排名"""
        stats = self._load_stats()
        
        ranking = []
        for provider_id, provider_stats in stats.items():
            ranking.append({
                'provider_id': provider_id,
                'average_score': provider_stats.get('average_score', 0),
                'total_ratings': provider_stats.get('total_ratings', 0),
                'trend': provider_stats.get('trend', 'stable'),
                'recent_5_avg': self._calc_recent_avg(provider_stats.get('recent_ratings', []))
            })
        
        # 按平均分数排序
        ranking.sort(key=lambda x: x['average_score'], reverse=True)
        
        return ranking
    
    def _calc_recent_avg(self, recent_ratings: List[Dict]) -> float:
        """计算最近 5 次平均分"""
        if not recent_ratings:
            return 0
        recent_5 = recent_ratings[-5:]
        return round(sum(r['score'] for r in recent_5) / len(recent_5), 2)
    
    def get_ratings_by_date(self, date: str = None) -> List[Dict]:
        """获取指定日期的评分记录"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        rating_file = os.path.join(RATING_DIR, f'rating-{date}.json')
        
        if os.path.exists(rating_file):
            try:
                with open(rating_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def get_recent_ratings(self, limit: int = 20) -> List[Dict]:
        """获取最近的评分记录"""
        all_ratings = []
        
        # 读取最近 7 天的评分
        for i in range(7):
            date = (datetime.now().timestamp() - i * 86400)
            date_str = datetime.fromtimestamp(date).strftime('%Y-%m-%d')
            ratings = self.get_ratings_by_date(date_str)
            all_ratings.extend(ratings)
        
        # 按时间倒序排序
        all_ratings.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_ratings[:limit]


# 全局实例
rating_system = AgentServiceRating()


# 便捷函数
def rate_service(provider_id, consumer_id, service_type, **kwargs):
    """便捷函数：给服务评分"""
    return rating_system.rate_service(provider_id, consumer_id, service_type, **kwargs)

def get_provider_stats(provider_id):
    """便捷函数：获取服务提供者统计"""
    return rating_system.get_provider_stats(provider_id)

def get_all_ranking():
    """便捷函数：获取所有提供者排名"""
    return rating_system.get_all_providers_ranking()

def get_recent_ratings(limit=20):
    """便捷函数：获取最近评分"""
    return rating_system.get_recent_ratings(limit)


# 测试
if __name__ == '__main__':
    print("🧪 测试 Agent 评分系统...")
    
    # 测试评分
    result = rate_service(
        provider_id='fundamental',
        consumer_id='coordinator',
        service_type='financial_analysis',
        accuracy=5,
        timeliness=4,
        completeness=4,
        usefulness=5,
        reliability=4,
        feedback='财务分析很准确，但希望能提供行业对比数据',
        suggestions=['增加行业对比数据', '补充现金流分析']
    )
    
    print(f"✅ 评分成功：{result['id']}")
    print(f"   综合得分：{result['overall_score']}/5.0")
    print(f"   乙方：{result['provider']}")
    print(f"   甲方：{result['consumer']}")
    
    # 获取统计
    stats = get_provider_stats('fundamental')
    print(f"\n📊 基本面 Agent 统计:")
    print(f"   总评分数：{stats.get('total_ratings', 0)}")
    print(f"   平均分：{stats.get('average_score', 0)}/5.0")
    print(f"   趋势：{stats.get('trend', 'stable')}")
    
    # 获取排名
    ranking = get_all_ranking()
    print(f"\n🏆 Agent 排名:")
    for i, agent in enumerate(ranking, 1):
        print(f"   #{i} {agent['provider_id']}: {agent['average_score']}/5.0 ({agent['trend']})")
    
    print("\n✅ 测试完成！")
