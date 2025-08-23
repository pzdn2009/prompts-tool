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
    tab1, tab2 = st.tabs(["🔍 搜索和浏览", "📝 自定义 Prompt"])
    
    with tab1:
        st.header("🔍 搜索和浏览 Prompt")
        
        # 顶部控制栏
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input(
                "搜索 Prompt",
                placeholder="输入关键词搜索，留空则显示所有 Prompt"
            )
        
        with col2:
            preview_lines = st.number_input("预览行数", min_value=1, max_value=10, value=3)
        
        with col3:
            if st.button("🔄 刷新", use_container_width=True):
                st.rerun()
        
        # 搜索和显示逻辑
        try:
            repo = PromptRepo(config)
            
            if search_query:
                # 搜索模式
                st.subheader(f"🔍 搜索结果: '{search_query}'")
                
                with st.spinner("正在搜索..."):
                    # 获取所有 Prompt 文件
                    all_prompts = repo.list_prompts()
                    
                    if not all_prompts:
                        st.warning("没有找到 Prompt 文件")
                        return
                    
                    # 关键词搜索
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
                    
                    # 显示搜索结果
                    for i, result in enumerate(results, 1):
                        with st.expander(f"#{i} {result['name']} (相关度: {result['score']})", expanded=i==1):
                            # 检查是否有变量
                            parser = PromptParser()
                            variables = parser.extract_variables(result['content'])
                            
                            if variables:
                                st.markdown("🔧 **发现变量，可以直接填写：**")
                                
                                # 变量输入区域
                                var_values = {}
                                var_cols = st.columns(min(3, len(variables)))
                                
                                for idx, var_name in enumerate(variables):
                                    col_idx = idx % len(var_cols)
                                    with var_cols[col_idx]:
                                        # 尝试从环境变量获取默认值
                                        env_value = os.environ.get(f"PROMPT_{var_name.upper()}", "")
                                        
                                        value = st.text_input(
                                            f"变量: {var_name}",
                                            value=env_value,
                                            key=f"search_var_{i}_{var_name}",
                                            help=f"环境变量 PROMPT_{var_name.upper()} 的默认值: {env_value}" if env_value else None
                                        )
                                        var_values[var_name] = value
                                
                                # 生成和复制按钮
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("🚀 生成最终 Prompt", key=f"generate_search_{i}", use_container_width=True):
                                        filled_prompt = parser.fill_variables(result['content'], var_values)
                                        st.session_state[f"filled_prompt_search_{i}"] = filled_prompt
                                        st.session_state[f"show_filled_search_{i}"] = True
                                
                                with col2:
                                    if st.button("📋 复制原始 Prompt", key=f"copy_original_search_{i}", use_container_width=True):
                                        clipboard = ClipboardManager()
                                        if clipboard.copy(result['content']):
                                            st.success("✅ 原始 Prompt 已复制！")
                                        else:
                                            st.error("❌ 复制失败！")
                                
                                # 显示填充后的 Prompt
                                if st.session_state.get(f"show_filled_search_{i}", False):
                                    filled_prompt = st.session_state.get(f"filled_prompt_search_{i}", "")
                                    st.markdown("**✅ 生成的 Prompt：**")
                                    st.code(filled_prompt)
                                    
                                    if st.button("📋 复制生成的 Prompt", key=f"copy_filled_search_{i}", use_container_width=True):
                                        clipboard = ClipboardManager()
                                        if clipboard.copy(filled_prompt):
                                            st.success("✅ 生成的 Prompt 已复制！")
                                        else:
                                            st.error("❌ 复制失败！")
                                
                                st.markdown("---")
                            
                            # 显示 Prompt 信息
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**文件路径:** `{result['relative_path']}`")
                                st.markdown(f"**摘要:** {result['summary']}")
                                
                                # 内容预览
                                st.markdown("**内容预览:**")
                                preview_content = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
                                st.code(preview_content)
                                
                                # 查看完整内容
                                if st.button(f"👀 查看完整内容", key=f"view_search_{i}"):
                                    st.text_area("完整内容", result['content'], height=300, key=f"content_search_{i}")
                            
                            with col2:
                                # 如果没有变量，显示简单的复制按钮
                                if not variables:
                                    if st.button(f"📋 复制", key=f"copy_search_{i}", use_container_width=True):
                                        clipboard = ClipboardManager()
                                        if clipboard.copy(result['content']):
                                            st.success("✅ 已复制！")
                                        else:
                                            st.error("❌ 复制失败！")
                                
                                # 变量信息
                                if variables:
                                    st.markdown("**🔧 变量列表:**")
                                    for var in variables:
                                        st.markdown(f"- `{var}`")
                else:
                    st.warning("没有找到相关的 Prompt")
                    st.info("💡 尝试使用不同的关键词，或者留空搜索框查看所有 Prompt")
            else:
                # 浏览模式 - 显示所有 Prompt
                st.subheader("📚 所有 Prompt 文件")
                
                # 过滤选项
                filter_keyword = st.text_input("按关键词过滤", placeholder="输入关键词进行过滤")
                
                # 获取 Prompt 列表
                prompts = repo.list_prompts(
                    preview_lines=preview_lines,
                    filter_keyword=filter_keyword
                )
                
                if prompts:
                    st.success(f"找到 {len(prompts)} 个 Prompt 文件")
                    
                    # 显示所有 Prompt
                    for i, prompt in enumerate(prompts, 1):
                        with st.expander(f"📄 {prompt['name']}", expanded=i<=3):  # 前3个默认展开
                            # 检查是否有变量
                            content = repo.get_prompt_content(prompt['file_path'])
                            parser = PromptParser()
                            variables = parser.extract_variables(content)
                            
                            if variables:
                                st.markdown("🔧 **发现变量，可以直接填写：**")
                                
                                # 变量输入区域
                                var_values = {}
                                var_cols = st.columns(min(3, len(variables)))
                                
                                for idx, var_name in enumerate(variables):
                                    col_idx = idx % len(var_cols)
                                    with var_cols[col_idx]:
                                        # 尝试从环境变量获取默认值
                                        env_value = os.environ.get(f"PROMPT_{var_name.upper()}", "")
                                        
                                        value = st.text_input(
                                            f"变量: {var_name}",
                                            value=env_value,
                                            key=f"browse_var_{i}_{var_name}",
                                            help=f"环境变量 PROMPT_{var_name.upper()} 的默认值: {env_value}" if env_value else None
                                        )
                                        var_values[var_name] = value
                                
                                # 生成和复制按钮
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("🚀 生成最终 Prompt", key=f"generate_browse_{i}", use_container_width=True):
                                        filled_prompt = parser.fill_variables(content, var_values)
                                        st.session_state[f"filled_prompt_browse_{i}"] = filled_prompt
                                        st.session_state[f"show_filled_browse_{i}"] = True
                                
                                with col2:
                                    if st.button("📋 复制原始 Prompt", key=f"copy_original_browse_{i}", use_container_width=True):
                                        clipboard = ClipboardManager()
                                        if clipboard.copy(content):
                                            st.success("✅ 原始 Prompt 已复制！")
                                        else:
                                            st.error("❌ 复制失败！")
                                
                                # 显示填充后的 Prompt
                                if st.session_state.get(f"show_filled_browse_{i}", False):
                                    filled_prompt = st.session_state.get(f"filled_prompt_browse_{i}", "")
                                    st.markdown("**✅ 生成的 Prompt：**")
                                    st.code(filled_prompt)
                                    
                                    if st.button("📋 复制生成的 Prompt", key=f"copy_filled_browse_{i}", use_container_width=True):
                                        clipboard = ClipboardManager()
                                        if clipboard.copy(filled_prompt):
                                            st.success("✅ 生成的 Prompt 已复制！")
                                        else:
                                            st.error("❌ 复制失败！")
                                
                                st.markdown("---")
                            
                            # 显示 Prompt 信息
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**路径:** `{prompt['relative_path']}`")
                                st.markdown(f"**摘要:** {prompt['summary']}")
                                
                                if 'preview' in prompt:
                                    st.markdown("**预览:**")
                                    st.code(prompt['preview'])
                                
                                # 查看完整内容
                                if st.button(f"👀 查看完整内容", key=f"view_browse_{i}"):
                                    st.text_area("完整内容", content, height=300, key=f"content_browse_{i}")
                            
                            with col2:
                                # 如果没有变量，显示简单的复制按钮
                                if not variables:
                                    if st.button(f"📋 复制", key=f"copy_browse_{i}", use_container_width=True):
                                        clipboard = ClipboardManager()
                                        if clipboard.copy(content):
                                            st.success("✅ 已复制！")
                                        else:
                                            st.error("❌ 复制失败！")
                                
                                # 变量信息
                                if variables:
                                    st.markdown("**🔧 变量列表:**")
                                    for var in variables:
                                        st.markdown(f"- `{var}`")
                else:
                    st.warning("没有找到 Prompt 文件")
                    
        except Exception as e:
            st.error(f"操作失败: {e}")
    
    with tab2:
        st.header("📝 自定义 Prompt")
        
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
                    
                    # 使用列布局优化变量输入
                    var_cols = st.columns(min(3, len(variables)))
                    for idx, var_name in enumerate(variables):
                        col_idx = idx % len(var_cols)
                        with var_cols[col_idx]:
                            # 尝试从环境变量获取默认值
                            env_value = os.environ.get(f"PROMPT_{var_name.upper()}", "")
                            
                            value = st.text_input(
                                f"变量: {var_name}",
                                value=env_value,
                                key=f"custom_var_{var_name}",
                                help=f"环境变量 PROMPT_{var_name.upper()} 的默认值: {env_value}" if env_value else None
                            )
                            var_values[var_name] = value
                    
                    # 生成和复制按钮
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🚀 生成最终 Prompt", use_container_width=True):
                            filled_prompt = parser.fill_variables(prompt_text, var_values)
                            st.session_state["custom_filled_prompt"] = filled_prompt
                            st.session_state["show_custom_filled"] = True
                    
                    with col2:
                        if st.button("📋 复制原始 Prompt", use_container_width=True):
                            clipboard = ClipboardManager()
                            if clipboard.copy(prompt_text):
                                st.success("✅ 原始 Prompt 已复制！")
                            else:
                                st.error("❌ 复制失败！")
                    
                    # 显示填充后的 Prompt
                    if st.session_state.get("show_custom_filled", False):
                        filled_prompt = st.session_state.get("custom_filled_prompt", "")
                        st.subheader("✅ 生成的 Prompt")
                        st.code(filled_prompt)
                        
                        if st.button("📋 复制生成的 Prompt", use_container_width=True):
                            clipboard = ClipboardManager()
                            if clipboard.copy(filled_prompt):
                                st.success("✅ 生成的 Prompt 已复制！")
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
