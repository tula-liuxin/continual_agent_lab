# src/app/cli/echo.py

from app.common.messages import Message
from app.common.state import AgentState
from app.graph.simple_graph import build_simple_graph
from app.infra.llm.vllm_client import VllmLLMClient


def main() -> None:
    """
    基于 LangGraph + vLLM(Qwen) 的命令行对话入口。

    - 使用 VllmLLMClient 调用本地 vLLM OpenAI-compatible 服务
    """
    print("🔹 continual_agent_lab CLI - LangGraph + Qwen(vLLM) 模式")
    print("提示：请确保另一个终端里已经启动了 vLLM 服务器。")
    print("输入内容后按回车，输入 'exit' / 'quit' / 'q' 退出。\n")

    # 1. 创建一个 vLLM 客户端实例
    llm_client = VllmLLMClient()

    # 2. 把客户端注入到图里
    graph = build_simple_graph(llm_client)

    messages: list[Message] = []

    while True:
        user_text = input("你：").strip()

        if user_text.lower() in ("exit", "quit", "q"):
            print("👋 再见！")
            break

        messages.append(Message(role="user", content=user_text))

        state: AgentState = {"messages": messages}

        # 调用 LangGraph 图（内部会用 vLLM + Qwen 生成回复）
        final_state = graph.invoke(state)

        messages = final_state["messages"]
        last_msg = messages[-1]

        print(f"agent：{last_msg.content}")


if __name__ == "__main__":
    main()
