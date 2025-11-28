# src/app/cli/rag_demo.py

from app.rag.service import RAGService


def main() -> None:
    print("🔹 RAG Demo - 使用 LlamaIndex + BGE-M3 + Qwen(vLLM)")
    print("提示：请先在另一个终端启动 vLLM Qwen 服务器。\n")

    # 1. 准备一小段“知识库”文本
    texts = [
        "这个系统使用 BGE-M3 作为统一的文本 embedding 模型。",
        "本地大语言模型采用 Qwen2.5-3B-Instruct，通过 vLLM 暴露 OpenAI 兼容的 HTTP 接口。",
        "我们用 LangGraph 1.0 来编排多 Agent 流程，统一管理 AgentState 和工具调用。",
    ]

    rag = RAGService.from_texts(texts)

    while True:
        question = input("\n你的问题（输入 q 退出）：").strip()
        if question.lower() in ("q", "quit", "exit"):
            print("👋 再见！")
            break

        result = rag.query(question, top_k=2)

        print("\n=== 回答 ===")
        print(result.answer)

        print("\n=== 使用到的检索片段 ===")
        for i, ctx in enumerate(result.contexts, start=1):
            print(f"\n[Top {i}] (score={ctx.score:.4f})")
            print(ctx.text)


if __name__ == "__main__":
    main()
