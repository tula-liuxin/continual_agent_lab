# src/app/infra/embed/base.py

from typing import Protocol, List
import numpy as np


class EmbeddingClient(Protocol):
    """
    Embedding 客户端统一接口。

    不管底层是 BGE-M3、别的模型，接口都保持一致：
    - embed_documents: 用于索引文档（批量）
    - embed_query:     用于查询向量
    """

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """
        输入多段文本，返回形状为 (N, D) 的向量矩阵。
        """
        ...

    def embed_query(self, text: str) -> np.ndarray:
        """
        输入单条查询文本，返回形状为 (D,) 的向量。
        """
        ...
