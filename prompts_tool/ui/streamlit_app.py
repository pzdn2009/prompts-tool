"""
Streamlit Web 应用 - 提供交互式的 Prompt 搜索和变量填充界面
"""

import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from prompts_tool.core.config import Config
from prompts_tool.core.repo import PromptRepo
from prompts_tool.core.search import PromptSearcher
from prompts_tool.core.parser import PromptParser
from prompts_tool.utils.clipboard import ClipboardManager


def create_app():
    """创建 Streamlit 应用"""
    st.set_page_config(
        page_title="Prompts Tool",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 Prompts Tool")
    st.markdown("一个智能的 Prompt 管理和搜索工具")
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # 加载配置
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
        model_name = st.selectbox(
            "模型名称",
            ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "all-MiniLM-L12-v2"],
            index=0
        )
        device = st.selectbox("设备", ["cpu", "cuda"], index=0)
        
        if st.button("💾 保存配置"):
            config.model.name = model_name
            config.model.device = device
            config.save()
            st.success("✅ 配置已保存！")
        
        # 索引信息
        st.subheader("🔍 索引状态")
        try:
            repo = PromptRepo(config)
            searcher = PromptSearcher(config, repo)
            index_info = searcher.get_index_info()
            
            if index_info["status"] == "ready":
                st.success(f"✅ 索引就绪")
                st.info(f"Prompt 数量: {index_info['total_prompts']}")
                st.info(f"模型: {index_info['model_name']}")
            else:
                st.warning("⚠️ 索引未构建")
                
            if st.button("🔨 重建索引"):
                with st.spinner("正在重建索引..."):
                    if searcher.rebuild_index():
                        st.success("✅ 索引重建成功！")
                        st.rerun()
                    else:
                        st.error("❌ 索引重建失败！")
        except Exception as e:
            st.error(f"❌ 获取索引信息失败: {e}")
    
    # 主界面
    tab1, tab2, tab3 = st.tabs(["🔍 搜索 Prompt", "📚 浏览 Prompt", "📝 变量填充"])
    
    with tab1:
        st.header("🔍 搜索 Prompt")
        
        # 搜索输入
        search_query = st.text_input(
            "输入你的需求描述",
            placeholder="例如：帮我写一个 Python 函数的文档字符串"
        )
        
        if search_query:
            try:
                repo = PromptRepo(config)
                searcher = PromptSearcher(config, repo)
                
                with st.spinner("正在搜索..."):
                    results = searcher.search(search_query, top_k=5)
                
                if results:
                    st.success(f"找到 {len(results)} 个相关 Prompt")
                    
                    for i, result in enumerate(results):
                        with st.expander(f"#{result['rank']} {result['name']} (相似度: {result['score']:.3f})"):
                            st.markdown(f"**文件路径:** `{result['relative_path']}`")
                            st.markdown(f"**相似度:** {result['score']:.3f}")
                            st.markdown("**内容预览:**")
                            st.code(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
                            
                            # 复制按钮
                            if st.button(f"📋 复制 Prompt #{result['rank']}", key=f"copy_{i}"):
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
            parser = PromptParser()
            variables = parser.extract_variables(prompt_text)
            
            if variables:
                st.success(f"发现 {len(variables)} 个变量")
                
                # 变量输入
                st.subheader("🔧 填写变量")
                var_values = {}
                
                for var_name in variables:
                    # 尝试从环境变量获取默认值
                    import os
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
    
    # 页脚
    st.markdown("---")
    st.markdown("**Prompts Tool** - 让 Prompt 管理变得简单高效 🚀")


if __name__ == "__main__":
    create_app()
