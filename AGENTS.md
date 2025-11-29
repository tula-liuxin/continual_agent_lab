# Repository Guidelines

## 目的
- 面向贡献者与后续 AI 助手的完整导航：一站式了解目标、分层、核心抽象、目录结构、运行方式、风格约定与未来演进。
- 默认环境：Ubuntu 22.04.5 + RTX 4060 Ti + Python 3.11（conda `continual_agent_env`），仅本地/开源模型，禁止付费 OpenAI 云。

## 技术栈与约束
- LLM：vLLM OpenAI-compatible + `Qwen/Qwen2.5-3B-Instruct`（默认），客户端 `app/infra/llm/vllm_client.py`；LlamaIndex 侧使用 `build_llamaindex_qwen_llm`.
- Embedding：`BAAI/bge-m3` via FlagEmbedding，封装 `app/infra/embed/bge_m3.py`；LlamaIndex 适配 `LlamaIndexBgeM3Embedding`.
- RAG：LlamaIndex VectorStoreIndex + 自定义 LLM/Embedding，服务封装 `app/rag/service.py`.
- 编排：LangGraph 1.0 `StateGraph`；图定义 `app/graph/*.py`。
- 配置：`AppSettings` (`app/config/base.py`)，环境变量前缀 `AGENT_`，读取 `.env`，`HF_ENDPOINT=https://hf-mirror.com`（大陆建议），关闭错误代理。

## 目录与模块（缩进表示层级）
- 根目录
  - `README.md`：项目简介与运行示例（中文）。
  - `VISION.md`：长期愿景（本地多 Agent + 工具 + RL）。
  - `ARCHITECTURE.md`：分层、核心数据结构、图设计。
  - `DEV_NOTES.md`：按时间记录重大改动/原因（务必更新）。
  - `PROMPT_HANDBOOK.md`：给新模型的交接 Prompt。
  - `report.md`：模块/函数清单速览。
  - `requirements.txt`：依赖列表。
  - `scripts/`：预留脚本目录（当前空）。
  - `tests/`：pytest 用例（当前空，新增测试放这里）。
- `src/app/`
  - `common/`：`Message`、`AgentState`、`RAGAnswer`、`TraceEvent` 基础类型；见 `MODULE.md`.
  - `config/`：`AppSettings` + `get_settings()`，统一配置入口。
  - `infra/`
    - `llm/`：`LLMClient` 协议、`DummyLLMClient`、`VllmLLMClient`、`build_llamaindex_qwen_llm`。
    - `embed/`：`EmbeddingClient` 协议、`BgeM3EmbeddingClient`、`LlamaIndexBgeM3Embedding`。
  - `rag/`：`RAGService`（构建索引、`query(question, top_k)` 返回 `RAGAnswer`）。
  - `graph/`：LangGraph 图
    - `simple_graph.py`：单 LLM 节点。
    - `rag_graph.py`：单 RAG 节点，写回 `rag_answer` + trace。
    - `routed_graph.py`：`router -> (llm|rag) -> END`，关键词路由 + trace。
  - `cli/`：入口脚本 `echo`/`rag_demo`/`rag_chat`/`router_chat`。
  - `agents/`：占位包，预留未来 Agent 实现。

## 核心抽象与数据流
- `Message`：Pydantic，`role` ∈ {user, assistant, system, tool}，`content` 文本。
- `AgentState`：TypedDict，`messages`（必填），可选 `rag_answer`、`traces`；LangGraph 节点返回 partial state。
- `RAGAnswer`/`RetrievedChunk`：RAG 结果与检索片段（text/score/metadata）。
- `TraceEvent`：轨迹事件（ts/node/kind/info），Router/RAG 节点写入，后续可扩展 reward/episode_id/tool_name。

## 图与 CLI
- `simple_graph`：入口 `llm`，调用 `LLMClient.chat`，单节点对话；CLI `python -m app.cli.echo`.
- `rag_graph`：入口 `rag`，取最后 user 问题 → `RAGService.query`，写 messages、rag_answer、trace；CLI `python -m app.cli.rag_chat`.
- `routed_graph`：入口 `router`，`route_by_keywords` 判定 `llm` or `rag`，`router_node` 记录决策；CLI `python -m app.cli.router_chat`.
- RAG Demo：不经 LangGraph，直接调用服务 `python -m app.cli.rag_demo`.

## 开发与运行
- 环境准备示例：
  - `conda create -n continual_agent_env python=3.11 -y && conda activate continual_agent_env`
  - `pip install -r requirements.txt`
  - 启动 vLLM（示例）：`python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-3B-Instruct --host 0.0.0.0 --port 8000 --dtype float16 --max-model-len 2048 --max-num-seqs 4 --max-num-batched-tokens 2048 --gpu-memory-utilization 0.5 --trust-remote-code`
- 运行命令：见“图与 CLI”；测试：`pytest`（新增用例请放 `tests/`，命名 `test_*.py`）。

## 风格与质量
- 代码：Python 3，4 空格缩进，PEP8 + 类型注解；命名 `snake_case`（函数/变量）、`CamelCase`（类）、`UPPER_SNAKE`（常量）。
- 设计：分层解耦，接口稳定（`LLMClient` / `EmbeddingClient` / `RAGService` / `AgentState`）；优先用 Pydantic/TypedDict，避免散落 dict。
- 注释：仅在行为非直观处简要说明；保持模块职责单一。
- 测试：图逻辑校验 messages 变更与 traces；RAG 校验 contexts 长度与可比较的 score；对外依赖（vLLM/HTTP）尽量 mock，样例小而确定。

## 配置与安全
- 环境变量统一 `AGENT_` 前缀：`AGENT_VLLM_BASE_URL`、`AGENT_QWEN_MODEL`、`AGENT_EMBEDDING_MODEL`、`AGENT_ENV` 等。
- 不提交密钥；vLLM 通常不校验 api_key，可用占位符；端点视为私有，生产避免记录完整 prompt/response。
- 大陆网络：设置 `HF_ENDPOINT=https://hf-mirror.com`，关闭错误的 HTTP(S) 代理。

## 文档与交接
- 重大改动写入 `DEV_NOTES.md`；架构/数据流参考 `ARCHITECTURE.md`；愿景与路线看 `VISION.md`；模块速览看 `report.md`。
- 新模型接手前，先阅读并粘贴 `PROMPT_HANDBOOK.md` 的交接 Prompt，保持设计/约束一致。

## 未来演进提示
- Router 可从关键词规则升级为 LLM/分类器或 RL policy，TraceEvent 扩展 reward/episode_id/tool 调用记录。
- RAG 扩展：文件系统加载、持久化/增量索引、多种检索模式，丰富 metadata（路径/行号）。
- 多工具/多 Agent/子图协作与强化学习是主要方向，保持现有接口稳定以便无痛演进。***
