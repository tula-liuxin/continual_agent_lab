# src/app/infra/llm/vllm_client.py

from typing import List, Optional, Union

from openai import OpenAI

from app.common.messages import Message
from app.infra.llm.base import LLMClient
from app.config.base import get_settings


class VllmLLMClient(LLMClient):
    """
    使用 vLLM OpenAI-compatible 接口的真正 LLM 客户端。

    - 通过 OpenAI 官方 SDK 调用你本地的 vLLM 服务器
    - base_url / model 从 AppSettings 读取
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        settings = get_settings()

        # vLLM 的 OpenAI 兼容服务通常不验证 api_key，用一个占位就行
        self.base_url = base_url or settings.vllm_base_url
        self.api_key = api_key or "EMPTY"
        self.model = model or settings.qwen_model

        # OpenAI v1 客户端
        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=timeout,
        )

    def _to_openai_messages(self, messages: List[Message]) -> list[dict]:
        """把内部 Message 转成 OpenAI 格式的 messages 列表。"""
        return [
            {
                "role": m.role,
                "content": m.content,
            }
            for m in messages
        ]

    def _normalize_content(
        self, content: Union[str, list, None]
    ) -> str:
        """
        OpenAI v1 里 message.content 可能是 str 或 list（多模态），
        我们这里统一成 str。
        """
        if content is None:
            return ""

        if isinstance(content, str):
            return content

        # list 形式：选出 text 段拼接
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text":
                    parts.append(part.get("text", ""))
        if parts:
            return "".join(parts)

        # 兜底：转成字符串
        return str(content)

    def chat(self, messages: List[Message]) -> Message:
        """
        给定对话历史，通过 vLLM 的 OpenAI 接口生成一条 assistant 回复。
        """
        oa_messages = self._to_openai_messages(messages)

        resp = self._client.chat.completions.create(
            model=self.model,
            messages=oa_messages,
            temperature=0.7,
        )

        choice = resp.choices[0]
        content = self._normalize_content(choice.message.content)

        return Message(role="assistant", content=content)
