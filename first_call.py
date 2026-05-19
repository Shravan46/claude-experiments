import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("Anthropic_API_key"))

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="You are a PM who writes crisp one-line feature descriptions followed by a single success metric.",
    messages=[
        {"role": "user", "content": "Feature: email suggestions"},
        {"role": "assistant", "content": "Description: AI suggests replies based on email context and tone.\nMetric: 40% reduction in average email response time."},
        {"role": "user", "content": "Feature: meeting summarizer"},
        {"role": "assistant", "content": "Description: Automatically generates action items and key decisions from meeting transcripts.\nMetric: 80% of users rate summaries as accurate within first week."},
        {"role": "user", "content": "Feature: Claude memory across conversations"},
    ]
)

print(message.content[0].text)