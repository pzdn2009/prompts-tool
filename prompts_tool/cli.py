"""
CLI 主入口 - 实现所有命令行功能
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
from .core.search import PromptSearcher
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
    🚀 Prompts Tool v0.1.0
    ========================
    智能 Prompt 管理助手
    """
    console.print(Panel(banner, style="bold blue"))


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
    Prompts Tool - 智能 Prompt 管理助手
    
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
        config = Config.load(config_path)
        console.print(f"✅ 配置加载成功", style="green")
    except Exception as e:
        console.print(f"❌ 配置加载失败: {e}", style="red")
        sys.exit(1)
    
    # 创建核心组件
    repo = PromptRepo(config)
    searcher = PromptSearcher(config, repo)
    parser = PromptParser()
    clipboard = ClipboardManager()
    
    # 处理不同的命令
    if update:
        handle_update(repo)
    elif list_prompts:
        handle_list_prompts(repo, preview, filter_keyword)
    elif ui:
        handle_ui(config)
    elif rebuild_index:
        handle_rebuild_index(searcher)
    elif query:
        handle_search(query, searcher, parser, clipboard, top_k)
    else:
        # 显示帮助信息
        show_help()


def handle_update(repo: PromptRepo):
    """处理仓库更新"""
    console.print("🔄 正在更新 Prompt 仓库...", style="yellow")
    
    if repo.update():
        console.print("✅ 仓库更新成功！", style="green")
    else:
        console.print("❌ 仓库更新失败！", style="red")
        sys.exit(1)


def handle_list_prompts(repo: PromptRepo, preview: Optional[int], filter_keyword: Optional[str]):
    """处理列出 Prompt 文件"""
    console.print("📚 正在获取 Prompt 列表...", style="yellow")
    
    prompts = repo.list_prompts(preview_lines=preview, filter_keyword=filter_keyword)
    
    if not prompts:
        console.print("❌ 没有找到 Prompt 文件", style="red")
        return
    
    # 创建表格
    table = Table(title=f"📚 Prompt 文件列表 ({len(prompts)} 个)")
    table.add_column("序号", style="cyan", no_wrap=True)
    table.add_column("文件名", style="magenta")
    table.add_column("路径", style="blue")
    table.add_column("摘要", style="green")
    
    if preview:
        table.add_column(f"预览 (前{preview}行)", style="yellow")
    
    for i, prompt in enumerate(prompts, 1):
        row = [
            str(i),
            prompt["name"],
            prompt["relative_path"],
            prompt["summary"]
        ]
        
        if preview and "preview" in prompt:
            row.append(prompt["preview"])
        
        table.add_row(*row)
    
    console.print(table)
    
    # 显示统计信息
    console.print(f"\n📊 统计信息:", style="bold")
    console.print(f"  总文件数: {len(prompts)}")
    if filter_keyword:
        console.print(f"  过滤关键词: {filter_keyword}")


def handle_search(query: str, searcher: PromptSearcher, parser: PromptParser, 
                 clipboard: ClipboardManager, top_k: int):
    """处理搜索请求"""
    console.print(f"🔍 正在搜索: {query}", style="yellow")
    
    # 执行搜索
    results = searcher.search(query, top_k=top_k)
    
    if not results:
        console.print("❌ 没有找到相关的 Prompt", style="red")
        return
    
    # 显示搜索结果
    console.print(f"✅ 找到 {len(results)} 个相关 Prompt", style="green")
    
    for i, result in enumerate(results, 1):
        # 创建结果面板
        content = f"""
        📄 文件名: {result['name']}
        📁 路径: {result['relative_path']}
        🎯 相似度: {result['score']:.3f}
        
        📝 内容预览:
        {result['content'][:300]}{'...' if len(result['content']) > 300 else ''}
        """
        
        panel = Panel(content, title=f"#{result['rank']} 搜索结果", border_style="blue")
        console.print(panel)
        
        # 检查是否有变量需要填充
        if parser.has_variables(result['content']):
            console.print(f"🔧 发现变量占位符，需要填充...", style="yellow")
            
            # 交互式填充变量
            filled_prompt, variables = parser.fill_variables_interactive(result['content'])
            
            if variables:
                # 显示填充后的结果
                console.print("\n" + "=" * 50)
                console.print("✅ 变量填充完成！", style="green")
                
                # 显示变量和值
                var_table = Table(title="🔧 变量值")
                var_table.add_column("变量名", style="cyan")
                var_table.add_column("值", style="green")
                
                for var_name, value in variables.items():
                    var_table.add_row(var_name, value)
                
                console.print(var_table)
                
                # 显示最终 Prompt
                console.print("\n📋 最终 Prompt:", style="bold")
                console.print(Panel(filled_prompt, border_style="green"))
                
                # 复制到剪贴板
                if clipboard.copy(filled_prompt):
                    console.print("✅ 已自动复制到剪贴板！", style="green")
                else:
                    console.print("❌ 复制到剪贴板失败", style="red")
            else:
                console.print("❌ 变量填充被取消", style="red")
        else:
            # 没有变量，直接复制
            console.print("📋 没有变量需要填充，直接复制...", style="yellow")
            
            if clipboard.copy(result['content']):
                console.print("✅ 已自动复制到剪贴板！", style="green")
            else:
                console.print("❌ 复制到剪贴板失败", style="red")
        
        console.print()  # 空行分隔


def handle_ui(config: Config):
    """启动 Web 界面"""
    console.print("🌐 正在启动 Web 界面...", style="yellow")
    
    try:
        import subprocess
        import sys
        
        # 获取 Streamlit 应用路径
        app_path = Path(__file__).parent / "ui" / "streamlit_app.py"
        
        if not app_path.exists():
            console.print("❌ 找不到 Streamlit 应用文件", style="red")
            return
        
        # 启动 Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", str(config.ui.port),
            "--server.address", config.ui.host
        ]
        
        console.print(f"🚀 启动命令: {' '.join(cmd)}", style="blue")
        console.print(f"🌐 访问地址: http://{config.ui.host}:{config.ui.port}", style="green")
        
        # 启动进程
        subprocess.run(cmd)
        
    except ImportError:
        console.print("❌ 未安装 Streamlit，请运行: pip install streamlit", style="red")
    except Exception as e:
        console.print(f"❌ 启动 Web 界面失败: {e}", style="red")


def handle_rebuild_index(searcher: PromptSearcher):
    """重建搜索索引"""
    console.print("🔨 正在重建搜索索引...", style="yellow")
    
    if searcher.rebuild_index():
        console.print("✅ 索引重建成功！", style="green")
    else:
        console.print("❌ 索引重建失败！", style="red")
        sys.exit(1)


def show_help():
    """显示帮助信息"""
    help_text = """
    🚀 Prompts Tool 使用说明
    
    基本用法:
      prompts "需求描述"           # 搜索最相关的 Prompt 并填充变量
      prompts --list              # 列出所有 Prompt 文件
      prompts --update            # 更新远程仓库的 Prompt Repo
      prompts --ui                # 启动 Web 界面
    
    高级选项:
      prompts --list --preview 5  # 显示前 5 行预览
      prompts --list --filter python  # 按关键词过滤
      prompts --top 10            # 返回前 10 个搜索结果
      prompts --rebuild-index     # 重建搜索索引
    
    示例:
      prompts "帮我写一个 Python 函数的文档字符串"
      prompts --list --preview 3 --filter "AI"
      prompts --update
      prompts --ui
    """
    
    console.print(Panel(help_text, title="📖 帮助信息", border_style="green"))


if __name__ == "__main__":
    app()
