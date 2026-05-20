# PRD Competitive Teardown
## AI-Powered Production Risk Assistant for Manufacturing Execution Systems

**Analyst:** Shravan Sudhakaran
**Date:** 2026-05-20
**Tools Evaluated:** Claude (Sonnet 4.6), ChatGPT (GPT-4o), Gemini (1.5 Pro), GitHub Copilot (PRD Builder)
**Prompt Given to Each:** Write a PRD for an AI assistant embedded in a manufacturing execution system that proactively flags at-risk production orders based on real-time machine data, inventory levels, and workforce availability. Include: problem statement, target users, key features, success metrics, and risks.

---

## Scoring Summary

| Criterion | Claude | ChatGPT | Gemini | Copilot |
|---|---|---|---|---|
| Structure & Completeness | 7/10 | 8/10 | 5/10 | 10/10 |
| Depth of Problem Definition | 10/10 | 6/10 | 7/10 | 4/10 |
| Quality of Success Metrics | 9/10 | 2/10 | 7/10 | 6/10 |
| Hallucination Risk (lower = better) | Medium | Low | Medium | Low |
| Practical Usefulness for a PM | 8/10 | 6/10 | 6/10 | 8/10 |
| **Total (of 40)** | **34** | **22** | **25** | **28** |

---

## 1. Structure and Completeness

### Claude — 7/10
Covers: Problem Statement, Target Users, Key Features, Out of Scope, Success Metrics, Risks, Open Questions.

Strong section hierarchy and an explicit out-of-scope list with planned v2 items. Missing the artifacts an engineer needs to act on the document: no functional requirements table, no non-functional requirements, no rollout plan, no dependency tracking, no changelog. The document reads as a very good executive briefing but requires a second document before engineering can begin work.

### ChatGPT — 8/10
Covers: Overview, Problem Statement, Goals & Objectives, Target Users, User Stories, Key Features, Functional Requirements (numbered table FR-1 to FR-10), Non-Functional Requirements, Success Metrics, Risks & Challenges.

The most section-rich of the four. Adds user stories and a functional requirements table that the others omit, which makes it closer to a complete engineering handoff document. Docks two points for having no rollout plan and no data instrumentation plan despite its otherwise comprehensive structure.

### Gemini — 5/10
Covers: Problem Statement, Target Users, Key Features, Success Metrics, Risks.

Structurally thin. No functional requirements, no NFRs, no user stories, no rollout plan, no out-of-scope section, no open questions, no dependency tracking. Hits every section the prompt requested and nothing more. A good first draft but requires significant scaffolding before it functions as a working PRD.

### GitHub Copilot — 10/10
Covers: Progress Tracker, Executive Summary, Problem Definition, Users & Personas, Scope (in/out/assumptions/constraints), Product Overview, Functional Requirements (table with IDs, acceptance criteria, traceability to goals), Non-Functional Requirements, Data & Analytics, Dependencies, Risks, Privacy/Security/Compliance, Operational Considerations, Rollout Plan, Open Questions, Changelog, References, Appendices/Glossary.

The only tool that produced a truly complete PRD template. Every section has an ID scheme (FR-001, NFR-001, R-001), an owner field, and a status column. The progress tracker at the top and the changelog at the bottom reflect real-world PM workflow. This is the closest to an artifact you could hand an engineering team on day one.

---

## 2. Depth of Problem Definition

### Claude — 10/10
The problem framing is the standout section. Claude identifies a precise and insightful diagnosis: "the gap is not data availability... the gap is *synthesis*." It explains *why* current MES platforms fail (reactivity), *how* operators currently compensate (floor walks, phone calls), and *what that costs* in cognitive terms. The problem statement is a story, not a list. This level of clarity would make a strong case to executive stakeholders and would help engineers understand what they are actually solving.

### ChatGPT — 6/10
Lists six root causes and five business consequences in bullet form. Accurate and complete, but reads like a literature review rather than a diagnosed problem. The framing is generic enough to apply to dozens of industrial software categories. A PM could not use this problem statement alone to argue for prioritization — it lacks the "why now" and "why us" angles.

### Gemini — 7/10
The "data silos" framing is effective and specific to manufacturing. Mentions unplanned downtime, missed shipment deadlines, and expediting costs as concrete consequences. Shorter than Claude's but more focused than ChatGPT's. Would benefit from one more layer of depth — what specifically fails in the workflow, not just the data architecture.

### GitHub Copilot — 4/10
Three bullet points for root causes, three for impact. This is template fill-in, not problem diagnosis. A PM reading this section would not come away with a clearer understanding of the problem than they started with. The section exists to check a box rather than to build conviction.

---

## 3. Quality of Success Metrics

### Claude — 9/10
Three-tier structure: Primary metrics (ship criteria with baselines and 90-day targets), Secondary metrics (ongoing health), and Guardrails (trigger thresholds that force a model review). Specific examples:

- Mean time to detect: 4.2 hours → <45 minutes
- Critical orders caught before slip: 31% → >75%
- Alert precision: >60%, Recall: >80%
- Override rate >60% triggers model review
- p95 conversational latency <3 seconds

The guardrails concept is especially sophisticated — it defines the conditions under which the product has failed even if top-line metrics look acceptable. The holdout group proposal for ROI attribution is the most rigorous experimental design in any of the four documents.

Loses one point because baselines like "4.2 hours (survey avg)" are asserted without citing the survey.

### ChatGPT — 2/10
Lists three categories of metrics (Operational KPIs, User Adoption, AI Performance) with no targets, no baselines, and no timelines. This is a metric *taxonomy*, not a measurement plan. A PM could not write a launch review with this section. It reads as a placeholder waiting to be filled in by someone who actually knows the numbers.

### Gemini — 7/10
Structured table with Category, Metric, and Target. Some specific and credible targets:

- Predictive Precision: >88%
- False Alert Rate: <5%
- Recommendation Acceptance: >60%
- Downtime Reduction: -15% within 6 months
- OTD Rate Improvement: +2.5%

Good structure. Docks three points for providing no baselines (making it impossible to measure progress), and the OTD improvement of "+2.5%" is oddly precise for a metric with no baseline.

### GitHub Copilot — 6/10
Best-structured metrics table: Metric, Type, Baseline, Target, Window, Source columns. Includes an instrumentation plan with specific event names, triggers, and payloads (OrderRiskFlagged, RiskFlagReviewed, RiskFlagResolved) — the only tool to include this. However, most baselines are "N/A" or "TBD", which undermines the table's value. Targets like "20% lower" and "80% reviewed" are directionally correct but need anchoring.

---

## 4. Hallucination Risk

*Assessed by identifying specific numbers that appear authoritative but have no cited source and would be difficult to verify.*

### Claude — Medium Risk
Three unverified specific numbers presented as facts:
- "Unplanned downtime averages 800 hours per plant per year (industry benchmark)" — no source
- "4.2 hours (survey avg)" for mean time to detect at-risk orders — no survey cited
- "31% (historical)" of critical orders caught before slip — no data source

These are plausible figures that align with published manufacturing research, but citing them as baselines in a working PRD without sources is problematic. A downstream stakeholder who questions these numbers will undermine the document's credibility.

### ChatGPT — Low Risk
Strategically avoids specific numbers in the problem statement and goals. When numbers appear in NFRs (e.g., "99.9% uptime", "30 seconds latency"), they are framed as requirements rather than observed facts. This is the safest approach — arguably too cautious, since the absence of any diagnostic data weakens the business case.

### Gemini — Medium Risk
The "+2.5% OTD rate" target and ">88% predictive precision" target are specific enough to raise eyebrows without basis. The example in the risk section ("CNC Machine 3 cycle time degraded by 14% over the last 2 hours + Sheet Metal inventory running 12 units short") is an illustrative example clearly labeled as such — this is fine. The "-15% downtime reduction within 6 months" target is ambitious and would need justification.

### GitHub Copilot — Low Risk
Defaults to "TBD" and "N/A" for most baseline figures. Requirements are framed as requirements. The tool appears to have been designed to avoid fabricated precision — a sensible choice, though it leaves the PM to fill in all the analytical work.

---

## 5. Practical Usefulness for a Real PM

### Claude — 8/10
Highest value at the two hardest moments in PM work: making the case to stakeholders (problem definition) and running a post-launch review (guardrail metrics). The open questions section is the only one that would immediately drive productive alignment meetings. The risk register includes specific mitigations rather than platitudes ("instrument a holdout group," "start with high-threshold alerting for first 30 days"). The missing functional requirements and rollout plan mean a PM would need to write a second document before engineering engagement.

### ChatGPT — 6/10
Most useful for engineering alignment — functional requirements and NFRs give developers something concrete to implement and validate against. Least useful for executive alignment or post-launch accountability, given the empty metrics section. A PM would use this as a structural template and fill in the problem framing and metrics from scratch.

### Gemini — 6/10
The "Option A / Option B / Option C" recommendation examples with specific estimated impacts ("+15 mins setup time", "Arrives in 45 mins") are excellent PM communication tools — more concrete than any other document's feature descriptions. The "Guardrail Matrix" architecture idea is the most safety-conscious feature design of the four. The document's brevity makes it a good starting point for discovery conversations, less useful as a finished artifact.

### GitHub Copilot — 8/10
The most immediately usable working document. ID schemes on every requirement, changelog with version tracking, feature flags with sunset criteria, rollout milestones with gate criteria, open questions with owners and deadlines. A PM inheriting this document knows exactly what is done, what is in progress, and what needs an owner. The instrumentation event plan would accelerate data engineering work significantly. Docks two points because the thin problem framing would require significant revision before this document could persuade anyone who wasn't already sold on the feature.

---

## 6. What Each Tool Does Uniquely Well

### Claude
Narrative problem framing that builds conviction. The "synthesis gap" diagnosis is the most precise articulation of the core problem across all four documents. The guardrail metrics (e.g., "override rate >60% signals model is not trusted — triggers model review") are the most sophisticated accountability mechanism. The holdout group design for isolating ROI is the only experimental design proposed by any tool. The "automation anxiety" risk (operators fearing performance evaluation) is the only document to surface the human change management dimension.

### ChatGPT
Secondary user coverage. ChatGPT is the only tool to explicitly include Maintenance Teams and Inventory/Warehouse Teams as secondary users, with specific needs for each. The explicit explainability and audit trail requirement ("each prediction should include contributing factors, confidence level, supporting operational data, historical comparison") is the strongest statement of AI governance requirements in any document.

### Gemini
Concrete recommendation examples. Option A/B/C mitigation strategies with specific estimated impacts are the most PM-communicable feature descriptions. The "Confidence of On-Time Delivery" score framing (positive metric, not a risk score) is more intuitive for floor operators than a risk-score-based framing. The "Guardrail Matrix" concept — constraining AI recommendations using a hard-coded rule engine validated against the plant's engineering routing rules — is the most architecturally sound safety design.

### GitHub Copilot
Operational completeness. The instrumentation plan with specific event schemas (OrderRiskFlagged, RiskFlagReviewed, RiskFlagResolved) is the only document that would allow a data engineering team to begin instrumentation work without a follow-up meeting. The progress tracker, changelog, and feature flag section reflect real-world PM workflow. The privacy/security/compliance section and the threat considerations sub-section are absent from all other documents.

---

## 7. What Each Tool Is Missing

### Claude
- No functional requirements or non-functional requirements (engineers cannot begin scoping)
- No rollout plan or milestone gates
- No user stories
- No dependency tracking (data feeds, platform integrations)
- Baselines for primary metrics are asserted without sources
- No instrumentation or analytics event plan

### ChatGPT
- Success metrics section has zero specific targets — entirely unusable for a launch review
- No rollout plan
- No data instrumentation plan
- No open questions section
- No dependency tracking
- Goals section (20% order delay reduction, 10% OEE improvement) is not connected to the metrics section, creating internal inconsistency

### Gemini
- Missing: functional requirements, NFRs, user stories, rollout plan, open questions, dependency tracking
- No out-of-scope definition (a PM needs to say what is NOT being built)
- No baselines for any success metric
- The "users can accept a recommendation directly within the chat/alert interface, which automatically updates the MES scheduling dispatch" feature is introduced in passing but has major workflow, auditability, and liability implications that go unaddressed
- No changelog or versioning

### GitHub Copilot
- Problem definition is template-depth only — provides no insight into why this problem is hard or why it is worth solving now
- UX/UI section is one sentence ("Deliver a prioritized risk dashboard within the MES and inline order warnings")
- No conversational AI feature (no natural language query interface is described)
- No what-if simulation feature
- Metrics baselines are almost entirely "N/A" or "TBD", leaving the PM to do all the baseline research
- No competitive or market context

---

## Overall Recommendation

### Winner: Claude

**Claude produced the best PRD for a PM who needs to align stakeholders and drive accountable outcomes.**

The two hardest parts of PRD writing are problem framing and metrics design. These are the sections that require genuine thinking about the product, the users, and the business — they cannot be scaffolded by a template. Claude is the only tool that excels at both.

The "synthesis gap" diagnosis in the problem statement is the kind of precise, defensible framing that survives executive scrutiny and helps engineers understand the actual job to be done. The three-tier metrics structure (primary/secondary/guardrails) with explicit trigger conditions for model review is the most rigorous accountability mechanism in any document — and the holdout group design is the kind of thinking a senior PM would be proud of.

GitHub Copilot is the runner-up and the better choice if your primary need is a working document for engineering handoff rather than stakeholder alignment. Its structural completeness, ID schemes, instrumentation plan, and operational considerations make it far more immediately usable as a shared artifact. The right workflow for a real PM would be: use Claude to write the problem statement and metrics, then use GitHub Copilot's structure as the skeleton for the final document.

ChatGPT's structural completeness is undermined by its empty metrics section — a PRD without measurable success criteria is a feature description, not a requirements document. Gemini's conciseness and strong recommendation examples make it a useful sketch tool but it is not a finished PRD.

### One Feature Gap Anthropic Could Fill

**Multi-artifact PRD generation with explicit separation between the analytical and operational layers.**

The teardown reveals a clear division of labor: Claude produces the hardest-to-automate content (diagnosis, metrics design, risk reasoning), while GitHub Copilot produces the hardest-to-skip structural scaffolding (requirement IDs, rollout gates, instrumentation events, changelog). No tool produces both.

Anthropic could close this gap by giving Claude a native **PRD mode** — invoked by a slash command or a system prompt trigger — that generates two outputs simultaneously:

1. The **narrative layer**: problem statement, strategic framing, metrics with guardrails, and risk reasoning in Claude's existing style
2. The **operational layer**: a structured requirements table with IDs and acceptance criteria, an NFR table, an instrumentation event schema, a rollout plan with milestone gates, and an open questions tracker with owner placeholders

This would not be a generic document template. It would be Claude's analytical output mapped into the structured artifacts that engineering, data, and operations teams need to act on the document. The result would make Claude the only AI tool that produces a PRD you can take from discovery to launch without switching tools — a significant competitive advantage in the PM tooling market where the current workflow requires at least two tools to produce one complete document.

---

*Teardown methodology: Each PRD was read in full and scored against consistent criteria. Where a section was absent, the tool received a 0 for that component of the criterion. Hallucination risk was assessed by identifying specific numbers that appear as established facts without cited sources. Practical usefulness was assessed from the perspective of a PM at a mid-size discrete manufacturer preparing to pitch a new MES feature to engineering and executive stakeholders.*
