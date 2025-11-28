# src/app/common/tracing.py

from typing import Any, Dict, Literal
from datetime import datetime

from pydantic import BaseModel


class TraceEvent(BaseModel):
    """
    用来记录一次“节点执行情况 / 决策过程”的结构化事件。

    字段：
    - ts: 发生时间（UTC）
    - node: 节点名，比如 "router" / "llm" / "rag"
    - kind: 粗粒度类型，方便过滤
    - info: 任意补充信息（dict），比如决策结果、问题文本等
    """

    ts: datetime
    node: str
    kind: Literal["router", "llm", "rag", "other"]
    info: Dict[str, Any] = {}
