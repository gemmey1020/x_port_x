#!/usr/bin/env python3

from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v7 as v7
import build_skill_reports_v8 as v8


ROOT = base.ROOT
OUTPUT_MD = ROOT / "output/reports/omega-planning-stack-wave2-operational-shakedown.md"
OUTPUT_HTML = ROOT / "output/html/omega-planning-stack-wave2-operational-shakedown.html"

ROADMAP_MD = ROOT / "output/reports/omega-planning-stack-mvp-roadmap.md"
PILOT_MD = ROOT / "output/reports/omega-planning-stack-pilot-wave.md"
WAVE1_HUD = ROOT / "output/html/omega-planning-stack-wave1-hud.html"
PILOT_HTML = ROOT / "output/html/omega-planning-stack-pilot-wave.html"
PLANNING_HUD = ROOT / "output/html/omega-planning-skills-hud.html"
SKILLS_HUD_V8 = ROOT / "output/html/omega-skills-hud-v8.html"

SKILL_SOURCES = {
    "Omega Third Eye / $omega-repo-map": Path.home() / ".codex/skills/omega-repo-map/SKILL.md",
    "God Plan Mode / $god-plan-mode": Path.home() / ".codex/skills/god-plan-mode/SKILL.md",
    "God Plan Critic / $plan-critic": Path.home() / ".codex/skills/plan-critic/SKILL.md",
    "Omega Conductor / $omega-conductor": Path.home() / ".codex/skills/omega-conductor/SKILL.md",
    "Omega Proof Lock / $omega-proof-gate": Path.home() / ".codex/skills/omega-proof-gate/SKILL.md",
}

EVIDENCE_SIGNALS = [
    {
        "label": "builder compile",
        "command": "python3 -m py_compile omega-runtime/skills/build_skill_reports.py omega-runtime/skills/build_skill_reports_v2.py omega-runtime/skills/build_skill_reports_v8.py omega-runtime/skills/build_planning_stack_wave1_hud.py omega-runtime/skills/build_planning_stack_pilot_wave.py",
        "result": "pass",
        "summary_ar": "الـplanning builders الأساسية تتجمع بدون أخطاء نحوية.",
        "summary_en": "The core planning builders compile without syntax errors.",
    },
    {
        "label": "repo map scan",
        "command": "python3 ~/.codex/skills/omega-repo-map/scripts/scan_repo_map.py --root \"$PWD\" --format json",
        "result": "shallow",
        "summary_ar": "الماسح اكتشف `AI integration` فقط تقريبًا ولم يعطِ map عميقة لworkspace builder-heavy.",
        "summary_en": "The scanner mostly detected `AI integration` and did not produce a deep map for this builder-heavy workspace.",
    },
    {
        "label": "proof discovery",
        "command": "python3 ~/.codex/skills/omega-proof-gate/scripts/discover_checks.py --root \"$PWD\" --format json",
        "result": "zero-checks",
        "summary_ar": "الريبو الحالي لا يقدّم automated checks مكتشفة عبر `discover_checks.py`.",
        "summary_en": "The current repo exposes no discovered automated checks through `discover_checks.py`.",
    },
    {
        "label": "critic self-check",
        "command": "python3 ~/.codex/skills/plan-critic/scripts/run_self_check.py",
        "result": "ok=true",
        "summary_ar": "الـcritic scaffold والـgolden cases validated بنجاح.",
        "summary_en": "The critic scaffold and golden cases validated successfully.",
    },
    {
        "label": "operator surfaces",
        "command": "rg -n \"Omega Third Eye|God Plan Mode|God Plan Critic|Omega Conductor|Omega Proof Lock|invoke now\" output/html/omega-planning-stack-wave1-hud.html output/html/omega-planning-stack-pilot-wave.html output/html/omega-planning-skills-hud.html output/html/omega-skills-hud-v8.html",
        "result": "present",
        "summary_ar": "السطوح الحية تعرض public names والـinvoke strings بشكل متسق.",
        "summary_en": "The live surfaces expose public names and invoke strings consistently.",
    },
]

SCENARIOS = [
    {
        "id": "P5",
        "title": "discovery-heavy task",
        "type": "discovery-heavy",
        "base": "repo-grounded / OMEGA_SKILL_CATALOG.yaml -> build_skill_reports_v8.py -> omega-skills-hud-v8.html",
        "expected_skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
        ],
        "actual_skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
        ],
        "expected_verdict": "findings-only",
        "actual_verdict": "findings-only",
        "expected_conductor_mode": "not-invoked",
        "actual_conductor_mode": "not-invoked",
        "expected_proof_shape": "stop at validated discovery + approved plan boundary",
        "actual_proof_shape": "stopped at discovery + planning boundary, but repo-map automation stayed shallow",
        "boundary_result": "pass",
        "stop_condition_result": "honest-blocked",
        "deviation_kind": "environment limitation",
        "fix_applied": "none",
        "final_status": "honest-blocked",
        "note_ar": "Boundary discipline صحيحة: `Omega Conductor` و`Omega Proof Lock` لم يدخلا. لكن scanner الخاص بـ`Omega Third Eye` كان سطحيًا في هذا الـworkspace، لذلك discovery اعتمدت أكثر على القراءة الموجهة من الاعتماد على scan قوي.",
        "note_en": "Boundary discipline was correct: `Omega Conductor` and `Omega Proof Lock` stayed out. The `Omega Third Eye` scanner was shallow in this workspace, so discovery relied more on targeted reading than on a strong automated scan.",
        "evidence": [
            "scan_repo_map.py returned only shallow AI markers for this workspace",
            "the expected no-conductor / no-proof boundary remained intact",
        ],
    },
    {
        "id": "P1",
        "title": "narrow bug fix",
        "type": "narrow-bug",
        "base": "repo-grounded / operator-facing planning surface sourced by build_skill_reports_v8.py",
        "expected_skill_order": [
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "actual_skill_order": [
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "expected_verdict": "findings-only",
        "actual_verdict": "findings-only",
        "expected_conductor_mode": "single-agent",
        "actual_conductor_mode": "single-agent",
        "expected_proof_shape": "targeted regression check + narrow manual smoke + explicit residual risk",
        "actual_proof_shape": "py_compile + regenerated output surface + targeted naming/invoke grep",
        "boundary_result": "pass",
        "stop_condition_result": "pass",
        "deviation_kind": "none",
        "fix_applied": "none",
        "final_status": "pass",
        "note_ar": "الـknown-path workflow متماسك: لا حاجة إلى `Omega Third Eye`, والـconductor يبقى single-agent، وproof package يمكن أن تظل ضيقة جدًا على compile + regenerate + inspect.",
        "note_en": "The known-path workflow is coherent: no need for `Omega Third Eye`, the conductor stays single-agent, and the proof package can stay narrow with compile + regenerate + inspect.",
        "evidence": [
            "planning builders compiled successfully",
            "live HUD outputs already expose consistent public names and invoke strings",
        ],
    },
    {
        "id": "P4",
        "title": "review-only task",
        "type": "review-only",
        "base": "prompt-only / critique and proof review mode without implementation",
        "expected_skill_order": [
            "God Plan Critic / $plan-critic",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "actual_skill_order": [
            "God Plan Critic / $plan-critic",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "expected_verdict": "findings-only",
        "actual_verdict": "findings-only",
        "expected_conductor_mode": "not-invoked",
        "actual_conductor_mode": "not-invoked",
        "expected_proof_shape": "review-mode proof gap callout + explicit Not Run/Blocked inventory",
        "actual_proof_shape": "review-first critique + proof layer that names Not Run and Blocked explicitly",
        "boundary_result": "pass",
        "stop_condition_result": "pass",
        "deviation_kind": "none",
        "fix_applied": "none",
        "final_status": "pass",
        "note_ar": "الحدود هنا نظيفة: `God Plan Critic` findings-first فعلًا، و`Omega Proof Lock` لديه review mode صريح ولا يحتاج orchestration.",
        "note_en": "The boundary is clean here: `God Plan Critic` is genuinely findings-first, and `Omega Proof Lock` has an explicit review mode without needing orchestration.",
        "evidence": [
            "Omega Proof Lock documents review mode and explicit Not Run / Blocked buckets",
            "Omega Conductor stays out of pure review-only work by contract",
        ],
    },
    {
        "id": "P6",
        "title": "intentionally broken plan",
        "type": "broken-plan-gate",
        "base": "prompt-only / synthetic broken plan with verification theater and blind spots",
        "expected_skill_order": [
            "God Plan Critic / $plan-critic",
        ],
        "actual_skill_order": [
            "God Plan Critic / $plan-critic",
        ],
        "expected_verdict": "replan-required",
        "actual_verdict": "replan-required",
        "expected_conductor_mode": "not-invoked",
        "actual_conductor_mode": "not-invoked",
        "expected_proof_shape": "none",
        "actual_proof_shape": "none; gate stops before orchestration or closeout",
        "boundary_result": "pass",
        "stop_condition_result": "pass",
        "deviation_kind": "none",
        "fix_applied": "none",
        "final_status": "pass",
        "note_ar": "هذه أقوى بوابة في الـwave، وهي سليمة: الـcritic يرفع `replan-required`، ولا يوجد أي مبرر لدخول `Omega Conductor` أو `Omega Proof Lock` بعد ذلك.",
        "note_en": "This is the strongest gate in the wave, and it is intact: the critic escalates to `replan-required`, and there is no reason for `Omega Conductor` or `Omega Proof Lock` to enter after that.",
        "evidence": [
            "God Plan Critic documents `replan-required` as a hard stop",
            "run_self_check.py returned ok=true across scaffold and golden-case validation",
        ],
    },
    {
        "id": "P3",
        "title": "high-coupling refactor",
        "type": "high-coupling-refactor",
        "base": "repo-grounded / shared planning HUD rendering and naming logic across planning builders",
        "expected_skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "actual_skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "expected_verdict": "findings-only",
        "actual_verdict": "findings-only",
        "expected_conductor_mode": "single-agent",
        "actual_conductor_mode": "single-agent",
        "expected_proof_shape": "type/build or static safety checks + focused regression around the refactored seam + manual join verification",
        "actual_proof_shape": "py_compile + focused output inspection on shared planning surfaces",
        "boundary_result": "pass",
        "stop_condition_result": "pass",
        "deviation_kind": "none",
        "fix_applied": "none",
        "final_status": "pass",
        "note_ar": "`Omega Conductor` يتصرف هنا بالشكل الصح: refactor عالي الترابط لا يستحق fake parallelization، والـproof يظل متمركزًا حول joins المشتركة لا حول suite ضخمة.",
        "note_en": "`Omega Conductor` behaves correctly here: a highly coupled refactor does not deserve fake parallelization, and proof stays centered on the shared joins instead of a broad suite.",
        "evidence": [
            "Omega Conductor explicitly prefers single-agent when the work is highly coupled or overlap-heavy",
            "God Plan Mode verification defaults for refactors focus on preserved invariants and focused checks",
        ],
    },
    {
        "id": "P2",
        "title": "cross-boundary feature",
        "type": "cross-boundary-feature",
        "base": "repo-grounded / catalog + descriptions + builder + HUD planning-stack feature",
        "expected_skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "actual_skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "expected_verdict": "bounded-repair",
        "actual_verdict": "bounded-repair",
        "expected_conductor_mode": "multi-agent",
        "actual_conductor_mode": "multi-agent",
        "expected_proof_shape": "cross-boundary build/test chain + integration smoke + blocked-path disclosure",
        "actual_proof_shape": "contract-level ownership and proof-handoff shape is sound, but runtime proof remains compile/artifact-inspection heavy",
        "boundary_result": "pass",
        "stop_condition_result": "honest-blocked",
        "deviation_kind": "environment limitation",
        "fix_applied": "none",
        "final_status": "honest-blocked",
        "note_ar": "هيكل الـmulti-agent موجود وصحيح: verdict bounded-repair، ثم ownership map، ثم proof handoff. لكن البيئة الحالية لا تقدم automated check chain ولا live transcript harness تثبت multi-agent execution end-to-end.",
        "note_en": "The multi-agent structure is present and correct: bounded-repair first, then ownership mapping, then proof handoff. The current environment does not provide an automated check chain or a live transcript harness to prove multi-agent execution end-to-end.",
        "evidence": [
            "Omega Conductor defines ownership, no-overlap rules, sync points, and ProofHandoff",
            "discover_checks.py returned an empty checks array for this repo",
        ],
    },
]

STACK_REVIEW = [
    {
        "title": "Omega Third Eye",
        "status": "clean boundary / shallow automation",
        "body_ar": "دوره كبداية للستاك واضح وصحيح، لكنه في هذا الـworkspace يعتمد على targeted repo reading أكثر من scan غني بالإشارات.",
        "body_en": "Its role as the start of the stack is clear and correct, but in this workspace it depends more on targeted repo reading than on a rich automated scan.",
        "bullets": [
            "Boundary trigger is correct for discovery-heavy work.",
            "Current scan output is shallow on builder/docs-heavy repos.",
        ],
    },
    {
        "title": "God Plan Mode",
        "status": "strong",
        "body_ar": "يقفل Mission وFacts وVerification بشكل ناضج ويمنع التخطيط الزخرفي، خاصة في الشغل متعدد الخطوات.",
        "body_en": "It locks Mission, Facts, and Verification in a mature way and prevents decorative planning, especially in multi-step work.",
        "bullets": [
            "Strong mission lock and verification-first planning.",
            "Refactor and feature proof defaults stay concrete.",
        ],
    },
    {
        "title": "God Plan Critic",
        "status": "strong gate",
        "body_ar": "الـhard stop سليم، والـfindings-first discipline واضحة، و`replan-required` يعمل كبوابة حقيقية لا كصياغة لفظية.",
        "body_en": "The hard stop is sound, the findings-first discipline is clear, and `replan-required` acts as a real gate rather than a verbal flourish.",
        "bullets": [
            "Self-check script passed.",
            "Bounded repair and replan boundaries are explicit.",
        ],
    },
    {
        "title": "Omega Conductor",
        "status": "structurally strong",
        "body_ar": "قواعد single-agent vs multi-agent والـownership/no-overlap منضبطة، لكن الإثبات هنا ما زال contract-level أكثر من live execution trace.",
        "body_en": "Its single-agent vs multi-agent and ownership/no-overlap rules are disciplined, but proof here remains more contract-level than live execution trace.",
        "bullets": [
            "Rejects fake parallelization correctly.",
            "Needs a future live shakedown harness for stronger runtime proof.",
        ],
    },
    {
        "title": "Omega Proof Lock",
        "status": "honest but sparse environment",
        "body_ar": "التمييز بين `Not Run` و`Blocked` ممتاز، لكن الريبو الحالي نفسه لا يقدم automated checks مكتشفة، فيجبر الـproof على البقاء compile/artifact heavy.",
        "body_en": "Its `Not Run` vs `Blocked` distinction is excellent, but the current repo itself exposes no discovered automated checks, forcing proof to stay compile/artifact heavy.",
        "bullets": [
            "Review mode is clean and useful.",
            "Zero discovered checks is the main environmental constraint.",
        ],
    },
]

DELTA_LIST = [
    "تقوية `Omega Third Eye` على workspaces التي يغلب عليها builders وreports بدل frameworks التقليدية.",
    "إضافة fixture أو automated check واحد على الأقل يخدم planning/HUD work حتى لا يبقى `Omega Proof Lock` بلا discoverable checks.",
    "تشغيل Wave 3 عبر live shakedown transcript صغير لـ`Omega Conductor` بدل الاكتفاء بالـcontract evidence في multi-agent case.",
]

NEXT_WAVE = [
    "Wave 3 يجب أن تركز على evidence quality والlive execution trace، لا على skill جديدة.",
    "Wave 3 لا يجب أن تتحول إلى eval platform كبيرة أو telemetry project.",
    "Wave 3 تبدأ من delta list الحالية فقط، لا من إعادة تعريف الستاك من الصفر.",
]

FINDINGS = {
    "stack_defects": [
        "No blocker-grade stack defect was found in the live skill contracts or operator-facing surfaces reviewed in this pass.",
    ],
    "pilot_assumption_challenges": [
        "Repo-grounded scenarios become much stronger when they are anchored to exact builder/output paths instead of generic task labels only.",
    ],
    "environment_limitations": [
        "`scan_repo_map.py` produced a shallow map on this builder-heavy workspace.",
        "`discover_checks.py` found zero automated checks in the current repo.",
        "The multi-agent case is structurally sound but still lacks a live transcript harness for end-to-end proof.",
    ],
}

VERDICT = {
    "label": "passed-with-contained-gaps",
    "headline_ar": "الستاك نجحت تشغيليًا على مستوى العقود والحدود، لكن لم تصل بعد إلى live shakedown proof كاملة.",
    "headline_en": "The stack passed operationally at the contract-and-boundary level, but it has not yet reached full live-shakedown proof.",
    "summary_ar": "لا توجد مشكلة blocker في ترتيب المهارات أو handoff logic. الفجوات المتبقية تتعلق بجودة evidence داخل هذا الـworkspace نفسه: repo scan ضحل، zero discovered checks، وعدم وجود live transcript harness لحالة الـmulti-agent.",
    "summary_en": "There is no blocker in skill ordering or handoff logic. The remaining gaps are about evidence quality inside this workspace itself: shallow repo scan, zero discovered checks, and no live transcript harness for the multi-agent case.",
}

SUMMARY_COUNTS = {
    "scenarios": len(SCENARIOS),
    "pass": sum(1 for item in SCENARIOS if item["final_status"] == "pass"),
    "honest_blocked": sum(1 for item in SCENARIOS if item["final_status"] == "honest-blocked"),
    "fail": sum(1 for item in SCENARIOS if item["final_status"] == "fail"),
    "delta": len(DELTA_LIST),
}

EXTRA_CSS = """
.wave2-page .hero-grid {
  grid-template-columns: minmax(0, 1.08fr) minmax(360px, 0.92fr);
}

.wave2-page .hero-copy h1 {
  max-width: 11ch;
}

.wave2-page .section-block {
  overflow: hidden;
}

.wave2-page .summary-grid,
.wave2-page .findings-grid,
.wave2-page .verdict-grid,
.wave2-page .sources-grid,
.wave2-page .review-grid,
.wave2-page .evidence-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.wave2-page .scenario-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.wave2-page .summary-card,
.wave2-page .scenario-card,
.wave2-page .finding-card,
.wave2-page .verdict-card,
.wave2-page .review-card,
.wave2-page .source-card,
.wave2-page .evidence-card {
  border: 1px solid var(--line);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 28%),
    color-mix(in srgb, var(--surface-strong) 94%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 20px 48px rgba(0, 0, 0, 0.16);
  padding: 20px 18px;
  display: grid;
  gap: 12px;
}

html[data-theme="light"] .wave2-page .summary-card,
html[data-theme="light"] .wave2-page .scenario-card,
html[data-theme="light"] .wave2-page .finding-card,
html[data-theme="light"] .wave2-page .verdict-card,
html[data-theme="light"] .wave2-page .review-card,
html[data-theme="light"] .wave2-page .source-card,
html[data-theme="light"] .wave2-page .evidence-card {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.35),
    0 16px 40px rgba(44, 30, 9, 0.08);
}

.wave2-page .summary-card h3,
.wave2-page .scenario-card h3,
.wave2-page .finding-card h3,
.wave2-page .verdict-card h3,
.wave2-page .review-card h3,
.wave2-page .source-card h3,
.wave2-page .evidence-card h3 {
  margin: 0;
  color: var(--ink);
}

.wave2-page .summary-card p,
.wave2-page .scenario-card p,
.wave2-page .finding-card p,
.wave2-page .verdict-card p,
.wave2-page .review-card p,
.wave2-page .source-card p,
.wave2-page .evidence-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.8;
}

.wave2-page .stack-list,
.wave2-page .fact-list,
.wave2-page .check-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.wave2-page .stack-list li,
.wave2-page .fact-list li,
.wave2-page .check-list li {
  padding: 10px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--muted);
  line-height: 1.8;
}

.wave2-page .stack-list li:first-child,
.wave2-page .fact-list li:first-child,
.wave2-page .check-list li:first-child {
  border-top: none;
}

.wave2-page .tag-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.wave2-page .mini-label {
  color: var(--dim);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.wave2-page .code-block {
  margin: 0;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(4, 14, 27, 0.72);
  font-family: var(--mono-font);
  font-size: 12px;
  line-height: 1.75;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  color: var(--ink);
}

html[data-theme="light"] .wave2-page .code-block {
  background: rgba(242, 248, 255, 0.92);
}

.wave2-page .status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  font-size: 12px;
  color: var(--ink);
  background: rgba(255, 255, 255, 0.04);
}

.wave2-page .status-pill--pass {
  border-color: rgba(91, 211, 166, 0.42);
  color: #9df0c8;
}

.wave2-page .status-pill--blocked {
  border-color: rgba(250, 191, 96, 0.42);
  color: #ffd58e;
}

.wave2-page .status-pill--fail {
  border-color: rgba(255, 117, 129, 0.42);
  color: #ffb0b8;
}

.wave2-page .matrix-pair {
  display: grid;
  gap: 10px;
}

.wave2-page .matrix-pair div {
  display: grid;
  gap: 6px;
}

@media (max-width: 1080px) {
  .wave2-page .hero-grid,
  .wave2-page .summary-grid,
  .wave2-page .scenario-grid,
  .wave2-page .findings-grid,
  .wave2-page .verdict-grid,
  .wave2-page .review-grid,
  .wave2-page .sources-grid,
  .wave2-page .evidence-grid {
    grid-template-columns: 1fr;
  }

  .wave2-page .hero-copy h1 {
    max-width: none;
  }
}
"""


def scenario_status_class(status: str) -> str:
    if status == "pass":
        return "status-pill status-pill--pass"
    if status == "honest-blocked":
        return "status-pill status-pill--blocked"
    return "status-pill status-pill--fail"


def render_list(items):
    return "".join(f"<li>{v2.escape(item)}</li>" for item in items)


def render_path_list(items):
    return "".join(
        f"<li><code>{v2.escape(label)}</code><span>{v2.escape(str(path))}</span></li>"
        for label, path in items
    )


def build_markdown() -> str:
    lines = [
        "# Omega Planning Stack Wave 2 Operational Shakedown",
        "",
        "## Executive Summary",
        f"- Wave verdict: `{VERDICT['label']}`",
        f"- Scenarios reviewed: `{SUMMARY_COUNTS['scenarios']}`",
        f"- Final status split: `{SUMMARY_COUNTS['pass']}` pass / `{SUMMARY_COUNTS['honest_blocked']}` honest-blocked / `{SUMMARY_COUNTS['fail']}` fail",
        f"- Delta list size: `{SUMMARY_COUNTS['delta']}`",
        f"- Summary: {VERDICT['summary_ar']}",
        "",
        "## Run Method",
        "- This pass was a contract-level operational shakedown on the live skill sources and the current planning artifacts, not a full transcript harness.",
        "- Run order: `P5 -> P1 -> P4 -> P6 -> P3 -> P2`",
        "- Mixed mode split:",
        "  - repo-grounded: `P5`, `P1`, `P3`, `P2`",
        "  - prompt-only: `P4`, `P6`",
        "- Evidence signals used:",
    ]

    for signal in EVIDENCE_SIGNALS:
        lines.append(
            f"  - `{signal['label']}`: `{signal['result']}` — {signal['summary_ar']}"
        )

    lines.extend(["", "## Scenario Matrix"])

    for scenario in SCENARIOS:
        lines.extend(
            [
                f"### {scenario['id']} — {scenario['title']}",
                f"- Type: `{scenario['type']}`",
                f"- Base: {scenario['base']}",
                f"- Expected skill order: {' -> '.join(f'`{item}`' for item in scenario['expected_skill_order'])}",
                f"- Actual skill order: {' -> '.join(f'`{item}`' for item in scenario['actual_skill_order'])}",
                f"- Expected verdict: `{scenario['expected_verdict']}`",
                f"- Actual verdict: `{scenario['actual_verdict']}`",
                f"- Expected conductor mode: `{scenario['expected_conductor_mode']}`",
                f"- Actual conductor mode: `{scenario['actual_conductor_mode']}`",
                f"- Expected proof shape: {scenario['expected_proof_shape']}",
                f"- Actual proof shape: {scenario['actual_proof_shape']}",
                f"- Boundary result: `{scenario['boundary_result']}`",
                f"- Stop condition result: `{scenario['stop_condition_result']}`",
                f"- Deviation kind: `{scenario['deviation_kind']}`",
                f"- Fix applied: `{scenario['fix_applied']}`",
                f"- Final status: `{scenario['final_status']}`",
                f"- Note: {scenario['note_ar']}",
                "- Evidence:",
            ]
        )
        lines.extend(f"  - {item}" for item in scenario["evidence"])
        lines.append("")

    lines.extend(
        [
            "## Findings",
            "### Stack defects",
        ]
    )
    lines.extend(f"- {item}" for item in FINDINGS["stack_defects"])
    lines.extend(["", "### Pilot assumption challenges"])
    lines.extend(f"- {item}" for item in FINDINGS["pilot_assumption_challenges"])
    lines.extend(["", "### Environment limitations"])
    lines.extend(f"- {item}" for item in FINDINGS["environment_limitations"])

    lines.extend(
        [
            "",
            "## Fixes Applied",
            "- No functional stack fix was required during this shakedown.",
            "- The contained work completed in this wave was the creation of the Wave 2 canonical report and the Omega HUD output surfaces.",
            "",
            "## Stack Behavior Review",
        ]
    )

    for item in STACK_REVIEW:
        lines.extend(
            [
                f"### {item['title']}",
                f"- Status: `{item['status']}`",
                f"- Review: {item['body_ar']}",
            ]
        )
        lines.extend(f"- {bullet}" for bullet in item["bullets"])
        lines.append("")

    lines.extend(
        [
            "## Delta List",
        ]
    )
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(DELTA_LIST, start=1))
    lines.extend(
        [
            "",
            "## Wave Verdict",
            f"- Verdict: `{VERDICT['label']}`",
            f"- Why: {VERDICT['headline_ar']}",
            f"- Summary: {VERDICT['summary_ar']}",
            "",
            "## Next Wave Guidance",
        ]
    )
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(NEXT_WAVE, start=1))
    lines.extend(
        [
            "",
            "## Sources",
            f"- Roadmap: `{ROADMAP_MD}`",
            f"- Pilot report: `{PILOT_MD}`",
            f"- Wave 1 HUD: `{WAVE1_HUD}`",
            f"- Pilot HTML: `{PILOT_HTML}`",
            f"- Planning HUD: `{PLANNING_HUD}`",
            f"- Skills HUD v8: `{SKILLS_HUD_V8}`",
        ]
    )
    for label, path in SKILL_SOURCES.items():
        lines.append(f"- {label}: `{path}`")

    return "\n".join(lines) + "\n"


def render_scenario_card(scenario: dict) -> str:
    expected_order = "".join(f"<li><code>{v2.escape(item)}</code></li>" for item in scenario["expected_skill_order"])
    actual_order = "".join(f"<li><code>{v2.escape(item)}</code></li>" for item in scenario["actual_skill_order"])
    evidence = "".join(f"<li>{v2.escape(item)}</li>" for item in scenario["evidence"])
    return f"""
      <article class="scenario-card">
        <div class="tag-strip">
          {v2.code_tag(scenario["id"])}
          {v2.inline_tag(scenario["type"], scenario["type"], "accent")}
          <span class="{scenario_status_class(scenario['final_status'])}">{v2.escape(scenario["final_status"])}</span>
        </div>
        <h3>{v2.escape(scenario["title"])}</h3>
        <p>{v2.escape(scenario["note_ar"])}</p>
        <ul class="fact-list">
          <li><code>base</code><span>{v2.escape(scenario["base"])}</span></li>
          <li><code>expected verdict</code><span>{v2.escape(scenario["expected_verdict"])}</span></li>
          <li><code>actual verdict</code><span>{v2.escape(scenario["actual_verdict"])}</span></li>
          <li><code>expected conductor</code><span>{v2.escape(scenario["expected_conductor_mode"])}</span></li>
          <li><code>actual conductor</code><span>{v2.escape(scenario["actual_conductor_mode"])}</span></li>
          <li><code>boundary result</code><span>{v2.escape(scenario["boundary_result"])}</span></li>
          <li><code>stop result</code><span>{v2.escape(scenario["stop_condition_result"])}</span></li>
          <li><code>deviation kind</code><span>{v2.escape(scenario["deviation_kind"])}</span></li>
        </ul>
        <div class="matrix-pair">
          <div>
            <span class="mini-label">Expected skill order</span>
            <ul class="stack-list">{expected_order}</ul>
          </div>
          <div>
            <span class="mini-label">Actual skill order</span>
            <ul class="stack-list">{actual_order}</ul>
          </div>
        </div>
        <div>
          <span class="mini-label">Proof shape</span>
          <ul class="fact-list">
            <li><code>expected</code><span>{v2.escape(scenario["expected_proof_shape"])}</span></li>
            <li><code>actual</code><span>{v2.escape(scenario["actual_proof_shape"])}</span></li>
            <li><code>fix applied</code><span>{v2.escape(scenario["fix_applied"])}</span></li>
          </ul>
        </div>
        <span class="mini-label">Evidence</span>
        <ul class="check-list">{evidence}</ul>
      </article>
    """


def render_review_card(item: dict) -> str:
    bullets = "".join(f"<li>{v2.escape(bullet)}</li>" for bullet in item["bullets"])
    return f"""
      <article class="review-card">
        <div class="tag-strip">
          {v2.inline_tag(item["status"], item["status"], "accent")}
        </div>
        <h3>{v2.escape(item["title"])}</h3>
        <p>{v2.escape(item["body_ar"])}</p>
        <ul class="check-list">{bullets}</ul>
      </article>
    """


def render_evidence_card(item: dict) -> str:
    return f"""
      <article class="evidence-card">
        <div class="tag-strip">
          {v2.inline_tag(item["result"], item["result"], "accent")}
        </div>
        <h3>{v2.escape(item["label"])}</h3>
        <p>{v2.escape(item["summary_ar"])}</p>
        <pre class="code-block">{v2.escape(item["command"])}</pre>
      </article>
    """


def build_html() -> str:
    meta_html = "".join(
        [
            v2.metric_pill(str(SUMMARY_COUNTS["scenarios"]), "سيناريوهات", "Scenarios"),
            v2.metric_pill(str(SUMMARY_COUNTS["pass"]), "pass", "Pass"),
            v2.metric_pill(str(SUMMARY_COUNTS["honest_blocked"]), "honest-blocked", "Honest blocked", "accent"),
            v2.metric_pill(VERDICT["label"], "Wave verdict", "Wave verdict"),
        ]
    )
    topbar = v8.build_topbar("Wave 2 operational shakedown", "Wave 2 operational shakedown", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Omega HUD / wave 2 report", "Omega HUD / wave 2 report", "span")}</p>
              <h1>{v2.bilingual_html("تقرير <span class=\"accent\">Wave 2</span> للـoperational shakedown", "The <span class=\"accent\">Wave 2</span> operational shakedown report", "span")}</h1>
              {v2.bilingual_text(VERDICT["summary_ar"], VERDICT["summary_en"], "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("operator-grade report", "operator-grade report", "accent")}
                {v2.inline_tag("mixed mode", "mixed mode")}
                {v2.inline_tag(VERDICT["label"], VERDICT["label"])}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("Wave 2 verdict", "Wave 2 verdict", "accent")}
                  {v2.code_tag("wave2")}
                </div>
                <div class="poster-surface__score">
                  <strong>{SUMMARY_COUNTS["pass"]}</strong>
                  <span>{v2.bilingual_html("pass من أصل 6", f"{SUMMARY_COUNTS['pass']} pass out of 6", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("`passed-with-contained-gaps`", "`passed-with-contained-gaps`", "span")}</div>
                {v2.bilingual_text("النتيجة هنا ليست victory lap، بل closeout honest: boundaries والـhandoffs قوية، لكن evidence quality في هذا الـworkspace ما زالت أخف من أن تمنحنا live runtime certainty كاملة.", "This is not a victory lap, but an honest closeout: the boundaries and handoffs are strong, but evidence quality in this workspace is still lighter than full live runtime certainty.", "p", "poster-surface__summary")}
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    summary = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Executive Summary", "Executive Summary", "span")}</p>
          <h2>{v2.bilingual_html("ما الذي اختبرناه، وكيف حكمنا عليه", "What we tested and how we judged it", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("Run method", "Run method", "accent")}
            </div>
            <h3>{v2.bilingual_html("طريقة التشغيل", "Run method", "span")}</h3>
            <ul class="check-list">
              <li>contract-level shakedown على live skill sources والـplanning artifacts الحالية.</li>
              <li>run order ثابت: <code>P5 -&gt; P1 -&gt; P4 -&gt; P6 -&gt; P3 -&gt; P2</code>.</li>
              <li>mixed mode: 4 repo-grounded + 2 prompt-only.</li>
              <li>grading محدود إلى <code>pass</code> / <code>honest-blocked</code> / <code>fail</code>.</li>
            </ul>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("Top 3", "Top 3")}
            </div>
            <h3>{v2.bilingual_html("أهم 3 نتائج", "Top 3 outcomes", "span")}</h3>
            <ul class="check-list">
              <li>ترتيب المهارات والـgates الأساسية سليم، خاصة hard-stop بتاع <code>God Plan Critic</code>.</li>
              <li><code>Omega Conductor</code> structurally mature، لكنه ما زال محتاج live shakedown evidence.</li>
              <li>أكبر gaps ليست role confusion، بل evidence limitations داخل هذا الـworkspace.</li>
            </ul>
          </article>
        </div>
      </section>
    """

    evidence = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Run Evidence", "Run Evidence", "span")}</p>
          <h2>{v2.bilingual_html("الإشارات التي بُني عليها الحكم", "The evidence signals behind the verdict", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="evidence-grid">
          {''.join(render_evidence_card(item) for item in EVIDENCE_SIGNALS)}
        </div>
      </section>
    """

    scenarios = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Scenario Matrix", "Scenario Matrix", "span")}</p>
          <h2>{v2.bilingual_html("expected vs actual عبر السيناريوهات الستة", "Expected vs actual across the six scenarios", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="scenario-grid">
          {''.join(render_scenario_card(item) for item in SCENARIOS)}
        </div>
      </section>
    """

    findings = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Findings", "Findings", "span")}</p>
          <h2>{v2.bilingual_html("العيوب، تحديات الفرضيات، وحدود البيئة", "Defects, assumption challenges, and environment limits", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="findings-grid">
          <article class="finding-card">
            <div class="tag-strip">
              {v2.inline_tag("stack defects", "stack defects", "accent")}
            </div>
            <h3>{v2.bilingual_html("Stack defects", "Stack defects", "span")}</h3>
            <ul class="check-list">{render_list(FINDINGS["stack_defects"])}</ul>
          </article>
          <article class="finding-card">
            <div class="tag-strip">
              {v2.inline_tag("pilot assumptions", "pilot assumptions")}
            </div>
            <h3>{v2.bilingual_html("Pilot assumption challenges", "Pilot assumption challenges", "span")}</h3>
            <ul class="check-list">{render_list(FINDINGS["pilot_assumption_challenges"])}</ul>
          </article>
          <article class="finding-card">
            <div class="tag-strip">
              {v2.inline_tag("environment", "environment")}
            </div>
            <h3>{v2.bilingual_html("Environment limitations", "Environment limitations", "span")}</h3>
            <ul class="check-list">{render_list(FINDINGS["environment_limitations"])}</ul>
          </article>
          <article class="finding-card">
            <div class="tag-strip">
              {v2.inline_tag("fixes applied", "fixes applied")}
            </div>
            <h3>{v2.bilingual_html("Fixes applied", "Fixes applied", "span")}</h3>
            <ul class="check-list">
              <li>لا يوجد functional stack fix مطلوب في هذه الموجة.</li>
              <li>العمل المحتوى الوحيد هنا: إنشاء report builder + canonical outputs للـWave 2.</li>
            </ul>
          </article>
        </div>
      </section>
    """

    review = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Stack Behavior Review", "Stack Behavior Review", "span")}</p>
          <h2>{v2.bilingual_html("كيف تصرفت كل مهارة داخل الشيكداون", "How each skill behaved inside the shakedown", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="review-grid">
          {''.join(render_review_card(item) for item in STACK_REVIEW)}
        </div>
      </section>
    """

    verdict = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Wave Verdict", "Wave Verdict", "span")}</p>
          <h2>{v2.bilingual_html("الحكم النهائي وما الذي يجب أن يحدث بعده", "The final verdict and what should happen next", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="verdict-grid">
          <article class="verdict-card">
            <div class="tag-strip">
              {v2.inline_tag(VERDICT["label"], VERDICT["label"], "accent")}
            </div>
            <h3>{v2.bilingual_html("Wave verdict", "Wave verdict", "span")}</h3>
            <p>{v2.escape(VERDICT["headline_ar"])}</p>
            <ul class="check-list">
              <li>{v2.escape(VERDICT["summary_ar"])}</li>
            </ul>
          </article>
          <article class="verdict-card">
            <div class="tag-strip">
              {v2.inline_tag("Delta list", "Delta list")}
            </div>
            <h3>{v2.bilingual_html("Delta list", "Delta list", "span")}</h3>
            <ul class="check-list">{render_list(DELTA_LIST)}</ul>
          </article>
          <article class="verdict-card">
            <div class="tag-strip">
              {v2.inline_tag("Wave 3", "Wave 3", "accent")}
            </div>
            <h3>{v2.bilingual_html("Next wave guidance", "Next wave guidance", "span")}</h3>
            <ul class="check-list">{render_list(NEXT_WAVE)}</ul>
          </article>
          <article class="verdict-card">
            <div class="tag-strip">
              {v2.inline_tag("Outcome", "Outcome")}
            </div>
            <h3>{v2.bilingual_html("النتيجة المختصرة", "Short outcome", "span")}</h3>
            <ul class="fact-list">
              <li><code>pass</code><span>{SUMMARY_COUNTS["pass"]}</span></li>
              <li><code>honest-blocked</code><span>{SUMMARY_COUNTS["honest_blocked"]}</span></li>
              <li><code>fail</code><span>{SUMMARY_COUNTS["fail"]}</span></li>
              <li><code>delta budget used</code><span>{SUMMARY_COUNTS["delta"]}</span></li>
            </ul>
          </article>
        </div>
      </section>
    """

    sources = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Sources", "Sources", "span")}</p>
          <h2>{v2.bilingual_html("المصادر التي بُني عليها هذا التقرير", "The sources used to build this report", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="sources-grid">
          <article class="source-card">
            <h3>{v2.bilingual_html("Core artifacts", "Core artifacts", "span")}</h3>
            <ul class="fact-list">
              <li><code>roadmap</code><span>{v2.escape(str(ROADMAP_MD))}</span></li>
              <li><code>pilot md</code><span>{v2.escape(str(PILOT_MD))}</span></li>
              <li><code>pilot html</code><span>{v2.escape(str(PILOT_HTML))}</span></li>
              <li><code>wave1 hud</code><span>{v2.escape(str(WAVE1_HUD))}</span></li>
              <li><code>planning hud</code><span>{v2.escape(str(PLANNING_HUD))}</span></li>
              <li><code>skills hud v8</code><span>{v2.escape(str(SKILLS_HUD_V8))}</span></li>
            </ul>
          </article>
          <article class="source-card">
            <h3>{v2.bilingual_html("Skill sources", "Skill sources", "span")}</h3>
            <ul class="fact-list">
              {render_path_list(list(SKILL_SOURCES.items()))}
            </ul>
          </article>
        </div>
      </section>
    """

    body_html = "\n".join([topbar, hero, summary, evidence, scenarios, findings, review, verdict, sources])
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-wave2-operational-shakedown">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>Omega Planning Stack Wave 2 Operational Shakedown | تقرير الشيكداون التشغيلي للموجة الثانية</title>
  <style>
{v7.V7_CSS}
{EXTRA_CSS}
  </style>
</head>
<body class="wave2-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA Planning Stack Wave 2 / operational shakedown / standalone report / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def main() -> None:
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(build_markdown(), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(), encoding="utf-8")
    print(OUTPUT_MD)
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
