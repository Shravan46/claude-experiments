#!/usr/bin/env python3
"""
DXM Vision Manufacturing AI — Production Risk Identification Eval Harness

Model under test : claude-sonnet-4-6
Scoring          : LLM-as-judge (second Claude call grades each response)
Test categories  : happy_path (5), edge_case (4), adversarial (3), regression (3)
"""

import anthropic
import csv
import json
import os
import re
import sys
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# System prompts
# ──────────────────────────────────────────────────────────────────────────────

MES_SYSTEM_PROMPT = """You are an AI assistant embedded in a Manufacturing Execution System (MES) \
for DXM Vision, a discrete manufacturer producing precision industrial components.

Your role is to analyze real-time operational data snapshots and identify production orders \
that are at risk of missing their due dates or completion milestones.

For each analysis you must:
1. List every production order that is at risk, or explicitly confirm that no orders are currently at risk.
2. For each at-risk order, identify the PRIMARY risk driver: machine, inventory, or workforce.
3. If a SECONDARY risk driver also contributes, name it.
4. Assign a severity: high (order will miss due date without immediate intervention), \
medium (order is in jeopardy but has some recovery options), or low (order is technically \
at risk but has significant buffer).
5. Provide a one-sentence rationale for each flagged order.

Respond only based on data present in the snapshot. Do not infer risk from conditions not \
described. Do not flag orders for risk drivers that do not apply to their remaining operations."""

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator assessing the quality of an AI system's \
manufacturing risk identification responses.

You will be given a test case with MES input data, expected output, a scoring rubric, \
and the AI's actual response.

Score the response and return your evaluation as valid JSON in this EXACT format:
{
  "score": <0.0, 0.5, or 1.0>,
  "rationale": "<one to three sentences explaining the score>"
}

Scoring rules:
- Be strict on adversarial cases: hallucinating risk for an order that is NOT at risk = 0.0.
- Be strict on regression cases: missing a secondary risk driver caps the score at 0.5.
- No partial credit for adversarial cases where the model invents risk.
- Return ONLY valid JSON — no markdown fences, no preamble."""


# ──────────────────────────────────────────────────────────────────────────────
# Test cases
# ──────────────────────────────────────────────────────────────────────────────

TEST_CASES = [

    # ── HAPPY PATH ─────────────────────────────────────────────────────────────

    {
        "id": "HP-001",
        "category": "happy_path",
        "description": "Machine down, single order — obvious high-severity risk",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 14:32 ===

ACTIVE PRODUCTION ORDERS
Order: PO-4821 | Product: Gear Housing Assembly | Due: 2026-05-20 20:00 | Status: In Progress
  Current Operation: CNC Machining (Op 30) | Assigned Machine: CNC-07 | Remaining: 3.2 hrs

MACHINE STATUS
CNC-07 | Status: DOWN | Fault Code: E-044 (Spindle motor overload) | OEE: 0% | Down since: 13:45
        Est. repair: 3–4 hrs

INVENTORY STATUS
PO-4821 BOM components: all on-hand and allocated

WORKFORCE
Shift 2 (14:00–22:00): 9/9 CNC operators scheduled and present""",
        "expected": {
            "at_risk_orders": ["PO-4821"],
            "drivers": {"PO-4821": {"primary": "machine"}},
            "severity": {"PO-4821": "high"},
            "notes": "3–4 hr repair, 3.2 hrs remaining work, due in 5.5 hrs — no buffer.",
        },
        "rubric": (
            "Full credit (1.0): Flags PO-4821, machine as primary driver, high severity.\n"
            "Partial credit (0.5): Flags PO-4821 with correct driver but wrong severity (medium).\n"
            "No credit (0.0): Does not flag PO-4821, or hallucinates risk for other orders."
        ),
    },

    {
        "id": "HP-002",
        "category": "happy_path",
        "description": "Inventory stockout — component exhausted before order completes",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 09:15 ===

ACTIVE PRODUCTION ORDERS
Order: PO-7712 | Product: Hydraulic Valve Body | Due: 2026-05-20 16:00 | Status: In Progress
  Current Operation: Sub-assembly (Op 20) | Required Component: Seal Kit A-104
  Qty Required: 500 | Consumption Rate: 120 units/hr

MACHINE STATUS
Assembly Line 2: Status: RUNNING | OEE: 91%

INVENTORY STATUS
Seal Kit A-104: On-hand: 47 units | Allocated to PO-7712: 47 units | Pending receipt: None

WORKFORCE
Shift 1 (06:00–14:00): 12/12 assemblers scheduled and present""",
        "expected": {
            "at_risk_orders": ["PO-7712"],
            "drivers": {"PO-7712": {"primary": "inventory"}},
            "severity": {"PO-7712": "high"},
            "notes": "47 units at 120/hr = ~23 min runtime. Order needs 500 units, due in ~7 hrs.",
        },
        "rubric": (
            "Full credit (1.0): Flags PO-7712, inventory as primary driver, high severity.\n"
            "Partial credit (0.5): Flags PO-7712 with correct driver but assigns medium severity.\n"
            "No credit (0.0): Does not flag PO-7712, or misidentifies the primary driver."
        ),
    },

    {
        "id": "HP-003",
        "category": "happy_path",
        "description": "Workforce gap — certified welders called out for next shift",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 13:50 ===

ACTIVE PRODUCTION ORDERS
Order: PO-3344 | Product: Structural Weldment W-220 | Due: 2026-05-20 23:00 | Status: Queued
  Next Operation: MIG Welding (Op 10) | Cert Required: AWS D1.1 | Operators Required: 3

MACHINE STATUS
Welding Bays 1–4: All operational | OEE: 88%

INVENTORY STATUS
PO-3344 BOM components: all on-hand

WORKFORCE
Shift 2 (14:00–22:00):
  AWS D1.1 certified welders scheduled: 3
  AWS D1.1 certified welders confirmed present: 1 (2 called out sick at 13:30)""",
        "expected": {
            "at_risk_orders": ["PO-3344"],
            "drivers": {"PO-3344": {"primary": "workforce"}},
            "severity": {"PO-3344": "high"},
            "notes": "Order requires 3 certified welders; only 1 confirmed for Shift 2.",
        },
        "rubric": (
            "Full credit (1.0): Flags PO-3344, workforce as primary driver, high severity.\n"
            "Partial credit (0.5): Flags PO-3344, correct driver, assigns medium severity.\n"
            "No credit (0.0): Does not flag PO-3344, or misidentifies primary driver."
        ),
    },

    {
        "id": "HP-004",
        "category": "happy_path",
        "description": "Three orders in snapshot — two at risk, one on track",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 11:00 ===

ACTIVE PRODUCTION ORDERS
Order: PO-1001 | Product: Bearing Housing | Due: 2026-05-20 18:00 | Status: In Progress
  Current Operation: Turning (Op 10) | Assigned Machine: LATHE-02 | Remaining: 2.5 hrs
  Required Component: Bearing Race BR-88 | Qty Required: 80 | On-hand: 8 | Pending receipt: None

Order: PO-2002 | Product: Pump Impeller | Due: 2026-05-20 19:00 | Status: In Progress
  Current Operation: Milling (Op 20) | Assigned Machine: MILL-05 | Remaining: 4.0 hrs
  MILL-05 Status: DOWN | Fault: Servo drive fault | Est. repair: 5–6 hrs

Order: PO-3003 | Product: Shaft Assembly | Due: 2026-05-21 08:00 | Status: In Progress
  Current Operation: Grinding (Op 30) | Assigned Machine: GRD-01 | Remaining: 1.5 hrs
  GRD-01 Status: RUNNING | OEE: 94%
  All BOM components on-hand | Workforce: nominal""",
        "expected": {
            "at_risk_orders": ["PO-1001", "PO-2002"],
            "not_at_risk": ["PO-3003"],
            "drivers": {
                "PO-1001": {"primary": "inventory"},
                "PO-2002": {"primary": "machine"},
            },
            "severity": {"PO-1001": "high", "PO-2002": "high"},
            "notes": (
                "PO-1001: 10% of required component on hand. "
                "PO-2002: repair estimate exceeds due date. "
                "PO-3003 is on track."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-1001 (inventory, high) AND PO-2002 (machine, high); "
            "correctly identifies PO-3003 as not at risk.\n"
            "Partial credit (0.5): Flags both at-risk orders but misidentifies one driver or "
            "severity, OR correctly flags both but also incorrectly flags PO-3003.\n"
            "No credit (0.0): Misses either PO-1001 or PO-2002, or flags all three."
        ),
    },

    {
        "id": "HP-005",
        "category": "happy_path",
        "description": "OEE degradation trend — throughput math shows order cannot complete on time",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 15:20 ===

ACTIVE PRODUCTION ORDERS
Order: PO-5566 | Product: Cam Follower Assembly | Due: 2026-05-20 19:00 | Status: In Progress
  Current Operation: Precision Boring (Op 40) | Assigned Machine: BOR-03
  Remaining at standard rate: 2.0 hrs

MACHINE STATUS
BOR-03 | Status: RUNNING | OEE: 57% (standard: 88%) | OEE trend: declining over past 90 min
        At current OEE, effective remaining time: ~3.5 hrs

INVENTORY STATUS
PO-5566 BOM components: all on-hand

WORKFORCE
Shift 2 (14:00–22:00): Fully staffed""",
        "expected": {
            "at_risk_orders": ["PO-5566"],
            "drivers": {"PO-5566": {"primary": "machine"}},
            "severity": {"PO-5566": "high"},
            "notes": (
                "At 57% OEE, 2 hrs of work ≈ 3.5 actual hours. "
                "Due in 3.67 hrs — negligible buffer with declining OEE."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-5566, machine (OEE degradation) as primary driver, "
            "high severity.\n"
            "Partial credit (0.5): Flags PO-5566 with machine driver but assigns medium severity, "
            "failing to account for declining OEE trend.\n"
            "No credit (0.0): Does not flag PO-5566, or claims order is on track."
        ),
    },

    # ── EDGE CASES ─────────────────────────────────────────────────────────────

    {
        "id": "EC-001",
        "category": "edge_case",
        "description": "Two degraded signals, neither catastrophic — model must identify both drivers",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 10:45 ===

ACTIVE PRODUCTION ORDERS
Order: PO-9901 | Product: Actuator Housing | Due: 2026-05-20 17:00 | Status: In Progress
  Current Operation: CNC Milling (Op 30) | Assigned Machine: MILL-09
  Remaining at standard: 2.8 hrs

MACHINE STATUS
MILL-09 | Status: RUNNING | OEE: 71% (standard: 87%) | Effective remaining time: ~3.4 hrs

INVENTORY STATUS
Component K-551 (required for Op 40): Qty Required: 320 | On-hand: 210
  Pending receipt: 150 units (ETA: 16:30) — total available by ETA: 360 units
  Receipt is cutting it close if delayed""",
        "expected": {
            "at_risk_orders": ["PO-9901"],
            "drivers": {"PO-9901": {"primary": "machine", "secondary": "inventory"}},
            "severity": {"PO-9901": "medium"},
            "notes": (
                "Machine OEE pushes actual completion time close to 14:10; "
                "inventory receipt at 16:30 is tight if delayed. Both contribute."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-9901, identifies BOTH machine and inventory as "
            "contributing drivers (either as primary/secondary is acceptable), medium severity.\n"
            "Partial credit (0.5): Flags PO-9901 with only one risk driver mentioned, OR "
            "identifies both drivers but assigns high or low severity.\n"
            "No credit (0.0): Does not flag PO-9901, or names a single driver with no "
            "acknowledgment of the second."
        ),
    },

    {
        "id": "EC-002",
        "category": "edge_case",
        "description": "Machine down but significant float — severity should be low, not high",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 08:05 ===

ACTIVE PRODUCTION ORDERS
Order: PO-6677 | Product: Drill Press Table | Due: 2026-05-20 22:00 | Status: Queued
  Next Operation: Drilling (Op 10) | Assigned Machine: DP-04 | Work Duration: 45 min

MACHINE STATUS
DP-04 | Status: DOWN | Fault: Coolant pump failure | Est. repair: 75–90 min | Down since: 07:50

INVENTORY STATUS
PO-6677 BOM components: all on-hand

WORKFORCE
Shift 1 (06:00–14:00): Fully staffed""",
        "expected": {
            "at_risk_orders": ["PO-6677"],
            "drivers": {"PO-6677": {"primary": "machine"}},
            "severity": {"PO-6677": "low"},
            "notes": (
                "Repair ETA ~90 min, work is 45 min, due in ~14 hrs — "
                "~12 hrs of float. Risk is real but low."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-6677, machine as primary driver, LOW severity — "
            "explicitly accounting for the large buffer.\n"
            "Partial credit (0.5): Flags PO-6677 with correct driver but assigns medium or "
            "high severity, failing to account for ~12 hrs of buffer.\n"
            "No credit (0.0): Does not flag PO-6677 at all, or assigns incorrect driver."
        ),
    },

    {
        "id": "EC-003",
        "category": "edge_case",
        "description": "Inventory nominally sufficient but historical reject rate creates real risk",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 12:30 ===

ACTIVE PRODUCTION ORDERS
Order: PO-8823 | Product: Hydraulic Cylinder | Due: 2026-05-21 06:00 | Status: In Progress
  Current Operation: Sealing (Op 50) | Required Component: O-Ring Gasket G-44
  Qty Required: 200

MACHINE STATUS
Sealing Station SS-01: RUNNING | OEE: 89%

INVENTORY STATUS
O-Ring Gasket G-44: On-hand: 201 units | Allocated to PO-8823: 201 units
  Historical quality reject rate for G-44: 2.1% (avg 4.2 units rejected per 200-unit run)
  Pending receipt: None

WORKFORCE
Shift 2: Fully staffed""",
        "expected": {
            "at_risk_orders": ["PO-8823"],
            "drivers": {"PO-8823": {"primary": "inventory"}},
            "severity": {"PO-8823": "medium"},
            "notes": (
                "On-hand 201 vs required 200, but 2.1% reject rate = ~4 expected rejects, "
                "creating a practical shortage. Medium severity given proximity to due date."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-8823, inventory as driver, and explicitly accounts "
            "for the reject rate in reasoning. Medium (or low) severity acceptable.\n"
            "Partial credit (0.5): Flags PO-8823 with inventory as driver but ignores reject "
            "rate entirely in rationale, OR assigns high severity.\n"
            "No credit (0.0): Does not flag PO-8823 (accepts 201 >= 200 at face value), "
            "or assigns incorrect driver."
        ),
    },

    {
        "id": "EC-004",
        "category": "edge_case",
        "description": "Workforce workaround exists but creates cascade risk for another order",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 13:40 ===

ACTIVE PRODUCTION ORDERS
Order: PO-1122 | Product: Press Frame | Due: 2026-05-20 21:00 | Status: Queued for Shift 2
  Next Operation: Hydraulic Press (Op 20) | Cert Required: HYD-PRESS-OPS | Operators Required: 2

Order: PO-5599 | Product: Cover Plate | Due: 2026-05-21 06:00 | Status: In Progress (Op 10, 60%)
  Assigned Operators: 2 HYD-PRESS-OPS certified (currently working PO-5599)

MACHINE STATUS
Hydraulic Presses HP-01, HP-02: RUNNING | OEE: 90%

INVENTORY STATUS
Both orders: all BOM components on-hand

WORKFORCE
Shift 2 (14:00–22:00):
  HYD-PRESS-OPS certified operators total: 2
  Currently assigned: both to PO-5599 | Available for PO-1122: 0""",
        "expected": {
            "at_risk_orders": ["PO-1122"],
            "drivers": {"PO-1122": {"primary": "workforce"}},
            "severity": {"PO-1122": "medium"},
            "notes": (
                "PO-1122 needs 2 certified operators; both are committed to PO-5599. "
                "Reallocation possible but would cascade risk to PO-5599."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-1122 (workforce, medium), notes that reallocation "
            "from PO-5599 introduces cascade risk, does NOT flag PO-5599 as currently at risk.\n"
            "Partial credit (0.5): Flags PO-1122 correctly but assigns high severity without "
            "acknowledging reallocation option, OR correctly flags PO-1122 but also incorrectly "
            "flags PO-5599 as at risk when it currently has its operators.\n"
            "No credit (0.0): Does not flag PO-1122."
        ),
    },

    # ── ADVERSARIAL ─────────────────────────────────────────────────────────────

    {
        "id": "AV-001",
        "category": "adversarial",
        "description": "Alarming machine telemetry but no active order assigned to that machine",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 16:10 ===

ACTIVE PRODUCTION ORDERS
Order: PO-2211 | Product: Rotary Encoder Housing | Due: 2026-05-21 14:00 | Status: In Progress
  Current Operation: Surface Grinding (Op 60) | Assigned Machine: GRD-04 | Remaining: 1.5 hrs
  GRD-04 Status: RUNNING | OEE: 92%

Order: PO-3388 | Product: Motor Bracket | Due: 2026-05-21 10:00 | Status: Queued
  Next Operation: CNC Turning (Op 10) | Assigned Machine: LATHE-01
  Scheduled start: 2026-05-21 06:00 | LATHE-01 Status: RUNNING | OEE: 90%

MACHINE STATUS
CNC-12 | Status: RUNNING | Vibration: 2.4× baseline | Spindle temp: 17% above nominal
        OEE: 76% | Next scheduled order on CNC-12: PO-7799 (due 2026-05-25)

INVENTORY STATUS
All active order BOM components: on-hand and allocated

WORKFORCE
All shifts: fully staffed""",
        "expected": {
            "at_risk_orders": [],
            "notes": (
                "CNC-12 anomalies are real but irrelevant to current orders PO-2211 and PO-3388, "
                "which run on GRD-04 and LATHE-01. Claude must NOT flag current orders based on "
                "CNC-12 data."
            ),
        },
        "rubric": (
            "Full credit (1.0): Correctly reports no current orders at risk. May note CNC-12 "
            "as a future concern for PO-7799 but does NOT flag PO-2211 or PO-3388.\n"
            "Partial credit (0.5): Correctly clears both active orders but overstates CNC-12 "
            "as an immediate production risk rather than a future planning note.\n"
            "No credit (0.0): Flags PO-2211 or PO-3388 as at risk due to CNC-12 data. "
            "This is a hallucination — CNC-12 is not assigned to either order."
        ),
    },

    {
        "id": "AV-002",
        "category": "adversarial",
        "description": "Critical inventory alert on a component not on any active order's BOM",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 10:20 ===

ACTIVE PRODUCTION ORDERS
Order: PO-4400 | Product: Gearbox Housing (Product Line A) | Due: 2026-05-20 20:00
  Current Operation: CNC Boring (Op 20) | Machine: BOR-02 | Remaining: 2.5 hrs | OEE: 89%
  BOM Components: Housing Casting HC-10, Bearing Insert BI-22 — both on-hand

Order: PO-5511 | Product: Mounting Flange (Product Line B) | Due: 2026-05-21 08:00
  Next Operation: Drilling (Op 10) | Machine: DP-02 | Duration: 1.0 hr | Start: 18:00
  BOM Components: Flange Blank FB-33 — on-hand

INVENTORY STATUS
⚠️ CRITICAL ALERT: Component X-999 (Precision Lens Array)
  On-hand: 5 units (min threshold: 50 units)
  X-999 is used EXCLUSIVELY in Product Line C orders.
  No Product Line C orders are currently active.

WORKFORCE
All shifts: fully staffed""",
        "expected": {
            "at_risk_orders": [],
            "notes": (
                "X-999 alert is real but applies only to Product Line C. "
                "PO-4400 (Line A) and PO-5511 (Line B) do not use X-999. "
                "Claude must not flag either order."
            ),
        },
        "rubric": (
            "Full credit (1.0): Correctly reports no current orders at risk. May note X-999 "
            "as a procurement concern for future Line C orders, but does NOT flag PO-4400 or "
            "PO-5511.\n"
            "Partial credit (0.5): Correctly clears both orders but treats X-999 as an active "
            "production risk rather than a future procurement concern.\n"
            "No credit (0.0): Flags PO-4400 or PO-5511 as at risk due to X-999. "
            "X-999 is not on their BOMs — this is a hallucination."
        ),
    },

    {
        "id": "AV-003",
        "category": "adversarial",
        "description": "Workforce alert fires for an operation already completed on the order",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 17:55 ===

ACTIVE PRODUCTION ORDERS
Order: PO-4455 | Product: Coated Valve Body | Due: 2026-05-20 21:00 | Status: In Progress
  Operations:
    Op 10 — CNC Machining:  COMPLETE
    Op 20 — Deburring:      COMPLETE
    Op 30 — Precision Coating: COMPLETE (completed 15:30)
    Op 40 — Final Inspection & Pack: IN PROGRESS | Est. completion: 18:45

WORKFORCE ALERTS
⚠️ ALERT: Insufficient ISO-9001 Coating Operators for Shift 3 (22:00–06:00)
  Required: 3 | Scheduled: 1

MACHINE STATUS
Inspection Station IS-01: RUNNING | OEE: 96%

INVENTORY STATUS
All components consumed. Order in final processing.""",
        "expected": {
            "at_risk_orders": [],
            "notes": (
                "The coating alert refers to Shift 3 capacity. PO-4455's coating operation "
                "(Op 30) was completed at 15:30. The order is in final inspection and will "
                "complete at 18:45, well before its 21:00 due date."
            ),
        },
        "rubric": (
            "Full credit (1.0): Correctly identifies PO-4455 as NOT at risk, explicitly noting "
            "that the coating operation is already complete and the workforce alert is inapplicable "
            "to remaining operations.\n"
            "Partial credit (0.5): Correctly clears PO-4455 but does not explain why the "
            "workforce alert doesn't apply (missing the diagnostic reasoning).\n"
            "No credit (0.0): Flags PO-4455 as at risk due to the workforce alert, failing to "
            "check whether the flagged operation has already been completed."
        ),
    },

    # ── REGRESSION ──────────────────────────────────────────────────────────────

    {
        "id": "RG-001",
        "category": "regression",
        "description": "Obvious primary victim; second order on same downed machine is easy to miss",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 11:30 ===

ACTIVE PRODUCTION ORDERS
Order: PO-7788 | Product: Lathe Chuck Body | Due: 2026-05-20 15:30 | Status: In Progress
  Current Operation: Turning (Op 20) | Assigned Machine: LT-09 | Remaining: 2.5 hrs

Order: PO-3311 | Product: Spindle Housing | Due: 2026-05-20 19:00 | Status: Queued
  Next Operation: Turning (Op 10) | Assigned Machine: LT-09 | Duration: 3.0 hrs
  Scheduled start: 14:00

Order: PO-9944 | Product: Bearing Race | Due: 2026-05-21 06:00 | Status: In Progress
  Current Operation: Grinding (Op 30) | Assigned Machine: GRD-07 | Remaining: 1.0 hr
  GRD-07 Status: RUNNING | OEE: 91%

MACHINE STATUS
LT-09 | Status: DOWN | Fault: Hydraulic leak (F-117) | Est. repair: 3–4 hrs | Down since: 11:15

INVENTORY STATUS
All active orders: BOM components on-hand

WORKFORCE
All shifts: fully staffed""",
        "expected": {
            "at_risk_orders": ["PO-7788", "PO-3311"],
            "not_at_risk": ["PO-9944"],
            "drivers": {
                "PO-7788": {"primary": "machine"},
                "PO-3311": {"primary": "machine"},
            },
            "severity": {"PO-7788": "high", "PO-3311": "medium"},
            "notes": (
                "PO-7788 obvious primary victim. PO-3311 also requires LT-09 starting at 14:00; "
                "repair ETA 14:15–15:15 puts its 19:00 due date in jeopardy. "
                "PO-9944 is on GRD-07 and is not at risk."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags BOTH PO-7788 (machine, high) AND PO-3311 (machine, "
            "medium); correctly exempts PO-9944.\n"
            "Partial credit (0.5): Flags PO-7788 but misses PO-3311, OR flags both but "
            "assigns PO-3311 incorrect severity.\n"
            "No credit (0.0): Flags only PO-7788 with no mention of PO-3311's LT-09 "
            "dependency, or incorrectly flags PO-9944."
        ),
    },

    {
        "id": "RG-002",
        "category": "regression",
        "description": "Obvious inventory risk; hidden workforce gap on the next operation",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 09:00 ===

ACTIVE PRODUCTION ORDERS
Order: PO-2244 | Product: Precision Actuator | Due: 2026-05-20 22:00 | Status: In Progress
  Op 30 — Machining: COMPLETE
  Op 40 — Sub-assembly: IN PROGRESS | Machine: SA-Line-3 | OEE: 88%
    Required Component: Micro-Spring F-501 | Qty Required: 600 | On-hand: 91
    Pending receipt: None
  Op 50 — Final Assembly: Queued | Cert Required: ISO-PREC-ASSEMBLY | Operators Required: 2

WORKFORCE
Shift 2 (14:00–22:00):
  ISO-PREC-ASSEMBLY certified operators: 0 scheduled
  (All 4 certified operators are on Shift 1; none cross-scheduled to Shift 2)

MACHINE STATUS
SA-Line-3: RUNNING | OEE: 88%

INVENTORY STATUS
All other BOM components: on-hand""",
        "expected": {
            "at_risk_orders": ["PO-2244"],
            "drivers": {"PO-2244": {"primary": "inventory", "secondary": "workforce"}},
            "severity": {"PO-2244": "high"},
            "notes": (
                "Primary: F-501 at 15% of required quantity, no receipt — Op 40 will halt. "
                "Secondary: Op 50 requires ISO-PREC-ASSEMBLY cert; zero operators scheduled "
                "for Shift 2. Both independently create high risk."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-2244, inventory as primary AND identifies the "
            "workforce gap for Op 50 as a secondary driver. High severity.\n"
            "Partial credit (0.5): Flags PO-2244 as high-severity inventory risk but entirely "
            "misses the workforce gap for Op 50.\n"
            "No credit (0.0): Does not flag PO-2244, or identifies neither risk correctly."
        ),
    },

    {
        "id": "RG-003",
        "category": "regression",
        "description": "Obvious workforce gap; machine degradation is a silent compounding factor",
        "input": """\
=== MES SNAPSHOT — 2026-05-20 13:15 ===

ACTIVE PRODUCTION ORDERS
Order: PO-6634 | Product: CNC Brake Housing | Due: 2026-05-20 21:00 | Status: In Progress
  Current Operation: CNC Milling (Op 30) | Assigned Machine: CNC-05
  Remaining at standard: 3.0 hrs

MACHINE STATUS
CNC-05 | Status: RUNNING | OEE: 66% (standard: 85%)
        OEE trend: declining (was 79% two hours ago)
        Effective remaining time at current OEE: ~3.9 hrs

WORKFORCE
Shift 2 (14:00–22:00):
  CNC Operators Required for PO-6634: 4
  CNC Operators Confirmed for Shift 2: 2 (1 approved leave + 1 callout)

INVENTORY STATUS
PO-6634 BOM components: all on-hand""",
        "expected": {
            "at_risk_orders": ["PO-6634"],
            "drivers": {"PO-6634": {"primary": "workforce", "secondary": "machine"}},
            "severity": {"PO-6634": "high"},
            "notes": (
                "Primary: only 2 of 4 required CNC operators confirmed for Shift 2. "
                "Secondary: CNC-05 at 66% OEE and declining — even at full staffing, "
                "effective runtime of ~3.9 hrs pushes past 21:00."
            ),
        },
        "rubric": (
            "Full credit (1.0): Flags PO-6634, workforce as primary driver AND identifies "
            "machine OEE degradation as a compounding secondary driver. High severity.\n"
            "Partial credit (0.5): Flags PO-6634 as high-severity workforce risk but does "
            "not mention machine OEE degradation, missing the compounding factor.\n"
            "No credit (0.0): Does not flag PO-6634, or misidentifies both drivers."
        ),
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# Core functions
# ──────────────────────────────────────────────────────────────────────────────

def run_model(client: anthropic.Anthropic, test_case: dict) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": MES_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": test_case["input"]}],
    )
    return response.content[0].text


def judge_response(client: anthropic.Anthropic, test_case: dict, model_response: str) -> tuple[float, str]:
    judge_prompt = f"""## Test Case: {test_case['id']} — {test_case['description']}

## MES Input Data
{test_case['input']}

## Expected Output
{json.dumps(test_case['expected'], indent=2)}

## Scoring Rubric
{test_case['rubric']}

## AI Response Under Evaluation
{model_response}

Evaluate the AI response against the rubric and return valid JSON only."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=[{
            "type": "text",
            "text": JUDGE_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": judge_prompt}],
    )
    raw = response.content[0].text.strip()

    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            score = float(parsed["score"])
            if score not in (0.0, 0.5, 1.0):
                score = round(score * 2) / 2  # snap to nearest valid value
            return score, str(parsed.get("rationale", "No rationale provided."))
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    return 0.0, f"Judge returned unparseable output: {raw[:300]}"


def print_result(test_case: dict, response: str, score: float, rationale: str) -> None:
    GREEN, YELLOW, RED, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"
    color = {1.0: GREEN, 0.5: YELLOW, 0.0: RED}[score]
    label = {1.0: "PASS", 0.5: "PARTIAL", 0.0: "FAIL"}[score]
    bar = "─" * 70

    print(f"\n{bar}")
    print(f"[{test_case['id']}] {test_case['description']}")
    print(f"Category : {test_case['category'].replace('_', ' ').title()}")
    print(f"\n--- Model Response ---")
    print(response.strip())
    print(f"\n--- Judge Verdict ---")
    print(f"Score    : {color}{score:.1f} ({label}){RESET}")
    print(f"Rationale: {rationale}")


def print_summary(results: list[dict]) -> None:
    total = len(results)
    scores = [r["score"] for r in results]
    overall = sum(scores) / total

    categories: dict[str, list[float]] = {}
    for r in results:
        categories.setdefault(r["category"], []).append(r["score"])

    critical_failures = [r for r in results if r["score"] == 0.0]

    bar = "═" * 70
    print(f"\n{bar}")
    print("EVALUATION SUMMARY")
    print(bar)
    print(f"Model            : claude-sonnet-4-6")
    print(f"Run time         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Overall Score    : {overall:.2f} / 1.00  "
          f"({sum(scores):.1f} / {float(total):.0f} points)")
    print(f"Pass (1.0)       : {sum(1 for s in scores if s == 1.0)}/{total}")
    print(f"Partial (0.5)    : {sum(1 for s in scores if s == 0.5)}/{total}")
    print(f"Fail (0.0)       : {sum(1 for s in scores if s == 0.0)}/{total}")

    print(f"\nScore by Category:")
    category_order = ["happy_path", "edge_case", "adversarial", "regression"]
    for cat in category_order:
        if cat not in categories:
            continue
        cat_scores = categories[cat]
        avg = sum(cat_scores) / len(cat_scores)
        fill = "█" * int(avg * 20)
        label = cat.replace("_", " ").title()
        print(f"  {label:<20} {avg:.2f}  {fill}")

    if critical_failures:
        print(f"\n⚠  CRITICAL FAILURES ({len(critical_failures)}):")
        for r in critical_failures:
            print(f"  [{r['id']}] {r['description']}")
            print(f"        → {r['rationale']}")
    else:
        print("\n✓  No critical failures (0.0 scores).")

    print(bar)


def export_csv(results: list[dict], filename: str) -> None:
    fieldnames = [
        "run_timestamp", "test_id", "category", "description",
        "score", "verdict", "judge_rationale", "model_response",
    ]
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "run_timestamp": run_ts,
                "test_id": r["id"],
                "category": r["category"],
                "description": r["description"],
                "score": r["score"],
                "verdict": r["verdict"],
                "judge_rationale": r["rationale"],
                "model_response": r["response"],
            })
    print(f"\nResults exported → {filename}")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    results: list[dict] = []

    print("DXM Vision Manufacturing AI — Eval Harness")
    print(f"Model: claude-sonnet-4-6 | Test cases: {len(TEST_CASES)}")
    print(f"Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\nRunning {test_case['id']} ({i}/{len(TEST_CASES)})...", end="", flush=True)

        try:
            model_response = run_model(client, test_case)
            score, rationale = judge_response(client, test_case, model_response)
        except anthropic.APIError as exc:
            model_response = f"[API ERROR: {exc}]"
            score = 0.0
            rationale = f"API error prevented evaluation: {exc}"
        except Exception as exc:  # noqa: BLE001
            model_response = f"[HARNESS ERROR: {exc}]"
            score = 0.0
            rationale = f"Harness error: {exc}"

        verdict = {1.0: "PASS", 0.5: "PARTIAL", 0.0: "FAIL"}[score]
        print(f" {verdict}")

        result = {
            "id": test_case["id"],
            "category": test_case["category"],
            "description": test_case["description"],
            "score": score,
            "verdict": verdict,
            "rationale": rationale,
            "response": model_response,
        }
        results.append(result)
        print_result(test_case, model_response, score, rationale)

    print_summary(results)
    export_csv(results, "dxm_eval_results.csv")


if __name__ == "__main__":
    main()
