1. 目前项目整体结构概览
1）分层结构（按你最初的要求）

现在代码基本已经按你一开始说的「分层 / 模块化」来走了，大致是这样：

Layer 0：配置 & 通用类型

src/app/config/base.py

AppSettings：全局配置（env、project_name、vllm_base_url、qwen_model、embedding_model 等）

支持 .env + 环境变量（AGENT_ 前缀）。

src/app/common/messages.py

统一的 Message（pydantic）：role + content

整个系统所有对话都用这个结构。

src/app/common/state.py

AgentState（TypedDict）：

messages: list[Message]

rag_answer?: RAGAnswer

traces?: list[TraceEvent]

src/app/common/rag_types.py

RetrievedChunk：一个检索片段（text + score + metadata）

RAGAnswer：RAG 的统一输出（answer + contexts）。

src/app/common/tracing.py

TraceEvent：记录每次节点/决策的结构化事件（node、kind、info、ts）。

这一层就是你说的「统一数据结构」，以后不管是 LangGraph、LlamaIndex、RL，都围绕这些结构转。

Layer 1：基础能力（Infra）

src/app/infra/llm/base.py

LLMClient(Protocol)：定义 chat(messages: list[Message]) -> Message 接口。

src/app/infra/llm/dummy.py

DummyLLMClient：一开始用的假 LLM（现在基本可以当测试用）。

src/app/infra/llm/vllm_client.py

VllmLLMClient：

用 OpenAI SDK 调你本地的 vLLM OpenAI-compatible 服务

模型名从 AppSettings.qwen_model 读（现在是 Qwen2.5-3B-Instruct）

src/app/infra/llm/llamaindex_qwen.py

build_llamaindex_qwen_llm()：

返回一个 OpenAILike LLM 给 LlamaIndex 用

同样走 vLLM，模型名和 base_url 统一从配置里来。

src/app/infra/embed/base.py

EmbeddingClient(Protocol)：

embed_documents(texts: List[str]) -> np.ndarray

embed_query(text: str) -> np.ndarray

src/app/infra/embed/bge_m3.py

BgeM3EmbeddingClient：

用 FlagEmbedding.BGEM3FlagModel 加载 BAAI/bge-m3

embed_query / embed_documents 输出 numpy 向量。

src/app/infra/embed/llamaindex_bge_m3.py

LlamaIndexBgeM3Embedding(BaseEmbedding)：

把 BGE-M3 包装成 LlamaIndex 能用的 Embedding 模型。

这一层相当于“所有模型相关的东西”：

LLM = Qwen(vLLM)

Embedding = BGE-M3
都隐藏在统一接口后面。

Layer 2：RAG 服务

src/app/rag/service.py

RAGService：

初始化时：用 LlamaIndex + BGE-M3 + Qwen 构建向量索引 + QueryEngine

对外只暴露：query(question: str, top_k:int=2) -> RAGAnswer

内部的 Document / Index / QueryEngine 对上层是透明的。

这是未来所有「查知识库」能力的统一入口，后面只要扩知识库、换存储、改检索策略，都在这层改。

Layer 3：LangGraph 图

src/app/graph/simple_graph.py

make_llm_node(llm_client)：

LangGraph 节点：读取 state["messages"] → 调 llm_client.chat() → 把 reply 追加到 messages。

build_simple_graph(llm_client)：

一个只有 LLM 节点的图：entry -> llm -> END。

src/app/graph/rag_graph.py

make_rag_node(rag_service)：

读最后一条 user message → 调 rag_service.query() →

把回答追加到 messages

把 RAGAnswer 写入 state["rag_answer"]

同时在 state["traces"] 里追加一条 TraceEvent(kind="rag")。

build_rag_graph(rag_service)：

图：entry -> rag -> END

src/app/graph/routed_graph.py

route_by_keywords(state)：简单关键词路由逻辑（决定 "llm" 或 "rag"）。

router_node(state)：

调 route_by_keywords，写入一条 TraceEvent(kind="router", info={"decision": ...})

不改 messages。

build_routed_graph(llm_client, rag_service)：

图结构：

entry -> router

router --(llm)--> llm -> END

router --(rag)--> rag -> END

这一层就是“Agent 的大脑结构”，后面加多工具、多 Agent、RL 等，都是在这层改图结构，而不是到处 if-else。

Layer 4：CLI / 对外入口

src/app/cli/echo.py

用 build_simple_graph(VllmLLMClient()) 做一个 LLM 对话 CLI。

src/app/cli/rag_demo.py

直接调用 RAGService 做命令行的 RAG demo（不走 LangGraph）。

src/app/cli/rag_chat.py

用 build_rag_graph(RAGService) 做“纯 RAG 对话” CLI。

src/app/cli/router_chat.py

用 build_routed_graph(VllmLLMClient, RAGService) 做“Router (LLM + RAG) 对话” CLI，

终端上还能看到 rag_answer 的 context 和 traces。
