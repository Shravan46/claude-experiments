# claude-experiments

AI engineering experiments and product artifacts built during a focused sprint using Claude, Claude Code, and the Anthropic API.

---

## Featured Project — DXM Production Risk Monitor

An AI agent that connects to a manufacturing execution system via MCP and identifies at-risk production orders in real time.

**Architecture**

```
Flask dashboard → Claude agent (claude-sonnet-4-6) → MCP stdio server → 4 MES tools
                                                          |
                                          machine telemetry · inventory levels
                                          workforce availability · active orders
```

The agent autonomously calls all four MES tools, cross-references the data, and returns a prioritized risk list — each order tagged with risk level (HIGH / MEDIUM / LOW), primary driver, estimated time to impact, and a recommended action.

**Swap point design**

`mes_mcp_server.py` exposes the four tools over MCP stdio. To connect to a real MES, replace the mock data functions in that file with API calls to your system. The tool signatures stay identical — zero changes required to the agent or the Flask app.

**Files**

| File | Description |
|---|---|
| `mes_mcp_server.py` | Mock MES MCP server — 4 tools, realistic interconnected industrial data |
| `dxm_agent.py` | Claude agent with agentic loop and MCP client integration |
| `app.py` | Flask web app — 3 routes serving the dashboard and JSON API |
| `templates/index.html` | Dashboard UI — pure CSS, auto-loads on open, refresh without reload |

**Running locally**

```bash
git clone https://github.com/Shravan46/claude-experiments.git
cd claude-experiments
pip install anthropic mcp flask
export ANTHROPIC_API_KEY=your_key_here
python app.py
# Open http://localhost:5001
```

---

## AI Evals

Evaluation infrastructure built to assess Claude's performance on the production risk flagging task before launch.

| File | Description |
|---|---|
| `dxm_eval_harness.py` | 15 test cases across 4 categories — happy path, edge cases, adversarial, regression. LLM-as-judge scoring with per-category pass rate reporting |
| `dxm_eval_results.csv` | Run 1 results — 73% pass rate overall, 2 critical adversarial failures identified |
| `dxm_eval_spec.html` | Full PM eval spec — eval objectives, scoring rubric, Run 1 findings, root cause analysis, and launch criteria |

---

## Prompt Engineering

Systematic experiments on prompting techniques applied to an industrial AI product vision.

| File | Description |
|---|---|
| `prompt_experiments.py` | Five techniques compared — zero-shot, role-based, chain-of-thought, skeptic framing, structured output |
| `prompt_findings.md` | PM findings document with technique-by-technique analysis |
| `temperature_test.py` | Temperature comparison — 0 vs 0.7 vs 1.0 on the same prompt |
| `temperature_test_output.md` | Documented output differences and implications for production use |

---

## Foundations

| File | Description |
|---|---|
| `first_call.py` | First Claude API call |
| `chatbot.py` | Conversational chatbot with message history and multi-turn memory |

---

## About

Written by Shravan Sudhakaran — AI Product Manager exploring the intersection of industrial AI, manufacturing systems, and LLM product development.

- LinkedIn: [linkedin.com/in/shravansudhakaran](https://www.linkedin.com/in/shravansudhakaran/)
- GitHub: [github.com/Shravan46](https://github.com/Shravan46)
