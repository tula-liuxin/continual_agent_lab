# app/infra/llm/llamaindex_qwen.py

from llama_index.llms.openai_like import OpenAILike
from app.config.base import get_settings


def build_llamaindex_qwen_llm() -> OpenAILike:
    """
    构建一个给 LlamaIndex 用的 LLM（Qwen + vLLM, OpenAI-compatible）。

    使用 OpenAILike 而不是 OpenAI：
    - 不再去查 OpenAI 官方模型表（避免 Qwen 模型名报错）
    - 手动指定 context_window / is_chat_model 等元信息
    """
    settings = get_settings()

    llm = OpenAILike(
        model=settings.qwen_model,          # "Qwen/Qwen2.5-3B-Instruct"
        api_base=settings.vllm_base_url,    # "http://localhost:8000/v1"
        api_key="EMPTY",                    # vLLM 默认不校验 key，随便给个字符串
        context_window=2048,                # 跟你启动 vLLM 时的 --max-model-len 对齐
        is_chat_model=True,                 # 走 /v1/chat/completions
        is_function_calling_model=False,    # 先不管 tools，后面再说
        temperature=0.7,
    )
    return llm
