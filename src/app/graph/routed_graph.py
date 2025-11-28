# src/app/graph/routed_graph.py

from typing import Dict
from datetime import datetime

from langgraph.graph import StateGraph, END

from app.common.state import AgentState
from app.common.tracing import TraceEvent
from app.infra.llm.base import LLMClient
from app.rag.service import RAGService
from app.graph.simple_graph import make_llm_node
from app.graph.rag_graph import make_rag_node


def route_by_keywords(state: AgentState) -> str:
    """
    一个非常简单的 Router 策略：
    - 如果用户问题中包含和“知识/文档/RAG”相关的关键词 -> 走 'rag'
    - 否则走 'llm'
    """
    messages = state.get("messages", [])
    if not messages:
        return "llm"

    last_user = None
    for msg in reversed(messages):
        if msg.role == "user":
            last_user = msg
            break

    if last_user is None:
        return "llm"

    q = last_user.content.lower()

    rag_keywords = [
        "资料",
        "文档",
        "知识库",
        "rag",
        "embedding",
        "嵌入",
        "检索",
        "查一下",
    ]

    if any(kw in q for kw in rag_keywords):
        return "rag"

    return "llm"


def router_node(state: AgentState) -> Dict:
    """
    Router 节点本身不修改 messages，只往 traces 里写一条“我做了路由决策”的事件。
    真正的分支选择由 add_conditional_edges + route_by_keywords 完成。
    """
    traces = list(state.get("traces", []))

    decision = route_by_keywords(state)

    traces.append(
        TraceEvent(
            ts=datetime.utcnow(),
            node="router",
            kind="router",
            info={"decision": decision},
        )
    )

    # 注意：这里返回的 partial_state 里不包含 messages 的修改，
    # LangGraph 照样会用 route_by_keywords 决定下一跳。
    return {"traces": traces}


def build_routed_graph(llm_client: LLMClient, rag_service: RAGService):
    """
    构建一个带 Router 的 StateGraph：

    结构：
      entry -> router -> (llm | rag) -> END
    """
    graph = StateGraph(AgentState)

    # 1. 注册节点
    graph.add_node("router", router_node)
    graph.add_node("llm", make_llm_node(llm_client))
    graph.add_node("rag", make_rag_node(rag_service))

    # 2. 设置入口
    graph.set_entry_point("router")

    # 3. 条件边：根据 route_by_keywords 决定从 router 走向哪个节点
    graph.add_conditional_edges(
        "router",
        route_by_keywords,
        {
            "llm": "llm",
            "rag": "rag",
        },
    )

    # 4. 两个分支最后都结束
    graph.add_edge("llm", END)
    graph.add_edge("rag", END)

    app = graph.compile()
    return app
