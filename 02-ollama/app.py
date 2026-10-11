
import ollama

print("Local AI Chatbot")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    if not user_input:
        continue

    response = ollama.chat(
        model="qwen2.5:0.5b",
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    print("\nAI:", response["message"]["content"], "\n")
