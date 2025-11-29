
---

### `src/app/infra/embed/MODULE.md`

```markdown
# MODULE - app/infra/embed

> 管理 Embedding 相关实现与 LlamaIndex 适配。

---

## 1. `base.py`

- 定义 Embedding 接口 `EmbeddingClient(Protocol)`：

```python
class EmbeddingClient(Protocol):
    def embed_documents(self, texts: List[str]) -> np.ndarray: ...
    def embed_query(self, text: str) -> np.ndarray: ...
上层（如 RAG）只关心统一接口，不关心底层库。

2. bge_m3.py

实现 BgeM3EmbeddingClient，使用 FlagEmbedding.BGEM3FlagModel("BAAI/bge-m3")。

特点：

embed_documents：批量文本 → (N, D) 向量；

embed_query：单条文本 → (D,) 向量；

依赖配置：

模型名来自 AppSettings.embedding_model（默认 BAAI/bge-m3）。

3. llamaindex_bge_m3.py

实现 LlamaIndexBgeM3Embedding(BaseEmbedding)：

内部组合 BgeM3EmbeddingClient；

对外提供 LlamaIndex 所需的接口：

_get_query_embedding

_get_text_embedding

_get_text_embeddings

用于：

在 RAGService 中设定 Settings.embed_model。

4. 与其他模块的关系

RAGService 使用 Settings.embed_model = LlamaIndexBgeM3Embedding()；

可以在未来添加更多 Embedding 实现：

比如多语言模型、领域特化模型等；

保持 EmbeddingClient 接口不变即可。