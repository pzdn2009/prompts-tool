"""
CLI 主入口 - 修复版本，延迟导入重型模块
"""

import sys
import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .core.config import Config
from .core.repo import PromptRepo
# 延迟导入，避免重型库导入错误
# from .core.search import PromptSearcher
from .core.parser import PromptParser
from .utils.clipboard import ClipboardManager

# 创建 Typer 应用
app = typer.Typer(
    name="prompts",
    help="🚀 一个智能的 Prompt 管理和搜索工具",
    add_completion=False,
)

# 创建 Rich 控制台
console = Console()


def print_banner():
    """打印欢迎横幅"""
    banner = """
    🚀 Prompts Tool v0.1.0 (修复版)
    ===================================
    智能 Prompt 管理助手
    """
    console.print(Panel(banner, style="bold blue"))


def get_searcher(config, repo):
    """延迟获取搜索器，避免导入错误"""
    try:
        from .core.search import PromptSearcher
        return PromptSearcher(config, repo)
    except ImportError:
        console.print("⚠️  语义搜索功能不可用（缺少 sentence-transformers 库）", style="yellow")
        console.print("💡 请运行: pip install sentence-transformers faiss-cpu", style="blue")
        console.print("🔍 将使用关键词搜索替代", style="blue")
        return None


@app.command()
def main(
    query: Optional[str] = typer.Argument(None, help="搜索查询或需求描述"),
    list_prompts: bool = typer.Option(False, "--list", "-l", help="列出所有 Prompt 文件"),
    update: bool = typer.Option(False, "--update", "-u", help="更新远程仓库的 Prompt Repo"),
    ui: bool = typer.Option(False, "--ui", help="启动 Web 界面"),
    preview: Optional[int] = typer.Option(None, "--preview", "-p", help="显示前 N 行预览"),
    filter_keyword: Optional[str] = typer.Option(None, "--filter", "-f", help="按关键词过滤"),
    top_k: int = typer.Option(5, "--top", "-t", help="返回前 K 个搜索结果"),
    rebuild_index: bool = typer.Option(False, "--rebuild-index", help="重建搜索索引"),
    config_path: Optional[str] = typer.Option(None, "--config", help="配置文件路径"),
):
    """
    Prompts Tool - 智能 Prompt 管理助手 (修复版)
    
    主要功能:
    - 搜索 Prompt: prompts "需求描述"
    - 列出 Prompt: prompts --list
    - 更新仓库: prompts --update
    - 启动 UI: prompts --ui
    """
    
    # 打印横幅
    print_banner()
    
    # 加载配置
    try:
        if config_path:
            config = Config.load(config_path)
        else:
            config = Config.load()
        console.print(f"✅ 配置加载成功", style="green")
    except Exception as e:
        console.print(f"❌ 配置加载失败: {e}", style="red")
        sys.exit(1)
    
    # 创建核心组件
    repo = PromptRepo(config)
    parser = PromptParser()
    clipboard = ClipboardManager()
    
    # 延迟创建搜索器
    searcher = None
    if query or rebuild_index:
        searcher = get_searcher(config, repo)
        if not searcher:
            # 如果语义搜索不可用，使用关键词搜索
            if query:
                handle_simple_search(query, repo, parser, clipboard, top_k)
                return
            elif rebuild_index:
                console.print("❌ 无法重建索引，语义搜索不可用", style="red")
                return
    
    # 处理不同的命令
    if update:
        handle_update(repo)
    elif list_prompts:
        handle_list_prompts(repo, preview, filter_keyword)
    elif ui:
        handle_ui(config)
    elif rebuild_index and searcher:
        handle_rebuild_index(searcher)
    elif query and searcher:
        handle_search(query, searcher, parser, clipboard, top_k)
    elif query:
        # 已经在上面处理了
        pass
    else:
        # 显示帮助信息
        show_help()


def handle_simple_search(query: str, repo: PromptRepo, parser: PromptParser, clipboard: ClipboardManager, top_k: int):
    """使用关键词搜索的简单搜索"""
    console.print(f"🔍 正在搜索: {query}", style="yellow")
    console.print("💡 使用关键词搜索（语义搜索不可用）", style="blue")
    
    try:
        # 获取所有 Prompt 文件
        all_prompts = repo.list_prompts()
        
        if not all_prompts:
            console.print("❌ 没有找到 Prompt 文件", style="red")
            return
        
        # 简单的关键词搜索
        results = []
        for prompt in all_prompts:
            score = 0
            content = repo.get_prompt_content(prompt["file_path"])
            
            # 检查文件名
            if query.lower() in prompt["name"].lower():
                score += 2
            
            # 检查内容
            if query.lower() in content.lower():
                score += 1
            
            # 检查路径
            if query.lower() in prompt["relative_path"].lower():
                score += 1
            
            if score > 0:
                results.append({
                    **prompt,
                    "score": score,
                    "content": content
                })
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        if results:
            console.print(f"✅ 找到 {len(results)} 个相关 Prompt", style="green")
            
            # 显示前 top_k 个结果
            for i, result in enumerate(results[:top_k], 1):
                console.print(f"\n#{i} {result['name']} (相关度: {result['score']})", style="bold")
                console.print(f"📁 路径: {result['relative_path']}", style="blue")
                console.print(f"📝 内容预览:")
                console.print(result['content'][:200] + "..." if len(result['content']) > 200 else result['content'])
                
                # 检查是否有变量
                variables = parser.extract_variables(result['content'])
                if variables:
                    console.print(f"🔧 变量: {', '.join(variables)}", style="yellow")
                
                # 复制选项
                if typer.confirm(f"📋 复制 Prompt #{i} 到剪贴板?"):
                    if clipboard.copy(result['content']):
                        console.print("✅ 已复制到剪贴板！", style="green")
                    else:
                        console.print("❌ 复制失败！", style="red")
        else:
            console.print("❌ 没有找到相关的 Prompt", style="red")
            
    except Exception as e:
        console.print(f"❌ 搜索失败: {e}", style="red")


def handle_update(repo: PromptRepo):
    """处理仓库更新"""
    console.print("🔄 正在更新 Prompt 仓库...", style="yellow")
    
    if repo.update():
        console.print("✅ 仓库更新成功！", style="green")
    else:
        console.print("❌ 仓库更新失败！", style="red")


def handle_list_prompts(repo: PromptRepo, preview: Optional[int], filter_keyword: Optional[str]):
    """处理列出 Prompt 文件"""
    console.print("📚 正在获取 Prompt 文件列表...", style="yellow")
    
    try:
        prompts = repo.list_prompts(
            preview_lines=preview,
            filter_keyword=filter_keyword
        )
        
        if prompts:
            console.print(f"✅ 找到 {len(prompts)} 个 Prompt 文件", style="green")
            
            # 创建表格
            table = Table(title="Prompt 文件列表")
            table.add_column("序号", style="cyan", no_wrap=True)
            table.add_column("文件名", style="magenta")
            table.add_column("路径", style="blue")
            table.add_column("摘要", style="green")
            
            if preview:
                table.add_column("预览", style="yellow")
            
            for i, prompt in enumerate(prompts, 1):
                row = [str(i), prompt['name'], prompt['relative_path'], prompt['summary']]
                if preview and 'preview' in prompt:
                    row.append(prompt['preview'])
                table.add_row(*row)
            
            console.print(table)
            
            # 复制选项
            if typer.confirm("📋 复制某个 Prompt 到剪贴板?"):
                try:
                    choice = int(typer.prompt("请输入序号", default=1))
                    if 1 <= choice <= len(prompts):
                        selected = prompts[choice - 1]
                        content = repo.get_prompt_content(selected['file_path'])
                        
                        if clipboard.copy(content):
                            console.print("✅ 已复制到剪贴板！", style="green")
                        else:
                            console.print("❌ 复制失败！", style="red")
                    else:
                        console.print("❌ 无效的序号", style="red")
                except ValueError:
                    console.print("❌ 请输入有效的数字", style="red")
        else:
            console.print("❌ 没有找到 Prompt 文件", style="red")
            
    except Exception as e:
        console.print(f"❌ 获取 Prompt 列表失败: {e}", style="red")


def handle_ui(config: Config):
    """启动 Web 界面"""
    console.print("🌐 正在启动 Web 界面...", style="yellow")
    
    try:
        import subprocess
        import sys
        
        # 获取简化版 Streamlit 应用路径
        app_path = Path(__file__).parent / "ui" / "streamlit_app.py"
        
        if not app_path.exists():
            console.print("❌ 找不到简化版 Streamlit 应用文件", style="red")
            return
        
        # 启动 Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", str(config.ui.port),
            "--server.address", config.ui.host
        ]
        
        console.print(f"🚀 启动命令: {' '.join(cmd)}", style="blue")
        console.print(f"🌐 访问地址: http://{config.ui.host}:{config.ui.port}", style="green")
        console.print("💡 使用简化版界面，无需重型依赖", style="yellow")
        
        # 启动进程
        subprocess.run(cmd)
        
    except ImportError:
        console.print("❌ 未安装 Streamlit，请运行: pip install streamlit", style="red")
    except Exception as e:
        console.print(f"❌ 启动 Web 界面失败: {e}", style="red")


def handle_search(query: str, searcher, parser: PromptParser, clipboard: ClipboardManager, top_k: int):
    """处理语义搜索"""
    console.print(f"🔍 正在搜索: {query}", style="yellow")
    
    try:
        results = searcher.search(query, top_k=top_k)
        
        if results:
            console.print(f"✅ 找到 {len(results)} 个相关 Prompt", style="green")
            
            for i, result in enumerate(results, 1):
                console.print(f"\n#{i} {result['name']} (相似度: {result['similarity']:.3f})", style="bold")
                console.print(f"📁 路径: {result['relative_path']}", style="blue")
                console.print(f"📝 内容预览:")
                console.print(result['content'][:200] + "..." if len(result['content']) > 200 else result['content'])
                
                # 检查是否有变量
                variables = parser.extract_variables(result['content'])
                if variables:
                    console.print(f"🔧 变量: {', '.join(variables)}", style="yellow")
                
                # 复制选项
                if typer.confirm(f"📋 复制 Prompt #{i} 到剪贴板?"):
                    if clipboard.copy(result['content']):
                        console.print("✅ 已复制到剪贴板！", style="green")
                    else:
                        console.print("❌ 复制失败！", style="red")
        else:
            console.print("❌ 没有找到相关的 Prompt", style="red")
            
    except Exception as e:
        console.print(f"❌ 搜索失败: {e}", style="red")


def handle_rebuild_index(searcher):
    """处理重建索引"""
    console.print("🔨 正在重建搜索索引...", style="yellow")
    
    try:
        searcher.rebuild_index()
        console.print("✅ 索引重建成功！", style="green")
    except Exception as e:
        console.print(f"❌ 索引重建失败: {e}", style="red")


def show_help():
    """显示帮助信息"""
    help_text = """
    🚀 Prompts Tool 使用说明
    
    基本用法:
    - prompts "需求描述"          # 搜索 Prompt
    - prompts --list             # 列出所有 Prompt
    - prompts --update           # 更新仓库
    - prompts --ui               # 启动 Web 界面
    
    高级选项:
    - prompts --list --preview 3     # 显示前3行预览
    - prompts --list --filter "关键词" # 按关键词过滤
    - prompts --top 10               # 返回前10个结果
    - prompts --rebuild-index        # 重建搜索索引
    
    示例:
    - prompts "Python 函数文档"
    - prompts --list --preview 5
    - prompts --ui
    """
    
    console.print(Panel(help_text, title="📖 帮助", style="green"))


if __name__ == "__main__":
    app()
