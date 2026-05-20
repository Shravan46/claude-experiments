# DXM Vision: Prompt Experiment Findings
**Date:** May 19, 2026 | **Author:** Shravan Sudhakaran | **For:** DXM Product Team

---

## Overview

We ran five structured prompt experiments against the DXM manufacturing AI product vision to evaluate how different prompting techniques affect the quality of AI-generated product insight. All five prompts used the same vision document as input, covering DXM's four core offerings: Process Efficiency, Intelligent Asset Maintenance, Production Quality and Control, and Production Execution Excellence.

The goal was not to validate the vision — it was to stress-test it. We used Claude to simulate five different analytical lenses: a generalist, a senior B2B PM, a structured reasoner, an industry skeptic, and a structured output generator. Each lens revealed something different. This document captures what we learned and what it means for DXM.

---

## Key Findings per Prompt Technique

**1. Zero-Shot — Decision Audit**
Without any framing, Claude identified eight product decisions that need to be made: agent architecture and autonomy scope, integration strategy, pre-trained model coverage, human-in-the-loop design, GTM sequencing, build/buy/partner tradeoffs, security and compliance, and success metrics definition. The output was exhaustive but unprioritized. Most useful as a completeness check — it confirms we haven't named a decision we haven't already identified, but it doesn't tell us which ones are load-bearing.

**2. Role-Based PM — GTM Risk Analysis**
Framing Claude as a senior B2B enterprise PM produced the sharpest strategic output. Three critical GTM risks surfaced: (1) proving ROI within 12–18 month enterprise sales cycles before customers commit at scale, (2) the gap between the "plug and play" integration promise and the reality of OT/IT complexity in brownfield manufacturing environments, and (3) change management — shop floor operators won't trust AI recommendations without a track record, and fear of displacement creates active resistance even when executives sponsor the rollout. These three risks are compounding: failed integration prevents ROI proof, and without credible ROI, adoption stalls. This sequencing has direct implications for how we scope the first pilots.

**3. Chain-of-Thought — Build Order**
When asked to reason step by step before reaching a conclusion, Claude traced a clear critical path: Connect Systems → Unify Data → Surface Insights → Recommend Actions → Automate. Every offering — maintenance, quality, execution, efficiency — is gated on the first step. The recommendation: the single most important feature to build first is a **Universal Integration and Data Connectivity Layer**. The reasoning holds regardless of which offering we lead with. Without reliable, fast system connectivity, pre-trained models can't run on real customer data and the "plug and play" differentiator is marketing copy, not product reality.

**4. Skeptic — Failure Modes**
Prompting from the perspective of a 25-year manufacturing veteran produced the most uncomfortable and most useful output. Three failure modes called out directly: "seamless integration" is a claim that doesn't survive contact with real OT environments — aging PLCs, proprietary protocols, IT/OT security walls, and 12-month integration timelines are the norm, not the exception. Pre-trained models will accumulate false positives quickly in plant environments, and once operators stop trusting the system, recovery is nearly impossible. Most importantly: the four-offering scope means DXM currently does nothing better than Siemens, Rockwell, or Sight Machine at any specific problem. Without a sharp wedge use case, the sales motion gets stuck in pilot purgatory. The closing note: *"The vision reads like it was written for an investor deck, not a plant manager."*

**5. Structured Output — Feature Brief**
A simple table prompt produced a clean mapping of all four offerings to target user, success metric, and risk. The output is immediately usable as a stakeholder alignment artifact and roadmap communication tool. Most valuable for ensuring each offering has a named owner, a measurable outcome, and an identified risk before any sprint planning begins.

---

## Most Valuable Insight

The skeptic and chain-of-thought outputs converged on the same conclusion from two different directions: **DXM's biggest risk is leading with breadth before proving depth.**

The vision document describes four offerings across two manufacturing segments. That is effectively eight distinct market bets before a single customer has gone live. The integration layer is both the critical path dependency and the most credible differentiator — but only if it actually works in production environments. The "plug and play" claim is the most powerful thing in the vision document and the most dangerous if it fails. Everything else — the agents, the pre-trained models, the human-in-the-loop design — depends on whether customers believe that claim after their first integration experience.

The insight is not to narrow the vision. It is to sequence execution so that the first thing customers experience is the one thing that proves the whole platform is real.

---

## Recommended Next Steps for DXM

1. **Scope the integration layer as the v1 foundation, not a feature.** Define which five to seven systems get native connectors first — prioritized by frequency in target customer environments, not by perceived prestige. MES, ERP (SAP/Oracle), and data historians (OSIsoft PI, Ignition) are the likely starting set. Set an internal definition of "plug and play" with a measurable time-to-connect SLA.

2. **Pick one offering as the wedge for the first three pilots.** Predictive maintenance has the lowest adoption resistance, the most mature data signals, and the clearest ROI story. Leading with it reduces the variables in the first customer relationship and creates a proof point that is transferable to the other three offerings.

3. **Rewrite the pilot success criteria before the next customer conversation.** The current vision defines value in strategic terms. Customers need a 90-day proof point they can take to their operations VP — specific downtime reduction, a maintenance cost figure, a measurable quality delta. Define this before the pilot starts, not after.

4. **Address the skeptic's objection list in the product narrative.** The three failure modes surfaced in Prompt 4 — integration complexity, model trust, and positioning against incumbents — will come up in every serious customer conversation. The product team should have a prepared, honest response to each one before the next external demo.

---

## Recommended Prompt Strategy Going Forward

These five techniques are not one-time tools. They map cleanly to recurring product work:

| When to use | Technique | Output |
|---|---|---|
| Starting a new initiative or decision | Zero-Shot | Exhaustive decision checklist |
| Strategy reviews, investor prep, pricing | Role-Based (B2B PM, CFO, Buyer) | Prioritized risks and tradeoffs |
| Build order, architecture, sequencing questions | Chain-of-Thought | Reasoned recommendation with logic exposed |
| Preparing for customer objections or competitive reviews | Skeptic (OT veteran, plant manager, competitor) | Unfiltered failure modes |
| Roadmap communication, sprint planning inputs | Structured Output | Stakeholder-ready tables and briefs |

The highest-leverage use is running Role-Based and Skeptic prompts together before any major product decision — one to surface strategic risks, the other to surface operational ones. Used together, they cover the two failure modes that kill enterprise products: the ones that show up in the boardroom and the ones that show up on the plant floor.
