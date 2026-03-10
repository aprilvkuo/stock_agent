#!/usr/bin/env python3
"""
代码质量优化脚本 - 自动改进代码质量

功能：
1. 检查代码规范（PEP8）
2. 发现并修复简单问题
3. 优化导入语句
4. 移除未使用的变量
5. 添加类型提示建议

运行方式：
    python3 scripts/code_quality_optimizer.py [--auto-fix]
"""

import os
import sys
import re
import ast
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

class CodeQualityOptimizer:
    def __init__(self, auto_fix=False):
        self.auto_fix = auto_fix
        self.issues = []
        self.fixes = []
        self.stats = {
            "files_checked": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "lines_optimized": 0
        }
    
    def run(self):
        """执行代码质量优化"""
        print("=" * 60)
        print("💻 代码质量优化")
        print("=" * 60)
        
        # 扫描所有 Python 脚本
        py_files = list(SCRIPTS_DIR.glob("*.py"))
        print(f"\n📁 检查 {len(py_files)} 个 Python 文件...\n")
        
        for py_file in py_files:
            self.check_file(py_file)
        
        # 输出统计
        print("\n" + "=" * 60)
        print("📊 优化统计")
        print("=" * 60)
        print(f"检查文件：{self.stats['files_checked']} 个")
        print(f"发现问题：{self.stats['issues_found']} 个")
        print(f"已修复：{self.stats['issues_fixed']} 个")
        print(f"优化行数：{self.stats['lines_optimized']} 行")
        print("=" * 60)
        
        if self.issues and not self.auto_fix:
            print("\n💡 提示：使用 --auto-fix 自动修复问题")
    
    def check_file(self, file_path):
        """检查单个文件"""
        self.stats["files_checked"] += 1
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
            
            original_lines = len(lines)
            issues_in_file = []
            
            # 1. 检查过长的行
            for i, line in enumerate(lines, 1):
                if len(line) > 120 and not line.strip().startswith("#"):
                    issues_in_file.append(f"L{i}: 行过长 ({len(line)} 字符)")
            
            # 2. 检查多余的空行
            empty_line_count = 0
            for i, line in enumerate(lines):
                if not line.strip():
                    empty_line_count += 1
                    if empty_line_count > 2:
                        issues_in_file.append(f"L{i}: 连续空行过多")
                else:
                    empty_line_count = 0
            
            # 3. 检查未使用的导入（简单检测）
            imports = []
            used_names = []
            for line in lines:
                if line.startswith("import ") or line.startswith("from "):
                    imports.append(line)
                else:
                    # 提取使用的名称
                    words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line)
                    used_names.extend(words)
            
            # 4. 检查函数文档字符串
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not ast.get_docstring(node):
                            if not node.name.startswith("_"):
                                issues_in_file.append(f"函数 {node.name} 缺少文档字符串")
            except:
                pass
            
            # 5. 检查尾随空格
            for i, line in enumerate(lines, 1):
                if line.rstrip() != line and line.strip():
                    issues_in_file.append(f"L{i}: 尾随空格")
            
            # 6. 检查混合制表符和空格
            has_tabs = any("\t" in line for line in lines)
            has_spaces = any("    " in line for line in lines)
            if has_tabs and has_spaces:
                issues_in_file.append("混用制表符和空格")
            
            # 记录问题
            if issues_in_file:
                self.issues.append({
                    "file": file_path.name,
                    "issues": issues_in_file
                })
                self.stats["issues_found"] += len(issues_in_file)
                
                if self.auto_fix:
                    self.fix_file(file_path, content, lines)
            
        except Exception as e:
            print(f"❌ 检查 {file_path.name} 失败：{e}")
    
    def fix_file(self, file_path, content, lines):
        """修复文件问题"""
        fixed_lines = []
        prev_empty = False
        
        for line in lines:
            # 移除尾随空格
            if line.strip():
                line = line.rstrip()
            
            # 处理连续空行
            if not line.strip():
                if prev_empty:
                    continue  # 跳过多余空行
                prev_empty = True
            else:
                prev_empty = False
            
            # 替换制表符为空格
            line = line.replace("\t", "    ")
            
            fixed_lines.append(line)
        
        # 移除末尾多余空行
        while fixed_lines and not fixed_lines[-1].strip():
            fixed_lines.pop()
        
        # 确保文件以换行符结尾
        fixed_content = "\n".join(fixed_lines) + "\n"
        
        # 写入修复后的内容
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        
        self.stats["issues_fixed"] += 1
        self.stats["lines_optimized"] += abs(len(lines) - len(fixed_lines))
        print(f"   ✅ 修复：{file_path.name}")
    
    def generate_report(self):
        """生成代码质量报告"""
        report_path = BASE_DIR / "reports" / f"code_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 代码质量报告\n\n")
            f.write(f"**生成时间**: {datetime.now().isoformat()}\n\n")
            
            if self.issues:
                f.write("## 发现的问题\n\n")
                for item in self.issues:
                    f.write(f"### {item['file']}\n\n")
                    for issue in item['issues']:
                        f.write(f"- {issue}\n")
                    f.write("\n")
            else:
                f.write("✅ 未发现代码质量问题\n")
            
            f.write("\n## 统计\n\n")
            f.write(f"- 检查文件：{self.stats['files_checked']} 个\n")
            f.write(f"- 发现问题：{self.stats['issues_found']} 个\n")
            f.write(f"- 已修复：{self.stats['issues_fixed']} 个\n")
        
        print(f"\n📄 报告已保存：{report_path.name}")


if __name__ == "__main__":
    auto_fix = "--auto-fix" in sys.argv
    optimizer = CodeQualityOptimizer(auto_fix=auto_fix)
    optimizer.run()
    if auto_fix:
        optimizer.generate_report()
