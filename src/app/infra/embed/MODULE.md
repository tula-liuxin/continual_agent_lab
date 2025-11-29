
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
