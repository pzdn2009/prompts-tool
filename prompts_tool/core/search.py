"""
搜索模块 - 使用 SentenceTransformers 和 FAISS 进行语义搜索
"""

import os
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import faiss

from .config import Config
from .repo import PromptRepo


class PromptSearcher:
    """Prompt 语义搜索器"""
    
    def __init__(self, config: Config, repo: PromptRepo):
        self.config = config
        self.repo = repo
        self.model = None
        self.index = None
        self.prompt_data = []
        self.index_path = config.get_index_path()
        
        # 初始化模型
        self._init_model()
    
    def _init_model(self):
        """初始化 SentenceTransformer 模型"""
        try:
            print(f"🔄 正在加载模型: {self.config.model.name}")
            self.model = SentenceTransformer(self.config.model.name, device=self.config.model.device)
            print(f"✅ 模型加载完成")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            print("请检查网络连接或模型名称是否正确")
            self.model = None
    
    def _build_index(self) -> bool:
        """构建 FAISS 索引"""
        if not self.model:
            print("❌ 模型未加载，无法构建索引")
            return False
        
        if not self.repo.exists():
            print("❌ 仓库不存在，无法构建索引")
            return False
        
        print("🔄 正在构建搜索索引...")
        
        try:
            # 获取所有 Prompt 文件
            prompt_files = self.repo.get_prompt_files()
            
            if not prompt_files:
                print("❌ 没有找到 Prompt 文件")
                return False
            
            print(f"📁 找到 {len(prompt_files)} 个 Prompt 文件")
            
            # 提取文本和元数据
            texts = []
            self.prompt_data = []
            
            for file_path in prompt_files:
                content = self.repo.get_prompt_content(file_path)
                if content.strip():
                    texts.append(content)
                    self.prompt_data.append({
                        "file_path": file_path,
                        "relative_path": str(file_path.relative_to(self.repo.repo_path)),
                        "name": file_path.name,
                        "content": content
                    })
            
            if not texts:
                print("❌ 没有有效的 Prompt 内容")
                return False
            
            print(f"📝 处理了 {len(texts)} 个有效 Prompt")
            
            # 生成 embeddings
            print("🧠 正在生成文本嵌入...")
            embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # 构建 FAISS 索引
            print("🔍 正在构建 FAISS 索引...")
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # 内积索引，用于余弦相似度
            
            # 归一化向量（余弦相似度）
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            # 保存索引和元数据
            self._save_index()
            
            print(f"✅ 索引构建完成，包含 {len(texts)} 个 Prompt")
            return True
            
        except Exception as e:
            print(f"❌ 构建索引失败: {e}")
            return False
    
    def _save_index(self):
        """保存索引和元数据"""
        try:
            self.index_path.mkdir(parents=True, exist_ok=True)
            
            # 保存 FAISS 索引
            faiss.write_index(self.index, str(self.index_path / "prompts.index"))
            
            # 保存元数据
            with open(self.index_path / "prompts_metadata.pkl", "wb") as f:
                pickle.dump(self.prompt_data, f)
            
            print(f"💾 索引已保存到: {self.index_path}")
            
        except Exception as e:
            print(f"❌ 保存索引失败: {e}")
    
    def _load_index(self) -> bool:
        """加载已存在的索引"""
        try:
            index_file = self.index_path / "prompts.index"
            metadata_file = self.index_path / "prompts_metadata.pkl"
            
            if not index_file.exists() or not metadata_file.exists():
                return False
            
            # 加载 FAISS 索引
            self.index = faiss.read_index(str(index_file))
            
            # 加载元数据
            with open(metadata_file, "rb") as f:
                self.prompt_data = pickle.load(f)
            
            print(f"✅ 索引加载完成，包含 {len(self.prompt_data)} 个 Prompt")
            return True
            
        except Exception as e:
            print(f"❌ 加载索引失败: {e}")
            return False
    
    def ensure_index(self) -> bool:
        """确保索引存在，如果不存在则构建"""
        if self.index is not None:
            return True
        
        # 尝试加载现有索引
        if self._load_index():
            return True
        
        # 构建新索引
        return self._build_index()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索最相关的 Prompt"""
        if not self.ensure_index():
            print("❌ 索引不可用，无法进行搜索")
            return []
        
        if not self.model:
            print("❌ 模型未加载，无法进行搜索")
            return []
        
        try:
            # 生成查询的 embedding
            query_embedding = self.model.encode([query])
            
            # 归一化查询向量
            faiss.normalize_L2(query_embedding)
            
            # 搜索最相似的向量
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # 构建结果
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.prompt_data):
                    prompt_info = self.prompt_data[idx].copy()
                    prompt_info["score"] = float(score)
                    prompt_info["rank"] = i + 1
                    results.append(prompt_info)
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def rebuild_index(self) -> bool:
        """重建索引"""
        print("🔄 正在重建搜索索引...")
        self.index = None
        self.prompt_data = []
        
        # 删除旧的索引文件
        if self.index_path.exists():
            try:
                import shutil
                shutil.rmtree(self.index_path)
                print("🗑️ 已删除旧索引")
            except Exception as e:
                print(f"警告: 无法删除旧索引: {e}")
        
        return self._build_index()
    
    def get_index_info(self) -> Dict[str, Any]:
        """获取索引信息"""
        if not self.index:
            return {"status": "not_built"}
        
        return {
            "status": "ready",
            "total_prompts": len(self.prompt_data),
            "index_type": "FAISS",
            "model_name": self.config.model.name,
            "device": self.config.model.device
        }
