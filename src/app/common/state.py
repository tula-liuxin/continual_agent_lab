# src/app/common/state.py

from typing import List, TypedDict, NotRequired

from app.common.messages import Message
from app.common.rag_types import RAGAnswer
from app.common.tracing import TraceEvent


class AgentState(TypedDict):
    """
    LangGraph 图里流动的“状态”结构（当前版本）：

    - messages: 对话消息列表（user / assistant / system / tool）
    - rag_answer: 最近一次 RAG 查询的结果（可选）
    - traces: 本轮对话中的轨迹事件列表（可选）
    """

    messages: List[Message]
    rag_answer: NotRequired[RAGAnswer]
    traces: NotRequired[List[TraceEvent]]
