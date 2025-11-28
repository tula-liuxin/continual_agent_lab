# src/app/rag/service.py

from typing import List, Optional

from llama_index.core import Document, VectorStoreIndex, Settings

from app.common.rag_types import RAGAnswer, RetrievedChunk
from app.infra.embed.llamaindex_bge_m3 import LlamaIndexBgeM3Embedding
from app.infra.llm.llamaindex_qwen import build_llamaindex_qwen_llm


class RAGService:
    """
    封装好的 RAG 服务：

    - 初始化时接收一组文本文档（后面可以扩展成从文件系统加载）
    - 内部用：
        - BGE-M3 作为 embedding（LlamaIndexBgeM3Embedding）
        - Qwen(vLLM) 作为 LLM（build_llamaindex_qwen_llm）
        - LlamaIndex VectorStoreIndex 做向量索引 + 检索 + QA
    - 对外只暴露一个简单方法：
        - query(question: str, top_k: int) -> RAGAnswer
    """

    def __init__(self, texts: List[str]) -> None:
        # 1. 配置全局的 embed_model / llm
        Settings.embed_model = LlamaIndexBgeM3Embedding()
        Settings.llm = build_llamaindex_qwen_llm()

        # 2. 把纯文本包装成 LlamaIndex 的 Document
        documents = [Document(text=t) for t in texts]

        # 3. 构建向量索引
        self._index = VectorStoreIndex.from_documents(documents)

        # 4. 创建一个 Query Engine（检索 + LLM 回答）
        self._query_engine = self._index.as_query_engine(similarity_top_k=2)

    def query(self, question: str, top_k: int = 2) -> RAGAnswer:
        """
        对外统一的查询接口：
        - question: 用户问题
        - top_k: 检索多少个相关片段（目前主要用于 contexts）
        """
        # 1. 用 query_engine 做一次完整的 RAG 问答
        response = self._query_engine.query(question)

        # 2. 从 response 中拿到“源节点”（检索到的上下文片段）
        #    某些版本里是 response.source_nodes
        source_nodes = getattr(response, "source_nodes", [])

        contexts: List[RetrievedChunk] = []
        for node in source_nodes[:top_k]:
            text = node.get_content()
            score = float(getattr(node, "score", 0.0) or 0.0)
            metadata = dict(node.metadata or {})
            contexts.append(
                RetrievedChunk(text=text, score=score, metadata=metadata)
            )

        # 3. 组装成统一的 RAGAnswer 对象
        return RAGAnswer(
            answer=str(response),
            contexts=contexts,
        )

    @classmethod
    def from_texts(cls, texts: List[str]) -> "RAGService":
        """
        方便的工厂方法：传入一批文本字符串，构建一个 RAGService 实例。
        """
        return cls(texts=texts)
