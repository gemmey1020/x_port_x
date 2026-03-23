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
OUTPUT_MD = ROOT / "output/reports/omega-planning-stack-pilot-wave.md"
OUTPUT_HTML = ROOT / "output/html/omega-planning-stack-pilot-wave.html"

ROADMAP_MD = ROOT / "output/reports/omega-planning-stack-mvp-roadmap.md"
WAVE1_HUD = ROOT / "output/html/omega-planning-stack-wave1-hud.html"

SKILL_SOURCES = {
    "God Plan Mode / $god-plan-mode": Path.home() / ".codex/skills/god-plan-mode/SKILL.md",
    "Omega Third Eye / $omega-repo-map": Path.home() / ".codex/skills/omega-repo-map/SKILL.md",
    "God Plan Critic / $plan-critic": Path.home() / ".codex/skills/plan-critic/SKILL.md",
    "Omega Conductor / $omega-conductor": Path.home() / ".codex/skills/omega-conductor/SKILL.md",
    "Omega Proof Lock / $omega-proof-gate": Path.home() / ".codex/skills/omega-proof-gate/SKILL.md",
}

SCENARIOS = [
    {
        "id": "P1",
        "title": "narrow bug fix",
        "prompt": "لدينا bug fix صغير في endpoint معروف والمسار معروف مسبقًا. نريد خطة مضغوطة، مراجعتها سريعًا، ثم تنفيذ single-agent مع proof ضيق ومقنع.",
        "skill_order": [
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "critic_verdict": "findings-only",
        "conductor_mode": "single-agent",
        "proof_shape": "targeted regression check + narrow manual smoke + explicit residual risk if any uncovered edge remains",
        "stop_conditions": [
            "Fail if `Omega Third Eye` triggers even though the path is already known.",
            "Fail if `Omega Conductor` chooses `multi-agent` for a narrow and known critical path.",
            "Fail if `Omega Proof Lock` recommends broad suites without naming the specific regression proof.",
        ],
    },
    {
        "id": "P2",
        "title": "cross-boundary feature",
        "prompt": "الميزة الجديدة تضرب frontend + API + storage، والـpath ليس واضحًا بالكامل من البداية. نريد pipeline كاملة تنتهي بأوركسترا multi-agent ثم proof واضح.",
        "skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "critic_verdict": "bounded-repair",
        "conductor_mode": "multi-agent",
        "proof_shape": "cross-boundary build/test chain + integration smoke + blocked-path disclosure if any environment edge cannot run",
        "stop_conditions": [
            "Fail if discovery is skipped before planning.",
            "Fail if bounded repair is not applied before orchestration begins.",
            "Fail if ownership/write scopes overlap across concurrent lanes.",
        ],
    },
    {
        "id": "P3",
        "title": "high-coupling refactor",
        "prompt": "لدينا refactor واسع لكنه شديد الترابط داخل path واحدة حساسة. نريد اختبار أن الستاك لا ينجرف إلى fake parallelization.",
        "skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
            "Omega Conductor / $omega-conductor",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "critic_verdict": "findings-only",
        "conductor_mode": "single-agent",
        "proof_shape": "type/build or static safety checks + focused regression around the refactored seam + manual join verification",
        "stop_conditions": [
            "Fail if `Omega Conductor` chooses `multi-agent` despite heavy coupling.",
            "Fail if the plan lacks rollback or containment notes for the sensitive seam.",
            "Fail if proof does not target the risky join points explicitly.",
        ],
    },
    {
        "id": "P4",
        "title": "review-only task",
        "prompt": "عندنا review plan أو review strategy لمهمة قائمة، لكن لا يوجد تنفيذ جديد مطلوب الآن. نريد اختبار boundary بين critique وproof review mode.",
        "skill_order": [
            "God Plan Critic / $plan-critic",
            "Omega Proof Lock / $omega-proof-gate",
        ],
        "critic_verdict": "findings-only",
        "conductor_mode": "not-invoked",
        "proof_shape": "review-mode proof gap callout + explicit `Not Run`/`Blocked` inventory for any missing verification",
        "stop_conditions": [
            "Fail if `Omega Conductor` is invoked for a pure review-only pass.",
            "Fail if critique turns into a rewrite instead of a findings-first review.",
            "Fail if proof mode reports success instead of missing-proof reality.",
        ],
    },
    {
        "id": "P5",
        "title": "discovery-heavy task",
        "prompt": "الطلب يبدأ بغموض عالٍ داخل repo غير مألوفة، والهدف المباشر هو map + plan صالحين، وليس التنفيذ الآن.",
        "skill_order": [
            "Omega Third Eye / $omega-repo-map",
            "God Plan Mode / $god-plan-mode",
            "God Plan Critic / $plan-critic",
        ],
        "critic_verdict": "findings-only",
        "conductor_mode": "not-invoked",
        "proof_shape": "no proof package yet; artifact stops at validated discovery + approved plan boundary",
        "stop_conditions": [
            "Fail if the repo map is replaced by guesswork.",
            "Fail if execution orchestration starts before the task is execution-ready.",
            "Fail if the scenario pretends to have closeout proof without implementation.",
        ],
    },
    {
        "id": "P6",
        "title": "intentionally broken plan",
        "prompt": "سنغذي `God Plan Critic` بخطة مكسورة عمدًا فيها verification theater وdependency blind spots ونراقب هل يوقف المسار فعليًا.",
        "skill_order": [
            "God Plan Critic / $plan-critic",
        ],
        "critic_verdict": "replan-required",
        "conductor_mode": "not-invoked",
        "proof_shape": "none; the gate should stop before orchestration or closeout",
        "stop_conditions": [
            "Fail if verdict is anything other than `replan-required`.",
            "Fail if `Omega Conductor` starts despite a broken plan.",
            "Fail if any closeout or proof language appears after the gate should have stopped the run.",
        ],
    },
]

EXTRA_CSS = """
.pilot-page .hero-grid {
  grid-template-columns: minmax(0, 1.14fr) minmax(340px, 0.86fr);
}

.pilot-page .hero-copy h1 {
  max-width: 13ch;
}

.pilot-page .section-block {
  overflow: hidden;
}

.pilot-page .scenarios-grid,
.pilot-page .sources-grid,
.pilot-page .gate-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.pilot-page .scenario-card,
.pilot-page .gate-card,
.pilot-page .source-card,
.pilot-page .summary-card {
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

.pilot-page .tag-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.pilot-page .mini-label {
  color: var(--dim);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.pilot-page .scenario-card h3,
.pilot-page .gate-card h3,
.pilot-page .source-card h3,
.pilot-page .summary-card h3 {
  margin: 0;
  color: var(--ink);
}

.pilot-page .scenario-card p,
.pilot-page .gate-card p,
.pilot-page .source-card p,
.pilot-page .summary-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.8;
}

.pilot-page .stack-list,
.pilot-page .check-list,
.pilot-page .fact-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.pilot-page .stack-list li,
.pilot-page .check-list li,
.pilot-page .fact-list li {
  padding: 10px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--muted);
  line-height: 1.8;
}

.pilot-page .stack-list li:first-child,
.pilot-page .check-list li:first-child,
.pilot-page .fact-list li:first-child {
  border-top: none;
}

.pilot-page .code-block {
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

html[data-theme="light"] .pilot-page .code-block {
  background: rgba(242, 248, 255, 0.92);
}

@media (max-width: 1080px) {
  .pilot-page .hero-grid,
  .pilot-page .scenarios-grid,
  .pilot-page .sources-grid,
  .pilot-page .gate-grid {
    grid-template-columns: 1fr;
  }

  .pilot-page .hero-copy h1 {
    max-width: none;
  }
}
"""


def build_markdown() -> str:
    lines = [
        "# Omega Planning Stack Pilot Wave",
        "",
        "## Summary",
        "- هذا الملف هو الـpilot pack الصغيرة لكن الصارمة قبل `Wave 2 operational shakedown`.",
        "- العقد الحالي للأسماء العامة والـinvoke strings:",
        "- `Omega Third Eye` / `$omega-repo-map`",
        "- `God Plan Mode` / `$god-plan-mode`",
        "- `God Plan Critic` / `$plan-critic`",
        "- `Omega Conductor` / `$omega-conductor`",
        "- `Omega Proof Lock` / `$omega-proof-gate`",
        "- الهدف من الـpilot ليس تنفيذ المزايا نفسها، بل إثبات أن skill order والـgates والـhandoff صالحة تحت 6 سيناريوهات ممثلة.",
        "",
        "## Scenarios",
    ]

    for scenario in SCENARIOS:
        lines.extend(
            [
                f"### {scenario['id']} — {scenario['title']}",
                f"- Prompt: {scenario['prompt']}",
                f"- Expected skill order: {' -> '.join(f'`{item}`' for item in scenario['skill_order'])}",
                f"- Expected critic verdict: `{scenario['critic_verdict']}`",
                f"- Expected conductor mode: `{scenario['conductor_mode']}`",
                f"- Expected proof shape: {scenario['proof_shape']}",
                "- Stop conditions:",
            ]
        )
        lines.extend(f"  - {item}" for item in scenario["stop_conditions"])
        lines.append("")

    lines.extend(
        [
            "## Gate Into Wave 2",
            "- لا تبدأ `Wave 2 operational shakedown` إلا بعد مرور هذه السيناريوهات الستة مرة واحدة على الأقل كمراجع تشغيلية.",
            "- يجب أن ينتهي الـpilot بـdelta list قصيرة لا تتجاوز 5 نقاط.",
            "- أي drift في `public name + invoke now` يعالج قبل بدء Wave 2.",
            "",
            "## Sources",
            f"- Roadmap: `{ROADMAP_MD}`",
            f"- Wave 1 HUD: `{WAVE1_HUD}`",
        ]
    )

    for label, path in SKILL_SOURCES.items():
        lines.append(f"- {label}: `{path}`")

    return "\n".join(lines) + "\n"


def render_scenario_card(scenario: dict) -> str:
    order_items = "".join(f"<li><code>{v2.escape(item)}</code></li>" for item in scenario["skill_order"])
    stop_items = "".join(f"<li>{v2.escape(item)}</li>" for item in scenario["stop_conditions"])
    return f"""
      <article class="scenario-card">
        <div class="tag-strip">
          {v2.inline_tag("Pilot scenario", "Pilot scenario", "accent")}
          {v2.code_tag(scenario["id"])}
        </div>
        <h3>{v2.escape(scenario["title"])}</h3>
        <p>{v2.escape(scenario["prompt"])}</p>
        <span class="mini-label">Expected skill order</span>
        <ul class="stack-list">
          {order_items}
        </ul>
        <ul class="fact-list">
          <li><code>critic verdict</code><span>{v2.escape(scenario["critic_verdict"])}</span></li>
          <li><code>conductor mode</code><span>{v2.escape(scenario["conductor_mode"])}</span></li>
          <li><code>proof shape</code><span>{v2.escape(scenario["proof_shape"])}</span></li>
        </ul>
        <span class="mini-label">Stop conditions</span>
        <ul class="check-list">
          {stop_items}
        </ul>
      </article>
    """


def render_path_list(items):
    return "".join(
        f"<li><code>{v2.escape(label)}</code><span>{v2.escape(str(path))}</span></li>"
        for label, path in items
    )


def build_html() -> str:
    meta_html = "".join(
        [
            v2.metric_pill("6", "سيناريوهات pilot", "Pilot scenarios"),
            v2.metric_pill("5", "مهارات في الستاك", "Skills in stack"),
            v2.metric_pill("<=5", "delta budget", "Delta budget", "accent"),
            v2.metric_pill("Wave 2", "بوابة الدخول", "Entry gate"),
        ]
    )
    topbar = v8.build_topbar("Pilot wave pack", "Pilot wave pack", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Omega HUD / pilot wave", "Omega HUD / pilot wave", "span")}</p>
              <h1>{v2.bilingual_html("مرجع <span class=\"accent\">Pilot Wave</span> قبل `Wave 2 operational shakedown`", "The <span class=\"accent\">pilot wave</span> reference before `Wave 2 operational shakedown`", "span")}</h1>
              {v2.bilingual_text("هذا الـartifact لا يهدف إلى تنفيذ المزايا نفسها، بل إلى اختبار الستاك تحت ستة أشكال ضغط مختلفة: narrow bug, cross-boundary feature, coupling-heavy refactor, review-only, discovery-heavy, and intentionally broken planning.", "This artifact is not meant to execute the features themselves. It tests the stack under six different pressure shapes: narrow bug, cross-boundary feature, coupling-heavy refactor, review-only, discovery-heavy, and intentionally broken planning.", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("public name + invoke now", "public name + invoke now", "accent")}
                {v2.inline_tag("small but strict", "small but strict")}
                {v2.inline_tag("Wave 2 gate", "Wave 2 gate")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("Stack under pressure", "Stack under pressure", "accent")}
                  {v2.code_tag("pilot")}
                </div>
                <div class="poster-surface__score">
                  <strong>6</strong>
                  <span>{v2.bilingual_html("سيناريوهات ممثلة", "Representative scenarios", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("اختبار السلوك قبل التوسع", "Test behavior before expansion", "span")}</div>
                {v2.bilingual_text("النجاح هنا لا يُقاس بعدد المهارات، بل بوضوح الـgates: هل discovery تبدأ في وقتها؟ هل `God Plan Critic` يوقف الخطة المكسورة؟ هل `Omega Conductor` يرفض fake parallelization؟ وهل `Omega Proof Lock` يظل honest؟", "Success here is not measured by the number of skills, but by gate clarity: does discovery start on time, does `God Plan Critic` stop the broken plan, does `Omega Conductor` reject fake parallelization, and does `Omega Proof Lock` stay honest?", "p", "poster-surface__summary")}
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    summary = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Pilot Contract", "Pilot Contract", "span")}</p>
          <h2>{v2.bilingual_html("العقد التشغيلي للـpilot wave", "The operating contract for the pilot wave", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="gate-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("Naming lock", "Naming lock", "accent")}
            </div>
            <h3>{v2.bilingual_html("عقد الأسماء والتشغيل", "Naming and invoke contract", "span")}</h3>
            <ul class="fact-list">
              <li><code>Omega Third Eye</code><span>$omega-repo-map</span></li>
              <li><code>God Plan Mode</code><span>$god-plan-mode</span></li>
              <li><code>God Plan Critic</code><span>$plan-critic</span></li>
              <li><code>Omega Conductor</code><span>$omega-conductor</span></li>
              <li><code>Omega Proof Lock</code><span>$omega-proof-gate</span></li>
            </ul>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("Pilot objective", "Pilot objective")}
            </div>
            <h3>{v2.bilingual_html("ما الذي يجب أن تثبته هذه الموجة", "What this wave must prove", "span")}</h3>
            <ul class="check-list">
              <li>skill order صحيح حسب نوع المهمة.</li>
              <li>`God Plan Critic` يوقف `replan-required` فعلًا.</li>
              <li>`Omega Conductor` لا يوازي إلا إذا كانت write scopes منفصلة بصدق.</li>
              <li>`Omega Proof Lock` يقفل proof honestly بدل confidence theater.</li>
            </ul>
          </article>
        </div>
      </section>
    """

    scenarios = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Scenarios", "Scenarios", "span")}</p>
          <h2>{v2.bilingual_html("السيناريوهات الستة التي تشغل الستاك تحت الضغط", "The six scenarios that exercise the stack under pressure", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="scenarios-grid">
          {''.join(render_scenario_card(item) for item in SCENARIOS)}
        </div>
      </section>
    """

    gate = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Gate Into Wave 2", "Gate Into Wave 2", "span")}</p>
          <h2>{v2.bilingual_html("شروط الدخول إلى `Wave 2 operational shakedown`", "Entry criteria for `Wave 2 operational shakedown`", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="gate-grid">
          <article class="gate-card">
            <div class="tag-strip">
              {v2.inline_tag("Must pass", "Must pass", "accent")}
            </div>
            <h3>{v2.bilingual_html("لا تبدأ Wave 2 إلا بعد", "Do not start Wave 2 until", "span")}</h3>
            <ul class="check-list">
              <li>السيناريوهات الستة صارت واضحة بexpected order وverdict وmode وproof shape.</li>
              <li>أسماء `public name + invoke now` صارت ثابتة على السطوح الحية.</li>
              <li>entry `omega-conductor` موجودة في الأرشيف الحي ومربوطة بتوصيفها الصحيح.</li>
              <li>الـpilot انتهت بـdelta list قصيرة لا تتجاوز 5 نقاط.</li>
            </ul>
          </article>
          <article class="gate-card">
            <div class="tag-strip">
              {v2.inline_tag("Wave 2 input", "Wave 2 input")}
            </div>
            <h3>{v2.bilingual_html("ما الذي يدخل Wave 2 فعليًا", "What actually enters Wave 2", "span")}</h3>
            <ul class="check-list">
              <li>findings منطقية من pilot behavior لا من انطباعات عامة.</li>
              <li>أي gap في ordering أو gates أو proof honesty.</li>
              <li>أي confusion باقٍ بين public naming وبين invoke strings الحية.</li>
              <li>أصغر delta set ممكنة، لا موجة redesign جديدة.</li>
            </ul>
          </article>
        </div>
      </section>
    """

    sources = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Sources", "Sources", "span")}</p>
          <h2>{v2.bilingual_html("المصادر التي بُني منها هذا الـpilot pack", "The sources used to build this pilot pack", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="sources-grid">
          <article class="source-card">
            <h3>{v2.bilingual_html("Core references", "Core references", "span")}</h3>
            <ul class="fact-list">
              <li><code>roadmap</code><span>{v2.escape(str(ROADMAP_MD))}</span></li>
              <li><code>wave1 hud</code><span>{v2.escape(str(WAVE1_HUD))}</span></li>
              <li><code>pilot md</code><span>{v2.escape(str(OUTPUT_MD))}</span></li>
              <li><code>pilot html</code><span>{v2.escape(str(OUTPUT_HTML))}</span></li>
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

    body_html = "\n".join([topbar, hero, summary, scenarios, gate, sources])
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-planning-stack-pilot-wave">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>Omega Planning Stack Pilot Wave | موجة الـPilot لطبقة التخطيط</title>
  <style>
{v7.V7_CSS}
{EXTRA_CSS}
  </style>
</head>
<body class="pilot-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA Planning Stack Pilot Wave / standalone artifact / local only / no external assets</div>
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
