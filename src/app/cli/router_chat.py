# src/app/cli/router_chat.py

from app.common.messages import Message
from app.common.state import AgentState
from app.graph.routed_graph import build_routed_graph
from app.infra.llm.vllm_client import VllmLLMClient
from app.rag.service import RAGService


def main() -> None:
    print("🔹 continual_agent_lab CLI - Router (LLM + RAG) 模式")
    print("提示：请确保另一个终端里已经启动了 vLLM Qwen 服务器。")
    print("Router 会根据你的问题内容选择：纯 LLM 回复 or 先 RAG 再答。")
    print("输入内容后按回车，输入 'exit' / 'quit' / 'q' 退出。\n")

    # 1. LLM 客户端：Qwen(vLLM)
    llm_client = VllmLLMClient()

    # 2. 简单“知识库”
    texts = [
        "这个系统使用 BGE-M3 作为统一的文本 embedding 模型。",
        "本地大语言模型采用 Qwen2.5-3B-Instruct，通过 vLLM 暴露 OpenAI 兼容的 HTTP 接口。",
        "我们用 LangGraph 1.0 来编排多 Agent 流程，统一管理 AgentState 和工具调用。",
    ]
    rag_service = RAGService.from_texts(texts)

    # 3. 构建带 Router 的图
    graph = build_routed_graph(llm_client, rag_service)

    messages: list[Message] = []

    while True:
        user_text = input("你：").strip()

        if user_text.lower() in ("exit", "quit", "q"):
            print("👋 再见！")
            break

        messages.append(Message(role="user", content=user_text))

        state: AgentState = {"messages": messages}

        final_state = graph.invoke(state)

        messages = final_state["messages"]
        last_msg = messages[-1]

        print(f"\nagent：{last_msg.content}")

        # 如果这次走的是 RAG 分支，会有 rag_answer 字段
        rag_answer = final_state.get("rag_answer")
        if rag_answer is not None and rag_answer.contexts:
            print("\n🔍 检索到的关键片段：")
            for i, ctx in enumerate(rag_answer.contexts, start=1):
                print(f"\n[Top {i}] (score={ctx.score:.4f})")
                print(ctx.text)

        # ⭐ 临时打印 trace 看看
        traces = final_state.get("traces", [])
        if traces:
            print("\n📜 当前对话 Trace：")
            for ev in traces:
                print(f"- [{ev.kind}] {ev.node}: {ev.info}")
                
        print("\n" + "-" * 40 + "\n")



if __name__ == "__main__":
    main()
