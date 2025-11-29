
---

### `DEV_NOTES.md`

```markdown
# DEV_NOTES - 开发记录与决策日志

> 记录项目中的“大改动 / 决策”。  
> 方便以后换人 / 换 Chat / 换自己回来时快速恢复上下文。

---

## 2025-11-27：项目基础骨架与配置

- **内容**
  - 建立项目结构：`src/app/...`
  - 使用 `pydantic-settings` 定义 `AppSettings`（`AGENT_` 前缀 + `.env`）
  - 约定：
    - 运行环境：`Ubuntu 22.04.5 LTS + conda + Python 3.11`
    - 不使用任何付费云 API（OpenAI 官方等）
- **原因**
  - 为后续所有模块预留统一的配置入口；
  - 确保可以通过环境变量一键切换模型名、vLLM base_url 等。

---

## 2025-11-27：定义统一的 Message 与 AgentState

- **内容**
  - `Message`：统一的对话消息结构（role + content）
  - `AgentState`（TypedDict）：
    - 初版只有：`messages: List[Message]`
- **原因**
  - 避免在 LangGraph / RAG / LLM 层互相传裸 `dict`；
  - 为未来扩展（RAG、trace、user profile 等）留出结构化容器。

---

## 2025-11-27：接入 LangGraph 1.0（simple_graph）

- **内容**
  - 使用 `langgraph.graph.StateGraph(AgentState)` 创建第一个图：
    - 节点：`echo` → 后来升级为 `llm`
  - CLI：`app/cli/echo.py` 调用 `graph.invoke(init_state)`
- **原因**
  - 熟悉 LangGraph 1.0 的 `StateGraph` + `END` + partial state 约定；
  - 把 CLI 与图解耦，便于后续替换节点实现。

---

## 2025-11-27：抽象 LLMClient，换成 vLLM + Qwen

- **内容**
  - 定义 `LLMClient(Protocol)`：`chat(messages) -> Message`
  - 实现 `DummyLLMClient`（假 LLM）用于打通图；
  - 实现 `VllmLLMClient`：
    - 使用 `openai.OpenAI` 客户端；
    - `base_url` 指向本地 vLLM；
    - `model` 为 `Qwen/Qwen2.5-3B-Instruct`。
- **原因**
  - 不直接把 OpenAI SDK / vLLM 细节散落在各处；
  - 将来可以轻松切换 LLM 实现（别的本地模型、mock、离线测试等）。

---

## 2025-11-27：接入 BGE-M3 与 EmbeddingClient

- **内容**
  - 定义 `EmbeddingClient(Protocol)`；
  - 实现 `BgeM3EmbeddingClient`：
    - 使用 `FlagEmbedding.BGEM3FlagModel("BAAI/bge-m3")`；
    - 提供 `embed_query`、`embed_documents`；
  - 解决大陆网络问题：
    - 在 conda env 的激活脚本中设置 `HF_ENDPOINT=https://hf-mirror.com`；
    - 同时关闭错误的 `socks://` 代理（`unset HTTP_PROXY...`）。
- **原因**
  - 为后续 RAG 打基础；
  - 确保在中国大陆环境下 HuggingFace 下载可用且可控。

---

## 2025-11-27：接入 LlamaIndex 与 RAGService（最小 RAG）

- **内容**
  - 安装 `llama-index` 与 `llama-index-llms-openai-like`；
  - 为 LlamaIndex 提供：
    - `LlamaIndexBgeM3Embedding`（使用 BGE-M3）；
    - `build_llamaindex_qwen_llm()`（使用本地 vLLM + Qwen，通过 `OpenAILike`）；
  - 封装 `RAGService`：
    - 内部用 `VectorStoreIndex.from_documents` 构建索引；
    - 对外提供 `query(question) -> RAGAnswer`。
- **原因**
  - LlamaIndex 负责 RAG 的“工程复杂度”；
  - 自己只需要关心统一的 RAG 接口与类型。

---

## 2025-11-27：构建 RAG LangGraph 图与 CLI

- **内容**
  - `rag_graph.py`：
    - 节点 `rag` 调用 `RAGService.query()`；
    - 把回答写回 `messages` 和 `rag_answer`；
  - `app/cli/rag_chat.py`：
    - 基于 RAG 图的对话 CLI；
    - 展示检索片段。
- **原因**
  - 验证 LlamaIndex + LangGraph 的整合；
  - 提供一个可以真正“查知识库再答”的对话入口。

---

## 2025-11-27：Router 图（LLM + RAG）

- **内容**
  - `routed_graph.py`：
    - 节点：`router` / `llm` / `rag`
    - `add_conditional_edges`：根据关键词路由到不同分支；
  - `app/cli/router_chat.py`：
    - 用户只看一个 CLI，内部自动选择 LLM / RAG。
- **原因**
  - 模拟真实场景下的多工具 / 多路径选择；
  - 为未来的“LLM Router / RL Router”做准备。

---

## 2025-11-27：TraceEvent 与 AgentState.traces

- **内容**
  - 定义 `TraceEvent`（ts / node / kind / info）；
  - 在 `AgentState` 中新增 `traces: List[TraceEvent]`；
  - 在 `router_node` 与 `rag_node` 中写入 trace：
    - Router：记录决策 `llm` or `rag`
    - RAG：记录 question / num_contexts 等
- **原因**
  - 为后续的强化学习 / 评估 / 可观测性打基础；
  - 所有图运行时的信息都统一集中在 `AgentState` 里。

---

## 后续建议（尚未实现）

- 用 LLM 替代关键词 Router；
- 为每轮对话 episode 添加 `episode_id`；
- 存储 `AgentState` + trace 到外部日志（DB 或文件）；
- 在此基础上尝试简单的 RL（例如 bandit、strategy selection）。
