# src/app/graph/rag_graph.py

from typing import Dict, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END

from app.common.state import AgentState
from app.common.messages import Message
from app.common.tracing import TraceEvent
from app.rag.service import RAGService


def make_rag_node(rag_service: RAGService):
    """
    基于 RAGService 的 LangGraph 节点工厂：
    - 读出最后一条 user 消息作为 question
    - 调用 rag_service.query(question)
    - 把 answer 加到 messages 里
    - 同时把完整 RAGAnswer 放到 state["rag_answer"]
    - 记录一个 TraceEvent
    """

    def rag_node(state: AgentState) -> Dict:
        messages = state.get("messages", [])
        traces = list(state.get("traces", []))  # 取出已有轨迹

        # 找最后一条 user 消息
        last_user: Optional[Message] = None
        for msg in reversed(messages):
            if msg.role == "user":
                last_user = msg
                break

        if last_user is None:
            reply_text = "RAG 节点：还没有收到用户问题。"
            rag_answer = None

            # 记录 trace
            traces.append(
                TraceEvent(
                    ts=datetime.utcnow(),
                    node="rag",
                    kind="rag",
                    info={"reason": "no_user_message"},
                )
            )
        else:
            question = last_user.content
            rag_answer = rag_service.query(question, top_k=2)
            reply_text = rag_answer.answer

            # 记录 trace
            traces.append(
                TraceEvent(
                    ts=datetime.utcnow(),
                    node="rag",
                    kind="rag",
                    info={
                        "question": question,
                        "num_contexts": len(rag_answer.contexts),
                    },
                )
            )

        # 构造 assistant 消息
        reply_msg = Message(role="assistant", content=reply_text)
        new_messages = messages + [reply_msg]

        # 按 LangGraph 约定返回“部分状态”
        new_state: Dict = {
            "messages": new_messages,
            "traces": traces,
        }
        if rag_answer is not None:
            new_state["rag_answer"] = rag_answer

        return new_state

    return rag_node


def build_rag_graph(rag_service: RAGService):
    """
    构建一个只包含 RAG 节点的 StateGraph：
    - 入口节点：rag
    - rag 节点执行完就结束
    """
    graph = StateGraph(AgentState)

    graph.add_node("rag", make_rag_node(rag_service))
    graph.set_entry_point("rag")
    graph.add_edge("rag", END)

    app = graph.compile()
    return app
