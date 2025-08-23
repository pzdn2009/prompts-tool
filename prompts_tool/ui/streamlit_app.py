"""Streamlit web app for interactive prompt search and management"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from prompts_tool.core.config import Config
from prompts_tool.core.repo import PromptRepo
from prompts_tool.core.search import PromptSearcher
from prompts_tool.core.parser import PromptParser
from prompts_tool.utils.clipboard import ClipboardManager


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

        # Model settings
        st.subheader("🧠 Model Settings")
        model_name = st.selectbox(
            "Model name",
            ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "all-MiniLM-L12-v2"],
            index=0,
        )
        device = st.selectbox("Device", ["cpu", "cuda"], index=0)

        if st.button("💾 Save configuration"):
            config.model.name = model_name
            config.model.device = device
            config.save()
            st.success("✅ Configuration saved")

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
    tab1, tab2, tab3 = st.tabs(["🔍 Search Prompts", "📚 Browse Prompts", "📝 Fill Variables"])

    with tab1:
        st.header("🔍 Search Prompts")

        # Search input
        search_query = st.text_input(
            "Describe your need",
            placeholder="e.g., Write a docstring for a Python function",
        )

        if search_query:
            try:
                repo = PromptRepo(config)
                searcher = PromptSearcher(config, repo)

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
                            st.markdown("**Preview:**")
                            st.code(
                                result['content'][:500] + "..."
                                if len(result['content']) > 500
                                else result['content']
                            )

                            # Copy button
                            if st.button(
                                f"📋 Copy Prompt #{result['rank']}", key=f"copy_{i}"
                            ):
                                clipboard = ClipboardManager()
                                if clipboard.copy(result['content']):
                                    st.success("✅ Copied to clipboard")
                                else:
                                    st.error("❌ Copy failed")
                else:
                    st.warning("No related prompts found")

            except Exception as e:
                st.error(f"Search failed: {e}")

    with tab2:
        st.header("📚 Browse Prompts")

        try:
            repo = PromptRepo(config)

            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_keyword = st.text_input(
                    "Keyword filter", placeholder="Enter keyword to filter"
                )
            with col2:
                preview_lines = st.number_input(
                    "Preview lines", min_value=1, max_value=10, value=3
                )

            if st.button("🔄 Refresh list"):
                st.rerun()

            # Get prompt list
            prompts = repo.list_prompts(
                preview_lines=preview_lines, filter_keyword=filter_keyword
            )

            if prompts:
                st.success(f"Found {len(prompts)} prompt files")

                for prompt in prompts:
                    with st.expander(f"📄 {prompt['name']}"):
                        st.markdown(f"**Path:** `{prompt['relative_path']}`")
                        st.markdown(f"**Summary:** {prompt['summary']}")

                        if "preview" in prompt:
                            st.markdown("**Preview:**")
                            st.code(prompt["preview"])

                        # View full content
                        if st.button(
                            f"👀 View full content", key=f"view_{prompt['name']}"
                        ):
                            full_content = repo.get_prompt_content(prompt["file_path"])
                            st.text_area(
                                "Full content",
                                full_content,
                                height=300,
                                key=f"content_{prompt['name']}",
                            )

                            # Copy button
                            if st.button(
                                f"📋 Copy content", key=f"copy_full_{prompt['name']}"
                            ):
                                clipboard = ClipboardManager()
                                if clipboard.copy(full_content):
                                    st.success("✅ Copied to clipboard")
                                else:
                                    st.error("❌ Copy failed")
            else:
                st.warning("No prompt files found")

        except Exception as e:
            st.error(f"Failed to list prompts: {e}")

    with tab3:
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

