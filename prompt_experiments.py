import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

VISION_DOC = """
Vision: Enable industrial manufacturers to automate workflows and processes across mission critical systems to improve process efficiency, increase productivity and reduce cost using the power of AI.

Target Market: Industrial Manufacturers across discrete and process manufacturing.

Customer Pain Points: Need to innovate faster and be competitive. Need deep expertise to leverage systems across enterprise to identify bottlenecks and perform continuous improvement. Need to improve product quality, reduce cost and respond quickly to demand fluctuations and supply chain disruptions. Silos across teams and systems. Lack of AI skill sets.

Offerings: AI Agents for Enhanced Manufacturing Process Efficiency, Intelligent Asset Maintenance, Advanced Production Quality and Control, Production Execution Excellence.

Value Proposition: Enable customers to quickly identify issues, review remediation plans and automate actions across the enterprise with end to end visibility. Seamless integrations with existing mission critical systems. Pre-trained models. Augments existing workforce. Secure, Flexible and Scalable.

Key Differentiators: Invisible plug and play services, Automation with OOTB recommendation systems, Human in the loop for critical decisions, Scale across factories, Best in Class UX, Pure Play Intelligence layer.
"""

PROMPTS = [
    {
        "number": 1,
        "label": "Zero-Shot",
        "instruction": "Summarize the key product decisions that need to be made.",
        "system": None,
        "user": f"Here is a product vision document:\n\n{VISION_DOC}\n\nSummarize the key product decisions that need to be made.",
    },
    {
        "number": 2,
        "label": "Role-Based",
        "instruction": "As a senior B2B product manager, identify the 3 most critical go-to-market risks.",
        "system": "You are a senior B2B product manager with 15 years of experience launching enterprise software products.",
        "user": f"Here is a product vision document:\n\n{VISION_DOC}\n\nIdentify the 3 most critical go-to-market risks for this product.",
    },
    {
        "number": 3,
        "label": "Chain-of-Thought",
        "instruction": "Think step by step, then identify the single most important feature to build first and why.",
        "system": None,
        "user": f"Here is a product vision document:\n\n{VISION_DOC}\n\nThink step by step through the customer pain points, offerings, and value proposition. Then identify the single most important feature to build first and explain why.",
    },
    {
        "number": 4,
        "label": "Skeptic",
        "instruction": "As a manufacturing industry veteran, what are the 3 biggest reasons this product could fail?",
        "system": "You are a manufacturing industry veteran with 25 years of experience on the plant floor and in operations leadership. You are deeply skeptical of technology vendors overpromising and underdelivering.",
        "user": f"Here is a product vision document:\n\n{VISION_DOC}\n\nWhat are the 3 biggest reasons this product could fail? Be direct and candid.",
    },
    {
        "number": 5,
        "label": "Structured Output",
        "instruction": "Respond in a table with columns: Feature, Target User, Success Metric, Risk.",
        "system": None,
        "user": f"Here is a product vision document:\n\n{VISION_DOC}\n\nBased on the offerings described, create a table with these exact columns: Feature | Target User | Success Metric | Risk. Include one row per major offering. Format it as a markdown table.",
    },
]

DIVIDER = "=" * 70


def run_prompt(prompt_config: dict) -> str:
    messages = [{"role": "user", "content": prompt_config["user"]}]
    kwargs = {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": messages,
    }
    if prompt_config["system"]:
        kwargs["system"] = prompt_config["system"]

    response = client.messages.create(**kwargs)
    return response.content[0].text


def main():
    print(DIVIDER)
    print("PROMPT EXPERIMENTS — Manufacturing AI Product Vision")
    print(f"Model: {MODEL}")
    print(DIVIDER)

    for prompt_config in PROMPTS:
        print(f"\nPROMPT {prompt_config['number']}: {prompt_config['label']}")
        print(f"Instruction: {prompt_config['instruction']}")
        if prompt_config["system"]:
            print(f"System Role: {prompt_config['system'][:80]}...")
        print("-" * 70)

        response_text = run_prompt(prompt_config)
        print(response_text)
        print(f"\n{DIVIDER}")


if __name__ == "__main__":
    main()
