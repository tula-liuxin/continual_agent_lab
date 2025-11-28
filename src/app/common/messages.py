# src/app/common/messages.py

from typing import Literal, Optional
from pydantic import BaseModel


# 约束消息的角色：只能是这几种字符串之一
Role = Literal["user", "assistant", "system", "tool"]


class Message(BaseModel):
    """
    系统内部统一使用的“消息”数据结构。

    为什么要单独建一个 Message 类型？
    - 以后所有模块（LangGraph、RAG、LLM 调用）都用它，避免满地 dict。
    - 便于做静态检查 / 自动补全 / 重构。
    - 设计时就考虑好：role、content、tool_call 等信息怎么统一表示。
    """

    role: Role
    content: str

    # 可选：工具调用 / 名字等信息，后面接 LangGraph / 工具调用时会用到
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
