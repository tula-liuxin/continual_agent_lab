
---

### `src/app/config/MODULE.md`

```markdown
# MODULE - app/config

> 负责全局配置与环境变量管理。

---

## 1. `base.py`

- 提供 `AppSettings`（pydantic-settings）：
  - 通过 `AGENT_` 前缀读取环境变量；
  - 支持 `.env` 文件。
- 示例字段：
  - `env`: `"dev" | "prod" | "test"`
  - `project_name`: 默认 `"continual_agent_lab"`
  - `vllm_base_url`: 默认 `"http://localhost:8000/v1"`
  - `qwen_model`: 默认 `"Qwen/Qwen2.5-3B-Instruct"`
  - `embedding_model`: 默认 `"BAAI/bge-m3"`

- 提供 `get_settings()` 工具函数：
  - 使用 `@lru_cache`，避免重复构造配置对象；
  - 在全局任意模块中都可以安全调用。

---

## 2. 使用约定

- 所有硬编码字符串（URL / 模型名 / 超参数）尽量从此处拉取：
  - 例如：`VllmLLMClient` 会从 `get_settings().vllm_base_url` 与 `qwen_model` 中读配置；
  - `BgeM3EmbeddingClient` 会从 `embedding_model` 字段中读取模型名。
- 不要在具体业务模块中写死本地 URL 或模型名，方便在不同环境中部署。

---

## 3. 环境变量建议

- 在 `.env` 中：
  - `AGENT_ENV=dev`
  - `AGENT_VLLM_BASE_URL=http://localhost:8000/v1`
  - `AGENT_QWEN_MODEL=Qwen/Qwen2.5-3B-Instruct`
  - `AGENT_EMBEDDING_MODEL=BAAI/bge-m3`

- 在 conda env 激活脚本中设置：
  - `HF_ENDPOINT=https://hf-mirror.com`
  - 关闭 HTTP(S) 代理，避免 `socks://` 之类错误。
