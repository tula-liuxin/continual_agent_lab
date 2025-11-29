# continual_agent_lab

> 一个面向 **本地开源 LLM + LangGraph 1.0 + LlamaIndex + RAG + RL** 的实验项目。  
> 目标是打造一个可扩展的「多 Agent / 多工具 / 可强化学习」的个人 AI 助手系统。

---

## 项目特点（当前阶段）

- **免费 / 开源栈**：  
  - 推理：`vLLM` + `Qwen/Qwen2.5-3B-Instruct`（本地 GPU，OpenAI-compatible HTTP API）
  - Embedding：`BAAI/bge-m3` via `FlagEmbedding`
  - 编排：`LangGraph 1.0`（使用 `StateGraph` API）
  - 检索与 RAG：`LlamaIndex` + 自定义 `Embedding` + OpenAI-like LLM
- **模块化 & 分层设计**：
  - `app/common`：统一的消息 / 状态 / RAG 类型 / Trace 事件
  - `app/infra`：LLM 客户端、Embedding 客户端等底层基础设施
  - `app/rag`：对 LlamaIndex 的封装（`RAGService`）
  - `app/graph`：LangGraph 图（纯 LLM / RAG / Router）
  - `app/cli`：命令行入口（Echo、RAG Demo、RAG Chat、Router Chat）
- **面向 RL / 评估 的可追踪设计**：
  - 所有图的状态使用统一的 `AgentState`（TypedDict）
  - 内含 `messages`、`rag_answer`、`traces` 等字段
  - 节点会记录 `TraceEvent`，方便后续做 RL / 评估 / 审计

---

## 目录结构（简版）

```text
continual_agent_lab/
├── README.md
├── VISION.md
├── ARCHITECTURE.md
├── DEV_NOTES.md
├── PROMPT_HANDBOOK.md
├── requirements.txt
└── src/
    └── app/
        ├── common/
        │   ├── messages.py
        │   ├── state.py
        │   ├── rag_types.py
        │   ├── tracing.py
        │   └── MODULE.md
        ├── config/
        │   ├── base.py
        │   └── MODULE.md
        ├── infra/
        │   ├── MODULE.md
        │   ├── llm/
        │   │   ├── base.py
        │   │   ├── dummy.py
        │   │   ├── vllm_client.py
        │   │   ├── llamaindex_qwen.py
        │   │   └── MODULE.md
        │   └── embed/
        │       ├── base.py
        │       ├── bge_m3.py
        │       ├── llamaindex_bge_m3.py
        │       └── MODULE.md
        ├── graph/
        │   ├── simple_graph.py
        │   ├── rag_graph.py
        │   ├── routed_graph.py
        │   └── MODULE.md
        ├── rag/
        │   ├── service.py
        │   └── MODULE.md
        └── cli/
            ├── echo.py
            ├── rag_demo.py
            ├── rag_chat.py
            ├── router_chat.py
            └── MODULE.md

环境与运行方式
硬件 & 系统假设

GPU：NVIDIA RTX 4060 Ti 16GB

系统：Ubuntu 22.04.5 LTS

Python：3.11.x（通过 conda 管理）

仅使用 本地开源模型，不依赖付费 OpenAI API

一次性准备
# 创建并激活环境
conda create -n continual_agent_env python=3.11 -y
conda activate continual_agent_env

# 进入项目目录
cd ~/projects/continual_agent_lab

# 安装依赖
pip install -r requirements.txt


建议：在 continual_agent_env 的 conda 激活脚本中设置：

HF_ENDPOINT=https://hf-mirror.com（解决大陆访问 huggingface 问题）

关闭 HTTP(S) 代理（避免 socks:// scheme 报错）

启动本地 vLLM + Qwen 服务

在一个终端中：

conda activate continual_agent_env
cd ~/projects/continual_agent_lab

python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-3B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype float16 \
  --max-model-len 2048 \
  --max-num-seqs 4 \
  --max-num-batched-tokens 2048 \
  --gpu-memory-utilization 0.5 \
  --trust-remote-code

运行几个入口示例

在另一个终端中，激活同一个环境：

conda activate continual_agent_env
cd ~/projects/continual_agent_lab/src


纯 LLM Echo 对话（LangGraph + Qwen）

python -m app.cli.echo


RAG Demo（只验证 RAGService）

python -m app.cli.rag_demo


RAG 对话（LangGraph + RAGService）

python -m app.cli.rag_chat


Router 模式（自动在 LLM / RAG 之间路由）

python -m app.cli.router_chat