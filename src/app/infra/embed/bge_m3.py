# src/app/infra/embed/bge_m3.py

from typing import List, Optional

import numpy as np
from FlagEmbedding import BGEM3FlagModel  # ✅ 正确的类名

from app.config.base import get_settings
from app.infra.embed.base import EmbeddingClient


class BgeM3EmbeddingClient(EmbeddingClient):
    """
    使用 BAAI/bge-m3 的 Embedding 客户端。

    默认行为：
    - 从配置里读取 embedding_model 名称（默认 BAAI/bge-m3）
    - 使用 FlagEmbedding 的 BGEM3FlagModel 加载模型
    - 只使用 dense 向量（后面需要 sparse / multi_vector 时可以扩展）
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        use_fp16: bool = True,
    ) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model

        # 官方示例用法：BGEM3FlagModel('BAAI/bge-m3', use_fp16=True) :contentReference[oaicite:1]{index=1}
        self._model = BGEM3FlagModel(
            self.model_name,
            use_fp16=use_fp16,
        )

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype="float32")

        outputs = self._model.encode(
            texts,
            batch_size=32,
        )
        # outputs["dense_vecs"] 形状: (N, D)
        dense_vecs = outputs["dense_vecs"]
        return np.array(dense_vecs)

    def embed_query(self, text: str) -> np.ndarray:
        outputs = self._model.encode(
            [text],
            batch_size=1,
        )
        dense_vecs = outputs["dense_vecs"]
        return np.array(dense_vecs[0])
