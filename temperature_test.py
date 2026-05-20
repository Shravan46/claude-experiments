import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

PROMPT = "Give me one creative product idea for reducing unplanned downtime in a factory."
MODEL = "claude-sonnet-4-6"
TEMPERATURES = [0.0, 0.7, 1.0]

for temperature in TEMPERATURES:
    print(f"\n{'='*60}")
    print(f"Temperature: {temperature}")
    print('='*60)

    for i in range(1, 4):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            temperature=temperature,
            messages=[{"role": "user", "content": PROMPT}],
        )
        text = next(block.text for block in response.content if block.type == "text")
        print(f"\nResponse {i}:\n{text}")
