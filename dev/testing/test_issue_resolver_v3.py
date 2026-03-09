#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issue 自动处理系统 v3.0 - 单元测试
测试优先级排序、单线程逻辑等核心功能
"""

import sys
import os

# 添加项目根目录到路径
workspace = "/Users/egg/.openclaw/workspace"
sys.path.insert(0, workspace)

# 模拟 GitHub Token（避免实际 API 调用）
os.environ["GITHUB_TOKEN"] = "test_token"

# 导入模块
import importlib.util
spec = importlib.util.spec_from_file_location("auto_issue_resolver", f"{workspace}/scripts/auto_issue_resolver.py")
auto_resolver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_resolver)

IssueValidator = auto_resolver.IssueValidator
IssueAutoResolver = auto_resolver.IssueAutoResolver
PRIORITY_LABELS = auto_resolver.PRIORITY_LABELS


def test_priority_sorting():
    """测试优先级排序"""
    print("\n" + "="*60)
    print("测试 1: 优先级排序")
    print("="*60)
    
    validator = IssueValidator()
    
    # 模拟 Issue 列表
    issues = [
        {
            "number": 1,
            "title": "低优先级任务",
            "labels": [{"name": "low"}],
            "created_at": "2026-03-01T00:00:00Z"
        },
        {
            "number": 2,
            "title": "紧急 Bug",
            "labels": [{"name": "critical"}],
            "created_at": "2026-03-02T00:00:00Z"
        },
        {
            "number": 3,
            "title": "改进工单",
            "labels": [{"name": "improvement-ticket"}],
            "created_at": "2026-03-03T00:00:00Z"
        },
        {
            "number": 4,
            "title": "高优先级任务",
            "labels": [{"name": "high"}],
            "created_at": "2026-03-04T00:00:00Z"
        },
        {
            "number": 5,
            "title": "无标签任务",
            "labels": [],
            "created_at": "2026-03-05T00:00:00Z"
        }
    ]
    
    print("\n原始 Issue 列表:")
    for issue in issues:
        print(f"  #{issue['number']}: {issue['title']} - 标签：{[l['name'] for l in issue['labels']]}")
    
    # 计算优先级
    print("\n优先级排序结果:")
    sorted_issues = sorted(issues, key=lambda x: validator.get_priority(x))
    
    for i, issue in enumerate(sorted_issues, 1):
        priority = validator.get_priority(issue)
        priority_name = validator.get_priority_name(priority)
        print(f"  {i}. #{issue['number']} [{priority_name}] {issue['title']}")
    
    # 验证排序
    assert sorted_issues[0]["number"] == 2, "紧急 Bug 应该排第一"
    assert sorted_issues[1]["number"] == 4, "高优先级应该排第二"
    assert sorted_issues[2]["number"] == 3, "改进工单应该排第三"
    
    print("\n✅ 优先级排序测试通过！")


def test_issue_validation():
    """测试 Issue 验证"""
    print("\n" + "="*60)
    print("测试 2: Issue 验证")
    print("="*60)
    
    validator = IssueValidator()
    
    # 测试用例
    test_cases = [
        {
            "title": "改进工单：优化代码结构",
            "body": "需要优化代码结构，提高可维护性",
            "labels": [{"name": "improvement-ticket"}],
            "expected_valid": True,
            "expected_reason": "改进工单"
        },
        {
            "title": "测试 Issue",
            "body": "这是一个测试",
            "labels": [],
            "expected_valid": False,
            "expected_reason": "测试"
        },
        {
            "title": "内容",
            "body": "短",
            "labels": [],
            "expected_valid": False,
            "expected_reason": "内容过短"
        },
        {
            "title": "添加新功能",
            "body": "需要添加一个新功能",
            "labels": [],
            "expected_valid": True,
            "expected_reason": "有效任务特征"
        },
        {
            "title": "修复 Bug",
            "body": "@programmer-agent 请修复这个 Bug",
            "labels": [],
            "expected_valid": True,
            "expected_reason": "指定 Agent"
        }
    ]
    
    print("\n验证测试:")
    for i, case in enumerate(test_cases, 1):
        issue = {
            "title": case["title"],
            "body": case["body"],
            "labels": case["labels"],
            "created_at": "2026-03-09T00:00:00Z"
        }
        
        is_valid, reason = validator.is_valid_issue(issue)
        
        status = "✅" if is_valid == case["expected_valid"] else "❌"
        print(f"\n  {status} 测试{i}: {case['title']}")
        print(f"     预期：{'有效' if case['expected_valid'] else '无效'}")
        print(f"     实际：{'有效' if is_valid else '无效'} - {reason}")
        
        assert is_valid == case["expected_valid"], f"测试{i}失败"
    
    print("\n✅ Issue 验证测试通过！")


def test_agent_identification():
    """测试 Agent 识别"""
    print("\n" + "="*60)
    print("测试 3: Agent 识别")
    print("="*60)
    
    resolver = IssueAutoResolver()
    
    # 测试用例
    test_cases = [
        {
            "title": "修复代码 Bug",
            "body": "需要修复代码中的 Bug",
            "expected_agent": "programmer"
        },
        {
            "title": "财报分析优化",
            "body": "改进财报分析逻辑",
            "expected_agent": "fundamental"
        },
        {
            "title": "技术指标改进",
            "body": "优化 MACD 和 RSI 计算",
            "expected_agent": "technical"
        },
        {
            "title": "任务",
            "body": "请 @programmer-agent 处理这个任务",
            "expected_agent": "programmer"
        }
    ]
    
    print("\nAgent 识别测试:")
    for i, case in enumerate(test_cases, 1):
        issue = {
            "title": case["title"],
            "body": case["body"]
        }
        
        agent = resolver.identify_responsible_agent(issue)
        
        status = "✅" if agent == case["expected_agent"] else "❌"
        print(f"\n  {status} 测试{i}: {case['title']}")
        print(f"     预期：{case['expected_agent']}")
        print(f"     实际：{agent}")
        
        assert agent == case["expected_agent"], f"测试{i}失败"
    
    print("\n✅ Agent 识别测试通过！")


def test_priority_labels():
    """测试优先级标签配置"""
    print("\n" + "="*60)
    print("测试 4: 优先级标签配置")
    print("="*60)
    
    print("\n优先级标签配置:")
    for label, priority in sorted(PRIORITY_LABELS.items(), key=lambda x: x[1]):
        print(f"  {label}: {priority}")
    
    assert PRIORITY_LABELS["critical"] == 1, "critical 应该是最高优先级"
    assert PRIORITY_LABELS["high"] == 2, "high 应该是第二优先级"
    assert PRIORITY_LABELS["medium"] == 3, "medium 应该是默认优先级"
    assert PRIORITY_LABELS["low"] == 4, "low 应该是最低优先级"
    
    print("\n✅ 优先级标签配置测试通过！")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 Issue 自动处理系统 v3.0 - 单元测试")
    print("="*60)
    
    try:
        test_priority_sorting()
        test_issue_validation()
        test_agent_identification()
        test_priority_labels()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常：{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
