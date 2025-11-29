# MODULE - app/common

> 定义整个系统跨模块共享的基础数据结构。

---

## 1. `messages.py`

- 定义统一的对话消息结构 `Message`（pydantic 模型）：
  - `role: Literal["user", "assistant", "system", "tool"]`
  - `content: str`
- 用于：
  - LLMClient 的输入 / 输出；
  - AgentState 中的对话历史。

---

## 2. `state.py`

- 定义系统统一的状态结构 `AgentState`（TypedDict）：

```python
class AgentState(TypedDict):
    messages: List[Message]
    rag_answer: NotRequired[RAGAnswer]
    traces: NotRequired[List[TraceEvent]]
所有 LangGraph 的 StateGraph(AgentState) 都围绕它流动；

优点：

避免到处用裸字典；

易于扩展（加入用户画像、长期记忆等）。

3. rag_types.py

定义 RAG 相关的类型：

RetrievedChunk：单个检索片段（text / score / metadata）

RAGAnswer：RAG 返回的统一结构（answer + contexts）

被以下模块使用：

RAGService（封装 LlamaIndex）

LangGraph 中的 RAG 节点（写入 AgentState.rag_answer）

4. tracing.py

定义轨迹事件 TraceEvent：

class TraceEvent(BaseModel):
    ts: datetime
    node: str
    kind: Literal["router", "llm", "rag", "other"]
    info: Dict[str, Any]


用于记录：

Router 决策（走 llm 还是 rag）

RAG 查询情况（问题是什么、检索了几个上下文）

未来可扩展：

加入 reward、episode_id、tool_name 等，为 RL 做准备。

5. 与其他模块的关系

infra/llm、infra/embed 都依赖 Message 作为输入 / 输出；

rag/service.py 使用 RAGAnswer；

LangGraph 各个节点依赖 AgentState、TraceEvent。

设计原则：common 不依赖任何更高层模块，避免循环依赖。


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