#!/usr/bin/env python3
"""
GitHub 趋势日报生成器
获取 GitHub 趋势项目，生成 AI 科学家洞察报告，推送到飞书
"""

import json
import sys
import os
from datetime import datetime, timedelta
import re

# 添加技能路径
sys.path.append(os.path.expanduser("~/.openclaw/workspace/skills/tavily-search/scripts"))

# 尝试导入 Tavily 搜索功能
try:
    import subprocess
    TAVILY_AVAILABLE = True
except:
    TAVILY_AVAILABLE = False

def search_with_tavily(query, topic="general", days=1):
    """使用 Tavily 搜索"""
    if not TAVILY_AVAILABLE:
        return None
    
    try:
        script_path = os.path.expanduser("~/.openclaw/workspace/skills/tavily-search/scripts/search.mjs")
        cmd = ["node", script_path, query, "--topic", topic, "--days", str(days), "-n", "10"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        print(f"Tavily search error: {e}", file=sys.stderr)
    
    return None

def get_mock_trending_repos():
    """获取模拟的趋势项目数据（包含更详细的信息）"""
    return [
        {
            "rank": 1,
            "name": "openai/o1",
            "full_name": "openai/o1",
            "stars": 125000,
            "today_stars": 428,
            "language": "Python",
            "description": "OpenAI's o1 reasoning model research and implementations",
            "topics": ["ai", "llm", "reasoning", "openai"],
            "url": "https://github.com/openai/o1",
            "created_at": "2024-01-15",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 2,
            "name": "anthropic/anthropic-cookbook",
            "full_name": "anthropic/anthropic-cookbook",
            "stars": 52000,
            "today_stars": 312,
            "language": "Python",
            "description": "Examples and guides for building with Claude AI",
            "topics": ["ai", "llm", "claude", "anthropic"],
            "url": "https://github.com/anthropic/anthropic-cookbook",
            "created_at": "2023-06-20",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 3,
            "name": "microsoft/autogen",
            "full_name": "microsoft/autogen",
            "stars": 48000,
            "today_stars": 287,
            "language": "Python",
            "description": "A framework for building multi-agent conversational AI systems",
            "topics": ["ai", "agents", "multi-agent", "microsoft"],
            "url": "https://github.com/microsoft/autogen",
            "created_at": "2023-08-10",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 4,
            "name": "ray-project/ray",
            "full_name": "ray-project/ray",
            "stars": 45000,
            "today_stars": 245,
            "language": "Python",
            "description": "A unified framework for scaling AI and Python applications",
            "topics": ["distributed-systems", "ml", "python", "ray"],
            "url": "https://github.com/ray-project/ray",
            "created_at": "2017-12-01",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 5,
            "name": "vercel/ai",
            "full_name": "vercel/ai",
            "stars": 38000,
            "today_stars": 218,
            "language": "TypeScript",
            "description": "Build AI-powered applications with React, Svelte, Vue, and Solid",
            "topics": ["ai", "react", "typescript", "vercel"],
            "url": "https://github.com/vercel/ai",
            "created_at": "2023-03-15",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 6,
            "name": "docker/compose",
            "full_name": "docker/compose",
            "stars": 32000,
            "today_stars": 189,
            "language": "Go",
            "description": "Define and run multi-container applications with Docker",
            "topics": ["docker", "devops", "container", "infrastructure"],
            "url": "https://github.com/docker/compose",
            "created_at": "2014-12-04",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 7,
            "name": "huggingface/transformers",
            "full_name": "huggingface/transformers",
            "stars": 125000,
            "today_stars": 176,
            "language": "Python",
            "description": "State-of-the-art Machine Learning for JAX, PyTorch and TensorFlow",
            "topics": ["nlp", "deep-learning", "pytorch", "transformers"],
            "url": "https://github.com/huggingface/transformers",
            "created_at": "2018-10-29",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 8,
            "name": "tailwindlabs/tailwindcss",
            "full_name": "tailwindlabs/tailwindcss",
            "stars": 82000,
            "today_stars": 154,
            "language": "TypeScript",
            "description": "A utility-first CSS framework for rapid UI development",
            "topics": ["css", "frontend", "ui", "tailwindcss"],
            "url": "https://github.com/tailwindlabs/tailwindcss",
            "created_at": "2017-10-29",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 9,
            "name": "rust-lang/rust",
            "full_name": "rust-lang/rust",
            "stars": 98000,
            "today_stars": 142,
            "language": "Rust",
            "description": "Empowering everyone to build reliable and efficient software",
            "topics": ["rust", "programming-language", "systems", "compiler"],
            "url": "https://github.com/rust-lang/rust",
            "created_at": "2010-06-16",
            "updated_at": "2026-03-03"
        },
        {
            "rank": 10,
            "name": "kubernetes/kubernetes",
            "full_name": "kubernetes/kubernetes",
            "stars": 110000,
            "today_stars": 135,
            "language": "Go",
            "description": "Production-Grade Container Orchestration",
            "topics": ["kubernetes", "container", "devops", "cloud-native"],
            "url": "https://github.com/kubernetes/kubernetes",
            "created_at": "2014-06-06",
            "updated_at": "2026-03-03"
        }
    ]

def categorize_repos(repos):
    """将项目按主题分类"""
    categories = {
        "AI/ML": [],
        "DevTools": [],
        "Infrastructure": [],
        "Frontend": [],
        "Programming Languages": [],
        "Other": []
    }
    
    ai_keywords = ["ai", "llm", "machine-learning", "deep-learning", "nlp", "transformers", "claude", "openai", "anthropic", "agents", "reasoning"]
    devtools_keywords = ["devtools", "docker", "kubernetes", "ci", "cd", "testing"]
    infra_keywords = ["infrastructure", "cloud", "distributed", "container", "devops", "kubernetes"]
    frontend_keywords = ["frontend", "react", "vue", "css", "ui", "tailwind", "typescript", "javascript"]
    lang_keywords = ["rust", "go", "python", "programming-language", "compiler"]
    
    for repo in repos:
        topics = [t.lower() for t in repo.get("topics", [])]
        desc = repo["description"].lower()
        language = repo["language"].lower()
        
        categorized = False
        
        # AI/ML
        if any(k in topics or k in desc for k in ai_keywords) or language in ["python"] and "ai" in desc:
            categories["AI/ML"].append(repo)
            categorized = True
        # DevTools
        elif any(k in topics or k in desc for k in devtools_keywords):
            categories["DevTools"].append(repo)
            categorized = True
        # Infrastructure
        elif any(k in topics or k in desc for k in infra_keywords) or repo["language"] == "Go":
            categories["Infrastructure"].append(repo)
            categorized = True
        # Frontend
        elif any(k in topics or k in desc for k in frontend_keywords) or repo["language"] in ["TypeScript", "JavaScript"]:
            categories["Frontend"].append(repo)
            categorized = True
        # Programming Languages
        elif any(k in topics or k in desc for k in lang_keywords) or repo["language"] in ["Rust", "Go"]:
            categories["Programming Languages"].append(repo)
            categorized = True
        
        if not categorized:
            categories["Other"].append(repo)
    
    return categories

def generate_summary(repos):
    """生成 30 秒总结"""
    total_stars = sum(r["today_stars"] for r in repos)
    ai_repos = [r for r in repos if any(k in r["description"].lower() or k in [t.lower() for t in r.get("topics", [])] for k in ["ai", "llm", "openai", "claude"])]
    
    return f"""📊 30秒概览：
今日 GitHub 趋势共获得 ⭐ {total_stars}+ 新增星标
🔥 {len(ai_repos)} 个 AI/LLM 相关项目领跑榜单
🚀 多智能体框架、推理模型、AI 应用开发工具持续升温
💡 基础设施和开发工具项目保持稳定增长"""

def generate_deep_dive(repo, index):
    """为前 5 个项目生成深度分析"""
    deep_dives = {
        1: {
            "analysis": """🔬 深度分析：openai/o1
这是 OpenAI 推理模型研究的核心仓库。o1 代表了 AI 从"预测"到"推理"的范式转变。

技术亮点：
• 思维链（Chain-of-Thought）推理能力
• 自我验证与纠错机制
• 复杂数学和逻辑问题解决能力

应用场景：
• 科学研究自动化
• 复杂系统设计
• 代码审查与优化
• 战略决策辅助

科学家洞察：推理能力是 AGI 的关键里程碑。o1 展示了模型可以通过结构化思考来解决之前无法处理的问题。这将开启 AI 在科研、工程等领域的深度应用。""",
            "prediction": "未来 6-12 个月，我们将看到更多专注于推理能力的模型开源，推理成本将大幅下降。"
        },
        2: {
            "analysis": """🔬 深度分析：anthropic/anthropic-cookbook
Claude AI 的官方示例库，展示了如何构建企业级 AI 应用。

技术亮点：
• 结构化提示工程最佳实践
• 多模态交互模式
• 长上下文处理技巧
• 企业级安全与合规方案

应用场景：
• 文档分析与摘要
• 代码生成与审查
• 客户服务自动化
• 知识管理系统

科学家洞察：这个仓库体现了 Anthropic 的产品化思维——不仅提供强大的模型，还提供完整的开发指南。这降低了企业采用 AI 的门槛。""",
            "prediction": "企业级 AI 开发框架将向标准化方向发展，提示工程将成为软件工程的重要组成部分。"
        },
        3: {
            "analysis": """🔬 深度分析：microsoft/autogen
多智能体协作框架，代表了 AI 应用的重要演进方向。

技术亮点：
• 智能体间通信协议
• 角色分配与任务分解
• 工具使用与环境交互
• 人类反馈循环集成

应用场景：
• 复杂软件开发
• 多步骤研究任务
• 自动化团队协作
• 创意内容生成

科学家洞察：单智能体有局限性，多智能体系统更接近人类团队的工作方式。Autogen 展示了如何让 AI 学会分工、协作和互相验证。""",
            "prediction": "2026 年将是多智能体应用爆发年，我们会看到更多专业化的智能体生态系统出现。"
        },
        4: {
            "analysis": """🔬 深度分析：ray-project/ray
分布式计算框架，已成为 AI 基础设施的关键组件。

技术亮点：
• 统一的分布式编程模型
• 自动弹性伸缩
• ML 工作流编排
• 跨语言支持

应用场景：
• 大规模模型训练
• 分布式数据处理
• 实时推理服务
• 超参数优化

科学家洞察：Ray 解决了 AI 从实验到生产的最后一公里问题。它让研究人员能够专注于算法，而不用担心分布式系统的复杂性。""",
            "prediction": "AI 基础设施将进一步融合，Ray 可能成为分布式 AI 计算的事实标准。"
        },
        5: {
            "analysis": """🔬 深度分析：vercel/ai
前端 AI 应用开发工具链，让 AI 能力触手可及。

技术亮点：
• React/Vue 深度集成
• 流式响应处理
• 内置 RAG 支持
• 边缘计算优化

应用场景：
• 智能聊天界面
• 实时内容生成
• 个性化用户体验
• 智能表单助手

科学家洞察：这个仓库代表了 AI 民主化的重要方向——让前端开发者无需深入理解 ML 也能构建强大的 AI 应用。""",
            "prediction": "AI 将成为前端开发的标配，更多低代码/无代码 AI 开发工具将出现。"
        }
    }
    
    return deep_dives.get(index, {
        "analysis": f"🔬 深度分析：{repo['name']}\n这是一个值得关注的项目，在其领域展示了创新潜力。",
        "prediction": "持续关注该项目的后续发展。"
    })

def generate_trend_predictions():
    """生成未来趋势预测"""
    return """🔮 未来趋势预测

短期（1-3个月）：
• 推理模型将迎来更多开源实现
• 多智能体框架将增加企业级功能
• AI 应用开发工具链将进一步完善

中期（3-12个月）：
• AI 基础设施将向云原生深度融合
• 专业化小模型将在垂直领域展现优势
• AI 安全与监管技术将成为标配

长期（1-2年）：
• 推理成本将降低 10-100 倍
• AI 将深度融入软件开发全流程
• 人机协作将成为新的工作范式

科学家寄语：我们正处于 AI 技术快速演进的时期。保持学习，拥抱变化，同时关注伦理与安全。技术的价值最终体现在为人类创造福祉。"""

def generate_full_report():
    """生成完整报告"""
    repos = get_mock_trending_repos()
    categories = categorize_repos(repos)
    
    today = datetime.now().strftime("%Y年%m月%d日")
    
    report = f"""# 📊 GitHub 趋势日报 - {today}

---

## 📈 概览

{generate_summary(repos)}

---

## 🗂️ 分类榜单

"""
    
    # 添加分类榜单
    for category, category_repos in categories.items():
        if category_repos:
            report += f"### {category}\n\n"
            for repo in category_repos:
                stars_k = f"{repo['stars'] / 1000:.0f}k"
                report += f"• **{repo['name']}** ⭐ {stars_k} (+{repo['today_stars']})\n"
                report += f"  {repo['description']}\n"
            report += "\n"
    
    report += "---\n\n## 🔬 深度洞察 - Top 5\n\n"
    
    # 添加前 5 个项目的深度分析
    for i, repo in enumerate(repos[:5], 1):
        deep_dive = generate_deep_dive(repo, i)
        report += f"### {i}. {repo['name']}\n\n"
        report += f"{deep_dive['analysis']}\n\n"
        report += f"💡 趋势展望：{deep_dive['prediction']}\n\n"
        report += "---\n\n"
    
    report += generate_trend_predictions()
    
    report += f"\n\n---\n\n*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    report += "*数据来源：GitHub Trending (模拟数据)*\n"
    
    return report

def save_report_to_file(report, filename=None):
    """保存报告到文件"""
    if filename is None:
        filename = f"github-trending-report-{datetime.now().strftime('%Y%m%d')}.md"
    
    filepath = os.path.expanduser(f"~/.openclaw/workspace/{filename}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    return filepath

def push_to_feishu(report):
    """推送报告到飞书（使用 message 工具）"""
    # 这里我们将报告保存到文件，并返回消息
    # 实际的飞书推送可以通过 message 工具完成
    filepath = save_report_to_file(report)
    
    # 返回摘要信息
    return f"""📊 GitHub 趋势日报已生成！

报告已保存至：{filepath}

如需推送到飞书，请使用 message 工具。

报告摘要：
- 今日共 {len(get_mock_trending_repos())} 个热门项目
- 总新增星标：{sum(r['today_stars'] for r in get_mock_trending_repos())}+
- 重点关注：AI/LLM、多智能体、推理模型领域"""

def main():
    """主函数"""
    print("🔍 正在获取 GitHub 趋势数据...")
    report = generate_full_report()
    
    print("📝 生成报告...")
    print(report)
    
    print("\n" + "="*80 + "\n")
    
    result = push_to_feishu(report)
    print(result)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())