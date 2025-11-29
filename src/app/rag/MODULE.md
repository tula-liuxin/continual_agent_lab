# MODULE - app/rag

> 封装基于 LlamaIndex 的 RAG 能力，对外提供统一的 RAGService。

---

## 1. `service.py`

- `RAGService` 主要职责：
  1. 初始化 LlamaIndex：
     - `Settings.embed_model = LlamaIndexBgeM3Embedding()`
     - `Settings.llm = build_llamaindex_qwen_llm()`
  2. 用一组文本 `texts: List[str]` 构建 `VectorStoreIndex`。
  3. 暴露方法：
     - `query(question: str, top_k: int = 2) -> RAGAnswer`

- `query()` 内部逻辑：
  - 调用 `self._query_engine.query(question)`；
  - 从 `response` 中提取 `source_nodes`；
  - 构造 `RetrievedChunk` 列表；
  - 返回 `RAGAnswer(answer=str(response), contexts=chunks)`。

- 工厂方法：
  - `@classmethod from_texts(cls, texts: List[str]) -> "RAGService"`

---

## 2. 与其他模块的关系

- `rag_graph.py` 中的 RAG 节点调用 `RAGService.query()`；
- `rag_demo.py` 和 `rag_chat.py` CLI 用于测试与 demo；
- `routed_graph.py` 的 RAG 分支也依赖此服务。

---

## 3. 未来扩展方向

- 从“内存中的 texts”扩展到：
  - 文件系统加载（md / pdf / html / csv 等）；
  - 增量更新和持久化索引；
- 支持多种索引类型（向量 + keyword + 混合检索）；
- 在 `RAGAnswer.metadata` 中加入更丰富的源信息（例如文件路径、行号）。
