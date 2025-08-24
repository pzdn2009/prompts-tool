"""Streamlit web app for interactive prompt search and management"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from prompts_tool.core.config import Config
from prompts_tool.core.repo import PromptRepo
from prompts_tool.core.search import PromptSearcher
from prompts_tool.core.parser import PromptParser
from prompts_tool.utils.clipboard import ClipboardManager


def render_prompt_with_variables(content: str, key_prefix: str) -> None:
    """Display variable inputs, preview and copy functionality for a prompt."""
    parser = PromptParser()
    clipboard = ClipboardManager()
    variables = parser.extract_variables(content)

    if variables:
        st.markdown("🔧 发现变量，可以直接填写：")
        var_cols = st.columns(min(3, len(variables)))
        var_values = {}
        for idx, var_name in enumerate(variables):
            col_idx = idx % len(var_cols)
            with var_cols[col_idx]:
                env_value = os.environ.get(f"PROMPT_{var_name.upper()}", "")
                var_values[var_name] = st.text_input(
                    var_name,
                    value=env_value,
                    key=f"{key_prefix}_{var_name}",
                    help=(
                        f"Default from PROMPT_{var_name.upper()}: {env_value}"
                        if env_value
                        else None
                    ),
                )

        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("🚀 生成最终 Prompt", key=f"{key_prefix}_generate"):
                filled = parser.fill_variables(content, var_values)
                st.session_state[f"{key_prefix}_filled"] = filled
                st.session_state[f"{key_prefix}_show_filled"] = True
        with btn_cols[1]:
            if st.button("📋 复制原始 Prompt", key=f"{key_prefix}_copy_raw"):
                if clipboard.copy(content):
                    st.success("✅ Copied to clipboard")
                else:
                    st.error("❌ Copy failed")

        if st.session_state.get(f"{key_prefix}_show_filled"):
            st.markdown("---")
            st.markdown("✅ 生成的 Prompt：")
            st.code(st.session_state[f"{key_prefix}_filled"])
            if st.button("📋 复制生成的 Prompt", key=f"{key_prefix}_copy_filled"):
                if clipboard.copy(st.session_state[f"{key_prefix}_filled"]):
                    st.success("✅ Copied to clipboard")
                else:
                    st.error("❌ Copy failed")
    else:
        if st.button("📋 复制 Prompt", key=f"{key_prefix}_copy_only"):
            if clipboard.copy(content):
                st.success("✅ Copied to clipboard")
            else:
                st.error("❌ Copy failed")


def create_app():
    """Create Streamlit application"""
    st.set_page_config(
        page_title="Prompts Tool",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🚀 Prompts Tool")
    st.markdown("An intelligent prompt management and search tool")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Load configuration
        config = Config.load()

        # Repository settings
        st.subheader("📁 Repository Settings")
        repo_url = st.text_input("Repository URL", value=config.repo.url)
        repo_paths_text = st.text_area(
            "Local paths (one per line)", value="\n".join(config.repo.local_paths)
        )

        if st.button("🔄 Update repository"):
            with st.spinner("Updating repository..."):
                config.repo.url = repo_url
                paths = [p.strip() for p in repo_paths_text.splitlines() if p.strip()]
                config.repo.local_paths = paths or config.repo.local_paths
                config.save()

                repo = PromptRepo(config)
                if repo.update():
                    st.success("✅ Repository updated")
                else:
                    st.error("❌ Repository update failed")


        # Index information
        st.subheader("🔍 Index Status")
        try:
            repo = PromptRepo(config)
            searcher = PromptSearcher(config, repo)
            index_info = searcher.get_index_info()

            if index_info["status"] == "ready":
                st.success("✅ Index ready")
                st.info(f"Prompts: {index_info['total_prompts']}")
                st.info(f"Model: {index_info['model_name']}")
            else:
                st.warning("⚠️ Index not built")

            if st.button("🔨 Rebuild index"):
                with st.spinner("Rebuilding index..."):
                    if searcher.rebuild_index():
                        st.success("✅ Index rebuilt")
                        st.rerun()
                    else:
                        st.error("❌ Index rebuild failed")
        except Exception as e:
            st.error(f"❌ Failed to get index info: {e}")

    # Main interface
    tab1, tab2 = st.tabs(["🔍 Search & Browse", "📝 Fill Variables"])

    with tab1:
        st.header("🔍 Search or Browse Prompts")

        col_search, col_filter = st.columns(2)
        with col_search:
            search_query = st.text_input(
                "Search prompts",
                placeholder="e.g., Write a docstring for a Python function",
            )
        with col_filter:
            filter_keyword = st.text_input(
                "Keyword filter", placeholder="Enter keyword to filter"
            )

        preview_lines = st.number_input(
            "Preview lines", min_value=1, max_value=10, value=3
        )

        if st.button("🔄 Refresh"):
            st.rerun()

        try:
            repo = PromptRepo(config)
            searcher = PromptSearcher(config, repo)

            if search_query:
                with st.spinner("Searching..."):
                    results = searcher.search(search_query, top_k=5)

                if results:
                    st.success(f"Found {len(results)} related prompts")

                    for i, result in enumerate(results):
                        with st.expander(
                            f"#{result['rank']} {result['name']} (score: {result['score']:.3f})"
                        ):
                            st.markdown(f"**Path:** `{result['relative_path']}`")
                            st.markdown(f"**Score:** {result['score']:.3f}")
                            st.markdown("**Content:**")
                            st.code(result["content"])

                            render_prompt_with_variables(result["content"], f"search_{i}")
                else:
                    st.warning("No related prompts found")

            else:
                prompts = repo.list_prompts(
                    preview_lines=preview_lines, filter_keyword=filter_keyword
                )

                if prompts:
                    st.success(f"Found {len(prompts)} prompt files")

                    for i, prompt in enumerate(prompts):
                        with st.expander(f"📄 {prompt['name']}"):
                            st.markdown(f"**Path:** `{prompt['relative_path']}`")
                            st.markdown(f"**Summary:** {prompt['summary']}")

                            full_content = repo.get_prompt_content(prompt["file_path"])
                            st.markdown("**Content:**")
                            st.code(full_content)

                            render_prompt_with_variables(full_content, f"list_{i}")
                else:
                    st.warning("No prompt files found")

        except Exception as e:
            st.error(f"Failed to search or browse prompts: {e}")

    with tab2:
        st.header("📝 Fill Variables")

        st.info(
            "You can manually enter prompt content here and fill variables in the form {{variable}}"
        )

        # Prompt input
        prompt_text = st.text_area(
            "Enter prompt content",
            height=200,
            placeholder="e.g., Write a {{style}} article about {{topic}} around {{length}} words.",
        )

        if prompt_text:
            parser = PromptParser()
            variables = parser.extract_variables(prompt_text)

            if variables:
                st.success(f"Found {len(variables)} variables")

                # Variable inputs
                st.subheader("🔧 Fill variables")
                var_values = {}

                for var_name in variables:
                    import os

                    env_value = os.environ.get(f"PROMPT_{var_name.upper()}", "")
                    value = st.text_input(
                        f"Variable: {var_name}",
                        value=env_value,
                        help=(
                            f"Default from environment PROMPT_{var_name.upper()}: {env_value}"
                            if env_value
                            else None
                        ),
                    )
                    var_values[var_name] = value

                # Filled result
                if st.button("🚀 Generate final prompt"):
                    filled_prompt = parser.fill_variables(prompt_text, var_values)

                    st.subheader("✅ Generated Prompt")
                    st.code(filled_prompt)

                    if st.button("📋 Copy to clipboard"):
                        clipboard = ClipboardManager()
                        if clipboard.copy(filled_prompt):
                            st.success("✅ Copied to clipboard")
                        else:
                            st.error("❌ Copy failed")
            else:
                st.info("No variable placeholders found")

    # Footer
    st.markdown("---")
    st.markdown("**Prompts Tool** - Make prompt management simple and efficient 🚀")


if __name__ == "__main__":
    create_app()
