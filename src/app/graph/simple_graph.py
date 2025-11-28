# src/app/graph/simple_graph.py

from typing import Dict

from langgraph.graph import StateGraph, END

from app.common.state import AgentState
from app.common.messages import Message
from app.infra.llm.base import LLMClient


def make_llm_node(llm_client: LLMClient):
    """
    返回一个“闭包节点”，内部持有 llm_client。
    LangGraph 节点签名仍然是：state -> partial_state。
    """

    def llm_node(state: AgentState) -> Dict:
        messages = state.get("messages", [])

        # 调用统一的 LLM 接口
        reply: Message = llm_client.chat(messages)

        new_messages = messages + [reply]
        return {"messages": new_messages}

    return llm_node


def build_simple_graph(llm_client: LLMClient):
    """
    构建并编译一个最简单的 StateGraph：
    - 只有一个节点：llm
    - 入口也是它，结束也是它
    - 节点内部使用注入进来的 llm_client
    """
    graph = StateGraph(AgentState)

    # 注册节点（使用闭包包装的 llm_node）
    graph.add_node("llm", make_llm_node(llm_client))

    # 设置入口节点
    graph.set_entry_point("llm")

    # llm 节点执行完就结束
    graph.add_edge("llm", END)

    # 编译成可执行图（LangGraph 1.0 的 StateGraph API）
    app = graph.compile()
    return app
