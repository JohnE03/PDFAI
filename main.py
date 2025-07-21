from module1 import answer_question

print("[DEBUG] main.py loaded")
print("[DEBUG] __name__ is:", __name__)

if __name__ == "__main__":
    print("[DEBUG] main.py is running")
    print("🔍 Ask questions about your PDFs (type 'exit' to quit):")

    while True:
        question = input(">>> ")
        if question.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        answer = answer_question(question)
        print("\n✅ Answer:\n", answer)
