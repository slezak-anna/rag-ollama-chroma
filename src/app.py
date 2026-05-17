from src.rag_answer import answer_question

def main() -> None:
    print("Local RAG: Ollama + Chroma")
    
    print("Type 'exit' to proceed.")
    print()

    history: list[dict[str, str]] = []

    while True:
        question = input("Your question: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        answer = answer_question(
            question=question, 
            history=history or []
        )

        print()
        print("RAG: ")
        print(answer)
        print()

        history.append(
            {
                "role": "user",
                "content": question
        })

        history.append(
            {
                "role": "assistant",
                "content": answer
        })

if __name__ == "__main__":
    main()