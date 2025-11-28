# src/app/infra/llm/dummy.py

from typing import List, Optional

from app.common.messages import Message
from app.infra.llm.base import LLMClient


class DummyLLMClient:
    """
    一个“假”的 LLM 实现，用来在还没接入 vLLM 时打通流程。

    行为：
    - 找到最后一条 user 消息
    - 返回一条简单的“模拟回复”
    """

    def chat(self, messages: List[Message]) -> Message:
        last_user: Optional[Message] = None

        for msg in reversed(messages):
            if msg.role == "user":
                last_user = msg
                break

        if last_user is None:
            content = "DummyLLM：还没有收到用户消息 🤔"
        else:
            content = f"DummyLLM 模拟回复：{last_user.content}"

        return Message(role="assistant", content=content)
    # 以后我们只需要再写一个 VllmLLMClient(LLMClient)，替换掉 Dummy 就行，
    # 上层 LangGraph 完全不用改，这就是“接口+依赖注入”的好处。