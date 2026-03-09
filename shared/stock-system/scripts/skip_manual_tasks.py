#!/usr/bin/env python3
"""跳过需要人工干预的任务"""
import re

TODO_FILE = '/Users/egg/.openclaw/workspace/TODO.md'

with open(TODO_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 需要跳过的任务（添加 [需人工] 标记）
skip_tasks = [
    '每 24 小时自动执行一次',
    '生成自我优化报告',
]

for task in skip_tasks:
    old = f'- [ ] {task}'
    new = f'- [ ] [需人工] {task}'
    content = content.replace(old, new, 1)

with open(TODO_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已标记需要人工干预的任务")
