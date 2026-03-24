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
OUTPUT_HTML = ROOT / "output/html/omega-planning-stack-operator-cheatsheet.html"

STACK_ORDER = [
    {
        "step": "01",
        "name": "Omega Third Eye",
        "invoke": "$omega-repo-map",
        "role": "discovery",
        "body_ar": "افتح بيه الريبو لما الطريق لسه مش واضح.",
        "body_en": "Use it to open the repo when the path is still unclear.",
    },
    {
        "step": "02",
        "name": "God Plan Mode",
        "invoke": "$god-plan-mode",
        "role": "planning",
        "body_ar": "يبني الخطة التنفيذية المحكمة ويثبت الـverification من البداية.",
        "body_en": "Builds the execution-ready plan and locks verification from the start.",
    },
    {
        "step": "03",
        "name": "God Plan Critic",
        "invoke": "$plan-critic",
        "role": "critique",
        "body_ar": "يضغط على الخطة قبل التنفيذ ويقرر: صالحة، محتاجة repair محدود، أو replan.",
        "body_en": "Stress-tests the plan before execution and decides: sound, bounded repair, or replan.",
    },
    {
        "step": "04",
        "name": "Omega Conductor",
        "invoke": "$omega-conductor",
        "role": "orchestration",
        "body_ar": "يدير التنفيذ فقط بعد الموافقة على الخطة، ويقرر single-agent ولا multi-agent.",
        "body_en": "Coordinates execution only after the plan is approved, deciding single-agent vs multi-agent.",
    },
    {
        "step": "05",
        "name": "Omega Proof Lock",
        "invoke": "$omega-proof-gate",
        "role": "proof",
        "body_ar": "يقفل المهمة بأصغر proof محترمة وhonest closeout.",
        "body_en": "Closes the task with the smallest convincing proof and an honest closeout.",
    },
]

DECISION_LADDER = [
    {
        "question_ar": "أنا لسه مش فاهم الريبو أو مش عارف الـpath الحقيقي.",
        "question_en": "I still do not understand the repo or the real code path.",
        "skill": "Omega Third Eye",
        "invoke": "$omega-repo-map",
        "why_ar": "لأن المشكلة هنا discovery وليس planning أو proof.",
        "why_en": "Because the blocker is discovery, not planning or proof.",
    },
    {
        "question_ar": "أنا فاهم المسار، لكن محتاج خطة محترمة قبل الشغل.",
        "question_en": "I understand the path, but I need a strong plan before touching the work.",
        "skill": "God Plan Mode",
        "invoke": "$god-plan-mode",
        "why_ar": "لأن التحدي الآن sequencing وverification وrisk handling.",
        "why_en": "Because the challenge is sequencing, verification, and risk handling.",
    },
    {
        "question_ar": "الخطة موجودة، وعاوز أكسرها قبل ما أبدأ.",
        "question_en": "The plan already exists, and I want to break it before execution.",
        "skill": "God Plan Critic",
        "invoke": "$plan-critic",
        "why_ar": "لأن المطلوب critique findings-first وليس بناء plan جديدة.",
        "why_en": "Because the need is findings-first critique, not generating a new plan.",
    },
    {
        "question_ar": "الخطة approved، وعاوز أعرف أوزع التنفيذ إزاي.",
        "question_en": "The plan is approved, and I need to decide how to execute it safely.",
        "skill": "Omega Conductor",
        "invoke": "$omega-conductor",
        "why_ar": "لأن المشكلة الآن orchestration وحدود الملكية وليست planning.",
        "why_en": "Because the blocker is orchestration and ownership boundaries, not planning.",
    },
    {
        "question_ar": "التنفيذ شبه خلص، وعاوز أقفل المهمة بإثبات صادق.",
        "question_en": "Implementation is nearly done, and I need an honest proof package.",
        "skill": "Omega Proof Lock",
        "invoke": "$omega-proof-gate",
        "why_ar": "لأن السؤال الآن validation وcloseout honesty.",
        "why_en": "Because the question is now validation and closeout honesty.",
    },
]

SKILL_CARDS = [
    {
        "name": "Omega Third Eye",
        "invoke": "$omega-repo-map",
        "role_ar": "Discovery layer",
        "role_en": "Discovery layer",
        "use_when": [
            "الريبو جديدة عليك.",
            "محتاج entrypoint أو blast radius قبل أول edit.",
            "عاوز تفصل facts عن assumptions قبل التخطيط.",
        ],
        "avoid_when": [
            "الـpath معروف بالفعل.",
            "المشكلة أصبحت proof أو closeout.",
            "السؤال الحقيقي عن AI runtime design.",
        ],
        "handoff": "يسلم `RepoFacts / FlowPath / ImpactMap` إلى `God Plan Mode`.",
        "source": str(Path.home() / ".codex/skills/omega-repo-map/SKILL.md"),
    },
    {
        "name": "God Plan Mode",
        "invoke": "$god-plan-mode",
        "role_ar": "Execution-ready planning",
        "role_en": "Execution-ready planning",
        "use_when": [
            "الشغل ambiguous أو risky أو multi-step.",
            "محتاج objective وconstraints وverification واضحة.",
            "عاوز خطة قابلة للتنفيذ والمراجعة بسرعة.",
        ],
        "avoid_when": [
            "المهمة trivial وواضحة جدًا.",
            "محتاج critique لخطة موجودة بالفعل، لا بناء خطة.",
            "لسه محتاج repo discovery أولًا.",
        ],
        "handoff": "يسلم الخطة إلى `God Plan Critic` للتثبيت أو الكسر قبل التنفيذ.",
        "source": str(Path.home() / ".codex/skills/god-plan-mode/SKILL.md"),
    },
    {
        "name": "God Plan Critic",
        "invoke": "$plan-critic",
        "role_ar": "Findings-first plan stress test",
        "role_en": "Findings-first plan stress test",
        "use_when": [
            "الخطة موجودة وعاوز تعرف ما الذي سيكسرها.",
            "محتاج verdict واضح: `findings-only` أو `bounded-repair` أو `replan-required`.",
            "عاوز proof gaps وdependency blind spots تطلع قبل التنفيذ.",
        ],
        "avoid_when": [
            "لا توجد plan أصلًا.",
            "المطلوب مجرد direct execution لمهمة بسيطة.",
            "المشكلة في التوزيع والتنفيذ بعد الموافقة على الخطة.",
        ],
        "handoff": "إذا verdict تسمح بالتنفيذ، يسلم الخطة المعتمدة إلى `Omega Conductor`.",
        "source": str(Path.home() / ".codex/skills/plan-critic/SKILL.md"),
    },
    {
        "name": "Omega Conductor",
        "invoke": "$omega-conductor",
        "role_ar": "Execution orchestration",
        "role_en": "Execution orchestration",
        "use_when": [
            "الخطة approved بالفعل.",
            "محتاج تقرر single-agent ولا multi-agent.",
            "محتاج ownership map وsync points وProofHandoff.",
        ],
        "avoid_when": [
            "لسه في مرحلة discovery أو planning.",
            "الـcritic حكم `replan-required`.",
            "الهدف النهائي proof أو closeout وليس orchestration.",
        ],
        "handoff": "يسلم `ProofHandoff` إلى `Omega Proof Lock` بعد نهاية التنفيذ.",
        "source": str(Path.home() / ".codex/skills/omega-conductor/SKILL.md"),
    },
    {
        "name": "Omega Proof Lock",
        "invoke": "$omega-proof-gate",
        "role_ar": "Validation and honest closeout",
        "role_en": "Validation and honest closeout",
        "use_when": [
            "التنفيذ خلص أو قرب يخلص.",
            "محتاج أصغر proof convincing package.",
            "عاوز تفصل `Ran / Not Run / Blocked / Residual Risk` بصدق.",
        ],
        "avoid_when": [
            "الـpath لسه غير معروف.",
            "لسه بتبني الخطة أو بتنتقدها.",
            "لسه بتوزع التنفيذ على agents.",
        ],
        "handoff": "يقفل المهمة ويعطي closeout honest للمستخدم أو للمرحلة النهائية.",
        "source": str(Path.home() / ".codex/skills/omega-proof-gate/SKILL.md"),
    },
]

QUICK_PROMPTS = [
    ("Omega Third Eye", "Use `$omega-repo-map` and map the real path before we edit anything."),
    ("God Plan Mode", "Use `$god-plan-mode` and give me an execution-ready plan with explicit verification."),
    ("God Plan Critic", "Use `$plan-critic` and tell me what can break in this plan before we start."),
    ("Omega Conductor", "Use `$omega-conductor` and decide whether this approved plan should stay single-agent or go multi-agent."),
    ("Omega Proof Lock", "Use `$omega-proof-gate` and give me the minimum convincing proof before closeout."),
]

COMMON_MISTAKES = [
    "تشغيل `Omega Proof Lock` بدري قبل ما الـpath أو التغيير نفسه يبقى مفهوم.",
    "تشغيل `Omega Conductor` قبل ما `God Plan Critic` يوافق على الخطة.",
    "استخدام `God Plan Critic` لبناء خطة من الصفر بدل نقد خطة موجودة.",
    "تخطي `Omega Third Eye` في ريبو جديدة ثم الدخول في planning على assumptions ضعيفة.",
    "تحويل `Omega Proof Lock` إلى success theater بدل proof honest.",
]

EXTRA_CSS = """
.cheatsheet-page .hero-grid {
  align-items: stretch;
}

.cheatsheet-page .poster-surface__score {
  display: flex;
  align-items: end;
  gap: 0.8rem;
  margin-top: 1rem;
}

.cheatsheet-page .poster-surface__score strong {
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  line-height: 0.92;
}

.cheatsheet-page .section-block {
  padding: 2rem;
  background: rgba(9, 15, 26, 0.82);
  border: 1px solid rgba(140, 166, 205, 0.16);
  border-radius: 28px;
  box-shadow: 0 22px 48px rgba(7, 10, 18, 0.24);
}

.cheatsheet-page .section-block + .section-block {
  margin-top: 1.5rem;
}

.cheatsheet-page .stack-grid,
.cheatsheet-page .ladder-grid,
.cheatsheet-page .card-grid,
.cheatsheet-page .summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.cheatsheet-page .summary-grid--single,
.cheatsheet-page .card-grid--single {
  grid-template-columns: 1fr;
}

.cheatsheet-page .stack-item,
.cheatsheet-page .ladder-card,
.cheatsheet-page .skill-card,
.cheatsheet-page .summary-card {
  padding: 1.15rem 1.2rem;
  border-radius: 22px;
  border: 1px solid rgba(140, 166, 205, 0.14);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
}

.cheatsheet-page .tag-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-bottom: 0.85rem;
}

.cheatsheet-page .step-badge {
  width: 3.2rem;
  height: 3.2rem;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--mono-font);
  font-size: 1rem;
  color: var(--ink);
  background: linear-gradient(135deg, rgba(255, 194, 117, 0.95), rgba(255, 224, 173, 0.86));
  box-shadow: 0 16px 36px rgba(255, 194, 117, 0.22);
}

.cheatsheet-page .fact-list,
.cheatsheet-page .check-list,
.cheatsheet-page .source-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.65rem;
}

.cheatsheet-page .fact-list li,
.cheatsheet-page .check-list li,
.cheatsheet-page .source-list li {
  display: grid;
  gap: 0.3rem;
  padding: 0.72rem 0.8rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(140, 166, 205, 0.12);
}

.cheatsheet-page .fact-list code,
.cheatsheet-page .source-list code,
.cheatsheet-page .code-block {
  direction: ltr;
  text-align: left;
  unicode-bidi: plaintext;
  font-family: "DejaVu Sans Mono", "Cascadia Mono", "Liberation Mono", monospace;
}

.cheatsheet-page .mini-label {
  display: inline-flex;
  margin-bottom: 0.55rem;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(214, 224, 241, 0.7);
}

.cheatsheet-page .code-block {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  padding: 0.8rem 0.9rem;
  border-radius: 18px;
  background: rgba(7, 10, 18, 0.5);
  border: 1px solid rgba(140, 166, 205, 0.14);
}

@media (max-width: 980px) {
  .cheatsheet-page .stack-grid,
  .cheatsheet-page .ladder-grid,
  .cheatsheet-page .card-grid,
  .cheatsheet-page .summary-grid {
    grid-template-columns: 1fr;
  }
}
"""


def render_list(items: list[str]) -> str:
    return "".join(f"<li>{v2.escape(item)}</li>" for item in items)


def render_source_list(items: list[tuple[str, str]]) -> str:
    return "".join(
        f"<li><strong>{v2.escape(label)}</strong><code>{v2.escape(path)}</code></li>"
        for label, path in items
    )


def render_stack_item(item: dict) -> str:
    return f"""
      <article class="stack-item">
        <div class="tag-strip">
          <span class="step-badge">{v2.escape(item["step"])}</span>
          {v2.inline_tag(item["role"], item["role"], "accent")}
          {v2.code_tag(item["invoke"])}
        </div>
        <h3>{v2.escape(item["name"])}</h3>
        {v2.bilingual_text(item["body_ar"], item["body_en"], "p", "muted-copy")}
      </article>
    """


def render_ladder_card(item: dict) -> str:
    return f"""
      <article class="ladder-card">
        <div class="tag-strip">
          {v2.inline_tag(item["skill"], item["skill"], "accent")}
          {v2.code_tag(item["invoke"])}
        </div>
        <h3>{v2.escape(item["question_ar"])}</h3>
        <p class="muted-copy" dir="ltr">{v2.escape(item["question_en"])}</p>
        <p>{v2.escape(item["why_ar"])}</p>
      </article>
    """


def render_skill_card(item: dict) -> str:
    return f"""
      <article class="skill-card">
        <div class="tag-strip">
          {v2.inline_tag(item["role_ar"], item["role_en"], "accent")}
          {v2.code_tag(item["invoke"])}
        </div>
        <h3>{v2.escape(item["name"])}</h3>
        <span class="mini-label">Use when</span>
        <ul class="check-list">{render_list(item["use_when"])}</ul>
        <span class="mini-label">Do not use when</span>
        <ul class="check-list">{render_list(item["avoid_when"])}</ul>
        <span class="mini-label">Handoff</span>
        <ul class="fact-list"><li>{v2.escape(item["handoff"])}</li></ul>
        <span class="mini-label">Source</span>
        <ul class="source-list">{render_source_list([(item["name"], item["source"])])}</ul>
      </article>
    """


def build_html() -> str:
    meta_html = "".join(
        [
            v2.metric_pill("5", "مهارات", "Skills"),
            v2.metric_pill("5", "handoffs", "Handoffs"),
            v2.metric_pill("1", "operator sheet", "Operator sheet", "accent"),
            v2.metric_pill("cheatsheet", "surface", "surface"),
        ]
    )
    topbar = v8.build_topbar("Planning stack cheatsheet", "Planning stack cheatsheet", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Omega HUD / operator cheatsheet", "Omega HUD / operator cheatsheet", "span")}</p>
              <h1>{v2.bilingual_html("دليل <span class=\"accent\">سريع</span> لتشغيل planning stack", "A <span class=\"accent\">quick</span> operator guide for the planning stack", "span")}</h1>
              {v2.bilingual_text("الملف ده معمول علشان يجاوب بسرعة: أستخدم مين إمتى؟ وإمتى ما أستخدموش؟ وإيه الـhandoff الطبيعي بين المهارات الخمس؟", "This file is built to answer fast: which skill do I use when, when should I not use it, and what is the natural handoff across the five skills?", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("operator-grade", "operator-grade", "accent")}
                {v2.inline_tag("fast lookup", "fast lookup")}
                {v2.inline_tag("stack order", "stack order")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("Golden Path", "Golden Path", "accent")}
                  {v2.code_tag("$omega-repo-map -> $god-plan-mode -> $plan-critic -> $omega-conductor -> $omega-proof-gate")}
                </div>
                <div class="poster-surface__score">
                  <strong>5</strong>
                  <span>{v2.bilingual_html("skills / one stack", "skills / one stack", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("Discovery → Planning → Critique → Orchestration → Proof", "Discovery → Planning → Critique → Orchestration → Proof", "span")}</div>
                {v2.bilingual_text("أهم قاعدة تشغيلية: كل skill لها boundary واضحة. لو شغلت مهارة بدري أو متأخر، هتلاقي stack فيها friction أو token waste أو confidence كاذبة.", "The most important operating rule: each skill has a clear boundary. If you trigger one too early or too late, the stack develops friction, token waste, or false confidence.", "p", "poster-surface__summary")}
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    stack = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Stack Order", "Stack Order", "span")}</p>
          <h2>{v2.bilingual_html("الترتيب الطبيعي للمهارات", "The natural order of the skills", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="stack-grid">
          {''.join(render_stack_item(item) for item in STACK_ORDER)}
        </div>
      </section>
    """

    ladder = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Decision Ladder", "Decision Ladder", "span")}</p>
          <h2>{v2.bilingual_html("لو في دماغك السؤال ده، استخدم المهارة دي", "If this is your question, use this skill", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="ladder-grid">
          {''.join(render_ladder_card(item) for item in DECISION_LADDER)}
        </div>
      </section>
    """

    cards = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Skill Cards", "Skill Cards", "span")}</p>
          <h2>{v2.bilingual_html("متى تستخدم كل مهارة ومتى لا", "When to use each skill and when not to", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="card-grid card-grid--single">
          {''.join(render_skill_card(item) for item in SKILL_CARDS)}
        </div>
      </section>
    """

    prompts = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Quick Prompts", "Quick Prompts", "span")}</p>
          <h2>{v2.bilingual_html("صياغات استدعاء سريعة", "Fast invocation prompts", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("prompts", "prompts", "accent")}
            </div>
            <h3>{v2.bilingual_html("أمثلة جاهزة", "Ready-made examples", "span")}</h3>
            <pre class="code-block">{v2.escape(chr(10).join(f'- {name}: {prompt}' for name, prompt in QUICK_PROMPTS))}</pre>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("common mistakes", "common mistakes")}
            </div>
            <h3>{v2.bilingual_html("أكثر الأخطاء الشائعة", "Most common mistakes", "span")}</h3>
            <ul class="check-list">{render_list(COMMON_MISTAKES)}</ul>
          </article>
        </div>
      </section>
    """

    sources = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Sources", "Sources", "span")}</p>
          <h2>{v2.bilingual_html("مصادر الـcheat sheet", "The sources behind the cheatsheet", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid summary-grid--single">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("live skill contracts", "live skill contracts", "accent")}
            </div>
            <h3>{v2.bilingual_html("العقود الحية للمهارات", "Live skill contracts", "span")}</h3>
            <ul class="source-list">{render_source_list([(item["name"], item["source"]) for item in SKILL_CARDS])}</ul>
          </article>
        </div>
      </section>
    """

    body_html = f"""
    {topbar}
    <main class="hud-frame cheatsheet-page">
      {hero}
      {stack}
      {ladder}
      {cards}
      {prompts}
      {sources}
    </main>
    """

    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-cheatsheet">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{v2.escape("Omega Planning Stack Operator Cheatsheet")} | {v2.escape("دليل تشغيل سريع للـplanning stack")}</title>
  <style>
{v7.V7_CSS}
{EXTRA_CSS}
  </style>
</head>
<body class="cheatsheet-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD / planning stack operator cheatsheet / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def main() -> int:
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(build_html(), encoding="utf-8")
    print(OUTPUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
