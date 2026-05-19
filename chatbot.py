import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

conversation_history = []

print("Claude Chatbot - type 'quit' to exit")
print("--------------------------------------")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    if user_input.lower() == "history":
        if not conversation_history:
            print("No conversation history yet.\n")
        else:
            print("\n--- Conversation History ---")
            for msg in conversation_history:
                label = "You" if msg["role"] == "user" else "Claude"
                print(f"{label}: {msg['content']}")
            print("----------------------------\n")
        continue
    
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a helpful assistant.You respond with crisp one line asnwers and mindful of token consumption",
        messages=conversation_history
    )
    
    reply = message.content[0].text
    
    conversation_history.append({
        "role": "assistant", 
        "content": reply
    })
    
    print(f"Claude: {reply}\n")