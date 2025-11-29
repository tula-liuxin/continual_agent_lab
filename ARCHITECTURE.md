# ARCHITECTURE - continual_agent_lab 架构说明

---

## 一、总体分层

从上到下，可以分成四层：

1. **接口层（Interface Layer）**
   - 目前主要是 CLI：  
     - `app/cli/echo.py`
     - `app/cli/rag_demo.py`
     - `app/cli/rag_chat.py`
     - `app/cli/router_chat.py`
   - 作用：把用户输入变成 `AgentState`，调用 LangGraph 图，并把结果展示出来。

2. **编排层（Orchestration Layer）**
   - LangGraph 1.0 的 `StateGraph` 图：  
     - `simple_graph.py`：最简单的 LLM 节点图  
     - `rag_graph.py`：只有一个 RAG 节点的图  
     - `routed_graph.py`：包含 Router + LLM + RAG 三种节点
   - 作用：定义“节点 → 边 → 状态流动”的逻辑。

3. **能力层（Capabilities Layer）**
   - RAG 能力：`app/rag/service.py` 中的 `RAGService`
   - LLM 能力：`app/infra/llm/*` 中的各类 `LLMClient` 实现
   - Embedding 能力：`app/infra/embed/*` 中的 `EmbeddingClient` 实现
   - 作用：以统一接口封装底层模型和 RAG 框架。

4. **基础设施层（Infra / Config Layer）**
   - 配置：`app/config/base.py`（使用 `pydantic-settings`）
   - 底层库：`vLLM`、`FlagEmbedding`、`LlamaIndex` 等
   - 环境变量：`AGENT_` 前缀、`HF_ENDPOINT` 等

---

## 二、核心数据结构

### 1. 对话消息：`Message`

位于：`app/common/messages.py`（略）

典型结构（pydantic 模型）：

```python
class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
用途：

所有对话历史都以 List[Message] 的形式存储在 AgentState.messages 中。

LLM / RAG / Router 都围绕这个统一的数据结构工作。

2. Agent 状态：AgentState

位于：app/common/state.py

class AgentState(TypedDict):
    messages: List[Message]
    rag_answer: NotRequired[RAGAnswer]
    traces: NotRequired[List[TraceEvent]]


messages：对话消息序列（user / assistant / system / tool）

rag_answer：最近一次 RAG 查询结果（RAGAnswer）

traces：本轮对话中的轨迹事件列表（TraceEvent）

3. RAG 类型：RAGAnswer 与 RetrievedChunk

位于：app/common/rag_types.py

class RetrievedChunk(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any] = {}

class RAGAnswer(BaseModel):
    answer: str
    contexts: List[RetrievedChunk]


RAG 节点的输出会写入 AgentState.rag_answer；

上层可以用它来：

展示“检索到的关键片段”；

后续给 RL 提供 reward 时参考。

4. Trace 事件：TraceEvent

位于：app/common/tracing.py

class TraceEvent(BaseModel):
    ts: datetime
    node: str
    kind: Literal["router", "llm", "rag", "other"]
    info: Dict[str, Any] = {}


ts：发生时间

node：节点名称（如 router / rag / llm）

kind：事件类型

info：任意补充信息（决策、问题、上下文数量等）

RAG 节点与 Router 节点会向 AgentState.traces 中 append 这些事件。

三、接口与实现的抽象层
1. LLMClient 接口

位于：app/infra/llm/base.py

class LLMClient(Protocol):
    def chat(self, messages: List[Message]) -> Message:
        ...


当前实现：

DummyLLMClient（早期打通流程，用来测试）

VllmLLMClient

使用 openai.OpenAI 客户端；

base_url 指向本地 vLLM 的 OpenAI-compatible API；

model 从配置中读取（默认 "Qwen/Qwen2.5-3B-Instruct"）。

在 LlamaIndex 侧，还有一个专门给 LlamaIndex 用的 LLM 封装：

build_llamaindex_qwen_llm()（app/infra/llm/llamaindex_qwen.py）

返回 llama_index.llms.openai_like.OpenAILike；

api_base 指向本地 vLLM；

避免使用 OpenAI 模型表（否则会因为 Qwen 模型名报错）。

2. EmbeddingClient 接口

位于：app/infra/embed/base.py

class EmbeddingClient(Protocol):
    def embed_documents(self, texts: List[str]) -> np.ndarray:
        ...

    def embed_query(self, text: str) -> np.ndarray:
        ...


当前实现：

BgeM3EmbeddingClient（app/infra/embed/bge_m3.py）

使用 FlagEmbedding.BGEM3FlagModel("BAAI/bge-m3")

通过 encode() 得到 dense 向量（shape = (N, D) 或 (D,)）

在 LlamaIndex 侧的适配器：

LlamaIndexBgeM3Embedding（app/infra/embed/llamaindex_bge_m3.py）

继承自 llama_index.core.embeddings.BaseEmbedding

内部调用 BgeM3EmbeddingClient

提供单条/多条 embedding 接口

3. RAGService 封装

位于：app/rag/service.py

职责：

初始化时：

设置 Settings.embed_model = LlamaIndexBgeM3Embedding()

设置 Settings.llm = build_llamaindex_qwen_llm()

用一组文本构建 VectorStoreIndex

保留 query_engine = index.as_query_engine(similarity_top_k=2)

提供：

query(question: str, top_k: int = 2) -> RAGAnswer

整个 LlamaIndex 的复杂度都被收敛在此处，上层（LangGraph 节点）只依赖：

rag_answer = rag_service.query(question, top_k=2)

四、LangGraph 图设计
1. simple_graph（纯 LLM 图）

位于：app/graph/simple_graph.py

结构：

节点：llm

Entry：llm

Edge：llm -> END

关键函数：

def make_llm_node(llm_client: LLMClient):
    def llm_node(state: AgentState) -> Dict:
        messages = state.get("messages", [])
        reply = llm_client.chat(messages)
        new_messages = messages + [reply]
        return {"messages": new_messages}
    return llm_node

def build_simple_graph(llm_client: LLMClient):
    graph = StateGraph(AgentState)
    graph.add_node("llm", make_llm_node(llm_client))
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)
    return graph.compile()

2. rag_graph（纯 RAG 图）

位于：app/graph/rag_graph.py

结构：

节点：rag

Entry：rag

Edge：rag -> END

RAG 节点行为：

找到最后一条 user 消息作为 question；

调 RAGService.query(question) 得到 RAGAnswer；

把 RAGAnswer.answer 作为 assistant 消息追加到 messages；

把 RAGAnswer 写入 state["rag_answer"]；

向 traces 写入一条 TraceEvent(kind="rag", info={...})。

3. routed_graph（Router + LLM + RAG）

位于：app/graph/routed_graph.py

结构：

entry -> router -> (llm | rag) -> END


路由策略（当前为规则路由）：

def route_by_keywords(state: AgentState) -> str:
    # 若最后一条 user 消息中包含“资料 / 文档 / 知识库 / rag / embedding / 检索 / 查一下”等关键词 -> "rag"
    # 否则 -> "llm"


Router 节点：

不修改 messages；

调用 route_by_keywords 得出决策；

往 traces append 一条 TraceEvent(kind="router", info={"decision": decision})；

返回 {"traces": traces} 作为 partial state；

LangGraph 中使用 add_conditional_edges("router", route_by_keywords, {"llm": "llm", "rag": "rag"})
来真正决定下一跳。

五、CLI 入口与用法
1. app/cli/echo.py

使用 build_simple_graph(VllmLLMClient())

实现一个最简单的「纯 LLM 对话」

2. app/cli/rag_demo.py

不用 LangGraph，只测试 RAGService 的行为；

在循环中：

从 stdin 读 question

调用 rag.query(question)

打印 answer 与 contexts

3. app/cli/rag_chat.py

使用 build_rag_graph(RAGService) 构建纯 RAG 图；

完整对话：

messages 中保留全部历史；

每轮调用 graph.invoke(state)；

打印回答和检索片段。

4. app/cli/router_chat.py

使用 build_routed_graph(VllmLLMClient(), RAGService)；

每轮对话：

Router 决定走 LLM 或 RAG；

若走 RAG，会展示检索片段；

traces 中记录路由与 RAG 行为。

六、未来扩展建议

Router 升级：

从简单关键词路由，升级为：

LLM 决策 Router 节点；

RL policy 控制 Router。

更多工具节点：

例如调用某个 API、代码执行环境、本地文件检索等。

更丰富的 Trace：

加入 reward、episode_id、tool_call_result 等字段；

做 offline RL 训练 / offline 评估。

多 Agent 图：

引入“Planner / Executor / Critic”等不同角色 Agent；

利用 LangGraph 1.0 的复杂图结构。