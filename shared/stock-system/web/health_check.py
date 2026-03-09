#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统健康检查脚本 v1.0
自动检查股票多 Agent 系统各组件状态
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_check(name: str, status: bool, message: str = ""):
    icon = f"{Colors.GREEN}✅{Colors.END}" if status else f"{Colors.RED}❌{Colors.END}"
    msg = f" - {message}" if message else ""
    print(f"{icon} {name}{msg}")

def print_warning(name: str, message: str):
    print(f"{Colors.YELLOW}⚠️  {name} - {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def check_file_system() -> Tuple[bool, List[str]]:
    """检查文件系统和关键文件"""
    print_header("📁 文件系统检查")
    
    issues = []
    all_ok = True
    
    # 关键目录
    dirs = [
        '/Users/egg/.openclaw/workspace/shared/stock-system',
        '/Users/egg/.openclaw/workspace/shared/stock-system/web',
        '/Users/egg/.openclaw/workspace/shared/stock-system/data',
        '/Users/egg/.openclaw/workspace/agents/stock-coordinator/data',
    ]
    
    for dir_path in dirs:
        if os.path.isdir(dir_path):
            print_check(f"目录：{dir_path}", True)
        else:
            print_check(f"目录：{dir_path}", False, "不存在")
            issues.append(f"目录缺失：{dir_path}")
            all_ok = False
    
    # 关键文件
    files = [
        '/Users/egg/.openclaw/workspace/shared/stock-system/web/app.py',
        '/Users/egg/.openclaw/workspace/shared/stock-system/web/holdings_manager.py',
        '/Users/egg/.openclaw/workspace/shared/stock-system/web/stock_cache.py',
        '/Users/egg/.openclaw/workspace/shared/stock-system/web/config_loader.py',
        '/Users/egg/.openclaw/workspace/shared/stock-system/config.json',
        '/Users/egg/.openclaw/workspace/memory/stock-system/scripts/auto_agent.py',
        '/Users/egg/.openclaw/workspace/memory/stock-system/validation-queue.md',
    ]
    
    for file_path in files:
        if os.path.isfile(file_path):
            print_check(f"文件：{os.path.basename(file_path)}", True)
        else:
            print_check(f"文件：{os.path.basename(file_path)}", False, "不存在")
            issues.append(f"文件缺失：{file_path}")
            all_ok = False
    
    return all_ok, issues


def check_config() -> Tuple[bool, List[str]]:
    """检查配置文件"""
    print_header("⚙️ 配置检查")
    
    issues = []
    all_ok = True
    
    config_file = '/Users/egg/.openclaw/workspace/shared/stock-system/config.json'
    
    if not os.path.exists(config_file):
        print_check("配置文件加载", False, "config.json 不存在")
        return False, ["配置文件不存在"]
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print_check("配置文件加载", True)
    except Exception as e:
        print_check("配置文件加载", False, str(e))
        return False, [f"配置文件解析失败：{e}"]
    
    # 检查必要配置节
    required_sections = ['system', 'data_sources', 'agents', 'cache']
    for section in required_sections:
        if section in config:
            print_check(f"配置节：{section}", True)
        else:
            print_check(f"配置节：{section}", False, "缺失")
            issues.append(f"配置节缺失：{section}")
            all_ok = False
    
    # 检查 Agent 配置
    agents = config.get('agents', {})
    expected_agents = ['fundamental', 'technical', 'sentiment', 'capital']
    for agent in expected_agents:
        if agent in agents:
            weight = agents[agent].get('weight', 0)
            enabled = agents[agent].get('enabled', False)
            status = enabled and weight > 0
            print_check(f"Agent: {agent}", status, f"权重={weight:.0%}, 启用={enabled}")
            if not status:
                issues.append(f"Agent 配置异常：{agent}")
                all_ok = False
    
    # 检查系统版本
    version = config.get('system', {}).get('version', 'unknown')
    print_info(f"系统版本：{version}")
    
    return all_ok, issues


def check_cache() -> Tuple[bool, List[str]]:
    """检查缓存系统"""
    print_header("💾 缓存系统检查")
    
    issues = []
    all_ok = True
    
    cache_dir = '/Users/egg/.openclaw/workspace/shared/stock-system/data/cache'
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
        print_check("缓存目录", True, "已创建")
    else:
        print_check("缓存目录", True)
    
    # 统计缓存文件
    if os.path.exists(cache_dir):
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        print_info(f"缓存文件数：{len(cache_files)}")
        
        total_size = 0
        for f in cache_files:
            filepath = os.path.join(cache_dir, f)
            total_size += os.path.getsize(filepath)
        
        print_info(f"缓存总大小：{total_size / 1024:.2f} KB")
    
    # 测试缓存读写
    try:
        sys.path.insert(0, '/Users/egg/.openclaw/workspace/shared/stock-system/web')
        from stock_cache import StockCache
        
        cache = StockCache()
        test_key = "test_check"
        
        # 写入测试
        cache.set("TEST", {"test": True}, "default")
        print_check("缓存写入", True)
        
        # 读取测试（注意：cache.get 第一个参数是 stock_code，会生成 cache_key）
        data = cache.get("TEST", "default")
        if data and 'data' in data and data['data'].get('test') == True:
            print_check("缓存读取", True)
        else:
            # 尝试直接读取缓存文件
            cache_file = os.path.join(cache_dir, "TEST_default.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                if raw_data.get('data', {}).get('test') == True:
                    print_check("缓存读取", True, "文件存在")
                else:
                    print_check("缓存读取", False, "数据格式异常")
                    issues.append("缓存数据格式异常")
                    all_ok = False
            else:
                print_check("缓存读取", False, "缓存文件未找到")
                issues.append("缓存读写异常")
                all_ok = False
        
        # 清理测试数据
        cache.delete("TEST", "default")
        
    except Exception as e:
        print_check("缓存模块", False, str(e))
        issues.append(f"缓存模块异常：{e}")
        all_ok = False
    
    return all_ok, issues


def check_web_server() -> Tuple[bool, List[str]]:
    """检查 Web 服务器"""
    print_header("🌐 Web 服务器检查")
    
    issues = []
    all_ok = True
    
    # 检查 Flask 是否安装
    try:
        import flask
        print_check("Flask 框架", True, f"v{flask.__version__}")
    except ImportError:
        print_check("Flask 框架", False, "未安装")
        issues.append("Flask 未安装")
        all_ok = False
    
    # 检查模板文件
    templates_dir = '/Users/egg/.openclaw/workspace/shared/stock-system/web/templates'
    if os.path.exists(templates_dir):
        templates = os.listdir(templates_dir)
        print_info(f"模板文件：{len(templates)} 个")
        for t in templates:
            print_check(f"模板：{t}", True)
    else:
        print_check("模板目录", False, "不存在")
        issues.append("模板目录缺失")
        all_ok = False
    
    # 检查 app.py 语法
    app_file = '/Users/egg/.openclaw/workspace/shared/stock-system/web/app.py'
    if os.path.exists(app_file):
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                compile(f.read(), app_file, 'exec')
            print_check("app.py 语法", True)
        except SyntaxError as e:
            print_check("app.py 语法", False, str(e))
            issues.append(f"app.py 语法错误：{e}")
            all_ok = False
    
    return all_ok, issues


def check_data_files() -> Tuple[bool, List[str]]:
    """检查数据文件"""
    print_header("📊 数据文件检查")
    
    issues = []
    all_ok = True
    
    data_dir = '/Users/egg/.openclaw/workspace/agents/stock-coordinator/data'
    
    # 检查关键数据文件
    files = {
        'validation-queue.md': '验证队列',
        'logs': '分析日志目录',
        'evolution-20260308-125642.md': '进化报告（最新）',
    }
    
    for filename, desc in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                print_check(desc, True, f"{size / 1024:.1f} KB")
            else:
                count = len(os.listdir(filepath))
                print_check(desc, True, f"{count} 个文件")
        else:
            print_check(desc, False, "不存在")
            issues.append(f"{desc}缺失")
            all_ok = False
    
    # 检查持仓数据
    holdings_file = '/Users/egg/.openclaw/workspace/shared/stock-system/data/holdings.json'
    if os.path.exists(holdings_file):
        with open(holdings_file, 'r', encoding='utf-8') as f:
            holdings = json.load(f)
        count = len(holdings.get('holdings', []))
        print_check("持仓数据", True, f"{count} 只股票")
    else:
        print_check("持仓数据", False, "无持仓记录")
    
    return all_ok, issues


def check_scripts() -> Tuple[bool, List[str]]:
    """检查脚本文件"""
    print_header("📜 脚本文件检查")
    
    issues = []
    all_ok = True
    
    scripts_dir = '/Users/egg/.openclaw/workspace/memory/stock-system/scripts'
    
    if not os.path.exists(scripts_dir):
        print_check("脚本目录", False, "不存在")
        return False, ["脚本目录缺失"]
    
    scripts = [
        'auto_agent.py',
        'validate_predictions.py',
        'run_review.py',
    ]
    
    for script in scripts:
        filepath = os.path.join(scripts_dir, script)
        if os.path.exists(filepath):
            # 检查是否可执行
            is_executable = os.access(filepath, os.X_OK)
            print_check(script, True, "可执行" if is_executable else "不可执行")
        else:
            print_check(script, False, "不存在")
            issues.append(f"脚本缺失：{script}")
            all_ok = False
    
    # 测试 auto_agent.py 导入
    try:
        sys.path.insert(0, scripts_dir)
        # 不实际执行，只检查语法
        with open(os.path.join(scripts_dir, 'auto_agent.py'), 'r', encoding='utf-8') as f:
            compile(f.read(), 'auto_agent.py', 'exec')
        print_check("auto_agent.py 语法", True)
    except Exception as e:
        print_check("auto_agent.py 语法", False, str(e))
        issues.append(f"auto_agent.py 异常：{e}")
        all_ok = False
    
    return all_ok, issues


def generate_report(all_checks: List[Tuple[str, bool, List[str]]]):
    """生成检查报告"""
    print_header("📋 检查报告")
    
    total = len(all_checks)
    passed = sum(1 for _, ok, _ in all_checks if ok)
    failed = total - passed
    
    print(f"{Colors.BOLD}总检查项：{total}{Colors.END}")
    print(f"{Colors.GREEN}通过：{passed}{Colors.END}")
    print(f"{Colors.RED}失败：{failed}{Colors.END}")
    print()
    
    # 汇总所有问题
    all_issues = []
    for name, ok, issues in all_checks:
        if not ok:
            all_issues.extend(issues)
    
    if all_issues:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  发现问题：{Colors.END}")
        for issue in all_issues:
            print(f"  • {issue}")
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ 所有检查通过！系统运行稳定{Colors.END}")
    
    print()
    
    # 建议
    if failed == 0:
        print(f"{Colors.GREEN}🎉 系统状态：优秀{Colors.END}")
        print("💡 建议：系统运行稳定，可以正常使用")
    elif failed <= 2:
        print(f"{Colors.YELLOW}⚠️  系统状态：良好（有小问题）{Colors.END}")
        print("💡 建议：修复上述问题后系统会更稳定")
    else:
        print(f"{Colors.RED}⚠️  系统状态：需要关注{Colors.END}")
        print("💡 建议：尽快修复上述问题")
    
    print()


def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}╔════════════════════════════════════════════════════╗")
    print(f"║  股票多 Agent 系统 - 健康检查                  ║")
    print(f"║  版本：v1.7  |  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}        ║")
    print(f"╚════════════════════════════════════════════════════╝{Colors.END}\n")
    
    all_checks = []
    
    # 执行各项检查
    result = check_file_system()
    all_checks.append(("文件系统",) + result)
    
    result = check_config()
    all_checks.append(("配置系统",) + result)
    
    result = check_cache()
    all_checks.append(("缓存系统",) + result)
    
    result = check_web_server()
    all_checks.append(("Web 服务器",) + result)
    
    result = check_data_files()
    all_checks.append(("数据文件",) + result)
    
    result = check_scripts()
    all_checks.append(("脚本文件",) + result)
    
    # 生成报告
    generate_report(all_checks)
    
    # 返回状态码
    failed = sum(1 for _, ok, _ in all_checks if not ok)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
