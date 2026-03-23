#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v7 as v7
import build_skill_reports_v8 as v8


ROOT = base.ROOT
OUTPUT_HTML_DIR = ROOT / "output/html"
OUTPUT_PATH = OUTPUT_HTML_DIR / "omega-planning-skills-hud.html"
CODEX_ROOT = Path.home() / ".codex"
SKILLS_ROOT = CODEX_ROOT / "skills"
SESSIONS_2026_ROOT = CODEX_ROOT / "sessions/2026"

GOD_PLAN_PATH = SKILLS_ROOT / "god-plan-mode/SKILL.md"
PLAN_CRITIC_PATH = SKILLS_ROOT / "plan-critic/SKILL.md"
REPO_MAP_PATH = SKILLS_ROOT / "omega-repo-map/SKILL.md"
PROOF_GATE_PATH = SKILLS_ROOT / "omega-proof-gate/SKILL.md"
CONDUCTOR_PATH = SKILLS_ROOT / "omega-conductor/SKILL.md"

GOD_PLAN_DESC_PATH = ROOT / "omega-runtime/skills/descriptions/god-plan-mode.skill.md"
PLAN_CRITIC_DESC_PATH = ROOT / "omega-runtime/skills/descriptions/plan-critic.skill.md"
REPO_MAP_DESC_PATH = ROOT / "omega-runtime/skills/descriptions/omega-repo-map.skill.md"
PROOF_GATE_DESC_PATH = ROOT / "omega-runtime/skills/descriptions/omega-proof-gate.skill.md"
CONDUCTOR_DESC_PATH = ROOT / "omega-runtime/skills/descriptions/omega-conductor.skill.md"

FALLBACK_PLAN_CRITIC_SNAPSHOT = """<skill>
<name>plan-critic</name>
<path>/home/gemmey1020/.codex/skills/plan-critic/SKILL.md</path>
---
name: plan-critic
description: Critique execution plans, implementation strategies, and multi-step coding proposals before work begins. Use when Codex or the user already has a draft plan and needs a findings-first review of assumptions, sequencing, verification, dependencies, scope, rollback, or risk; especially for debugging, feature work, refactors, migrations, repository changes, or plan stress-testing. Prefer this skill when the goal is to challenge or repair a plan rather than generate one from scratch. Do not trigger for trivial direct-execution requests or when no plan artifact exists to critique.
---

# Plan Critic

Review plans the way a strong engineer reviews risky code: identify what can break, what is weakly justified, what is missing, and what should be repaired before execution starts. Keep the output findings-first. Do not rewrite a decent plan from scratch unless the original is structurally unsalvageable.

## Core workflow

### 1. Lock the mission before criticizing
- Restate the plan objective in one sentence.
- Identify the task type and definition of done.
- Separate plan facts from assumptions and inferred intent.
- If the plan is too vague to critique meaningfully, say so and identify the minimum missing inputs.

### 2. Evaluate the plan against the rubric
- Use `references/critique-rubric.md` as the default review frame.
- Focus on material issues: objective drift, sequencing errors, hidden dependencies, missing proof, unsafe assumptions, over-scope, and weak rollback.
- Ignore stylistic differences unless they materially affect execution quality.

### 3. Rank findings by execution impact
- Use the severity model below.
- Prefer a small number of high-value findings over long cosmetic lists.
- Tie each finding to a concrete failure mode or execution risk.
- If a criticism cannot change a decision, deprioritize it.

### 4. Decide whether to repair
- If the plan is mostly sound, provide findings only.
- If the plan is fixable with bounded changes, provide a repaired plan after the findings.
- If the plan is unsalvageable, say why and recommend replanning instead of producing a fake repair.
- Use `references/repair-patterns.md` for limited, targeted repair moves.

### 5. Keep evidence and best practices explicit
- Distinguish repo evidence, user constraints, and external best-practice guidance.
- If the plan depends on current OpenAI APIs, models, prompting guidance, or tool behavior, invoke `$openai-docs` before freezing the critique.
- Prefer primary sources for fast-moving technical guidance.

## Output contract

When critique is the main deliverable, prefer this structure:

```md
## Mission
- Objective:
- Task type:
- Definition of done:

## Findings
1. [SEVERITY] Title
   - Why it matters:
   - Evidence:
   - Required repair:

## Open Questions
- ...

## Repair Decision
- findings-only | bounded-repair | replan-required

## Repaired Plan
1. ...
2. ...

## Residual Risk
- ...
```

## References

- `references/critique-rubric.md`: review dimensions and what to check in each
- `references/failure-patterns.md`: common ways plans fail before execution
- `references/repair-patterns.md`: bounded repair moves that improve a plan without replacing it

</skill>
"""

GOD_PLAN_EDITORIAL_BASELINE = {
    "mission": {
        "ar": "مخطط قوي للمهمات المعقدة، لكنه أقرب إلى strict blueprint يجهز الخطوات أكثر من كونه orchestrator متكامل مع بقية طبقة التخطيط.",
        "en": "A strong planner for complex work, but closer to a strict blueprint generator than a fully integrated orchestrator for the rest of the planning stack.",
    },
    "workflow": {
        "ar": "يثبّت الهدف ويقترح الترتيب العام، لكن handoff مع النقد والإثبات ليس جزءًا واضحًا من contract نفسه.",
        "en": "It locks the goal and proposes the rough order, but handoff to critique and proof is not yet part of the explicit contract.",
    },
    "proof_model": {
        "ar": "التحقق حاضر كمطلب جيد داخل الخطة، لكنه أقل صراحة كمنظومة gates مستقلة أو external-guidance branch مؤثر في المسار.",
        "en": "Verification is present as a healthy requirement inside the plan, but it is less explicit as a gate system or an external-guidance branch that can reshape the path.",
    },
    "output_contract": {
        "ar": "هيكل الخطة الأساسي موجود، لكن التحكم في mode selection وOmega presentation وbest-practice separation أقل صرامة.",
        "en": "The basic plan structure exists, but mode selection, Omega presentation, and best-practice separation are less tightly governed.",
    },
    "tooling": {
        "ar": "المساعدة الأداتية أخف: أقل اعتمادًا على scaffold + reference matrix واضحة، وأكثر اعتمادًا على جودة الصياغة اليدوية نفسها.",
        "en": "Tooling support is lighter: less reliance on an explicit scaffold plus reference matrix, and more reliance on strong manual planning prose.",
    },
    "failure_resistance": {
        "ar": "أقل وضوحًا في ask-vs-assume discipline، ومتى يلزم replan، وكيف تظل الخطة حيّة لو تحركت الحقائق.",
        "en": "It is less explicit about ask-vs-assume discipline, when replanning is required, and how the plan stays live when facts move.",
    },
}

ASPECTS = [
    ("mission", "المهمة", "Mission"),
    ("workflow", "سير العمل", "Workflow"),
    ("proof_model", "نموذج الإثبات", "Proof model"),
    ("output_contract", "عقد المخرج", "Output contract"),
    ("tooling", "الأدوات", "Tooling"),
    ("failure_resistance", "مقاومة الفشل", "Failure resistance"),
]

RELATION_ROWS = [
    (
        "الدور الأساسي",
        "Primary role",
        "يبني خطة تنفيذ جاهزة للحركة ويقفل الهدف والاستراتيجية والتحقق قبل التنفيذ.",
        "Builds the execution-ready plan and locks objective, strategy, and verification before implementation.",
        "يهاجم الخطة بعد بنائها ويكشف أين يمكن أن تنكسر أو تضلل المنفذ قبل أن يبدأ.",
        "Attacks the built plan and exposes where it can break or mislead the implementer before work starts.",
    ),
    (
        "متى تبدأ",
        "Start condition",
        "تبدأ عندما تكون المشكلة غامضة أو عالية المخاطر أو متعددة الخطوات وتحتاج sequencing واعيًا.",
        "Starts when the task is ambiguous, risky, or multi-step and needs deliberate sequencing.",
        "تبدأ فقط بعد وجود artifact تخطيطي فعلي يحتاج stress test findings-first.",
        "Starts only after a real plan artifact exists and needs a findings-first stress test.",
    ),
    (
        "مصدر الحقيقة",
        "Source of truth",
        "تعتمد على طلب المستخدم، أدلة الريبو، القيود الفعلية، والمصادر الأولية عندما تغير المسار.",
        "Relies on user request, repository evidence, actual constraints, and primary sources when they can alter the path.",
        "تعتمد على نفس عناصر الخطة نفسها، ثم تميز بوضوح بين repo evidence وuser constraints وexternal guidance وinferred intent.",
        "Relies on the same plan elements, then cleanly separates repo evidence, user constraints, external guidance, and inferred intent.",
    ),
    (
        "نوع الخرج",
        "Output type",
        "خطة مرتبة فيها Mission, Facts, Strategy, Plan, Verification, Risks مع support لـ Omega mode.",
        "A structured plan with Mission, Facts, Strategy, Plan, Verification, and Risks, plus Omega mode support.",
        "نقد findings-first مع severity, evidence lane, repair decision, وbounded repair فقط عند الحاجة.",
        "A findings-first critique with severity, evidence lane, repair decision, and bounded repair only when justified.",
    ),
    (
        "الحلقة المشتركة",
        "Handoff loop",
        "يسلم artifact واضح يمكن لـ plan-critic مراجعته بدل نقد نوايا عامة أو خطوات مبهمة.",
        "Hands off a clear artifact that plan-critic can review instead of critiquing vague intent or fuzzy steps.",
        "يرجع findings-only أو bounded-repair أو replan-required؛ ولو كسر الخطة يدفع المنظومة للرجوع إلى planning بدل التجميل.",
        "Returns findings-only, bounded-repair, or replan-required; if the plan is broken, it pushes the system back to planning instead of cosmetic patching.",
    ),
    (
        "التداخل مقابل التكامل",
        "Overlap vs complement",
        "قد يلمس المخاطر والقيود، لكنه ليس reviewer للنفس؛ وظيفته البناء لا الكبح.",
        "It can touch risk and constraints, but it is not a self-reviewer; its job is to build, not to brake.",
        "قد يقترح repair محدودًا، لكنه ليس planner بديلًا؛ وظيفته النقد والانضباط لا إنتاج خطة كاملة من الصفر.",
        "It may suggest bounded repair, but it is not an alternate planner; its job is critique and discipline, not full-plan generation from scratch.",
    ),
]

EXTRA_CSS = """
.planning-page .hero-grid {
  grid-template-columns: minmax(0, 1.16fr) minmax(340px, 0.84fr);
}

.planning-page .hero-copy h1 {
  max-width: 14ch;
}

.planning-page .hero-brief {
  margin-top: 20px;
}

.planning-page .hero-brief li {
  grid-template-columns: minmax(0, 1fr);
}

.planning-page .method-grid,
.planning-page .next-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.planning-page .section-block {
  overflow: hidden;
}

.planning-page .signal-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.planning-page .aspect-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
}

.planning-page .aspect-card,
.planning-page .matrix-cell,
.planning-page .next-card,
.planning-page .source-card {
  border: 1px solid var(--line);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 28%),
    color-mix(in srgb, var(--surface-strong) 94%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 20px 48px rgba(0, 0, 0, 0.16);
}

html[data-theme="light"] .planning-page .aspect-card,
html[data-theme="light"] .planning-page .matrix-cell,
html[data-theme="light"] .planning-page .next-card,
html[data-theme="light"] .planning-page .source-card {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.76),
    0 18px 40px rgba(77, 60, 35, 0.08);
}

.planning-page .aspect-card {
  padding: 18px;
  display: grid;
  gap: 14px;
}

.planning-page .aspect-card__header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.planning-page .aspect-card__header h3 {
  margin: 0;
  font-size: 1.16rem;
  letter-spacing: -0.02em;
}

.planning-page .aspect-card__lanes {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.planning-page .lane {
  min-height: 100%;
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(255, 194, 117, 0.12);
  background: rgba(255, 255, 255, 0.02);
}

.planning-page .lane--before {
  border-color: rgba(255, 255, 255, 0.08);
}

.planning-page .lane--after {
  border-color: var(--line-strong);
  background: var(--accent-soft);
}

.planning-page .lane__label {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 10px;
  color: var(--dim);
}

.planning-page .lane p,
.planning-page .matrix-cell p,
.planning-page .next-card p,
.planning-page .source-card p {
  margin: 0;
}

.planning-page .method-stack,
.planning-page .source-stack {
  display: grid;
  gap: 18px;
}

.planning-page .source-card,
.planning-page .next-card {
  padding: 18px;
  display: grid;
  gap: 12px;
}

.planning-page .source-card h3,
.planning-page .next-card h3 {
  margin: 0;
  font-size: 1.22rem;
}

.planning-page .meta-grid {
  display: grid;
  gap: 12px;
}

.planning-page .matrix {
  display: grid;
  gap: 0;
  border-top: 1px solid var(--line);
}

.planning-page .matrix-row {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid rgba(255, 194, 117, 0.1);
  align-items: start;
}

.planning-page .matrix-row:first-child {
  border-top: none;
}

.planning-page .matrix-topic {
  display: grid;
  gap: 6px;
  align-content: start;
}

.planning-page .matrix-topic strong {
  font-size: 0.98rem;
}

.planning-page .matrix-cell {
  padding: 14px;
  display: grid;
  gap: 10px;
}

.planning-page .matrix-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.planning-page .evidence-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
  gap: 24px;
}

.planning-page .snapshot-caption {
  display: grid;
  gap: 8px;
}

.planning-page .snapshot-meta {
  color: var(--dim);
  font-size: 12px;
}

.planning-page .lifecycle-rail {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.planning-page .report-list li span,
.planning-page .fact-list li span {
  color: var(--muted);
}

.planning-page .source-path {
  color: var(--accent-strong);
  font-family: var(--mono-font);
  font-size: 11px;
  word-break: break-word;
}

@media (max-width: 1100px) {
  .planning-page .hero-grid,
  .planning-page .method-grid,
  .planning-page .aspect-grid,
  .planning-page .next-grid,
  .planning-page .evidence-grid {
    grid-template-columns: 1fr;
  }

  .planning-page .matrix-row {
    grid-template-columns: 1fr;
  }

  .planning-page .aspect-card__lanes {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .planning-page .utility-bar {
    grid-template-columns: 1fr;
    justify-items: start;
  }
}
"""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def core_workflow_titles(text: str) -> list[str]:
    block = re.search(r"## Core workflow\s*(.*?)(?:\n## |\Z)", text, re.S)
    if not block:
        return []
    return [clean_text(item) for item in re.findall(r"^###\s+\d+\.\s+(.+)$", block.group(1), re.M)]


def output_contract_titles(text: str) -> list[str]:
    block = re.search(r"## Output contract.*?```md\s*(.*?)```", text, re.S)
    if not block:
        return []
    return [clean_text(item) for item in re.findall(r"^##\s+(.+)$", block.group(1), re.M)]


def reference_names(text: str) -> list[str]:
    found = re.findall(r"`references/([^`]+)`", text)
    return list(dict.fromkeys(found))


def script_names(skill_root: Path) -> list[str]:
    scripts_dir = skill_root / "scripts"
    if not scripts_dir.exists():
        return []
    return sorted(item.name for item in scripts_dir.glob("*.py"))


def golden_case_count(skill_root: Path) -> int:
    assets_dir = skill_root / "assets/golden-cases"
    if not assets_dir.exists():
        return 0
    return len(list(assets_dir.glob("*.json")))


def reference_count(skill_root: Path) -> int:
    refs_dir = skill_root / "references"
    if not refs_dir.exists():
        return 0
    return len(list(refs_dir.glob("*.md")))


def agent_file_count(skill_root: Path) -> int:
    agents_dir = skill_root / "agents"
    if not agents_dir.exists():
        return 0
    return len(list(agents_dir.glob("*.yaml")))


def format_title_chain(items: list[str]) -> str:
    return " -> ".join(items)


def build_plan_critic_snapshot() -> dict:
    for jsonl_path in sorted(SESSIONS_2026_ROOT.rglob("*.jsonl")):
        try:
            with jsonl_path.open("r", encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if "<name>plan-critic</name>" not in line:
                        continue
                    if "### 2. Evaluate the plan against the rubric" not in line:
                        continue
                    payload = json.loads(line)
                    content = payload.get("payload", {}).get("content") or []
                    for block in content:
                        text = block.get("text") or ""
                        if "<name>plan-critic</name>" not in text:
                            continue
                        if "### 2. Evaluate the plan against the rubric" not in text:
                            continue
                        match = re.search(r"(<skill>\n<name>plan-critic</name>\n.*?</skill>)", text, re.S)
                        if not match:
                            continue
                        return {
                            "text": match.group(1),
                            "source_path": str(jsonl_path),
                            "line_number": line_number,
                            "timestamp": payload.get("timestamp") or "",
                            "fallback_used": False,
                        }
        except (OSError, json.JSONDecodeError):
            continue
    return {
        "text": FALLBACK_PLAN_CRITIC_SNAPSHOT,
        "source_path": "fallback-baseline",
        "line_number": 0,
        "timestamp": "",
        "fallback_used": True,
    }


def snapshot_excerpt(text: str) -> str:
    workflow = core_workflow_titles(text)
    contract = output_contract_titles(text)
    excerpt = [
        "# Plan Critic / before snapshot",
        "",
        "Core workflow:",
    ]
    excerpt.extend(f"- {item}" for item in workflow)
    excerpt.extend(
        [
            "",
            "Output contract:",
        ]
    )
    excerpt.extend(f"- {item}" for item in contract)
    return "\n".join(excerpt)


def render_path_list(items: list[tuple[str, str]]) -> str:
    return "".join(
        "<li>"
        f"<strong>{v2.escape(label)}</strong>"
        f"<span class=\"source-path\">{v2.escape(path)}</span>"
        "</li>"
        for label, path in items
    )


def render_lane(label_ar: str, label_en: str, body_ar: str, body_en: str, tone: str) -> str:
    return (
        f'<div class="lane lane--{v2.escape(tone)}">'
        f'<div class="lane__label">{v2.bilingual_html(label_ar, label_en, "span")}</div>'
        f'{v2.bilingual_text(body_ar, body_en, "p", "rail-copy")}'
        "</div>"
    )


def render_aspect_card(
    title_ar: str,
    title_en: str,
    before_label_ar: str,
    before_label_en: str,
    before_ar: str,
    before_en: str,
    after_label_ar: str,
    after_label_en: str,
    after_ar: str,
    after_en: str,
) -> str:
    return f"""
      <article class="aspect-card">
        <div class="aspect-card__header">
          <h3>{v2.bilingual_html(title_ar, title_en, "span")}</h3>
          <div class="signal-strip">
            {v2.inline_tag(before_label_ar, before_label_en)}
            {v2.inline_tag(after_label_ar, after_label_en, "accent")}
          </div>
        </div>
        <div class="aspect-card__lanes">
          {render_lane(before_label_ar, before_label_en, before_ar, before_en, "before")}
          {render_lane(after_label_ar, after_label_en, after_ar, after_en, "after")}
        </div>
      </article>
    """


def render_evolution_section(profile: dict) -> str:
    cards = []
    for key, title_ar, title_en in ASPECTS:
        before = profile["before"][key]
        after = profile["after"][key]
        cards.append(
            render_aspect_card(
                title_ar,
                title_en,
                profile["before_label_ar"],
                profile["before_label_en"],
                before["ar"],
                before["en"],
                profile["after_label_ar"],
                profile["after_label_en"],
                after["ar"],
                after["en"],
            )
        )
    return f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html(profile["kicker_ar"], profile["kicker_en"], "span")}</p>
          <h2>{v2.bilingual_html(profile["title_ar"], profile["title_en"], "span")}</h2>
          {v2.bilingual_text(profile["summary_ar"], profile["summary_en"], "p", "section-copy")}
          <div class="signal-strip">
            {v2.code_tag(profile.get("public_name", profile["skill_id"]))}
            {v2.code_tag(profile.get("invoke_now", f"${profile['skill_id']}"))}
            {v2.inline_tag(profile["before_mode_ar"], profile["before_mode_en"])}
            {v2.inline_tag(profile["after_mode_ar"], profile["after_mode_en"], "accent")}
          </div>
        </div>
        <div class="section-divider"></div>
        <div class="aspect-grid">
          {"".join(cards)}
        </div>
      </section>
    """


def build_god_plan_profile(text: str) -> dict:
    skill_root = GOD_PLAN_PATH.parent
    workflow = format_title_chain(core_workflow_titles(text))
    contract = format_title_chain(output_contract_titles(text))
    refs = reference_count(skill_root)
    scripts = script_names(skill_root)
    agents = agent_file_count(skill_root)
    return {
        "skill_id": "god-plan-mode",
        "public_name": "God Plan Mode",
        "invoke_now": "$god-plan-mode",
        "title_ar": "تطور `God Plan Mode`",
        "title_en": "Evolution of `God Plan Mode`",
        "kicker_ar": "مسار التخطيط",
        "kicker_en": "Planner lane",
        "summary_ar": "هذا الجزء يعرض لماذا `god-plan-mode` لم يعد مجرد skill يكتب خطة جيدة، بل صار execution orchestrator يفرض contract واضح على التخطيط نفسه.",
        "summary_en": "This section shows why `god-plan-mode` is no longer just a skill that writes good plans, but an execution orchestrator that imposes a clear planning contract.",
        "before_label_ar": "قبل التطوير",
        "before_label_en": "Before",
        "after_label_ar": "بعد التطوير",
        "after_label_en": "After",
        "before_mode_ar": "خط أساس تحليلي",
        "before_mode_en": "Editorial baseline",
        "after_mode_ar": "مصدر حي",
        "after_mode_en": "Live source",
        "before": GOD_PLAN_EDITORIAL_BASELINE,
        "after": {
            "mission": {
                "ar": "أصبح يخطط كـ execution orchestrator: يقفل Objective وConstraints وDefinition of done، ويفضل الدليل على التخمين، ويعامل الخطة كأصل تشغيلي حي.",
                "en": "It now plans as an execution orchestrator: locking Objective, Constraints, and Definition of done, preferring evidence over guesses, and treating the plan as a live operational artifact.",
            },
            "workflow": {
                "ar": f"سير العمل الحالي صريح ومجزأ: {workflow}. هذا التسلسل ينقل التخطيط من good structure إلى governed execution path.",
                "en": f"The current workflow is explicit and segmented: {workflow}. That sequence moves planning from good structure into a governed execution path.",
            },
            "proof_model": {
                "ar": "كل خطوة meaningful لها validation method، مع فصل واضح بين repo evidence وexternal best-practice checks، وتفعيل `openai-docs` عندما يمكن أن يغيّر guidance المسار.",
                "en": "Every meaningful step gets a validation method, with a clear separation between repo evidence and external best-practice checks, and explicit `openai-docs` activation when guidance can change the path.",
            },
            "output_contract": {
                "ar": f"عقد الخرج الحالي ثابت وقابل للمراجعة: {contract}. كذلك تمت إضافة Omega mode selection وMarkdown-safe RTL guidance داخل نفس الـcontract.",
                "en": f"The current output contract is stable and auditable: {contract}. Omega mode selection and Markdown-safe RTL guidance are now part of the same contract.",
            },
            "tooling": {
                "ar": f"الطبقة الأداتية أصبحت عملية: {refs} مراجع، {len(scripts)} scaffold/tool script، و{agents} agent config. المسار المهم هنا هو `plan_scaffold.py` بدل الاعتماد على improvisation فقط.",
                "en": f"The tooling layer is now operational: {refs} references, {len(scripts)} scaffold/tool script, and {agents} agent config. The key shift is `plan_scaffold.py` instead of relying on improvisation alone.",
            },
            "failure_resistance": {
                "ar": "الجودة لم تعد implicit. هناك quality gates صريحة، ask-vs-assume discipline، وحالة `keep the plan live` عندما تتغير الحقائق أو يتحرك الـcritical path.",
                "en": "Quality is no longer implicit. There are explicit quality gates, ask-vs-assume discipline, and a `keep the plan live` rule when facts shift or the critical path moves.",
            },
        },
    }


def build_plan_critic_profile(text: str, snapshot: dict) -> dict:
    skill_root = PLAN_CRITIC_PATH.parent
    before_workflow = format_title_chain(core_workflow_titles(snapshot["text"]))
    before_contract = format_title_chain(output_contract_titles(snapshot["text"]))
    before_refs = reference_names(snapshot["text"])
    after_workflow = format_title_chain(core_workflow_titles(text))
    after_contract = format_title_chain(output_contract_titles(text))
    refs = reference_count(skill_root)
    scripts = script_names(skill_root)
    agents = agent_file_count(skill_root)
    golden_cases = golden_case_count(skill_root)
    return {
        "skill_id": "plan-critic",
        "public_name": "God Plan Critic",
        "invoke_now": "$plan-critic",
        "title_ar": "تطور `God Plan Critic`",
        "title_en": "Evolution of `God Plan Critic`",
        "kicker_ar": "مسار النقد",
        "kicker_en": "Critique lane",
        "summary_ar": "هذا الجزء يوضح انتقال `plan-critic` من rubric reviewer جيد إلى execution critic مكمل لـ `god-plan-mode` ويعرف متى يصلح، ومتى يرفض، ومتى يدفع إلى إعادة التخطيط.",
        "summary_en": "This section shows `plan-critic` moving from a solid rubric reviewer into an execution critic that complements `god-plan-mode` and knows when to repair, reject, or force replanning.",
        "before_label_ar": "قبل التطوير",
        "before_label_en": "Before",
        "after_label_ar": "بعد التطوير",
        "after_label_en": "After",
        "before_mode_ar": "Snapshot حرفي",
        "before_mode_en": "Literal snapshot",
        "after_mode_ar": "مصدر حي",
        "after_mode_en": "Live source",
        "before": {
            "mission": {
                "ar": "النسخة الأقدم كانت review skill مركزة على نقد خطط التنفيذ findings-first، لكنها لم تكن بعد twin كامل لـ `god-plan-mode`.",
                "en": "The older version was a review skill focused on findings-first plan critique, but it was not yet a full twin to `god-plan-mode`.",
            },
            "workflow": {
                "ar": f"سير العمل قبل الترقية كان: {before_workflow}. هذا قوي، لكنه rubric-led أكثر من كونه blocker-first engine.",
                "en": f"The pre-upgrade workflow was: {before_workflow}. Strong, but more rubric-led than blocker-first.",
            },
            "proof_model": {
                "ar": "الإثبات كان يظهر غالبًا كجزء من finding عن missing proof أو weak rollback، من غير proof-gap checklist مستقلة أو evidence lanes أو confidence calibration.",
                "en": "Proof mostly appeared as a finding about missing proof or weak rollback, without a dedicated proof-gap checklist, evidence lanes, or confidence calibration.",
            },
            "output_contract": {
                "ar": f"عقد الخرج كان منظمًا: {before_contract}. لكنه لم يحمل `critique_depth` أو `openai_aware` أو تفاصيل evidence lanes داخل Mission/Findings.",
                "en": f"The output contract was organized: {before_contract}. But it did not carry `critique_depth`, `openai_aware`, or evidence-lane detail inside Mission and Findings.",
            },
            "tooling": {
                "ar": f"الأدوات المرئية في snapshot كانت محدودة إلى {len(before_refs)} مراجع أساسية فقط: critique rubric, failure patterns, repair patterns. لا scaffold ظاهر ولا eval corpus.",
                "en": f"The visible tooling in the snapshot was limited to {len(before_refs)} core references only: critique rubric, failure patterns, and repair patterns. No visible scaffold or eval corpus.",
            },
            "failure_resistance": {
                "ar": "النسخة القديمة كانت حذرة من over-rewrite واختراع متطلبات، لكنها أقل صراحة في verdict calibration، bounded repair discipline، ورفض إهدار التوكنز على polish ثانوي عندما يكون الأصل مكسورًا.",
                "en": "The older version was careful about over-rewriting and inventing requirements, but less explicit about verdict calibration, bounded repair discipline, and refusing to spend tokens on secondary polish when the foundation was already broken.",
            },
        },
        "after": {
            "mission": {
                "ar": "أصبح يعمل كنصف المنظومة النقدي: twin لـ `god-plan-mode` يثبت mission lock أولًا ثم يختبر الخطة كأصل تنفيذي قابل للفشل أو الإنقاذ.",
                "en": "It now works as the critique half of the system: a twin to `god-plan-mode` that locks the mission first, then tests the plan as an execution artifact that can fail or be salvaged.",
            },
            "workflow": {
                "ar": f"سير العمل الحالي صار أعمق وأكثر انضباطًا: {after_workflow}. المهم هنا هو وجود triage pass يسبق deep critique بدل القفز مباشرة إلى rubric expansion.",
                "en": f"The current workflow is deeper and more disciplined: {after_workflow}. The key shift is a triage pass before deep critique instead of jumping straight into rubric expansion.",
            },
            "proof_model": {
                "ar": "أضيفت طبقة proof-awareness كاملة: `critique_depth`, `evidence_lane`, `repair_scope`, `confidence`, `openai_aware`, مع `proof-gap-checklist` و`verdict-decision-tree` لربط النقد بالإثبات والقرار.",
                "en": "A full proof-awareness layer was added: `critique_depth`, `evidence_lane`, `repair_scope`, `confidence`, and `openai_aware`, backed by a `proof-gap-checklist` and `verdict-decision-tree` that connect critique to proof and final decision.",
            },
            "output_contract": {
                "ar": f"عقد الخرج توسع إلى بنية قابلة للقياس: {after_contract}. الآن الـFinding نفسه يحمل why, evidence lane, evidence, repair, confidence، و`Repaired Plan` لا يظهر إلا عند `bounded-repair`.",
                "en": f"The output contract expanded into a measurable structure: {after_contract}. Each finding now carries why, evidence lane, evidence, repair, and confidence, and `Repaired Plan` appears only for `bounded-repair`.",
            },
            "tooling": {
                "ar": f"صار لديه package حقيقية: {refs} reference docs، {len(scripts)} scripts، {agents} agent config، و{golden_cases} golden cases. هذه النقلة حولت المهارة من prompt جيد إلى governed skill package.",
                "en": f"It now has a real package: {refs} reference docs, {len(scripts)} scripts, {agents} agent config, and {golden_cases} golden cases. That shift turns the skill from a good prompt into a governed skill package.",
            },
            "failure_resistance": {
                "ar": "النسخة الحالية تقاوم ثلاث آفات بوضوح: planner drift، generic advice، وfake repair. verdict model الجديد مع blocker triage يمنع التجميل عندما يكون replan هو القرار الصادق.",
                "en": "The current version explicitly resists three failure modes: planner drift, generic advice, and fake repair. The new verdict model plus blocker triage prevents cosmetic patching when replanning is the honest call.",
            },
        },
    }


def build_methodology_section(snapshot: dict) -> str:
    live_sources = [
        ("God Plan Mode / live / $god-plan-mode", str(GOD_PLAN_PATH)),
        ("God Plan Critic / live / $plan-critic", str(PLAN_CRITIC_PATH)),
        ("Omega Third Eye / live / $omega-repo-map", str(REPO_MAP_PATH)),
        ("Omega Conductor / live / $omega-conductor", str(CONDUCTOR_PATH)),
        ("Omega Proof Lock / live / $omega-proof-gate", str(PROOF_GATE_PATH)),
        ("God Plan Mode / description", str(GOD_PLAN_DESC_PATH)),
        ("God Plan Critic / description", str(PLAN_CRITIC_DESC_PATH)),
        ("Omega Third Eye / description", str(REPO_MAP_DESC_PATH)),
        ("Omega Conductor / description", str(CONDUCTOR_DESC_PATH)),
        ("Omega Proof Lock / description", str(PROOF_GATE_DESC_PATH)),
    ]
    snapshot_mode_ar = "Baseline بديل" if snapshot["fallback_used"] else "Snapshot حرفي"
    snapshot_mode_en = "Fallback baseline" if snapshot["fallback_used"] else "Literal session snapshot"
    return f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("مصدر الحقيقة", "Source of truth", "span")}</p>
          <h2>{v2.bilingual_html("المنهجية ومصادر before/after", "Methodology and before/after sources", "span")}</h2>
          {v2.bilingual_text("النسخة الحالية لكل مهارة مأخوذة من المصدر الحي مباشرة. أما الـbefore فله مساران فقط: snapshot literal لـ `plan-critic`، وeditorial baseline معلن بوضوح لـ `god-plan-mode` بدل الادعاء بوجود archive غير موجود.", "Each current skill state is taken from the live source directly. The `before` lane uses only two paths: a literal snapshot for `plan-critic`, and an explicitly declared editorial baseline for `god-plan-mode` instead of pretending an archive exists.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="evidence-grid">
          <div class="method-stack">
            <article class="source-card">
              <div class="signal-strip">
                {v2.inline_tag("المصادر الحية", "Live after sources", "accent")}
                {v2.inline_tag("5 مهارات", "5 skills")}
              </div>
              <h3>{v2.bilingual_html("المصادر الحية المعتمدة", "Live sources used", "span")}</h3>
              {v2.bilingual_text("كل comparisons الحالية بُنيت من ملفات `SKILL.md` الحية، مع وصف skill docs المحلية كطبقة توضيح ثانوية فقط.", "All current comparisons are grounded in live `SKILL.md` files, with local skill description docs used only as secondary explanatory support.", "p", "rail-copy")}
              <ul class="report-list">
                {render_path_list(live_sources)}
              </ul>
            </article>
            <article class="source-card">
              <div class="signal-strip">
                {v2.inline_tag("خط أساس تحليلي", "Editorial baseline")}
              </div>
              <h3>{v2.bilingual_html("كيف قُمنا بتأطير `god-plan-mode` قبل التطوير", "How `god-plan-mode` before-state is framed", "span")}</h3>
              {v2.bilingual_text("لم نعثر على file snapshot مختلف بوضوح يمكن عرضه كنسخة قديمة مستقلة، لذلك هذا الـbefore ليس claim أرشيفي. هو baseline تحليلي يصف النسخة الأقل نضجًا التي كنا نناقش ترقيتها مقارنةً بالعقد الحالي.", "We did not find a clearly distinct historical file snapshot that could be shown as a separate older version, so this `before` state is not an archival claim. It is an analytical baseline describing the less mature planner we were discussing upgrading relative to the current contract.", "p", "rail-copy")}
              <ul class="report-list">
                <li><strong>before_type</strong><span>editorial-baseline / not a live snapshot</span></li>
                <li><strong>guardrail</strong><span>do not claim a historical file that we cannot prove locally</span></li>
                <li><strong>purpose</strong><span>show the contract delta without faking source provenance</span></li>
              </ul>
            </article>
          </div>
          <div class="method-stack">
            <article class="source-card">
              <div class="signal-strip">
                {v2.inline_tag(snapshot_mode_ar, snapshot_mode_en, "accent")}
                {v2.code_tag("God Plan Critic")}
                {v2.code_tag("$plan-critic")}
              </div>
              <h3>{v2.bilingual_html("مصدر `God Plan Critic` قبل التطوير", "Source for `God Plan Critic` before-state", "span")}</h3>
              <div class="snapshot-caption">
                {v2.bilingual_text("هذا الـbefore مستخرج حرفيًا من session logs المحلية عندما كانت المهارة ما تزال بصيغتها الأقدم. لذلك المقارنة هنا ليست تخمينًا نظريًا بل مبنية على artifact نصي سابق.", "This `before` state is extracted literally from local session logs when the skill still appeared in its older form. That makes the comparison here grounded in an earlier text artifact rather than pure theory.", "p", "rail-copy")}
                <div class="snapshot-meta">{v2.escape(snapshot["source_path"])}{f" : line {snapshot['line_number']}" if snapshot['line_number'] else ""}</div>
              </div>
              <pre class="code-panel">{v2.escape(snapshot_excerpt(snapshot["text"]))}</pre>
            </article>
            <article class="source-card">
              <div class="signal-strip">
                {v2.inline_tag("سياق السلسلة", "Pipeline context")}
              </div>
              <h3>{v2.bilingual_html("السياق الحالي داخل Planning + Execution + Proof Stack", "Current context inside the Planning + Execution + Proof Stack", "span")}</h3>
              {v2.bilingual_text("الحزمة التي نقارنها هنا ليست مهارتين معزولتين. السلسلة الحية الآن أوضح: `Omega Third Eye` يقرأ الطريق، `God Plan Mode` يبني الخطة، `God Plan Critic` يضغط عليها، `Omega Conductor` ينسق التنفيذ، و`Omega Proof Lock` يقفل الإثبات.", "The package compared here is not just two isolated skills. The live chain is now clearer: `Omega Third Eye` reads the path, `God Plan Mode` builds the plan, `God Plan Critic` stresses it, `Omega Conductor` orchestrates execution, and `Omega Proof Lock` locks the proof.", "p", "rail-copy")}
              <div class="lifecycle-rail">
                {v2.inline_tag("Omega Third Eye / $omega-repo-map", "Omega Third Eye / $omega-repo-map")}
                {v2.inline_tag("God Plan Mode / $god-plan-mode", "God Plan Mode / $god-plan-mode", "accent")}
                {v2.inline_tag("God Plan Critic / $plan-critic", "God Plan Critic / $plan-critic", "accent")}
                {v2.inline_tag("Omega Conductor / $omega-conductor", "Omega Conductor / $omega-conductor")}
                {v2.inline_tag("Omega Proof Lock / $omega-proof-gate", "Omega Proof Lock / $omega-proof-gate")}
              </div>
            </article>
          </div>
        </div>
      </section>
    """


def build_relationship_section() -> str:
    rows = []
    for topic_ar, topic_en, left_ar, left_en, right_ar, right_en in RELATION_ROWS:
        rows.append(
            f"""
              <div class="matrix-row">
                <div class="matrix-topic">
                  <strong>{v2.bilingual_html(topic_ar, topic_en, "span")}</strong>
                </div>
                <article class="matrix-cell">
                  <div class="matrix-head">
                    {v2.code_tag("God Plan Mode")}
                    {v2.code_tag("$god-plan-mode")}
                    {v2.inline_tag("Planner", "Planner", "accent")}
                  </div>
                  {v2.bilingual_text(left_ar, left_en, "p", "rail-copy")}
                </article>
                <article class="matrix-cell">
                  <div class="matrix-head">
                    {v2.code_tag("God Plan Critic")}
                    {v2.code_tag("$plan-critic")}
                    {v2.inline_tag("Critic", "Critic", "accent")}
                  </div>
                  {v2.bilingual_text(right_ar, right_en, "p", "rail-copy")}
                </article>
              </div>
            """
        )
    return f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("العلاقة الحالية", "Current relationship", "span")}</p>
          <h2>{v2.bilingual_html("المقارنة الحالية بين `God Plan Mode` و`God Plan Critic`", "Current comparison between `God Plan Mode` and `God Plan Critic`", "span")}</h2>
          {v2.bilingual_text("الهدف هنا ليس إعلان winner. الهدف هو توضيح contract التكامل الحالي: أين يبدأ كل skill، ماذا يعتبر truth basis، وكيف يتم الـhandoff بين البناء والنقد.", "The point here is not to declare a winner. It is to clarify the current complement contract: where each skill starts, what it treats as truth basis, and how the handoff works between building and critiquing.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="matrix">
          {"".join(rows)}
        </div>
      </section>
    """


def build_next_review_section(repo_map_text: str, proof_gate_text: str) -> str:
    repo_map_workflow = " -> ".join(
        [
            "RepoFacts",
            "FlowPath",
            "ImpactMap",
            "Unknowns",
        ]
    )
    proof_gate_outputs = " -> ".join(
        [
            "CheckCatalog",
            "ProofPlan",
            "ExecutionLedger",
            "ManualCoverage",
            "ResidualRisk",
        ]
    )
    repo_refs = reference_count(REPO_MAP_PATH.parent)
    proof_refs = reference_count(PROOF_GATE_PATH.parent)
    repo_scripts = script_names(REPO_MAP_PATH.parent)
    proof_scripts = script_names(PROOF_GATE_PATH.parent)
    return f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("حدود الستاك", "Stack boundaries", "span")}</p>
          <h2>{v2.bilingual_html("كيف يثبت `Omega Third Eye` البداية ويقفل `Omega Proof Lock` النهاية", "How `Omega Third Eye` anchors the start and `Omega Proof Lock` closes the end", "span")}</h2>
          {v2.bilingual_text("بعد دخول `Omega Conductor`، لم يعد السؤال من سيأتي لاحقًا، بل كيف تظل حدود البداية والنهاية واضحة: discovery قبل التخطيط، وproof/closeout بعد orchestration.", "After `Omega Conductor` landed, the question is no longer who comes next, but how the start and end boundaries stay explicit: discovery before planning, and proof closeout after orchestration.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="next-grid">
          <article class="next-card">
            <div class="signal-strip">
              {v2.code_tag("Omega Third Eye")}
              {v2.code_tag("$omega-repo-map")}
              {v2.inline_tag("Discovery", "Discovery", "accent")}
            </div>
            <h3>{v2.bilingual_html("قبل التخطيط: من يثبت أرضية الواقع", "Before planning: who proves the terrain", "span")}</h3>
            {v2.bilingual_text("هذه المهارة تبدأ عندما يكون المسار داخل الريبو غير واضح. دورها الآن هو تقليل first-contact ambiguity عبر `RepoFacts`, `FlowPath`, `ImpactMap`, و`Unknowns` بدل البدء بتخطيط أو تنفيذ فوق افتراضات غير مثبتة.", "This skill starts when the path through the repository is unclear. Its current role is to reduce first-contact ambiguity through `RepoFacts`, `FlowPath`, `ImpactMap`, and `Unknowns` rather than planning or editing on top of unproven assumptions.", "p", "rail-copy")}
            <ul class="report-list">
              <li><strong>lifecycle</strong><span>before planning / before editing</span></li>
              <li><strong>core outputs</strong><span>{v2.escape(repo_map_workflow)}</span></li>
              <li><strong>tooling</strong><span>{repo_refs} refs + {len(repo_scripts)} scanner script</span></li>
              <li><strong>why it matters now</strong><span>it remains the evidence floor that `God Plan Mode` should stand on</span></li>
            </ul>
          </article>
          <article class="next-card">
            <div class="signal-strip">
              {v2.code_tag("Omega Proof Lock")}
              {v2.code_tag("$omega-proof-gate")}
              {v2.inline_tag("Proof", "Proof", "accent")}
            </div>
            <h3>{v2.bilingual_html("بعد التنفيذ: من يقفل الثقة بإثبات صادق", "After execution: who closes confidence with honest proof", "span")}</h3>
            {v2.bilingual_text("هذه المهارة تتحرك قرب النهاية. دورها الآن هو اختيار smallest convincing proof package ثم فصل `Ran`, `Manual`, `Not Run`, `Blocked`, و`Residual Risk` بدل closeout فضفاض أو ادعاءات `tested` غير موثقة.", "This skill moves near the end. Its current role is to choose the smallest convincing proof package, then separate `Ran`, `Manual`, `Not Run`, `Blocked`, and `Residual Risk` instead of a vague closeout or undocumented `tested` claims.", "p", "rail-copy")}
            <ul class="report-list">
              <li><strong>lifecycle</strong><span>after implementation / review / targeted debugging</span></li>
              <li><strong>core outputs</strong><span>{v2.escape(proof_gate_outputs)}</span></li>
              <li><strong>tooling</strong><span>{proof_refs} refs + {len(proof_scripts)} discovery script</span></li>
              <li><strong>why it matters now</strong><span>it operationalizes the proof expectations that `God Plan Critic` and `Omega Conductor` now hand off</span></li>
            </ul>
          </article>
        </div>
      </section>
    """


def build_evidence_section(snapshot: dict) -> str:
    evidence_items = [
        ("builder", str(SCRIPT_DIR / "build_planning_skills_hud.py")),
        ("live / god-plan-mode", str(GOD_PLAN_PATH)),
        ("live / God Plan Critic / $plan-critic", str(PLAN_CRITIC_PATH)),
        ("live / Omega Third Eye / $omega-repo-map", str(REPO_MAP_PATH)),
        ("live / Omega Conductor / $omega-conductor", str(CONDUCTOR_PATH)),
        ("live / Omega Proof Lock / $omega-proof-gate", str(PROOF_GATE_PATH)),
        ("desc / god-plan-mode", str(GOD_PLAN_DESC_PATH)),
        ("desc / God Plan Critic", str(PLAN_CRITIC_DESC_PATH)),
        ("desc / Omega Third Eye", str(REPO_MAP_DESC_PATH)),
        ("desc / Omega Conductor", str(CONDUCTOR_DESC_PATH)),
        ("desc / Omega Proof Lock", str(PROOF_GATE_DESC_PATH)),
        ("before / God Plan Critic snapshot", f"{snapshot['source_path']}{f':{snapshot['line_number']}' if snapshot['line_number'] else ''}"),
        ("after / output html", str(OUTPUT_PATH)),
    ]
    return f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("مسار الأدلة", "Evidence rail", "span")}</p>
          <h2>{v2.bilingual_html("المصادر التي بُني عليها هذا الـHUD", "Sources used to build this HUD", "span")}</h2>
          {v2.bilingual_text("هذا القسم موجود لإغلاق أي لبس: ما تم عرضه هنا مبني على ملفات محلية محددة، وليس على إعادة سرد عامة أو claims غير قابلة للتحقق.", "This section closes any ambiguity: what you see here is grounded in specific local files, not in generic retelling or unverifiable claims.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <article class="source-card">
          <div class="signal-strip">
            {v2.inline_tag("محلي فقط", "Local only", "accent")}
            {v2.inline_tag("بدون أصول خارجية", "No external assets")}
          </div>
          <ul class="report-list">
            {render_path_list(evidence_items)}
          </ul>
        </article>
      </section>
    """


def build_shell(title_en: str, title_ar: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-planning-stack">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{v2.escape(title_en)} | {v2.escape(title_ar)}</title>
  <style>
{v7.V7_CSS}
{EXTRA_CSS}
  </style>
</head>
<body class="planning-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA Planning Skills HUD / standalone artifact / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def build_page() -> str:
    snapshot = build_plan_critic_snapshot()
    god_plan_text = read_text(GOD_PLAN_PATH)
    plan_critic_text = read_text(PLAN_CRITIC_PATH)
    repo_map_text = read_text(REPO_MAP_PATH)
    proof_gate_text = read_text(PROOF_GATE_PATH)
    god_plan_profile = build_god_plan_profile(god_plan_text)
    plan_critic_profile = build_plan_critic_profile(plan_critic_text, snapshot)

    meta_html = "".join(
        [
            v2.metric_pill("4", "مهارات في المشهد", "Skills in view"),
            v2.metric_pill("2", "مسارات before/after", "Before/after lanes"),
            v2.metric_pill("1", "snapshot حرفي", "Literal snapshot"),
            v2.metric_pill("1", "baseline تحليلي", "Editorial baseline"),
        ]
    )
    topbar = v8.build_topbar("خريطة stack التخطيط", "Planning stack map", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("طبقة التخطيط / قبل وبعد", "Planning stack / before & after", "span")}</p>
              <h1>{v2.bilingual_html("خريطة تطور <span class=\"accent\">مهارات التخطيط والنقد</span> داخل أوميجا", "A map of how Omega's <span class=\"accent\">planning and critique skills</span> evolved", "span")}</h1>
              {v2.bilingual_text("هذا الـHUD مستقل عن `omega-skills-hud-v8.html` ومخصص لطبقة التخطيط بصيغتها الحالية: كيف نضج `God Plan Mode`، كيف تغير `God Plan Critic`، وكيف أصبح `Omega Third Eye` و`Omega Conductor` و`Omega Proof Lock` يحددون بداية ونهاية نفس السلسلة.", "This HUD is separate from `omega-skills-hud-v8.html` and focuses on the planning layer in its current form: how `God Plan Mode` matured, how `God Plan Critic` changed, and how `Omega Third Eye`, `Omega Conductor`, and `Omega Proof Lock` now define the start and end of the same chain.", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("map -> plan -> critique -> proof", "map -> plan -> critique -> proof", "accent")}
                {v2.inline_tag("مقارنة سلوكية", "behavior-first comparison")}
                {v2.inline_tag("أدلة محلية فقط", "local evidence only")}
              </div>
              <ul class="report-list hero-brief">
                <li>{v2.bilingual_html("`God Plan Mode` يُعرض against baseline تحليلي موثق بدل claim أرشيفي غير مثبت.", "`God Plan Mode` is shown against a documented editorial baseline instead of an unproven archival claim.", "span")}</li>
                <li>{v2.bilingual_html("`God Plan Critic` يُعرض against snapshot حرفي أقدم من session logs المحلية.", "`God Plan Critic` is shown against an older literal snapshot from local session logs.", "span")}</li>
                <li>{v2.bilingual_html("السياق الحالي يربط المنتصف بطرفي السلسلة: `Omega Third Eye` في البداية، `Omega Conductor` في المنتصف التنفيذي، و`Omega Proof Lock` في الإغلاق.", "The current context reconnects the middle to both ends of the chain: `Omega Third Eye` at the start, `Omega Conductor` as the execution middle, and `Omega Proof Lock` at closeout.", "span")}</li>
              </ul>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("باقة التخطيط والتنفيذ والإثبات", "Planning + Execution + Proof Stack", "accent")}
                  {v2.code_tag("omega")}
                </div>
                <div class="poster-surface__score">
                  <strong>4</strong>
                  <span>{v2.bilingual_html("محطات السلسلة", "Pipeline stages", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("من discovery إلى closeout", "From discovery to closeout", "span")}</div>
                {v2.bilingual_text("الفرق الحقيقي هنا ليس في الزخرفة، بل في وضوح handoff: `Omega Third Eye` يثبت الطريق، `God Plan Mode` يبني الخطة، `God Plan Critic` يكسرها إن كانت ضعيفة، `Omega Conductor` ينسق التنفيذ، و`Omega Proof Lock` يقفل النتيجة بأقل proof صادق.", "The real gain here is not visual polish, but handoff clarity: `Omega Third Eye` proves the path, `God Plan Mode` builds the plan, `God Plan Critic` breaks it if it is weak, `Omega Conductor` orchestrates execution, and `Omega Proof Lock` closes the result with the smallest honest proof.", "p", "poster-surface__summary")}
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  <span class="poster-meter"><span>live</span><strong>4</strong></span>
                  <span class="poster-meter"><span>before</span><strong>2</strong></span>
                  <span class="poster-meter"><span>literal</span><strong>1</strong></span>
                  <span class="poster-meter"><span>editorial</span><strong>1</strong></span>
                </div>
                <p class="dim-copy">Standalone HUD / planning-stack focused / deterministic local build</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    body_html = "\n".join(
        [
            topbar,
            hero,
            build_methodology_section(snapshot),
            render_evolution_section(god_plan_profile),
            render_evolution_section(plan_critic_profile),
            build_relationship_section(),
            build_next_review_section(repo_map_text, proof_gate_text),
            build_evidence_section(snapshot),
        ]
    )
    return build_shell("Omega Planning Skills HUD", "لوحة تطور المهارات التخطيطية", body_html)


def main() -> None:
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_page(), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
