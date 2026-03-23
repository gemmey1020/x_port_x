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
OUTPUT_MD = ROOT / "output/reports/omega-planning-stack-preflight-gate.md"
OUTPUT_HTML = ROOT / "output/html/omega-planning-stack-preflight-gate.html"
FIXTURE_ROOT = ROOT / "omega-runtime/skills/fixtures/omega-planning-stack-preflight"

SKILL_SOURCES = [
    ("Omega Third Eye / $omega-repo-map", Path.home() / ".codex/skills/omega-repo-map/SKILL.md"),
    ("God Plan Mode / $god-plan-mode", Path.home() / ".codex/skills/god-plan-mode/SKILL.md"),
    ("God Plan Critic / $plan-critic", Path.home() / ".codex/skills/plan-critic/SKILL.md"),
    ("Omega Conductor / $omega-conductor", Path.home() / ".codex/skills/omega-conductor/SKILL.md"),
    ("Omega Proof Lock / $omega-proof-gate", Path.home() / ".codex/skills/omega-proof-gate/SKILL.md"),
]

SUMMARY = {
    "verdict": "ready-for-first-real-repo",
    "scope_ar": "تقوية `Omega Third Eye` و`Omega Proof Lock` وإضافة rehearsal صغيرة لـ`Omega Conductor`.",
    "scope_en": "Harden `Omega Third Eye`, harden `Omega Proof Lock`, and add a small rehearsal pack for `Omega Conductor`.",
    "reason_ar": "الفجوات الثلاث من Wave 2 اتقفلت الآن عبر scan أعمق، واكتشاف checks فعلية، وfixture tracked تثبت حدود `single-agent` و`multi-agent` قبل أول real repo trial.",
    "reason_en": "The three Wave 2 gaps are now addressed through deeper scanning, real check discovery, and a tracked fixture that proves the `single-agent` and `multi-agent` boundaries before the first real repo trial.",
}

CHANGE_CARDS = [
    {
        "title": "Omega Third Eye",
        "tag": "repo scan hardening",
        "body_ar": "الـscanner اتقوّى لمشاريع الـbuilders والـreports: بقى يلتقط `output/html`, `output/reports`, `OMEGA_SKILL_CATALOG.yaml`, `build_*.py`، وself-check scripts بدل scan سطحي.",
        "body_en": "The scanner is now stronger on builder/report workspaces: it picks up `output/html`, `output/reports`, `OMEGA_SKILL_CATALOG.yaml`, `build_*.py`, and self-check scripts instead of staying shallow.",
        "bullets": [
            "Hardened `~/.codex/skills/omega-repo-map/scripts/scan_repo_map.py`.",
            "Added builder/report examples in `references/trigger-examples.md`.",
            "Added builder/report markers in `references/framework-markers.md`.",
        ],
    },
    {
        "title": "Omega Proof Lock",
        "tag": "proof discovery hardening",
        "body_ar": "اكتشاف الـchecks بقى يفهم workspaces من نوع HUD/builders، ويرجع `python-compile` و`artifact-regen` و`python-self-check` بدل `zero-checks`.",
        "body_en": "Check discovery now understands builder/HUD workspaces and returns `python-compile`, `artifact-regen`, and `python-self-check` instead of `zero-checks`.",
        "bullets": [
            "Hardened `~/.codex/skills/omega-proof-gate/scripts/discover_checks.py`.",
            "Extended `references/proof-matrix.md` with builder/report proof mode.",
            "Extended `references/trigger-examples.md` with Omega builder examples.",
        ],
    },
    {
        "title": "Omega Conductor",
        "tag": "rehearsal pack",
        "body_ar": "اتضاف له preflight rehearsal tracked بدل الاعتماد على contract-only confidence: fixture صغيرة فيها حالة `parallel-safe` وحالة `high-coupling` مع expected modes واضحة.",
        "body_en": "It now has a tracked preflight rehearsal instead of relying on contract-only confidence: a small fixture with one `parallel-safe` case and one `high-coupling` case with explicit expected modes.",
        "bullets": [
            "Added `~/.codex/skills/omega-conductor/references/preflight-rehearsal.md`.",
            "Added fixture repo under `omega-runtime/skills/fixtures/omega-planning-stack-preflight/`.",
            "Added `build_fixture_preview.py` and `scripts/run_self_check.py`.",
        ],
    },
]

VALIDATION_CARDS = [
    {
        "label": "workspace scan",
        "result": "pass",
        "body_ar": "الـworkspace الحالي بقى يتصنف `Builder/report workspace`، والـmarkers بقت تشمل planning HUD outputs والـcatalog والـbuilders.",
        "body_en": "The current workspace is now classified as `Builder/report workspace`, and the markers include planning HUD outputs, the catalog, and the builders.",
        "evidence": [
            "`scan_repo_map.py --root \"$PWD\" --format json`",
            "Frameworks: `AI integration`, `Builder/report workspace`",
            "Markers include planning HTML, planning reports, the skill catalog, and builder scripts",
        ],
    },
    {
        "label": "proof discovery",
        "result": "pass",
        "body_ar": "الـproof discovery بقت ترجع checks فعلية بدل الفراغ: compile للـbuilders، artifact regeneration، وself-check للـfixture.",
        "body_en": "Proof discovery now returns actual checks instead of an empty result: builder compile, artifact regeneration, and a fixture self-check.",
        "evidence": [
            "`python3 -m py_compile omega-runtime/skills/build_*.py`",
            "`python3 omega-runtime/skills/fixtures/omega-planning-stack-preflight/scripts/run_self_check.py`",
            "multiple `artifact-regen` candidates discovered automatically",
        ],
    },
    {
        "label": "fixture rehearsal",
        "result": "pass",
        "body_ar": "الـfixture rehearsal نفسها جاهزة واشتغلت: preview generated، وself-check رجّعت `ok=true` في الحالتين.",
        "body_en": "The fixture rehearsal itself is ready and ran successfully: the preview was generated, and the self-check returned `ok=true` for both cases.",
        "evidence": [
            "`python3 omega-runtime/skills/fixtures/omega-planning-stack-preflight/build_fixture_preview.py`",
            "`python3 omega-runtime/skills/fixtures/omega-planning-stack-preflight/scripts/run_self_check.py`",
            "parallel-safe and high-coupling cases are both present",
        ],
    },
]

REHEARSAL_CASES = [
    {
        "title": "parallel-safe",
        "expected_mode": "multi-agent",
        "body_ar": "الحالة دي مقصود بها proving إن `Omega Conductor` يعرف إمتى يوزع التنفيذ فعلًا: write scopes منفصلة بين catalog وdocs، وsync واحدة في الآخر.",
        "body_en": "This case is meant to prove that `Omega Conductor` can actually distribute execution: the write scopes are split between catalog and docs, with one final sync.",
        "reasons": [
            "source: `parallel-safe/approved-plan.md`",
            "disjoint write scopes between `catalog/public_names.yaml` and `docs/operator_runbook.md`",
            "proof handoff can combine both surfaces without a shared code seam",
        ],
    },
    {
        "title": "high-coupling",
        "expected_mode": "single-agent",
        "body_ar": "الحالة دي تمنع fake parallelization: في seam مشتركة داخل render shell، وأي توزيع concurrent هنا هيبقى خطر merge مقنّع.",
        "body_en": "This case blocks fake parallelization: there is a shared seam inside the render shell, and any concurrent split here would be a disguised merge hazard.",
        "reasons": [
            "source: `high-coupling/approved-plan.md`",
            "shared seam lives in `high-coupling/render/render_shell.py`",
            "downstream card rendering depends on that shared contract directly",
        ],
    },
]

GUARDRAILS = [
    "ابدأ أول real repo trial بمهمة ضيقة وقابلة للرجوع، لا refactor واسع.",
    "`Omega Conductor` بقى عنده rehearsal pack، لكن أول multi-agent run حي يظل observed shakedown وليس routine execution.",
    "`Omega Proof Lock` أصبح يكتشف proof candidates، لكنه ما زال مطالبًا بأصغر proof convincing package بدل تشغيل كل builders بلا داعٍ.",
]

NEXT_STEP = [
    "اختيار ريبو حقيقية صغيرة كنقطة دخول.",
    "تشغيل `Omega Third Eye` فقط لو path ما زال مجهولًا.",
    "المرور على `God Plan Mode -> God Plan Critic` قبل أي orchestration.",
    "استدعاء `Omega Conductor` فقط إذا approved plan تستحق فعلًا single-agent/multi-agent decision.",
    "إقفال المهمة بـ`Omega Proof Lock` مع closeout honest مبني على proof حقيقية.",
]

COMMANDS_RUN = [
    "python3 -m py_compile ~/.codex/skills/omega-repo-map/scripts/scan_repo_map.py ~/.codex/skills/omega-proof-gate/scripts/discover_checks.py omega-runtime/skills/fixtures/omega-planning-stack-preflight/build_fixture_preview.py omega-runtime/skills/fixtures/omega-planning-stack-preflight/scripts/run_self_check.py",
    "python3 ~/.codex/skills/omega-repo-map/scripts/scan_repo_map.py --root \"$PWD\" --format json",
    "python3 ~/.codex/skills/omega-proof-gate/scripts/discover_checks.py --root \"$PWD\" --format json",
    "python3 ~/.codex/skills/plan-critic/scripts/run_self_check.py",
    "python3 ~/.codex/skills/omega-repo-map/scripts/scan_repo_map.py --root omega-runtime/skills/fixtures/omega-planning-stack-preflight --format json",
    "python3 ~/.codex/skills/omega-proof-gate/scripts/discover_checks.py --root omega-runtime/skills/fixtures/omega-planning-stack-preflight --format json",
    "python3 omega-runtime/skills/fixtures/omega-planning-stack-preflight/build_fixture_preview.py",
    "python3 omega-runtime/skills/fixtures/omega-planning-stack-preflight/scripts/run_self_check.py",
]

EXTRA_CSS = """
.preflight-page .hero-grid {
  align-items: stretch;
}

.preflight-page .poster-surface__score {
  display: flex;
  align-items: end;
  gap: 0.85rem;
  margin-top: 1rem;
}

.preflight-page .poster-surface__score strong {
  font-size: clamp(2.4rem, 5vw, 4.25rem);
  line-height: 0.95;
}

.preflight-page .section-block {
  padding: 2rem;
  background: rgba(9, 15, 26, 0.82);
  border: 1px solid rgba(140, 166, 205, 0.16);
  border-radius: 28px;
  box-shadow: 0 22px 48px rgba(7, 10, 18, 0.24);
}

.preflight-page .section-block + .section-block {
  margin-top: 1.5rem;
}

.preflight-page .summary-grid,
.preflight-page .change-grid,
.preflight-page .validation-grid,
.preflight-page .rehearsal-grid,
.preflight-page .source-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.preflight-page .change-card,
.preflight-page .validation-card,
.preflight-page .rehearsal-card,
.preflight-page .summary-card,
.preflight-page .source-card {
  padding: 1.15rem 1.2rem;
  border-radius: 22px;
  border: 1px solid rgba(140, 166, 205, 0.14);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
}

.preflight-page .summary-card--full,
.preflight-page .source-card--full {
  grid-column: 1 / -1;
}

.preflight-page .tag-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-bottom: 0.85rem;
}

.preflight-page .fact-list,
.preflight-page .check-list,
.preflight-page .stack-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.65rem;
}

.preflight-page .fact-list li,
.preflight-page .check-list li,
.preflight-page .stack-list li {
  display: grid;
  gap: 0.3rem;
  padding: 0.72rem 0.8rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(140, 166, 205, 0.12);
}

.preflight-page .fact-list code,
.preflight-page .stack-list code,
.preflight-page .code-block {
  direction: ltr;
  text-align: left;
  unicode-bidi: plaintext;
  font-family: "DejaVu Sans Mono", "Cascadia Mono", "Liberation Mono", monospace;
}

.preflight-page .mini-label {
  display: inline-flex;
  margin-bottom: 0.55rem;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(214, 224, 241, 0.7);
}

.preflight-page .code-block {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  padding: 0.8rem 0.9rem;
  border-radius: 18px;
  background: rgba(7, 10, 18, 0.5);
  border: 1px solid rgba(140, 166, 205, 0.14);
}

.preflight-page .stack-list {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.preflight-page .source-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.65rem;
}

.preflight-page .source-list li {
  display: grid;
  gap: 0.35rem;
  padding: 0.8rem 0.9rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(140, 166, 205, 0.12);
}

.preflight-page .source-list code {
  direction: ltr;
  text-align: left;
  unicode-bidi: plaintext;
}

@media (max-width: 980px) {
  .preflight-page .summary-grid,
  .preflight-page .change-grid,
  .preflight-page .validation-grid,
  .preflight-page .rehearsal-grid,
  .preflight-page .source-grid,
  .preflight-page .stack-list {
    grid-template-columns: 1fr;
  }
}
"""


def result_tag(result: str) -> str:
    tone = "accent" if result in {"pass", "ready-for-first-real-repo", "multi-agent", "single-agent"} else ""
    return v2.inline_tag(result, result, tone)


def render_list(items: list[str]) -> str:
    return "".join(f"<li>{v2.escape(item)}</li>" for item in items)


def render_source_list(items: list[tuple[str, Path]]) -> str:
    return "".join(
        f"<li><strong>{v2.escape(label)}</strong><code>{v2.escape(str(path))}</code></li>"
        for label, path in items
    )


def render_change_card(item: dict) -> str:
    return f"""
      <article class="change-card">
        <div class="tag-strip">
          {v2.inline_tag(item["tag"], item["tag"], "accent")}
          {v2.code_tag(item["title"])}
        </div>
        <h3>{v2.escape(item["title"])}</h3>
        {v2.bilingual_text(item["body_ar"], item["body_en"], "p", "muted-copy")}
        <ul class="check-list">{render_list(item["bullets"])}</ul>
      </article>
    """


def render_validation_card(item: dict) -> str:
    return f"""
      <article class="validation-card">
        <div class="tag-strip">
          {result_tag(item["result"])}
          {v2.code_tag(item["label"])}
        </div>
        <h3>{v2.escape(item["label"])}</h3>
        {v2.bilingual_text(item["body_ar"], item["body_en"], "p", "muted-copy")}
        <span class="mini-label">Evidence</span>
        <ul class="fact-list">{render_list(item["evidence"])}</ul>
      </article>
    """


def render_rehearsal_card(item: dict) -> str:
    return f"""
      <article class="rehearsal-card">
        <div class="tag-strip">
          {result_tag(item["expected_mode"])}
          {v2.code_tag(item["title"])}
        </div>
        <h3>{v2.escape(item["title"])}</h3>
        {v2.bilingual_text(item["body_ar"], item["body_en"], "p", "muted-copy")}
        <span class="mini-label">Why this mode is correct</span>
        <ul class="fact-list">{render_list(item["reasons"])}</ul>
      </article>
    """


def build_html() -> str:
    meta_html = "".join(
        [
            v2.metric_pill("3", "فجوات اتقفلت", "Gaps closed"),
            v2.metric_pill("2", "حالات rehearsal", "Rehearsal cases"),
            v2.metric_pill("3", "validation passes", "Validation passes", "accent"),
            v2.metric_pill(SUMMARY["verdict"], "Gate verdict", "Gate verdict"),
        ]
    )
    topbar = v8.build_topbar("Preflight gate", "Preflight gate", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Omega HUD / preflight gate", "Omega HUD / preflight gate", "span")}</p>
              <h1>{v2.bilingual_html("تقرير <span class=\"accent\">Preflight Gate</span> قبل أول real repo", "The <span class=\"accent\">Preflight Gate</span> before the first real repo", "span")}</h1>
              {v2.bilingual_text(SUMMARY["reason_ar"], SUMMARY["reason_en"], "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("operator-ready report", "operator-ready report", "accent")}
                {v2.inline_tag("harden + rehearse", "harden + rehearse")}
                {v2.inline_tag(SUMMARY["verdict"], SUMMARY["verdict"])}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("Preflight verdict", "Preflight verdict", "accent")}
                  {v2.code_tag("preflight")}
                </div>
                <div class="poster-surface__score">
                  <strong>3/3</strong>
                  <span>{v2.bilingual_html("gaps اتقفلت", "gaps closed", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html(f"`{SUMMARY['verdict']}`", f"`{SUMMARY['verdict']}`", "span")}</div>
                {v2.bilingual_text(SUMMARY["scope_ar"], SUMMARY["scope_en"], "p", "poster-surface__summary")}
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
          <h2>{v2.bilingual_html("إيه اللي اتعمل وليه النتيجة مطمّنة", "What changed and why the result is reassuring", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("verdict", "verdict", "accent")}
            </div>
            <h3>{v2.bilingual_html("حكم الـgate", "Gate verdict", "span")}</h3>
            <p>{v2.escape(SUMMARY["reason_ar"])}</p>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("scope", "scope")}
            </div>
            <h3>{v2.bilingual_html("نطاق الإصلاح", "Fix scope", "span")}</h3>
            <p>{v2.escape(SUMMARY["scope_ar"])}</p>
          </article>
          <article class="summary-card summary-card--full">
            <div class="tag-strip">
              {v2.inline_tag("decision", "decision", "accent")}
            </div>
            <h3>{v2.bilingual_html("قرار الدخول على الريبو الجديدة", "Decision before the first new repo", "span")}</h3>
            <ul class="check-list">{render_list(NEXT_STEP)}</ul>
          </article>
        </div>
      </section>
    """

    changes = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("What Changed", "What Changed", "span")}</p>
          <h2>{v2.bilingual_html("التغييرات الفعلية في المهارات الثلاث", "The concrete changes across the three skills", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="change-grid">
          {''.join(render_change_card(item) for item in CHANGE_CARDS)}
        </div>
      </section>
    """

    validation = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Validation", "Validation", "span")}</p>
          <h2>{v2.bilingual_html("التحقق الذي قفل الـpreflight", "The validation that closed the preflight", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="validation-grid">
          {''.join(render_validation_card(item) for item in VALIDATION_CARDS)}
        </div>
      </section>
    """

    rehearsal = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Conductor Rehearsal", "Conductor Rehearsal", "span")}</p>
          <h2>{v2.bilingual_html("الحالتان اللتان يثبتان حدود التنفيذ", "The two cases that prove execution boundaries", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="rehearsal-grid">
          {''.join(render_rehearsal_card(item) for item in REHEARSAL_CASES)}
        </div>
      </section>
    """

    guardrails = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Guardrails", "Guardrails", "span")}</p>
          <h2>{v2.bilingual_html("ما الذي يجب الحفاظ عليه قبل أول trial", "What must stay true before the first trial", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="summary-grid">
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("residual guardrails", "residual guardrails", "accent")}
            </div>
            <h3>{v2.bilingual_html("حدود لازالت مهمة", "Still-important limits", "span")}</h3>
            <ul class="check-list">{render_list(GUARDRAILS)}</ul>
          </article>
          <article class="summary-card">
            <div class="tag-strip">
              {v2.inline_tag("commands", "commands")}
            </div>
            <h3>{v2.bilingual_html("الأوامر التي بُني عليها الحكم", "Commands behind the verdict", "span")}</h3>
            <pre class="code-block">{v2.escape(chr(10).join(COMMANDS_RUN))}</pre>
          </article>
        </div>
      </section>
    """

    sources = f"""
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Sources", "Sources", "span")}</p>
          <h2>{v2.bilingual_html("المراجع والملفات الأساسية", "The key files and sources", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="source-grid">
          <article class="source-card">
            <div class="tag-strip">
              {v2.inline_tag("canonical report", "canonical report", "accent")}
            </div>
            <h3>{v2.bilingual_html("مصدر التقرير النصي", "Canonical markdown source", "span")}</h3>
            <ul class="source-list">
              <li><strong>Preflight gate report</strong><code>{v2.escape(str(OUTPUT_MD))}</code></li>
              <li><strong>Fixture root</strong><code>{v2.escape(str(FIXTURE_ROOT))}</code></li>
            </ul>
          </article>
          <article class="source-card source-card--full">
            <div class="tag-strip">
              {v2.inline_tag("skill sources", "skill sources")}
            </div>
            <h3>{v2.bilingual_html("مصادر المهارات", "Skill source files", "span")}</h3>
            <ul class="source-list">{render_source_list(SKILL_SOURCES)}</ul>
          </article>
        </div>
      </section>
    """

    body_html = f"""
    {topbar}
    <main class="hud-frame preflight-page">
      {hero}
      {summary}
      {changes}
      {validation}
      {rehearsal}
      {guardrails}
      {sources}
    </main>
    """

    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-preflight">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{v2.escape("Omega Planning Stack Preflight Gate")} | {v2.escape("تقرير Preflight Gate")}</title>
  <style>
{v7.V7_CSS}
{EXTRA_CSS}
  </style>
</head>
<body class="preflight-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD / preflight gate / local only / no external assets</div>
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
