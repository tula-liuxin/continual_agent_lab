
---

### `src/app/graph/MODULE.md`

```markdown
# MODULE - app/graph

> 使用 LangGraph 1.0 构建 Agent 的状态流图。

---

## 使用的 API 风格

- 使用 `langgraph.graph.StateGraph(AgentState)`：
  - 节点：函数签名 `node(state: AgentState) -> Dict`（返回 partial state）
  - 结束：`END`
  - 条件边：`add_conditional_edges(node, condition_fn, mapping)`

---

## 1. `simple_graph.py`

- `make_llm_node(llm_client: LLMClient)`
  - 调用 `llm_client.chat(messages)`；
  - 追加 assistant 消息到 `messages` 中。
- `build_simple_graph(llm_client)`
  - 只有一个节点 `llm`；
  - `entry = llm`，`llm -> END`。

用途：  
- 提供最简单的纯 LLM 对话图。

---

## 2. `rag_graph.py`

- `make_rag_node(rag_service: RAGService)`：
  - 找最后一条 user 消息；
  - 调用 `rag_service.query(question)`；
  - 将回答写入 `messages` 和 `rag_answer`；
  - 向 `traces` 中 append 一个 `TraceEvent(kind="rag", info={...})`。
- `build_rag_graph(rag_service)`
  - 只有一个节点 `rag`；
  - `entry = rag`，`rag -> END`。

用途：  
- 提供纯 RAG 对话图，常用于测试 RAG pipeline。

---

## 3. `routed_graph.py`

- Router：
  - `route_by_keywords(state) -> "llm" | "rag"`：
    - 根据关键字（资料 / 文档 / 知识库 / rag / embedding / 检索 / 查一下等）决定走 RAG；
    - 否则走 LLM。
  - `router_node(state)`：
    - 在 `traces` 中写入一条 `TraceEvent(kind="router", info={"decision": decision})`；
    - 返回 `{"traces": traces}`。

- 图结构：
  - 节点：`router` / `llm` / `rag`
  - `entry = router`
  - `add_conditional_edges("router", route_by_keywords, {"llm": "llm", "rag": "rag"})`
  - `llm -> END`，`rag -> END`

用途：  
- 提供多分支图的基础；
- 未来可以将 `route_by_keywords` 替换为：
  - LLM 决策；
  - RL policy 等。

---

## 4. 与其他模块的关系

- 所有图都依赖：
  - `AgentState`（统一状态类型）
  - `LLMClient` / `RAGService` 等能力接口
- CLI：
  - `echo.py` 使用 `build_simple_graph(VllmLLMClient())`
  - `rag_chat.py` 使用 `build_rag_graph(RAGService)`
  - `router_chat.py` 使用 `build_routed_graph(VllmLLMClient(), RAGService)`
