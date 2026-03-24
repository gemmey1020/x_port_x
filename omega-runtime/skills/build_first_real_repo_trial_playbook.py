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
OUTPUT_MD = ROOT / "output/reports/omega-first-real-repo-trial-playbook.md"
OUTPUT_HTML = ROOT / "output/html/omega-first-real-repo-trial-playbook.html"

SOURCES = [
    ("Preflight gate report", ROOT / "output/reports/omega-planning-stack-preflight-gate.md"),
    ("Preflight HUD", ROOT / "output/html/omega-planning-stack-preflight-gate.html"),
    ("Operator cheatsheet", ROOT / "output/html/omega-planning-stack-operator-cheatsheet.html"),
    ("Omega Third Eye", Path.home() / ".codex/skills/omega-repo-map/SKILL.md"),
    ("God Plan Mode", Path.home() / ".codex/skills/god-plan-mode/SKILL.md"),
    ("God Plan Critic", Path.home() / ".codex/skills/plan-critic/SKILL.md"),
    ("Omega Conductor", Path.home() / ".codex/skills/omega-conductor/SKILL.md"),
    ("Omega Proof Lock", Path.home() / ".codex/skills/omega-proof-gate/SKILL.md"),
]

SUMMARY = {
    "title_ar": "أول real repo trial playbook",
    "title_en": "The first real repo trial playbook",
    "reason_ar": "الهدف هنا ليس إننا نثبت إن الستاك خارقة في أي مهمة؛ الهدف إننا نجربها على ريبو حقيقية صغيرة، قابلة للسيطرة، ونخرج منها transcript نقدر نثق فيه.",
    "reason_en": "The goal here is not to prove the stack is magical on any task; the goal is to run it on one small, controllable real repo and leave with a trustworthy transcript.",
    "verdict": "narrow-first-run",
}

TRIAL_CONTRACT = [
    "ابدأ بمهمة صغيرة، قابلة للرجوع، وواضحة التأثير.",
    "لا تختبر skill boundaries كلها مرة واحدة في مهمة كبيرة.",
    "لو الـpath مجهول، discovery أولًا. لو الـpath معروف، لا تستدعِ discovery لمجرد الاحتياط.",
    "لا تشغل multi-agent إلا لو write scopes فعلًا منفصلة.",
    "النتيجة المطلوبة من أول trial: transcript honest + delta list صغيرة، لا victory theater.",
]

REPO_SELECTION = [
    "اختر ريبو حقيقية لكن صغيرة أو مألوفة نسبيًا، وليست monolith كبيرة من أول مرة.",
    "يفضل أن يكون فيها على الأقل build/check/test path واحدة discoverable، أو artifact deterministic واضح.",
    "يفضل أن تكون المهمة operator-facing لكن narrow: bug fix صغير، naming drift، render artifact محدود، أو docs/config change معلوم blast radius.",
    "تجنب أولًا: auth core، payments، migrations الخطيرة، infra deployment، أو أي path فيها side effects عالية.",
    "لو الريبو غامضة جدًا أو checks صفرية تمامًا، انقلها من first trial إلى later trial.",
]

PHASES = [
    {
        "id": "Phase 0",
        "title": "Pick the trial",
        "skill": "No skill yet",
        "invoke": "none",
        "goal_ar": "اختيار ريبو ومهمة يصلحوا لأول run.",
        "goal_en": "Choose a repo and a task that fit a first run.",
        "checks": [
            "هل المهمة narrow فعلًا؟",
            "هل يمكن الرجوع عنها بسهولة؟",
            "هل عندنا proof path معقول؟",
        ],
    },
    {
        "id": "Phase 1",
        "title": "Discovery only if needed",
        "skill": "Omega Third Eye",
        "invoke": "$omega-repo-map",
        "goal_ar": "ارسم الـpath الحقيقي وblast radius لو الطريق مش واضح.",
        "goal_en": "Map the real path and blast radius if the path is unclear.",
        "checks": [
            "Produce `RepoFacts / FlowPath / ImpactMap`.",
            "Stop once the next edit target is obvious.",
            "Do not drift into implementation or proof.",
        ],
    },
    {
        "id": "Phase 2",
        "title": "Build the plan",
        "skill": "God Plan Mode",
        "invoke": "$god-plan-mode",
        "goal_ar": "ابنِ execution-ready plan مضغوطة وواضحة.",
        "goal_en": "Build a compact execution-ready plan.",
        "checks": [
            "Lock objective, constraints, definition of done.",
            "Separate facts, assumptions, unknowns.",
            "Give every meaningful step a verification method.",
        ],
    },
    {
        "id": "Phase 3",
        "title": "Stress-test the plan",
        "skill": "God Plan Critic",
        "invoke": "$plan-critic",
        "goal_ar": "اكسر الخطة قبل ما التنفيذ يبدأ.",
        "goal_en": "Break the plan before execution starts.",
        "checks": [
            "If verdict = `replan-required`, stop.",
            "If verdict = `bounded-repair`, approve the repair first.",
            "Only proceed when execution is genuinely allowed.",
        ],
    },
    {
        "id": "Phase 4",
        "title": "Orchestrate only if justified",
        "skill": "Omega Conductor",
        "invoke": "$omega-conductor",
        "goal_ar": "قرر هل الشغل single-agent ولا multi-agent بأمان.",
        "goal_en": "Decide whether the work should stay single-agent or go multi-agent safely.",
        "checks": [
            "Prefer `single-agent` by default on the first live run.",
            "Allow `multi-agent` only if ownership and write scopes are truly disjoint.",
            "Produce `ProofHandoff` before leaving this phase.",
        ],
    },
    {
        "id": "Phase 5",
        "title": "Close honestly",
        "skill": "Omega Proof Lock",
        "invoke": "$omega-proof-gate",
        "goal_ar": "اقفل المهمة بأصغر proof convincing package.",
        "goal_en": "Close the task with the smallest convincing proof package.",
        "checks": [
            "Name `Ran / Not Run / Blocked / Residual Risk` explicitly.",
            "Do not claim proof that did not run.",
            "Prefer one strong proof chain over many weak commands.",
        ],
    },
]

PROMPTS = [
    ("Discovery", "Use `$omega-repo-map` and map the real path for this task before we edit anything."),
    ("Planning", "Use `$god-plan-mode` and build an execution-ready plan with explicit verification and risks."),
    ("Critique", "Use `$plan-critic` and tell me what can break in this plan before we start."),
    ("Orchestration", "Use `$omega-conductor` only if this approved plan genuinely benefits from orchestration."),
    ("Proof", "Use `$omega-proof-gate` and give me the minimum convincing proof before we close this task."),
]

ARTIFACTS_TO_KEEP = [
    "Repo map output إذا تم استخدام `Omega Third Eye`.",
    "الـapproved plan نفسها.",
    "الـcritic verdict النهائي.",
    "`Omega Conductor` output لو دخل orchestration.",
    "الـcloseout النهائي من `Omega Proof Lock`.",
    "delta list قصيرة: ماذا تعلمنا من أول real repo run.",
]

STOP_RULES = [
    "لو `God Plan Critic` رفعت `replan-required`، التوقف فوري.",
    "لو الـwrite scopes متداخلة، لا multi-agent.",
    "لو proof path غير موجودة تمامًا، اعترف بذلك ولا تمثل confidence غير حقيقية.",
    "لو المهمة بدأت تتضخم أثناء التنفيذ، اقفلها وارجع لخطة أضيق بدل الاستمرار.",
]

SUCCESS_SIGNAL = [
    "المهمة narrow واتقفلت بدون scope explosion.",
    "الـskill order كانت صحيحة ولم يحصل overlap غير ضروري.",
    "الـcloseout سمّى evidence حقيقية لا عناوين عامة.",
    "خرجنا transcript نقدر نبني عليها Wave التالية.",
]

EXTRA_CSS = """
.trial-page .hero-grid {
  align-items: stretch;
}

.trial-page .poster-surface__score {
  display: flex;
  align-items: end;
  gap: 0.8rem;
  margin-top: 1rem;
}

.trial-page .poster-surface__score strong {
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  line-height: 0.92;
}

.trial-page .section-block {
  padding: 2rem;
  background: rgba(9, 15, 26, 0.82);
  border: 1px solid rgba(140, 166, 205, 0.16);
  border-radius: 28px;
  box-shadow: 0 22px 48px rgba(7, 10, 18, 0.24);
}

.trial-page .section-block + .section-block {
  margin-top: 1.5rem;
}

.trial-page .summary-grid,
.trial-page .phase-grid,
.trial-page .source-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.trial-page .summary-grid--single,
.trial-page .source-grid--single {
  grid-template-columns: 1fr;
}

.trial-page .summary-card,
.trial-page .phase-card,
.trial-page .source-card {
  padding: 1.15rem 1.2rem;
  border-radius: 22px;
  border: 1px solid rgba(140, 166, 205, 0.14);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
}

.trial-page .tag-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-bottom: 0.85rem;
}

.trial-page .fact-list,
.trial-page .check-list,
.trial-page .source-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.65rem;
}

.trial-page .fact-list li,
.trial-page .check-list li,
.trial-page .source-list li {
  display: grid;
  gap: 0.3rem;
  padding: 0.72rem 0.8rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(140, 166, 205, 0.12);
}

.trial-page .source-list code,
.trial-page .code-block {
  direction: ltr;
  text-align: left;
  unicode-bidi: plaintext;
  font-family: "DejaVu Sans Mono", "Cascadia Mono", "Liberation Mono", monospace;
}

.trial-page .code-block {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  padding: 0.8rem 0.9rem;
  border-radius: 18px;
  background: rgba(7, 10, 18, 0.5);
  border: 1px solid rgba(140, 166, 205, 0.14);
}

.trial-page .mini-label {
  display: inline-flex;
  margin-bottom: 0.55rem;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(214, 224, 241, 0.7);
}

@media (max-width: 980px) {
  .trial-page .summary-grid,
  .trial-page .phase-grid,
  .trial-page .source-grid {
    grid-template-columns: 1fr;
  }
}
"""


def render_list(items: list[str]) -> str:
    return "".join(f"<li>{v2.escape(item)}</li>" for item in items)


def render_source_list(items: list[tuple[str, Path]]) -> str:
    return "".join(
        f"<li><strong>{v2.escape(label)}</strong><code>{v2.escape(str(path))}</code></li>"
        for label, path in items
    )


def render_phase_card(item: dict) -> str:
    return f"""
      <article class="phase-card">
        <div class="tag-strip">
          {v2.inline_tag(item["id"], item["id"], "accent")}
          {v2.inline_tag(item["skill"], item["skill"])}
          {v2.code_tag(item["invoke"])}
        </div>
        <h3>{v2.escape(item["title"])}</h3>
        {v2.bilingual_text(item["goal_ar"], item["goal_en"], "p", "muted-copy")}
        <span class="mini-label">Checks</span>
        <ul class="check-list">{render_list(item["checks"])}</ul>
      </article>
    """


def build_markdown() -> str:
    lines = [
        "# Omega First Real Repo Trial Playbook",
        "",
        "## Executive Summary",
        f"- Verdict: `{SUMMARY['verdict']}`",
        f"- Summary: {SUMMARY['reason_ar']}",
        "",
        "## Trial Contract",
    ]
    lines.extend(f"- {item}" for item in TRIAL_CONTRACT)
    lines.extend(["", "## Repo Selection"])
    lines.extend(f"- {item}" for item in REPO_SELECTION)
    lines.extend(["", "## Run Phases"])
    for item in PHASES:
        lines.extend(
            [
                f"### {item['id']} — {item['title']}",
                f"- Skill: `{item['skill']}`",
                f"- Invoke: `{item['invoke']}`",
                f"- Goal: {item['goal_ar']}",
            ]
        )
        lines.extend(f"  - {check}" for check in item["checks"])
        lines.append("")
    lines.extend(["## Quick Prompts"])
    lines.extend(f"- `{name}`: {prompt}" for name, prompt in PROMPTS)
    lines.extend(["", "## Stop Rules"])
    lines.extend(f"- {item}" for item in STOP_RULES)
    lines.extend(["", "## Success Signals"])
    lines.extend(f"- {item}" for item in SUCCESS_SIGNAL)
    lines.extend(["", "## Artifacts To Keep"])
    lines.extend(f"- {item}" for item in ARTIFACTS_TO_KEEP)
    lines.extend(["", "## Sources"])
    lines.extend(f"- {label}: `{path}`" for label, path in SOURCES)
    return "\n".join(lines) + "\n"


def build_html() -> str:
    meta_html = "".join(
        [
            v2.metric_pill("1", "first trial", "First trial"),
            v2.metric_pill("6", "phases", "Phases"),
            v2.metric_pill("narrow", "scope", "Scope", "accent"),
            v2.metric_pill(SUMMARY["verdict"], "mode", "Mode"),
        ]
    )
    topbar = v8.build_topbar("First real repo trial", "First real repo trial", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Omega HUD / trial playbook", "Omega HUD / trial playbook", "span")}</p>
              <h1>{v2.bilingual_html("خطة <span class=\"accent\">أول تجربة</span> على ريبو حقيقية", "The <span class=\"accent\">first run</span> on a real repo", "span")}</h1>
              {v2.bilingual_text(SUMMARY["reason_ar"], SUMMARY["reason_en"], "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("narrow-first-run", "narrow-first-run", "accent")}
                {v2.inline_tag("operator playbook", "operator playbook")}
                {v2.inline_tag("real repo", "real repo")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("Golden flow", "Golden flow", "accent")}
                  {v2.code_tag("$omega-repo-map -> $god-plan-mode -> $plan-critic -> $omega-conductor -> $omega-proof-gate")}
                </div>
                <div class="poster-surface__score">
                  <strong>1st</strong>
                  <span>{v2.bilingual_html("real repo run", "real repo run", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("Narrow scope. Honest evidence. Small delta list.", "Narrow scope. Honest evidence. Small delta list.", "span")}</div>
                {v2.bilingual_text("أول trial لازم تبقى controlled، مش استعراض قوة. المطلوب transcript نثق فيها، لا مهمة عملاقة نضيع فيها boundaries من أول مرة.", "The first trial must be controlled, not a power demo. The goal is a transcript we trust, not a giant task that erases boundaries on day one.", "p", "poster-surface__summary")}
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    contract = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Trial Contract", "Trial Contract", "span")}</p>
          <h2>{v2.bilingual_html("الخطوط الحمراء لأول run", "The red lines for the first run", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("contract", "contract", "accent")}
            </div>
            <h3>{v2.bilingual_html("عقد التجربة", "Run contract", "span")}</h3>
            <ul class="check-list">{render_list(TRIAL_CONTRACT)}</ul>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("selection", "selection")}
            </div>
            <h3>{v2.bilingual_html("شروط اختيار الريبو", "Repo selection rules", "span")}</h3>
            <ul class="check-list">{render_list(REPO_SELECTION)}</ul>
          </article>
        </div>
      </section>
    """

    phases = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Run Order", "Run Order", "span")}</p>
          <h2>{v2.bilingual_html("المراحل الست لأول real repo trial", "The six phases of the first real repo trial", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="phase-grid">
          {''.join(render_phase_card(item) for item in PHASES)}
        </div>
      </section>
    """

    operator = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Operator Kit", "Operator Kit", "span")}</p>
          <h2>{v2.bilingual_html("الـprompts والـartifacts المطلوبة", "The prompts and artifacts you should keep", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("quick prompts", "quick prompts", "accent")}
            </div>
            <h3>{v2.bilingual_html("صياغات جاهزة", "Ready prompts", "span")}</h3>
            <pre class="code-block">{v2.escape(chr(10).join(f'- {name}: {prompt}' for name, prompt in PROMPTS))}</pre>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("keep these", "keep these")}
            </div>
            <h3>{v2.bilingual_html("الـartifacts التي نحتفظ بها", "Artifacts to keep", "span")}</h3>
            <ul class="check-list">{render_list(ARTIFACTS_TO_KEEP)}</ul>
          </article>
        </div>
      </section>
    """

    gates = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Stop / Success", "Stop / Success", "span")}</p>
          <h2>{v2.bilingual_html("متى نوقف ومتى نعتبر التجربة نجحت", "When to stop and when to call the run successful", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("stop rules", "stop rules", "accent")}
            </div>
            <h3>{v2.bilingual_html("شروط الإيقاف", "Stop rules", "span")}</h3>
            <ul class="check-list">{render_list(STOP_RULES)}</ul>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("success", "success")}
            </div>
            <h3>{v2.bilingual_html("إشارات النجاح", "Success signals", "span")}</h3>
            <ul class="check-list">{render_list(SUCCESS_SIGNAL)}</ul>
          </article>
        </div>
      </section>
    """

    sources = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Sources", "Sources", "span")}</p>
          <h2>{v2.bilingual_html("المراجع التي بُني عليها الـplaybook", "The sources behind the playbook", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="source-grid source-grid--single">
          <article class="source-card">
            <div class="tag-strip">
              {v2.inline_tag("live references", "live references", "accent")}
            </div>
            <h3>{v2.bilingual_html("المصادر الحية", "Live references", "span")}</h3>
            <ul class="source-list">{render_source_list(SOURCES)}</ul>
          </article>
        </div>
      </section>
    """

    body_html = f"""
    {topbar}
    <main class="hud-frame trial-page">
      {hero}
      {contract}
      {phases}
      {operator}
      {gates}
      {sources}
    </main>
    """

    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-real-repo-playbook">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{v2.escape("Omega First Real Repo Trial Playbook")} | {v2.escape("خطة أول تجربة على ريبو حقيقية")}</title>
  <style>
{v7.V7_CSS}
{EXTRA_CSS}
  </style>
</head>
<body class="trial-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD / first real repo trial playbook / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def main() -> int:
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text(build_markdown(), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(), encoding="utf-8")
    print(OUTPUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
