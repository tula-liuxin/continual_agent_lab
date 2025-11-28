# src/app/common/rag_types.py

from typing import Dict, List, Any
from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    """
    表示从知识库里检索到的一个“片段”。

    字段：
    - text: 片段内容
    - score: 相似度 / 相关性分数（越高越相关）
    - metadata: 源文档的一些元信息（比如 doc_id、索引、额外标签等）
    """

    text: str
    score: float
    metadata: Dict[str, Any] = {}


class RAGAnswer(BaseModel):
    """
    RAG 的统一输出格式：
    - answer: LLM 生成的最终回答
    - contexts: 用到的检索片段列表（方便展示 / 调试 / RL 打分）
    """

    answer: str
    contexts: List[RetrievedChunk]
