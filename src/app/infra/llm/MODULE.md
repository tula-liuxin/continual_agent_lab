# MODULE - app/infra/llm

> 封装各种 LLM 客户端与 LlamaIndex 所需的 LLM 封装。

---

## 1. `base.py`

- 定义 LLM 接口 `LLMClient(Protocol)`：

```python
class LLMClient(Protocol):
    def chat(self, messages: List[Message]) -> Message:
        ...
任何实现只要提供 chat() 方法即可被当作 LLMClient 使用；

避免强继承，保持灵活性。

2. dummy.py

DummyLLMClient：

用于早期测试 / fallback：

从 messages 中找最后一条 user 消息；

返回一个简单的 “DummyLLM 模拟回复：xxx”。

现在主要作为示例，真实对话已由 VllmLLMClient 负责。

3. vllm_client.py

VllmLLMClient(LLMClient)：

使用 openai.OpenAI 客户端；

将 base_url 指向本地 vLLM 的 OpenAI-compatible server；

api_key 使用占位字符串（vLLM 通常不校验）。

主要逻辑：

self._client = OpenAI(base_url=settings.vllm_base_url, api_key="EMPTY")
resp = self._client.chat.completions.create(
    model=self.model,
    messages=oa_messages,
    temperature=0.7,
)


供 LangGraph 中的 llm 节点调用；

返回值统一为 Message(role="assistant", content=...)。

4. llamaindex_qwen.py

提供 build_llamaindex_qwen_llm()：

返回 llama_index.llms.openai_like.OpenAILike 实例；

使用 api_base=settings.vllm_base_url；

model=settings.qwen_model；

手动指定 context_window、is_chat_model=True。

作用：

给 LlamaIndex 提供一个“不会因为 Qwen 模型名报错”的 LLM 实现；

避免使用 llama_index.llms.openai.OpenAI 默认的 OpenAI 模型表。

5. 与其他模块的关系

LangGraph 的 LLM 节点：只依赖 LLMClient 接口；

LlamaIndex：通过 build_llamaindex_qwen_llm() 获取 OpenAILike 实例；

配置来源：app/config/base.py 中的 AppSettings。