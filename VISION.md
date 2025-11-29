# VISION - continual_agent_lab 最终愿景

> 把一台装着 Ubuntu + RTX 4060 Ti 的个人电脑，变成一个  
> **可以不断进化的本地 AI Agent 实验室**  
> ——在这里，你可以用开源模型、LangGraph 1.0、RAG、RL  
>  逐步打造出真正理解你、能陪你长期成长的 AI 研究伙伴。

---

## 1. 一句话愿景

在 **完全本地、完全开源、可控成本** 的前提下，  
打造一个围绕 LangGraph 1.0 的多 Agent 框架：

- 能统一地接入：本地 LLM（Qwen 系列）、Embedding（BGE-M3）、RAG（LlamaIndex）、各种工具；
- 能通过 **轨迹记录 + 评估 + 强化学习**，不断改善自身的决策和行为；
- 最终成为一个 **“个人 AI 操作系统 / 一人公司搭档 / 研究助手”**，而不只是一个聊天机器人。

---

## 2. 设计哲学

### 2.1 本地优先 · 开源优先 · 免费优先

- 推理和检索全部跑在本地：
  - LLM：`vLLM + Qwen/Qwen2.5-3B-Instruct`（或未来的其他 Qwen 系列）；
  - Embedding：`BAAI/bge-m3`，通过 `FlagEmbedding`；
  - 检索与 RAG：`LlamaIndex` + 本地向量索引。
- 不依赖任何付费云 API（特别是 OpenAI 官方云），所有能力都可以在离线或“只用镜像站”的条件下运行。
- 所有关键组件都用开源方案，方便未来替换和深度定制（包括 RL 训练阶段）。

### 2.2 模块化与分层：每一层都有清晰边界

框架分为几个层级，每一层都尽量只关注一类问题：

1. **基础设施层**（Infra）
   - 配置管理：`AppSettings`（pydantic-settings + `AGENT_` 前缀 + `.env`）
   - LLM 客户端：`LLMClient` 协议 + `VllmLLMClient`
   - Embedding 客户端：`EmbeddingClient` 协议 + `BgeM3EmbeddingClient`
   - 对 LlamaIndex 的适配：`LlamaIndexBgeM3Embedding`、`OpenAILike` Qwen LLM
2. **能力层**（Capabilities）
   - `RAGService`：统一封装 LlamaIndex + BGE-M3 + Qwen，实现 “问问题 → 检索 + 生成回答” 的完整链路。
3. **编排层**（Orchestration）
   - 使用 **LangGraph 1.0 的 StateGraph API** 构建：
     - 纯 LLM 图
     - 纯 RAG 图
     - Router 图（在 LLM / RAG 之间路由）
   - 未来扩展到多 Agent / 多工具 / 子图 / 分层规划。
4. **接口层**（Interface）
   - 目前是 CLI（命令行交互）：
     - `echo`、`rag_demo`、`rag_chat`、`router_chat`
   - 未来可能是：
     - Web UI / REST API / 和其他系统的桥接。

> **核心原则：**  
> - 统一接口（`LLMClient`、`EmbeddingClient`、`RAGService`、`AgentState`）  
> - 层与层之间不要互相穿透、互相引用内部细节。  
> 这样未来改一层，不必推翻重做整个系统。

### 2.3 状态统一与可观测性：一切都写进 AgentState

- 全系统局部“真相来源”：`AgentState`（TypedDict）
  - `messages`: 对话历史（user / assistant / system / tool）
  - `rag_answer`: 最近一次 RAG 查询的结果（带 contexts）
  - `traces`: 一次对话 / 一轮调用中发生的关键事件（TraceEvent 列表）
- 所有 LangGraph 图都以 `AgentState` 为“流动的黑盒”：
  - 节点读取部分字段，写回部分字段；
  - 不需要每个节点到处发 print，而是通过 `traces` 做结构化记录。
- `TraceEvent` 明确记录：
  - 哪个节点被调用（router / rag / llm / other）
  - 决策结果（比如 router 决定走 llm 还是 rag）
  - 重要参数（问题是什么、RAG 检索到多少上下文等）

> 这为后续的 **评估 / 诊断 / RL 训练** 提供天然的数据基础。

### 2.4 渐进式复杂化：先跑起来，再变聪明

- 不追求一上来就做“超级多 Agent + 复杂协作”的系统；
- 当前路线是：
  1. 单 Agent + 单图（简单 LLM 对话）  
  2. 单 Agent + RAG（知识库问答）  
  3. 单 Agent + Router（在 LLM / RAG 之间决策）  
  4. 在这个基础上，增加更多工具节点 / 子 Agent / trace / RL。
- 每一个阶段都保持：
  - 有可以运行的 CLI / 示例；
  - 文档配套更新（尤其是 `DEV_NOTES.md`，记录重大决策）。
- 以后即便改用多 Agent、大规模管线，也只是在现在的基础上“堆模块”，而不是重写一切。

---

## 3. 三阶段发展路线图

> 这不是死板的时间表，而是一种“系统演化难度”的分层。

### Phase 1：稳定的本地 Agent 底座（当前所在阶段）

**目标：**  
在你的 Ubuntu + 4060 Ti 环境上，稳定跑起来一个“能用、可调试、结构清晰”的 Agent 系统。

- ✅ 本地 Qwen(vLLM) + OpenAI-compatible API  
- ✅ BGE-M3 Embedding + FlagEmbedding  
- ✅ LlamaIndex RAG + 自定义 Embedding / LLM 适配  
- ✅ LangGraph 1.0 的图：
  - 纯 LLM 图（对话）
  - 纯 RAG 图（知识库问答）
  - Router 图（在 LLM / RAG 之间路由）
- ✅ 统一数据结构：
  - `Message`、`AgentState`、`RAGAnswer`、`TraceEvent`
- ✅ 初步可观测性：
  - Router 决策写入 trace
  - RAG 查询行为写入 trace

**Phase 1 的交付物：**

- 可以通过 CLI 和 Agent 稳定互动；
- 能够查看每次对话的 trace，理解系统是怎么做决策的；
- 文档清晰：`README` / `VISION` / `ARCHITECTURE` / `DEV_NOTES` 已经可读。

---

### Phase 2：多工具、多任务、多 Agent 的“个人 AI 中枢”

**目标：**  
在稳定底座之上，把 Agent 变成真正能“帮你做事”的中枢，而不是只有聊天 / 查文档。

可能的演化方向：

1. **更多工具节点**
   - 文件系统工具：读取 / 搜索本地项目代码、笔记、数据；
   - HTTP 工具：访问你指定的 API（例如 A 股数据、健康数据、工作项目 API 等）；
   - 代码执行环境：在安全沙箱中跑 Python / 脚本。
2. **多个专长 Agent / 子图**
   - RAG 专家：负责检索、总结文档；
   - 代码助手：负责阅读 / 修改代码；
   - 任务规划 Agent：负责拆解复杂任务，调度其他 Agent；
3. **更强的观察与评估**
   - 针对不同任务类型定义不同的“成功标准”和打分逻辑；
   - 使用 `TraceEvent` 中的信息，对每个 episode 做 offline 评估：
     - 是否走对了路径（LLM or RAG or 工具）？
     - 决策是否合理？

在这一阶段，LangGraph 不再只是“一条线的对话图”，而是：

- 多个子图 / 子 Agent；
- 带有分支、循环、工具调用的复杂图结构；
- 可以根据任务类型和上下文动态选择不同子图。

---

### Phase 3：引入强化学习，让 Agent 真正“学会做决策”

**目标：**  
利用前面阶段积累下来的轨迹（traces + 回答质量 + 用户反馈），  
训练出更好的决策策略，而不是永远靠“写死的 if-else 或 prompt”。

可能的 RL 切入点：

1. **Router 策略学习**
   - 当前 router 是简单关键词规则；
   - 未来可以：
     - 用一个轻量 LLM / 分类器来预测 “走 LLM / RAG / 某工具”；
     - 用 offline RL（基于历史 trace 和 reward）训练一个 policy；
   - 状态输入：
     - 当前对话上下文（messages 的摘要）；
     - 最近若干步的 `traces`；
   - 动作空间：
     - 选择下一个节点（llm / rag / 某工具 / 某子图）。

2. **工具调用策略 / 参数策略**
   - 学会在什么场景调用哪个工具；
   - 学会如何设置合适的参数（例如检索 top_k、温度、工具链长度等）。

3. **长期“自我改进”循环**
   - 利用 `TraceEvent + AgentState` 存档：
     - 收集 episode；
     - 分析失败 case；
     - 微调策略网络或 LLM；
   - 概念上类似于：
     - “一人公司 + 一群 Agent 员工 + 持续改进的 SOP + 不断训练的决策系统”。

---

## 4. 面向“未来的你”和“未来接手这个项目的 AI / 人类”

### 4.1 未来的你

- 当你几年后再打开这个仓库，希望你能快速恢复记忆：
  - 看 `VISION.md`，知道你当时想做的是一个 **持续进化的本地 Agent Lab**；
  - 看 `ARCHITECTURE.md`，知道当前抽象与模块边界；
  - 看 `DEV_NOTES.md`，知道你走到了 Phase 1 的哪个子阶段；
  - 看代码中的 `AgentState` / `TraceEvent`，一眼就理解“数据流长什么样”。

### 4.2 后续接手的 AI 助手（新的 GPT / 新模型）

- 每次切换到一个新的 GPT / 新大模型协作者时：
  - 把 `PROMPT_HANDBOOK.md` 中的“交接 prompt”复制过去；
  - 让它阅读：`VISION.md` + `ARCHITECTURE.md` + `DEV_NOTES.md`；
  - 再开始新一轮的“边设计边实现”。
- 希望任何一个足够聪明的模型，看完这些文档之后：
  - 不需要你重新讲一遍整个项目历史；
  - 就能顺畅地延续你的设计风格和技术约束。

### 4.3 后续可能加入的人类合作者

- 一眼能看出：
  - 这是一个“本地化、多 Agent、可追踪、可做 RL 的 Agent 框架”；
  - 而不是一堆散装的脚本。
- 可以从自己熟悉的点切入：
  - LangGraph 架构设计；
  - RAG 与向量库；
  - RL 设计与实现。

---

## 5. 总结：一个能陪你持续成长的本地 Agent 实验室

`continual_agent_lab` 的最终目标不是：

- “做一个 ChatGPT 克隆”，也不是  
- “做一个炫技式的巨型框架”。

而是：

- 在你可控的硬件与网络环境中，  
- 通过反复迭代、压缩复杂度、引入 RL 与工具链，  
- 打造一个真正能理解你、陪你一起实验、一起成长的 **长期 AI 研究伙伴**。

它既是你的一人公司神经中枢，也是你未来做更大项目的试验田。

> 这个 VISION 文件的职责，就是帮你和未来的协作者（包括新的 GPT）  
> 在任何时候都能对齐：  
> **“我们到底要把这个系统带向哪里？”**
