# MODULE - app/cli

> 存放各种命令行入口，便于本地测试和日常使用。

---

## 1. `echo.py`

- 使用 `build_simple_graph(VllmLLMClient())` 搭建纯 LLM 对话；
- 逻辑：
  - 循环从 stdin 读 user 文本；
  - 追加到 `messages`；
  - 调用 `graph.invoke(state)`；
  - 打印最后一条 assistant 消息。

---

## 2. `rag_demo.py`

- 不依赖 LangGraph；
- 用于测试 `RAGService`：
  - 输入一个问题；
  - 直接调用 `RAGService.query()`；
  - 打印 answer 和使用到的检索片段。

---

## 3. `rag_chat.py`

- 使用 `build_rag_graph(RAGService)`；
- 通过 LangGraph 驱动的 RAG 对话：
  - 支持 `messages` 里包含完整对话历史；
  - 在 CLI 中展示 RAG 回答 + 检索片段。

---

## 4. `router_chat.py`

- 使用 `build_routed_graph(VllmLLMClient(), RAGService)`；
- 集成 Router + LLM + RAG：
  - Router 根据用户问题内容决定走 LLM 或 RAG；
  - 若走 RAG，CLI 会展示检索片段；
  - 可以临时打印 `traces` 看路由和 RAG 行为。

---

## 5. 编写新的 CLI 的建议

- 尽量保持：
  - 状态维护逻辑（`messages` 列表）简单、透明；
  - 与 LangGraph 图之间的接口清晰：
    - 构建初始 `AgentState`；
    - 调用 `graph.invoke(state)`；
    - 读取 `final_state` 中的 `messages` / `rag_answer` / `traces`。
- 可以根据需要添加：
  - debugging 模式（打印更详细的 trace）；
  - 日志输出到文件等。
