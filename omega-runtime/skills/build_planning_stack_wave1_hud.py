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
OUTPUT_PATH = ROOT / "output/html/omega-planning-stack-wave1-hud.html"
SKILLS_ROOT = Path.home() / ".codex/skills"

ROADMAP_MD = ROOT / "output/reports/omega-planning-stack-mvp-roadmap.md"
ROADMAP_HTML = ROOT / "output/html/omega-planning-stack-mvp-roadmap.html"

SKILL_SOURCES = {
    "omega-third-eye": SKILLS_ROOT / "omega-repo-map/SKILL.md",
    "god-plan-mode": SKILLS_ROOT / "god-plan-mode/SKILL.md",
    "god-plan-critic": SKILLS_ROOT / "plan-critic/SKILL.md",
    "omega-conductor": SKILLS_ROOT / "omega-conductor/SKILL.md",
    "omega-proof-lock": SKILLS_ROOT / "omega-proof-gate/SKILL.md",
}

DESCRIPTION_SOURCES = {
    "omega-third-eye": ROOT / "omega-runtime/skills/descriptions/omega-repo-map.skill.md",
    "god-plan-mode": ROOT / "omega-runtime/skills/descriptions/god-plan-mode.skill.md",
    "god-plan-critic": ROOT / "omega-runtime/skills/descriptions/plan-critic.skill.md",
    "omega-conductor": ROOT / "omega-runtime/skills/descriptions/omega-conductor.skill.md",
    "omega-proof-lock": ROOT / "omega-runtime/skills/descriptions/omega-proof-gate.skill.md",
}

SKILLS = [
    {
        "public": "Omega Third Eye",
        "internal": "$omega-repo-map",
        "role_ar": "يرسم أرض المشروع بسرعة: المسار المرجح، الـblast radius، والـunknowns التي يجب كشفها قبل التخطيط.",
        "role_en": "Maps the repo quickly: likely flow path, blast radius, and the unknowns that must be surfaced before planning.",
        "use_ar": "عندما يكون سؤالنا الأول: إحنا واقفين فين داخل الريبو؟ وما المسار الفعلي لهذا التغيير؟",
        "use_en": "Use when the first question is: where are we in the repo, and what is the real path for this change?",
        "avoid_ar": "لا تستخدمه لكتابة الخطة أو لتحديد proof package أو لإدارة sub-agents.",
        "avoid_en": "Do not use it to write the plan, choose the proof package, or manage sub-agents.",
        "handoff_ar": "يسلم `RepoFacts`, `FlowPath`, `ImpactMap`, `Unknowns` إلى `god-plan-mode`.",
        "handoff_en": "Hands off `RepoFacts`, `FlowPath`, `ImpactMap`, and `Unknowns` to `god-plan-mode`.",
        "prompt": 'استخدم `$omega-repo-map` وطلعلي map سريع للمسار المسؤول عن هذا الـflow، مع entrypoints والـblast radius والـunknowns.',
    },
    {
        "public": "god-plan-mode",
        "internal": "$god-plan-mode",
        "role_ar": "يبني خطة تنفيذ محكمة تقفل الهدف، الحقائق، الافتراضات، الاستراتيجية، والتحقق قبل أن نتحرك.",
        "role_en": "Builds a tight execution plan that locks objective, facts, assumptions, strategy, and verification before we move.",
        "use_ar": "عندما تكون المهمة غامضة أو عالية المخاطر أو متعددة الخطوات ونحتاج sequencing واعيًا.",
        "use_en": "Use when the task is ambiguous, risky, or multi-step and needs deliberate sequencing.",
        "avoid_ar": "لا تستخدمه إذا لم نفهم الريبو أصلًا، ولا إذا كانت الخطة موجودة بالفعل وتحتاج stress test فقط.",
        "avoid_en": "Do not use it if the repo is still unclear, or when a plan already exists and only needs a stress test.",
        "handoff_ar": "يسلم `Mission`, `Facts`, `Assumptions`, `Strategy`, `Verification`, `Risks` إلى `god-plan-critic`.",
        "handoff_en": "Hands off `Mission`, `Facts`, `Assumptions`, `Strategy`, `Verification`, and `Risks` to `god-plan-critic`.",
        "prompt": 'استخدم `$god-plan-mode` وابني خطة تنفيذ محكمة لهذه المهمة، مع Mission وFacts وPlan وVerification وRisks.',
    },
    {
        "public": "God Plan Critic",
        "internal": "$plan-critic",
        "role_ar": "يضغط على الخطة قبل التنفيذ: يلتقط hidden dependencies، gaps في التحقق، وscope drift قبل أن تتحول إلى تكلفة حقيقية.",
        "role_en": "Stresses the plan before execution: catches hidden dependencies, proof gaps, and scope drift before they become real cost.",
        "use_ar": "عندما تكون عندنا خطة حقيقية ونريد findings-first verdict: `findings-only` أو `bounded-repair` أو `replan-required`.",
        "use_en": "Use when a real plan exists and we want a findings-first verdict: `findings-only`, `bounded-repair`, or `replan-required`.",
        "avoid_ar": "لا تستخدمه بدل التخطيط من الصفر، ولا بدل proof closeout بعد التنفيذ.",
        "avoid_en": "Do not use it as a from-scratch planner or as the proof closeout layer after execution.",
        "handoff_ar": "إذا الخطة صالحة، يسلم verdict مع الإصلاحات المحدودة إلى `omega-conductor`.",
        "handoff_en": "If the plan is viable, it hands the verdict and any bounded repair to `omega-conductor`.",
        "prompt": 'استخدم `$plan-critic` وراجع الخطة findings-first، ورتب العيوب حسب severity، ثم قرر هل هي findings-only أم bounded-repair أم replan-required.',
    },
    {
        "public": "Omega Conductor",
        "internal": "$omega-conductor",
        "role_ar": "يحوّل الخطة المعتمدة إلى execution graph آمن: يختار single-agent أو multi-agent، ويثبت ownership وsync points وintegration order.",
        "role_en": "Turns the approved plan into a safe execution graph: chooses single-agent or multi-agent, then locks ownership, sync points, and integration order.",
        "use_ar": "عندما تكون الخطة approved وسؤالنا الفعلي أصبح: من يعمل ماذا، ومتى نوازي، ومتى نوقف أو ندمج؟",
        "use_en": "Use when the plan is approved and the real question becomes: who does what, when do we parallelize, and when do we stop or merge?",
        "avoid_ar": "لا تستخدمه لو verdict = `replan-required`، ولا لتوليد الخطة من جديد، ولا لاختيار proof نهائي.",
        "avoid_en": "Do not use it when verdict = `replan-required`, to regenerate the plan, or to choose final proof.",
        "handoff_ar": "يسلم `ProofHandoff` منظمًا إلى `omega-proof-lock` بعد تثبيت `WorkGraph` و`OwnershipMap`.",
        "handoff_en": "Hands a structured `ProofHandoff` to `omega-proof-lock` after locking the `WorkGraph` and `OwnershipMap`.",
        "prompt": 'استخدم `$omega-conductor` وحوّل الخطة المعتمدة إلى WorkGraph مع AgentAllocation وOwnershipMap وSyncPoints وProofHandoff.',
    },
    {
        "public": "Omega Proof Lock",
        "internal": "$omega-proof-gate",
        "role_ar": "يقفل أقل proof صادق قبل الإغلاق: يختار checks واقعية، ويفصل بوضوح بين `Ran`, `Not Run`, `Blocked`, و`Residual Risk`.",
        "role_en": "Locks the smallest honest proof before closeout: chooses realistic checks and clearly separates `Ran`, `Not Run`, `Blocked`, and `Residual Risk`.",
        "use_ar": "عندما يكون التنفيذ شبه مكتمل، ونحتاج closeout صادق مبني على evidence بدل الإحساس.",
        "use_en": "Use when implementation is almost complete and we need an honest evidence-based closeout.",
        "avoid_ar": "لا تستخدمه للـrepo mapping، ولا لكتابة الخطة، ولا لتوزيع الـsub-agents.",
        "avoid_en": "Do not use it for repo mapping, planning, or sub-agent allocation.",
        "handoff_ar": "يسلم closeout نهائي يوضح ماذا شُغّل، ماذا لم يُشغّل، وما المخاطر المتبقية.",
        "handoff_en": "Produces the final closeout describing what ran, what did not, and what risks remain.",
        "prompt": 'استخدم `$omega-proof-gate` وحدد أقل proof package مقنع لهذا التغيير، ثم افصل بين Ran وManual وNot Run وBlocked وResidual Risk.',
    },
]

WHAT_CHANGED = [
    {
        "title": "Omega Proof Lock",
        "body_ar": "حصل له light refresh فقط: public naming أوضح، boundary أوضح، وworkflow صار يفهم `ProofHandoff` من `omega-conductor` من غير أن يتحول إلى orchestration skill.",
        "body_en": "Received a light refresh only: clearer public naming, clearer boundary, and a workflow that now understands `ProofHandoff` from `omega-conductor` without turning into an orchestration skill.",
        "bullets": [
            "`CheckCatalog`, `ProofPlan`, `ExecutionLedger`, `ManualCoverage`, `ResidualRisk` ظلوا ثابتين.",
            "إضافة intake awareness لـ `ProofHandoff` بدل أي contract rewrite ثقيل.",
            "الحفاظ على الفصل بين proof selection وagent allocation.",
        ],
    },
    {
        "title": "Omega Conductor",
        "body_ar": "هذه هي المهارة الجديدة في الـwave: execution orchestration حقيقية بدل gap صامت بين التخطيط والإثبات.",
        "body_en": "This is the new skill in the wave: real execution orchestration instead of a silent gap between planning and proof.",
        "bullets": [
            "مخرج ثابت: `ExecutionReadiness`, `WorkGraph`, `AgentAllocation`, `OwnershipMap`, `SyncPoints`, `EscalationRules`, `IntegrationOrder`, `ProofHandoff`.",
            "تمنع fake parallelization وتمنع overlapping write scopes.",
            "ترفض التنفيذ مباشرة إذا verdict = `replan-required`.",
        ],
    },
    {
        "title": "Docs And Naming",
        "body_ar": "طبقة الأسماء العامة ظهرت فعليًا في الوصف وagent metadata، مع قرار واضح أن internal paths لن تتغير في هذه الـwave.",
        "body_en": "The public naming layer is now visible in descriptions and agent metadata, with a clear decision that internal paths stay unchanged in this wave.",
        "bullets": [
            "`omega-repo-map` -> `Omega Third Eye`",
            "`plan-critic` -> `God Plan Critic`",
            "`omega-proof-gate` -> `Omega Proof Lock`",
        ],
    },
]

EXTRA_CSS = """
.wave1-page .hero-grid {
  grid-template-columns: minmax(0, 1.14fr) minmax(340px, 0.86fr);
}

.wave1-page .hero-copy h1 {
  max-width: 13ch;
}

.wave1-page .section-block {
  overflow: hidden;
}

.wave1-page .cards-grid,
.wave1-page .changes-grid,
.wave1-page .sources-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.wave1-page .changes-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.wave1-page .stack-flow {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  margin-top: 24px;
}

.wave1-page .flow-card,
.wave1-page .skill-card,
.wave1-page .change-card,
.wave1-page .loop-card,
.wave1-page .source-card {
  border: 1px solid var(--line);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 28%),
    color-mix(in srgb, var(--surface-strong) 94%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 20px 48px rgba(0, 0, 0, 0.16);
}

html[data-theme="light"] .wave1-page .flow-card,
html[data-theme="light"] .wave1-page .skill-card,
html[data-theme="light"] .wave1-page .change-card,
html[data-theme="light"] .wave1-page .loop-card,
html[data-theme="light"] .wave1-page .source-card {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.35),
    0 16px 40px rgba(44, 30, 9, 0.08);
}

.wave1-page .flow-card,
.wave1-page .skill-card,
.wave1-page .change-card,
.wave1-page .loop-card,
.wave1-page .source-card {
  padding: 20px 18px;
  display: grid;
  gap: 12px;
}

.wave1-page .flow-card strong,
.wave1-page .skill-card h3,
.wave1-page .change-card h3,
.wave1-page .loop-card h3,
.wave1-page .source-card h3 {
  margin: 0;
  color: var(--ink);
}

.wave1-page .flow-card span,
.wave1-page .change-card p,
.wave1-page .loop-card p,
.wave1-page .source-card p {
  color: var(--muted);
  line-height: 1.8;
}

.wave1-page .skill-card__meta,
.wave1-page .tag-strip {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.wave1-page .mini-label {
  color: var(--dim);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.wave1-page .skill-card__block {
  display: grid;
  gap: 6px;
}

.wave1-page .skill-card__block p {
  margin: 0;
  color: var(--muted);
  line-height: 1.85;
}

.wave1-page .run-grid,
.wave1-page .loop-grid,
.wave1-page .outcome-grid {
  display: grid;
  gap: 24px;
}

.wave1-page .run-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.wave1-page .loop-grid {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.wave1-page .outcome-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.wave1-page .check-list {
  margin: 0;
  padding-inline-start: 18px;
}

.wave1-page .check-list li {
  list-style: none;
  position: relative;
  padding-inline-start: 18px;
  margin-bottom: 8px;
  color: var(--muted);
  line-height: 1.8;
}

.wave1-page .check-list li::before {
  content: "•";
  position: absolute;
  inset-inline-start: 0;
  color: var(--accent);
}

.wave1-page .code-block {
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

html[data-theme="light"] .wave1-page .code-block {
  background: rgba(242, 248, 255, 0.92);
}

@media (max-width: 1240px) {
  .wave1-page .changes-grid,
  .wave1-page .stack-flow,
  .wave1-page .loop-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1080px) {
  .wave1-page .hero-grid,
  .wave1-page .cards-grid,
  .wave1-page .changes-grid,
  .wave1-page .run-grid,
  .wave1-page .loop-grid,
  .wave1-page .sources-grid,
  .wave1-page .outcome-grid,
  .wave1-page .stack-flow {
    grid-template-columns: 1fr;
  }

  .wave1-page .hero-copy h1 {
    max-width: none;
  }
}
"""


def render_path_list(items):
    return "".join(
        f'<li><code>{v2.escape(label)}</code><span>{v2.escape(str(path))}</span></li>'
        for label, path in items
    )


def render_skill_card(skill):
    return f"""
      <article class="skill-card">
        <div class="tag-strip">
          {v2.inline_tag("اسم التشغيل", "Operator name", "accent")}
          {v2.code_tag(skill["public"])}
          {v2.inline_tag("Invoke now", "Invoke now")}
          {v2.code_tag(skill["internal"])}
        </div>
        <h3>{v2.escape(skill["public"])}</h3>
        <div class="skill-card__block">
          <span class="mini-label">Role</span>
          {v2.bilingual_text(skill["role_ar"], skill["role_en"], "p")}
        </div>
        <div class="skill-card__block">
          <span class="mini-label">Use when</span>
          {v2.bilingual_text(skill["use_ar"], skill["use_en"], "p")}
        </div>
        <div class="skill-card__block">
          <span class="mini-label">Do not use when</span>
          {v2.bilingual_text(skill["avoid_ar"], skill["avoid_en"], "p")}
        </div>
        <div class="skill-card__block">
          <span class="mini-label">Handoff</span>
          {v2.bilingual_text(skill["handoff_ar"], skill["handoff_en"], "p")}
        </div>
      </article>
    """


def render_run_card(skill):
    return f"""
      <article class="skill-card">
        <div class="tag-strip">
          {v2.inline_tag("Quick start", "Quick start", "accent")}
          {v2.code_tag(skill["internal"])}
        </div>
        <h3>{v2.escape(skill["public"])}</h3>
        {v2.bilingual_text("صياغة تشغيل عملية", "Practical trigger prompt", "p")}
        <pre class="code-block">{v2.escape(skill["prompt"])}</pre>
      </article>
    """


def render_change_card(item):
    bullets = "".join(f"<li>{v2.escape(bullet)}</li>" for bullet in item["bullets"])
    return f"""
      <article class="change-card">
        <div class="tag-strip">
          {v2.inline_tag("Wave 1 delta", "Wave 1 delta", "accent")}
        </div>
        <h3>{v2.escape(item["title"])}</h3>
        {v2.bilingual_text(item["body_ar"], item["body_en"], "p")}
        <ul class="check-list">
          {bullets}
        </ul>
      </article>
    """


def render_loop_step(title, body_ar, body_en, output_name):
    return f"""
      <article class="loop-card">
        <div class="tag-strip">
          {v2.inline_tag("Handoff", "Handoff", "accent")}
          {v2.code_tag(output_name)}
        </div>
        <h3>{v2.escape(title)}</h3>
        {v2.bilingual_text(body_ar, body_en, "p")}
      </article>
    """


def build_shell(title_en, title_ar, body_html):
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-planning-stack-wave1">
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
<body class="wave1-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA Planning Stack Wave 1 HUD / standalone artifact / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def build_page():
    meta_html = "".join(
        [
            v2.metric_pill("5", "مهارات في الستاك", "Skills in stack"),
            v2.metric_pill("1", "مهارة جديدة", "New skill", "accent"),
            v2.metric_pill("1", "proof refresh", "Proof refresh"),
            v2.metric_pill("Wave 1", "closeout جاهز", "Closeout ready", "accent"),
        ]
    )
    topbar = v8.build_topbar("Wave 1 closeout", "Wave 1 closeout", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Omega HUD / Wave 1", "Omega HUD / Wave 1", "span")}</p>
              <h1>{v2.bilingual_html("مرجع <span class=\"accent\">التشغيل الفعلي</span> لطبقة التخطيط بعد Wave 1", "The <span class=\"accent\">operator reference</span> for the planning stack after Wave 1", "span")}</h1>
              {v2.bilingual_text("هذا الـHUD هو closeout مرجعي بعد التنفيذ: يوضح ما الذي تغيّر، ترتيب المهارات الحالي، متى تستخدم كل مهارة ومتى لا تستخدمها، وكيف تنتقل المهمة من discovery إلى proof من غير overlap أو غموض.", "This HUD is the post-implementation reference closeout: it shows what changed, the current skill order, when each skill should and should not be used, and how work moves from discovery to proof without overlap or ambiguity.", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("operator guide", "operator guide", "accent")}
                {v2.inline_tag("map -> plan -> critique -> execute -> proof", "map -> plan -> critique -> execute -> proof")}
                {v2.inline_tag("public names + invoke names", "public names + invoke names")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("Wave 1 Outcome", "Wave 1 Outcome", "accent")}
                  {v2.code_tag("usable MVP")}
                </div>
                <div class="poster-surface__score">
                  <strong>5</strong>
                  <span>{v2.bilingual_html("محطات stack واضحة", "Clear stack stages", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("من المعرفة إلى الحقيقة", "From understanding to proof", "span")}</div>
                {v2.bilingual_text("الـgap بين التخطيط والإثبات تم غلقه بمهارة `omega-conductor`. وفي نفس الوقت ظل `omega-proof-lock` خفيفًا وصادقًا بدل أن يتحول إلى orchestrator متضخم.", "The gap between planning and proof is now closed by `omega-conductor`. At the same time, `omega-proof-lock` stays light and honest instead of turning into an overgrown orchestrator.", "p", "poster-surface__summary")}
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  <span class="poster-meter"><span>new</span><strong>1</strong></span>
                  <span class="poster-meter"><span>refresh</span><strong>1</strong></span>
                  <span class="poster-meter"><span>paths</span><strong>stable</strong></span>
                  <span class="poster-meter"><span>mode</span><strong>docs+core</strong></span>
                </div>
                <p class="dim-copy">Wave 1 closeout / operator guide / deterministic local build</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    executive = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Executive Summary", "Executive Summary", "span")}</p>
          <h2>{v2.bilingual_html("ما الذي تم ولماذا كان مهمًا", "What shipped and why it mattered", "span")}</h2>
          <p class="section-copy">
            <span data-lang="ar">الـWave هذه لم تعِد كتابة الستاك، بل أغلقت gap واحدة كانت واضحة: من يترجم plan approved إلى execution graph آمن ثم يسلم proof handoff منظمًا؟</span>
            <span data-lang="en">This wave did not rewrite the stack. It closed one visible gap: who translates an approved plan into a safe execution graph, then hands a structured proof package forward?</span>
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="changes-grid">
          {''.join(render_change_card(item) for item in WHAT_CHANGED)}
        </div>
      </section>
    """

    stack_order = """
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker"><span data-lang="ar">Stack Order</span><span data-lang="en">Stack Order</span></p>
          <h2><span data-lang="ar">الترتيب الحالي للمهارات الخمس</span><span data-lang="en">The current order of the five-skill stack</span></h2>
          <p class="section-copy">
            <span data-lang="ar">هذا هو الترتيب الطبيعي الآن. أي كسر لهذا التسلسل يجب أن يكون deliberate، لا عادة عشوائية.</span>
            <span data-lang="en">This is the natural order now. Any deviation from this sequence should be deliberate, not a random habit.</span>
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="stack-flow">
          <article class="flow-card">
            <strong>Omega Third Eye</strong>
            <span>Discovery / RepoFacts / FlowPath / ImpactMap</span>
          </article>
          <article class="flow-card">
            <strong>god-plan-mode</strong>
            <span>Planning / Mission / Strategy / Verification</span>
          </article>
          <article class="flow-card">
            <strong>God Plan Critic</strong>
            <span>Critique / findings-only / bounded-repair / replan-required</span>
          </article>
          <article class="flow-card">
            <strong>Omega Conductor</strong>
            <span>Execution / WorkGraph / Ownership / SyncPoints</span>
          </article>
          <article class="flow-card">
            <strong>Omega Proof Lock</strong>
            <span>Proof / CheckCatalog / ExecutionLedger / ResidualRisk</span>
          </article>
        </div>
      </section>
    """

    skill_cards = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Skill Cards", "Skill Cards", "span")}</p>
          <h2>{v2.bilingual_html("دور كل مهارة ومتى تبدأ ومتى لا تبدأ", "Each skill's role, when it starts, and when it should stay out", "span")}</h2>
          <p class="section-copy">
            <span data-lang="ar">لكل مهارة هنا اسم ذهني للاستخدام البشري، واسم invoke فعلي للاستخدام الحالي داخل النظام.</span>
            <span data-lang="en">Each skill here has a public/operator name for humans and a current invoke name for the live system.</span>
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="cards-grid">
          {''.join(render_skill_card(skill) for skill in SKILLS)}
        </div>
      </section>
    """

    how_to_run = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("How To Run", "How To Run", "span")}</p>
          <h2>{v2.bilingual_html("صياغات تشغيل عملية للستاك", "Practical trigger prompts for the stack", "span")}</h2>
          <p class="section-copy">
            <span data-lang="ar">الأمثلة التالية ليست templates جامدة، لكنها أفضل starting prompts لتشغيل كل طبقة في وقتها الصحيح.</span>
            <span data-lang="en">These examples are not rigid templates, but they are strong starting prompts for activating each layer at the right moment.</span>
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="run-grid">
          {''.join(render_run_card(skill) for skill in SKILLS)}
        </div>
      </section>
    """

    handoff_loop = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Handoff Loop", "Handoff Loop", "span")}</p>
          <h2>{v2.bilingual_html("كيف تنتقل المهمة من discovery إلى proof", "How work moves from discovery to proof", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="loop-grid">
          {render_loop_step("1. Omega Third Eye", "يحوّل الغموض إلى صورة أولية للمسار والـblast radius.", "Turns ambiguity into a first picture of the path and blast radius.", "RepoFacts / FlowPath")}
          {render_loop_step("2. god-plan-mode", "يحوّل المعرفة الأولية إلى خطة تنفيذية فيها هدف واستراتيجية وتحقق.", "Turns the initial understanding into an execution plan with objective, strategy, and verification.", "Mission / Plan / Verification")}
          {render_loop_step("3. God Plan Critic", "يضغط على الخطة ويقرر هل تمشي، تتصلح إصلاحًا محدودًا، أم تعاد من البداية.", "Stresses the plan and decides whether it can proceed, needs bounded repair, or must be replanned.", "Verdict / Repairs")}
          {render_loop_step("4. Omega Conductor", "إذا كانت الخطة صالحة، يحولها إلى work graph آمن بملكية واضحة ونقاط مزامنة.", "If the plan is viable, turns it into a safe work graph with clear ownership and sync points.", "WorkGraph / ProofHandoff")}
          {render_loop_step("5. Omega Proof Lock", "في النهاية يقفل أقل proof صادق ويكتب closeout honest بدل confidence مزيف.", "At the end it locks the smallest honest proof and writes an honest closeout instead of fake confidence.", "ExecutionLedger / ResidualRisk")}
        </div>
      </section>
    """

    outcomes = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Wave 1 Outcome", "Wave 1 Outcome", "span")}</p>
          <h2>{v2.bilingual_html("ما أصبح جاهزًا الآن وما الذي ما زال مؤجلًا", "What is ready now and what is still deferred", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="outcome-grid">
          <article class="source-card">
            <div class="tag-strip">
              {v2.inline_tag("Ready now", "Ready now", "accent")}
            </div>
            <h3>{v2.bilingual_html("جاهز الآن", "Ready now", "span")}</h3>
            <ul class="check-list">
              <li>الستاك usable كـMVP كامل: `map -> plan -> critique -> execute -> proof`.</li>
              <li>`omega-conductor` أصبح execution layer واضح بدل فجوة ضمنية.</li>
              <li>`omega-proof-lock` يفهم `ProofHandoff` ويحافظ على honesty closeout.</li>
              <li>public naming layer ظهرت في docs وagent metadata.</li>
            </ul>
          </article>
          <article class="source-card">
            <div class="tag-strip">
              {v2.inline_tag("Deferred", "Deferred")}
            </div>
            <h3>{v2.bilingual_html("مؤجل للـwaves القادمة", "Deferred for later waves", "span")}</h3>
            <ul class="check-list">
              <li>filesystem rename للمهارات الحالية.</li>
              <li>automation أو scripts إضافية لـ `omega-conductor`.</li>
              <li>eval harness ثقيل أو dashboard تشغيلية.</li>
              <li>أي توسيع خارج حدود `Core + Docs` قبل مراجعته صراحة.</li>
            </ul>
          </article>
        </div>
      </section>
    """

    sources_items = []
    for key, path in SKILL_SOURCES.items():
        sources_items.append((f"{key} skill", path))
    for key, path in DESCRIPTION_SOURCES.items():
        sources_items.append((f"{key} doc", path))
    sources_items.extend(
        [
            ("roadmap markdown", ROADMAP_MD),
            ("roadmap hud", ROADMAP_HTML),
            ("wave1 hud", OUTPUT_PATH),
        ]
    )

    sources = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Sources", "Sources", "span")}</p>
          <h2>{v2.bilingual_html("المصادر التي بُني عليها هذا الـHUD", "The sources used to build this HUD", "span")}</h2>
          <p class="section-copy">
            <span data-lang="ar">كل شيء هنا محلي فقط. لا توجد assets خارجية، ولا claims مبنية على web context.</span>
            <span data-lang="en">Everything here is local only. No external assets and no claims grounded in web context.</span>
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="sources-grid">
          <article class="source-card">
            <div class="tag-strip">
              {v2.inline_tag("Primary files", "Primary files", "accent")}
            </div>
            <h3>{v2.bilingual_html("ملفات المهارات", "Skill files", "span")}</h3>
            <ul class="fact-list">
              {render_path_list(list(SKILL_SOURCES.items()))}
            </ul>
          </article>
          <article class="source-card">
            <div class="tag-strip">
              {v2.inline_tag("Docs + references", "Docs + references")}
            </div>
            <h3>{v2.bilingual_html("الوصف والمراجع", "Descriptions and references", "span")}</h3>
            <ul class="fact-list">
              {render_path_list(list(DESCRIPTION_SOURCES.items()) + [("roadmap markdown", ROADMAP_MD), ("roadmap hud", ROADMAP_HTML)])}
            </ul>
          </article>
        </div>
      </section>
    """

    body_html = "\n".join(
        [
            topbar,
            hero,
            executive,
            stack_order,
            skill_cards,
            how_to_run,
            handoff_loop,
            outcomes,
            sources,
        ]
    )
    return build_shell("Omega Planning Stack Wave 1 HUD", "لوحة إغلاق Wave 1 لطبقة التخطيط", body_html)


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_page(), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
