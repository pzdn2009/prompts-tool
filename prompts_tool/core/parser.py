"""
占位符解析模块 - 处理 {{variable}} 格式的变量替换
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class PromptParser:
    """Prompt 占位符解析器"""
    
    def __init__(self):
        # 匹配 {{variable}} 格式的占位符
        self.placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')
    
    def extract_variables(self, prompt_text: str) -> List[str]:
        """提取 Prompt 中的所有变量名"""
        variables = self.placeholder_pattern.findall(prompt_text)
        # 去重并保持顺序
        seen = set()
        unique_variables = []
        for var in variables:
            if var not in seen:
                seen.add(var)
                unique_variables.append(var)
        return unique_variables
    
    def has_variables(self, prompt_text: str) -> bool:
        """检查 Prompt 是否包含变量"""
        return bool(self.placeholder_pattern.search(prompt_text))
    
    def fill_variables(self, prompt_text: str, variables: Dict[str, str]) -> str:
        """填充变量到 Prompt 中"""
        def replace_placeholder(match):
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            else:
                # 如果变量未提供，保留原始占位符
                return match.group(0)
        
        return self.placeholder_pattern.sub(replace_placeholder, prompt_text)
    
    def fill_variables_interactive(self, prompt_text: str) -> Tuple[str, Dict[str, str]]:
        """交互式填充变量（CLI 模式）"""
        variables = {}
        extracted_vars = self.extract_variables(prompt_text)
        
        if not extracted_vars:
            return prompt_text, variables
        
        print(f"\n📝 发现 {len(extracted_vars)} 个变量需要填写:")
        print("=" * 50)
        
        for var_name in extracted_vars:
            while True:
                try:
                    # 显示变量名和提示
                    print(f"\n🔧 变量: {var_name}")
                    
                    # 尝试从环境变量获取默认值
                    env_value = os.environ.get(f"PROMPT_{var_name.upper()}")
                    if env_value:
                        print(f"💡 环境变量默认值: {env_value}")
                    
                    # 获取用户输入
                    user_input = input(f"请输入 {var_name} 的值: ").strip()
                    
                    if user_input:
                        variables[var_name] = user_input
                        break
                    elif env_value:
                        variables[var_name] = env_value
                        print(f"✅ 使用环境变量默认值: {env_value}")
                        break
                    else:
                        print("❌ 值不能为空，请重新输入")
                        
                except KeyboardInterrupt:
                    print("\n\n❌ 用户取消操作")
                    return prompt_text, {}
                except Exception as e:
                    print(f"❌ 输入错误: {e}")
        
        # 填充变量
        filled_prompt = self.fill_variables(prompt_text, variables)
        
        print("\n" + "=" * 50)
        print("✅ 变量填充完成!")
        
        return filled_prompt, variables
    
    def validate_variables(self, prompt_text: str, variables: Dict[str, str]) -> List[str]:
        """验证变量是否完整"""
        required_vars = set(self.extract_variables(prompt_text))
        provided_vars = set(variables.keys())
        missing_vars = required_vars - provided_vars
        return list(missing_vars)
    
    def get_variable_hints(self, prompt_text: str) -> Dict[str, str]:
        """从 Prompt 中提取变量提示信息"""
        # 这个功能可以扩展，比如从注释中提取变量说明
        # 目前返回空字典
        return {}
    
    def format_prompt_preview(self, prompt_text: str, variables: Dict[str, str]) -> str:
        """格式化 Prompt 预览，显示变量和值"""
        if not variables:
            return prompt_text
        
        preview = "📋 Prompt 预览:\n"
        preview += "=" * 50 + "\n"
        
        # 显示变量和值
        for var_name, value in variables.items():
            preview += f"🔧 {var_name}: {value}\n"
        
        preview += "=" * 50 + "\n\n"
        preview += prompt_text
        
        return preview
    
    def parse_file(self, file_path: Path) -> Tuple[str, List[str]]:
        """解析文件并返回内容和变量列表"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            variables = self.extract_variables(content)
            return content, variables
        except Exception as e:
            print(f"❌ 无法解析文件 {file_path}: {e}")
            return "", []


# 为了支持环境变量，需要导入 os
import os
