# app/infra/embed/llamaindex_bge_m3.py

from typing import Any, List

from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.embeddings import BaseEmbedding

from app.infra.embed.bge_m3 import BgeM3EmbeddingClient


class LlamaIndexBgeM3Embedding(BaseEmbedding):
    """
    把你已有的 BgeM3EmbeddingClient 封装成 LlamaIndex 的 Embedding 模型。

    设计思路：
    - LlamaIndex 只认 BaseEmbedding 这个抽象类；
    - 我们内部再去调用 BgeM3EmbeddingClient（FlagEmbedding.BGEM3FlagModel）；
    - 返回值统一用 List[float]（LlamaIndex 要的格式）。
    """

    _client: BgeM3EmbeddingClient = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # 这里直接复用你已经写好的 embedding 客户端
        self._client = BgeM3EmbeddingClient()

    @classmethod
    def class_name(cls) -> str:
        # 只是一个标识名，后面如果要做配置 / 日志会用到
        return "bge_m3"

    # ----- 异步接口（直接复用同步实现） -----

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    # ----- 同步接口：单条 -----

    def _get_query_embedding(self, query: str) -> List[float]:
        vec = self._client.embed_query(query)  # numpy.ndarray, shape=(1024,)
        return vec.tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        # 对于 BGE-M3，query / text 的接口是一样的，这里直接复用
        vec = self._client.embed_query(text)
        return vec.tolist()

    # ----- 同步接口：批量 -----

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        # 为了保险起见，不依赖 embed_documents，逐条调用也可以
        return [self._client.embed_query(t).tolist() for t in texts]
