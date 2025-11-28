# src/app/infra/llm/base.py

from typing import Protocol, List

from app.common.messages import Message


class LLMClient(Protocol):
    """
    LLM 客户端的统一接口定义。

    以后不管底层是：
      - vLLM + Qwen
      - 其他开源推理框架
    只要实现了 chat() 这个方法，就能接到系统里。
    """

    def chat(self, messages: List[Message]) -> Message:
        """
        给定一段对话历史，返回一条 assistant 回复。
        """
        ...
        
    # 新概念：Protocol = 接口（鸭子类型）
    # 任何类只要有 chat(self, messages) -> Message 这个方法，就自动被当成 LLMClient，不需要继承。
