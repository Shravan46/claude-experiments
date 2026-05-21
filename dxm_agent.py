import asyncio
import json
import os
import sys
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
MES_SERVER_PATH = Path(__file__).parent / "mes_mcp_server.py"

SYSTEM_PROMPT = (
    "You are an AI risk analyst in a manufacturing execution system. "
    "Analyze MES data and identify at-risk production orders. "
    "For each at-risk order return JSON with fields: order_id, product_name, "
    "risk_level (HIGH/MEDIUM/LOW), primary_driver (machine/inventory/workforce/combined), "
    "time_to_impact (hours), recommended_action, confidence (high/medium/low). "
    "HIGH = no recovery path. MEDIUM = recovery possible if acted now. LOW = buffer exists. "
    "Return JSON list only."
)

USER_TASK = (
    "Call all four MES tools to gather current production data, then identify every "
    "production order that is at risk. Return your analysis as a JSON list."
)


def _extract_json(text: str) -> str:
    """Extract JSON from a response that may contain prose or markdown code fences."""
    # Prefer a ```json...``` fence block anywhere in the response
    if "```" in text:
        parts = text.split("```")
        # Odd-indexed parts are fence contents
        for part in parts[1::2]:
            candidate = part.lstrip("json").lstrip("JSON").strip()
            if candidate.startswith("[") or candidate.startswith("{"):
                return candidate
    # Fall back to the first JSON array/object in the raw text
    for start_char, end_char in (("[", "]"), ("{", "}")):
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end > start:
            return text[start : end + 1]
    return text



async def _analyze(api_key: str) -> list:
    import anthropic as _anthropic
    from mcp import ClientSession as _ClientSession
    from mcp.client.stdio import StdioServerParameters as _Params, stdio_client as _stdio_client

    client = _anthropic.Anthropic(api_key=api_key)
    params = _Params(
        command=sys.executable,
        args=[str(MES_SERVER_PATH)],
    )

    async with _stdio_client(params) as (read, write):
        async with _ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from the MCP server
            tools_result = await session.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.inputSchema,
                }
                for t in tools_result.tools
            ]

            messages = [{"role": "user", "content": USER_TASK}]

            while True:
                # Synchronous Anthropic SDK call — no await
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages,
                )

                messages.append({"role": "assistant", "content": response.content})

                if response.stop_reason == "end_turn":
                    text_blocks = [b for b in response.content if b.type == "text"]
                    if not text_blocks:
                        raise ValueError("Claude returned end_turn with no text content")
                    raw = _extract_json(text_blocks[0].text.strip())
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError as e:
                        raise ValueError(
                            f"Failed to parse Claude response as JSON: {e}\nRaw: {raw}"
                        )

                if response.stop_reason != "tool_use":
                    raise ValueError(f"Unexpected stop_reason: {response.stop_reason}")

                # Execute each tool call via MCP — these are async
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    try:
                        call_result = await session.call_tool(block.name, block.input or {})
                        content_text = "\n".join(
                            c.text for c in call_result.content if hasattr(c, "text")
                        )
                        if not content_text and call_result.structuredContent:
                            content_text = json.dumps(call_result.structuredContent)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": content_text,
                        })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Error calling {block.name}: {e}",
                            "is_error": True,
                        })

                messages.append({"role": "user", "content": tool_results})


async def analyze_production_risk() -> list:
    """Connect to the MES MCP server, run the risk analysis agent, and return at-risk orders."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set")
    try:
        return await _analyze(api_key)
    except BaseExceptionGroup as eg:
        # anyio wraps exceptions from the stdio client's TaskGroup; unwrap to the real cause
        raise eg.exceptions[0] from None


async def run_demo():
    print("DXM Vision — Production Risk Analysis")
    print("=" * 60)
    print("Connecting to MES MCP server and running agent...\n")

    try:
        at_risk = await analyze_production_risk()
    except EnvironmentError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Agent error: {e}")
        sys.exit(1)

    if not at_risk:
        print("No at-risk production orders detected.")
        return

    print(f"Found {len(at_risk)} at-risk order(s):\n")
    for order in at_risk:
        risk = order.get("risk_level", "?")
        prefix = {"HIGH": "!!!", "MEDIUM": ">> ", "LOW": "   "}.get(risk, "   ")
        print(f"{prefix} [{risk}] {order.get('order_id')} — {order.get('product_name')}")
        print(f"     Driver     : {order.get('primary_driver')}")
        print(f"     Time impact: {order.get('time_to_impact')} hours")
        print(f"     Action     : {order.get('recommended_action')}")
        print(f"     Confidence : {order.get('confidence')}")
        print()

    print("Raw JSON:")
    print(json.dumps(at_risk, indent=2))


if __name__ == "__main__":
    asyncio.run(run_demo())
