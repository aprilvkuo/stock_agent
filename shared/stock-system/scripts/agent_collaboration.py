#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 协作上下文管理器
功能：管理 Agent 间的共享信息、讨论记录、判断调整
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# 配置
WORKSPACE = '/Users/egg/.openclaw/workspace'
COORDINATOR_DIR = os.path.join(WORKSPACE, 'agents/stock-coordinator')
DATA_DIR = os.path.join(COORDINATOR_DIR, 'data')
COLLAB_DIR = os.path.join(DATA_DIR, 'collaboration')

class AgentCollaboration:
    """Agent 协作管理器"""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.collab_file = os.path.join(COLLAB_DIR, f"{request_id}.json")
        self._ensure_collab_dir()
        self._init_collab_data()
    
    def _ensure_collab_dir(self):
        """确保协作目录存在"""
        os.makedirs(COLLAB_DIR, exist_ok=True)
    
    def _init_collab_data(self):
        """初始化协作数据"""
        if not os.path.exists(self.collab_file):
            self.data = {
                'request_id': self.request_id,
                'created_at': datetime.now().isoformat(),
                'agents': {},
                'discussion': [],
                'final_decision': None,
            }
        else:
            with open(self.collab_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
    
    def _save(self):
        """保存协作数据"""
        self.data['updated_at'] = datetime.now().isoformat()
        with open(self.collab_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def register_agent(self, agent_name: str, initial_judgment: Dict):
        """
        Agent 注册并提交初始判断
        
        参数:
            agent_name: Agent 名称
            initial_judgment: 初始判断
                {
                    'rating': '买入/持有/卖出',
                    'confidence': 85,
                    'reasons': ['原因 1', '原因 2'],
                    'data_quality': 'high/medium/low'
                }
        """
        self.data['agents'][agent_name] = {
            'initial': initial_judgment,
            'adjusted': None,
            'self_assessment': None,
            'comments': []
        }
        self._save()
        
        print(f"✅ {agent_name} 已注册，初始判断：{initial_judgment['rating']} (置信度：{initial_judgment['confidence']}%)")
    
    def share_context(self, agent_name: str) -> Dict:
        """
        共享其他 Agent 的判断给指定 Agent
        
        参数:
            agent_name: 接收上下文的 Agent
        
        返回:
            其他 Agent 的判断
        """
        other_agents = {k: v for k, v in self.data['agents'].items() if k != agent_name}
        
        context = {
            'request_id': self.request_id,
            'other_agents': {}
        }
        
        for name, data in other_agents.items():
            context['other_agents'][name] = {
                'rating': data['initial']['rating'],
                'confidence': data['initial']['confidence'],
                'reasons': data['initial']['reasons'][:2]  # 只给前 2 个原因
            }
        
        return context
    
    def adjust_judgment(self, agent_name: str, adjusted_judgment: Dict, reason: str):
        """
        Agent 调整自己的判断
        
        参数:
            agent_name: Agent 名称
            adjusted_judgment: 调整后的判断
            reason: 调整原因
        """
        if agent_name not in self.data['agents']:
            print(f"❌ {agent_name} 未注册")
            return
        
        self.data['agents'][agent_name]['adjusted'] = adjusted_judgment
        self.data['agents'][agent_name]['adjust_reason'] = reason
        
        print(f"✅ {agent_name} 调整判断：{adjusted_judgment['rating']} (原因：{reason})")
        self._save()
    
    def add_discussion(self, agent_name: str, message: str, message_type: str = 'comment'):
        """
        添加讨论记录
        
        参数:
            agent_name: Agent 名称
            message: 讨论内容
            message_type: comment/question/answer
        """
        discussion_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'type': message_type,
            'message': message
        }
        
        self.data['discussion'].append(discussion_entry)
        self._save()
        
        print(f"💬 {agent_name}: {message}")
    
    def self_assess(self, agent_name: str, assessment: Dict):
        """
        Agent 自我评估
        
        参数:
            agent_name: Agent 名称
            assessment: 自我评估
                {
                    'confidence_level': 'high/medium/low',
                    'data_quality': 'high/medium/low',
                    'issues': ['问题 1', '问题 2'],
                    'suggestions': ['建议 1', '建议 2']
                }
        """
        if agent_name not in self.data['agents']:
            return
        
        self.data['agents'][agent_name]['self_assessment'] = assessment
        self._save()
        
        print(f"📊 {agent_name} 自我评估：{assessment['confidence_level']}")
    
    def get_final_judgments(self) -> Dict:
        """
        获取所有 Agent 的最终判断（优先使用调整后的）
        
        返回:
            所有 Agent 的最终判断
        """
        final = {}
        
        for agent_name, data in self.data['agents'].items():
            # 优先使用调整后的判断
            if data['adjusted']:
                final[agent_name] = data['adjusted']
            else:
                final[agent_name] = data['initial']
        
        return final
    
    def get_discussion_log(self) -> str:
        """获取讨论记录（Markdown 格式）"""
        if not self.data['discussion']:
            return "无讨论记录"
        
        log = "## Agent 讨论记录\n\n"
        
        for entry in self.data['discussion']:
            time = entry['timestamp'].split('T')[1].split('.')[0]
            agent = entry['agent']
            msg_type = entry['type']
            message = entry['message']
            
            icon = {'comment': '💬', 'question': '❓', 'answer': '✅'}.get(msg_type, '💬')
            log += f"**{time}** {icon} **{agent}**: {message}\n"
        
        return log
    
    def finalize(self, final_decision: Dict):
        """
        完成协作，记录最终决策
        
        参数:
            final_decision: 最终决策
        """
        self.data['final_decision'] = final_decision
        self._save()
        
        print(f"🎯 协作完成，最终决策：{final_decision['rating']}")


# 工具函数

def create_collaboration_session(request_id: str) -> AgentCollaboration:
    """创建协作会话"""
    return AgentCollaboration(request_id)


# 测试
if __name__ == "__main__":
    print("测试 Agent 协作系统...")
    
    # 创建协作会话
    collab = AgentCollaboration("test-20260308")
    
    # Agent 注册
    collab.register_agent('基本面 Agent', {
        'rating': '买入',
        'confidence': 85,
        'reasons': ['ROE 25%', '营收增速 30%', '现金流充足'],
        'data_quality': 'high'
    })
    
    collab.register_agent('技术面 Agent', {
        'rating': '持有',
        'confidence': 70,
        'reasons': ['均线粘合', '成交量萎缩'],
        'data_quality': 'medium'
    })
    
    # 共享上下文
    context = collab.share_context('技术面 Agent')
    print(f"\n技术面 Agent 看到的其他 Agent 判断:")
    for agent, data in context['other_agents'].items():
        print(f"  {agent}: {data['rating']} (置信度：{data['confidence']}%)")
    
    # 调整判断
    collab.adjust_judgment('技术面 Agent', {
        'rating': '买入',
        'confidence': 75,
        'reasons': ['均线粘合', '基本面强劲', '北向资金流入'],
        'data_quality': 'medium'
    }, reason='参考基本面 Agent 的判断，上调评级')
    
    # 添加讨论
    collab.add_discussion('基本面 Agent', '我认为这只股票基本面非常强劲，ROE 连续 3 年>25%', 'comment')
    collab.add_discussion('技术面 Agent', '技术面确实一般，但基本面好可以弥补', 'comment')
    
    # 自我评估
    collab.self_assess('技术面 Agent', {
        'confidence_level': 'medium',
        'data_quality': 'medium',
        'issues': ['缺少布林带数据', '成交量分析不足'],
        'suggestions': ['增加布林带分析', '改进成交量算法']
    })
    
    # 获取最终判断
    final = collab.get_final_judgments()
    print(f"\n最终判断:")
    for agent, judgment in final.items():
        print(f"  {agent}: {judgment['rating']} (置信度：{judgment['confidence']}%)")
    
    # 获取讨论记录
    print(f"\n讨论记录:")
    print(collab.get_discussion_log())
    
    # 完成协作
    collab.finalize({
        'rating': '买入',
        'confidence': 80,
        'reason': '基本面强劲 + 技术面改善'
    })
    
    print("\n✅ 测试完成！")
