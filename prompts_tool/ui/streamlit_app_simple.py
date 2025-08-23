"""
简化版 Streamlit Web 应用 - 不依赖重型库
"""

import streamlit as st
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 只导入必要的模块，避免导入有问题的模块
try:
    from prompts_tool.core.config import Config
    from prompts_tool.core.repo import PromptRepo
    from prompts_tool.core.parser import PromptParser
    from prompts_tool.utils.clipboard import ClipboardManager
    IMPORTS_OK = True
except ImportError as e:
    st.error(f"❌ 模块导入失败: {e}")
    st.info("请确保所有依赖已正确安装")
    IMPORTS_OK = False


def create_app():
    """创建简化版 Streamlit 应用"""
    st.set_page_config(
        page_title="Prompts Tool (简化版)",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 Prompts Tool (简化版)")
    st.markdown("一个智能的 Prompt 管理和搜索工具 - 基于关键词搜索")
    
    if not IMPORTS_OK:
        st.error("❌ 无法启动应用，请检查依赖安装")
        return
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # 加载配置
        try:
            config = Config.load()
            
            # 仓库配置
            st.subheader("📁 仓库设置")
            repo_url = st.text_input("仓库 URL", value=config.repo.url)
            repo_path = st.text_input("本地路径", value=config.repo.local_path)
            
            if st.button("🔄 更新仓库"):
                with st.spinner("正在更新仓库..."):
                    config.repo.url = repo_url
                    config.repo.local_path = repo_path
                    config.save()
                    
                    repo = PromptRepo(config)
                    if repo.update():
                        st.success("✅ 仓库更新成功！")
                    else:
                        st.error("❌ 仓库更新失败！")
            
            # 模型配置
            st.subheader("🧠 模型设置")
            st.info("简化版本使用关键词搜索，无需安装重型模型")
            
            # 索引信息
            st.subheader("🔍 搜索状态")
            try:
                repo = PromptRepo(config)
                if repo.exists():
                    prompt_files = repo.get_prompt_files()
                    st.success(f"✅ 搜索就绪")
                    st.info(f"Prompt 数量: {len(prompt_files)}")
                    st.info("搜索方式: 关键词匹配")
                else:
                    st.warning("⚠️ 仓库不存在")
                    
            except Exception as e:
                st.error(f"❌ 获取搜索信息失败: {e}")
                
        except Exception as e:
            st.error(f"❌ 配置加载失败: {e}")
            return
    
    # 主界面
    tab1, tab2, tab3 = st.tabs(["🔍 搜索 Prompt", "📚 浏览 Prompt", "📝 变量填充"])
    
    with tab1:
        st.header("🔍 搜索 Prompt (关键词搜索)")
        
        # 搜索输入
        search_query = st.text_input(
            "输入你的需求描述",
            placeholder="例如：Python 函数文档"
        )
        
        if search_query:
            try:
                repo = PromptRepo(config)
                parser = PromptParser()
                
                with st.spinner("正在搜索..."):
                    # 获取所有 Prompt 文件
                    all_prompts = repo.list_prompts()
                    
                    if not all_prompts:
                        st.warning("没有找到 Prompt 文件")
                        return
                    
                    # 简单的关键词搜索
                    results = []
                    for prompt in all_prompts:
                        score = 0
                        content = repo.get_prompt_content(prompt["file_path"])
                        
                        # 检查文件名
                        if search_query.lower() in prompt["name"].lower():
                            score += 2
                        
                        # 检查内容
                        if search_query.lower() in content.lower():
                            score += 1
                        
                        # 检查路径
                        if search_query.lower() in prompt["relative_path"].lower():
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
                    st.success(f"找到 {len(results)} 个相关 Prompt")
                    
                    for i, result in enumerate(results[:5], 1):  # 显示前5个
                        with st.expander(f"#{i} {result['name']} (相关度: {result['score']})"):
                            st.markdown(f"**文件路径:** `{result['relative_path']}`")
                            st.markdown(f"**相关度:** {result['score']}")
                            st.markdown("**内容预览:**")
                            st.code(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
                            
                            # 复制按钮
                            if st.button(f"📋 复制 Prompt #{i}", key=f"copy_{i}"):
                                clipboard = ClipboardManager()
                                if clipboard.copy(result['content']):
                                    st.success("✅ 已复制到剪贴板！")
                                else:
                                    st.error("❌ 复制失败！")
                else:
                    st.warning("没有找到相关的 Prompt")
                    
            except Exception as e:
                st.error(f"搜索失败: {e}")
    
    with tab2:
        st.header("📚 浏览 Prompt")
        
        try:
            repo = PromptRepo(config)
            
            # 过滤选项
            col1, col2 = st.columns(2)
            with col1:
                filter_keyword = st.text_input("关键词过滤", placeholder="输入关键词进行过滤")
            with col2:
                preview_lines = st.number_input("预览行数", min_value=1, max_value=10, value=3)
            
            if st.button("🔄 刷新列表"):
                st.rerun()
            
            # 获取 Prompt 列表
            prompts = repo.list_prompts(
                preview_lines=preview_lines,
                filter_keyword=filter_keyword
            )
            
            if prompts:
                st.success(f"找到 {len(prompts)} 个 Prompt 文件")
                
                for prompt in prompts:
                    with st.expander(f"📄 {prompt['name']}"):
                        st.markdown(f"**路径:** `{prompt['relative_path']}`")
                        st.markdown(f"**摘要:** {prompt['summary']}")
                        
                        if 'preview' in prompt:
                            st.markdown("**预览:**")
                            st.code(prompt['preview'])
                        
                        # 查看完整内容
                        if st.button(f"👀 查看完整内容", key=f"view_{prompt['name']}"):
                            full_content = repo.get_prompt_content(prompt['file_path'])
                            st.text_area("完整内容", full_content, height=300, key=f"content_{prompt['name']}")
                            
                            # 复制按钮
                            if st.button(f"📋 复制内容", key=f"copy_full_{prompt['name']}"):
                                clipboard = ClipboardManager()
                                if clipboard.copy(full_content):
                                    st.success("✅ 已复制到剪贴板！")
                                else:
                                    st.error("❌ 复制失败！")
            else:
                st.warning("没有找到 Prompt 文件")
                
        except Exception as e:
            st.error(f"获取 Prompt 列表失败: {e}")
    
    with tab3:
        st.header("📝 变量填充")
        
        st.info("在这个标签页中，你可以手动输入 Prompt 内容并填充变量")
        
        # Prompt 输入
        prompt_text = st.text_area(
            "输入 Prompt 内容（支持 {{variable}} 格式的变量）",
            height=200,
            placeholder="例如：请帮我写一个关于 {{topic}} 的 {{style}} 文章，长度约 {{length}} 字。"
        )
        
        if prompt_text:
            try:
                parser = PromptParser()
                variables = parser.extract_variables(prompt_text)
                
                if variables:
                    st.success(f"发现 {len(variables)} 个变量")
                    
                    # 变量输入
                    st.subheader("🔧 填写变量")
                    var_values = {}
                    
                    for var_name in variables:
                        # 尝试从环境变量获取默认值
                        env_value = os.environ.get(f"PROMPT_{var_name.upper()}", "")
                        
                        value = st.text_input(
                            f"变量: {var_name}",
                            value=env_value,
                            help=f"环境变量 PROMPT_{var_name.upper()} 的默认值: {env_value}" if env_value else None
                        )
                        var_values[var_name] = value
                    
                    # 填充结果
                    if st.button("🚀 生成最终 Prompt"):
                        filled_prompt = parser.fill_variables(prompt_text, var_values)
                        
                        st.subheader("✅ 生成的 Prompt")
                        st.code(filled_prompt)
                        
                        # 复制按钮
                        if st.button("📋 复制到剪贴板"):
                            clipboard = ClipboardManager()
                            if clipboard.copy(filled_prompt):
                                st.success("✅ 已复制到剪贴板！")
                            else:
                                st.error("❌ 复制失败！")
                else:
                    st.info("没有发现变量占位符")
            except Exception as e:
                st.error(f"变量填充失败: {e}")
    
    # 页脚
    st.markdown("---")
    st.markdown("**Prompts Tool (简化版)** - 让 Prompt 管理变得简单高效 🚀")
    st.info("💡 这是简化版本，使用关键词搜索。如需语义搜索，请安装完整版本。")


if __name__ == "__main__":
    create_app()
