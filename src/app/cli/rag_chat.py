# src/app/cli/rag_chat.py

from app.common.messages import Message
from app.common.state import AgentState
from app.graph.rag_graph import build_rag_graph
from app.rag.service import RAGService


def main() -> None:
    print("🔹 continual_agent_lab CLI - LangGraph + RAG 模式")
    print("提示：请确保另一个终端里已经启动了 vLLM Qwen 服务器。")
    print("我会先用 RAG 检索内置“知识库”，然后用 Qwen 生成回答。")
    print("输入内容后按回车，输入 'exit' / 'quit' / 'q' 退出。\n")

    # 1. 构建一个简单的“知识库”
    texts = [
        "这个系统使用 BGE-M3 作为统一的文本 embedding 模型。",
        "本地大语言模型采用 Qwen2.5-3B-Instruct，通过 vLLM 暴露 OpenAI 兼容的 HTTP 接口。",
        "我们用 LangGraph 1.0 来编排多 Agent 流程，统一管理 AgentState 和工具调用。",
    ]
    rag_service = RAGService.from_texts(texts)

    # 2. 构建 RAG 图
    graph = build_rag_graph(rag_service)

    messages: list[Message] = []

    while True:
        user_text = input("你：").strip()

        if user_text.lower() in ("exit", "quit", "q"):
            print("👋 再见！")
            break

        # 把用户消息加入对话历史
        messages.append(Message(role="user", content=user_text))

        # 组装当前状态
        state: AgentState = {"messages": messages}

        # 调用 LangGraph 图（内部会执行 RAG 节点）
        final_state = graph.invoke(state)

        # 更新本地状态
        messages = final_state["messages"]
        rag_answer = final_state.get("rag_answer")

        # 打印回答（最后一条 assistant 消息）
        last_msg = messages[-1]
        print(f"\nagent：{last_msg.content}")

        # 可选：顺便展示一下用到的检索片段（方便你看效果）
        if rag_answer is not None and rag_answer.contexts:
            print("\n🔍 检索到的关键片段：")
            for i, ctx in enumerate(rag_answer.contexts, start=1):
                print(f"\n[Top {i}] (score={ctx.score:.4f})")
                print(ctx.text)

        print("\n" + "-" * 40 + "\n")


if __name__ == "__main__":
    main()
