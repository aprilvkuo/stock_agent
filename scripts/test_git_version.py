#!/usr/bin/env python3
"""
Git 版本控制测试脚本
测试 Git 提交流程是否正常工作
"""

import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from git_version_control import GitVersionControl

def test_basic_commit():
    """测试基本提交功能"""
    print("\n" + "="*60)
    print("🧪 测试 1: 基本 Git 提交")
    print("="*60)
    
    git = GitVersionControl()
    
    # 创建测试文件
    test_file = os.path.join(os.path.dirname(__file__), 'test_temp.md')
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("# 测试文件\n\n这是 Git 版本控制测试文件\n")
    
    # 提交
    record = git.commit(
        agent_name="系统 Agent",
        message="测试基本提交功能",
        files=['test_temp.md'],
        auto_push=False  # 测试时不 push
    )
    
    if record:
        print(f"✅ 提交成功：{record['hash'][:8]}")
        print(f"   Agent: {record['agent']}")
        print(f"   消息：{record['message']}")
        print(f"   时间：{record['timestamp']}")
    else:
        print("❌ 提交失败")
    
    # 清理测试文件
    os.remove(test_file)
    print(f"✅ 测试文件已清理\n")
    
    return record is not None


def test_history():
    """测试历史记录查询"""
    print("\n" + "="*60)
    print("🧪 测试 2: 查询提交历史")
    print("="*60)
    
    git = GitVersionControl()
    history = git.get_history(limit=5)
    
    if history:
        print(f"✅ 查询到 {len(history)} 条记录")
        for record in history:
            print(f"   - [{record['timestamp']}] {record['agent']}: {record['message'][:50]}")
    else:
        print("⚠️ 暂无历史记录")
    
    print()
    return True


def test_agent_mapping():
    """测试 Agent 映射"""
    print("\n" + "="*60)
    print("🧪 测试 3: Agent Git User 映射")
    print("="*60)
    
    from git_version_control import AGENT_GIT_USERS
    
    print("\n已配置的 Agent Git Users:\n")
    for agent, value in AGENT_GIT_USERS.items():
        if isinstance(value, tuple):
            name, email = value
            print(f"   {agent:15} → {name:15} <{email}>")
        else:
            print(f"   {agent:15} → {value}")
    
    print()
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Git 版本控制模块 - 功能测试")
    print("="*60)
    
    results = []
    
    # 测试 1: 基本提交
    results.append(("基本提交", test_basic_commit()))
    
    # 测试 2: 历史记录
    results.append(("历史记录", test_history()))
    
    # 测试 3: Agent 映射
    results.append(("Agent 映射", test_agent_mapping()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} - {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过\n")
    
    if passed == total:
        print("🎉 所有测试通过！Git 版本控制模块工作正常\n")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
