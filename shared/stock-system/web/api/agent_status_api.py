#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 状态 API

提供 Agent TODO/DOING 状态数据
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

STATUS_DIR = '/Users/egg/.openclaw/workspace/shared/stock-system/agent-status'


class AgentStatusHandler(SimpleHTTPRequestHandler):
    """Agent 状态 API 处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/agent-status':
            # 获取所有 Agent 状态
            self.send_json(self.get_all_status())
        elif parsed.path.startswith('/api/agent-status/'):
            # 获取单个 Agent 状态
            agent_id = parsed.path.split('/')[-1]
            self.send_json(self.get_agent_status(agent_id))
        elif parsed.path == '/api/agent-summary':
            # 获取汇总数据
            self.send_json(self.get_summary())
        else:
            self.send_error(404, "Not Found")
    
    def get_all_status(self):
        """获取所有 Agent 状态"""
        status_list = []
        
        if not os.path.exists(STATUS_DIR):
            return {'error': 'Status directory not found'}
        
        for filename in os.listdir(STATUS_DIR):
            if filename.endswith('.json') and filename != 'summary.json':
                filepath = os.path.join(STATUS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    status_list.append(json.load(f))
        
        return {'agents': status_list}
    
    def get_agent_status(self, agent_id):
        """获取单个 Agent 状态"""
        filepath = os.path.join(STATUS_DIR, f"{agent_id}.json")
        
        if not os.path.exists(filepath):
            return {'error': 'Agent not found'}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_summary(self):
        """获取汇总数据"""
        filepath = os.path.join(STATUS_DIR, 'summary.json')
        
        if not os.path.exists(filepath):
            return {'error': 'Summary not found'}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


def run_server(port=8001):
    """运行 API 服务器"""
    server = HTTPServer(('localhost', port), AgentStatusHandler)
    print(f"🚀 Agent Status API 运行在 http://localhost:{port}")
    print(f"📊 状态目录：{STATUS_DIR}")
    print()
    print("API 端点:")
    print("  GET /api/agent-status      - 获取所有 Agent 状态")
    print("  GET /api/agent-status/:id  - 获取单个 Agent 状态")
    print("  GET /api/agent-summary     - 获取汇总数据")
    print()
    server.serve_forever()


if __name__ == "__main__":
    run_server()
