#!/usr/bin/env python3

import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v5 as v5


ROOT = base.ROOT
OUTPUT_HTML = ROOT / "output/html/omega-ui-skills-boundary-hud.html"


def build_topbar(meta_html: str) -> str:
    return f"""
      <header class="utility-bar">
        <div class="brand-lockup">
          <strong>OMEGA HUD</strong>
          <span>{v2.bilingual_html("ملف حدود منظومة UI", "UI Boundary Artifact", "span")}</span>
        </div>
        <div class="metric-strip">
          {meta_html}
        </div>
        <div class="control-cluster">
          {v2.state_readout("lang-state")}
          {v2.control_button("lang-toggle", "تبديل اللغة", "Switch Lang")}
          {v2.state_readout("theme-state")}
          {v2.control_button("theme-toggle", "تبديل الثيم", "Switch Theme")}
        </div>
      </header>
    """


def render_governance_item(item: dict) -> str:
    return f"""
      <article class="stack-item">
        <div>
          <span class="tier-token">GOV</span>
        </div>
        <div>
          <div class="tag-row">
            {v2.code_tag(item["skill_id"])}
            {v2.inline_tag("حوكمة", "Governance", "accent")}
          </div>
          <h3>{v2.escape(item["skill_id"])}</h3>
          {v2.bilingual_text(item["job"]["ar"], item["job"]["en"], "p", "rail-copy")}
          {v2.bilingual_text(item["why"]["ar"], item["why"]["en"], "p", "dim-copy")}
        </div>
      </article>
    """


def render_handoff_step(index: int, step: dict) -> str:
    return f"""
      <article class="insight-panel">
        <div class="tag-row">
          {v2.inline_tag(f"الخطوة {index}", f"Step {index}", "accent")}
          {"".join(v2.code_tag(skill_id) for skill_id in step["skills"])}
        </div>
        <h3>{v2.bilingual_html(step["title"]["ar"], step["title"]["en"], "span")}</h3>
        {v2.bilingual_text(step["detail"]["ar"], step["detail"]["en"], "p", "rail-copy")}
      </article>
    """


def render_contract_ledger(item: dict) -> str:
    inputs = "".join(
        v2.bilingual_html(value["ar"], value["en"], "li")
        for value in item["inputs"]
    )
    outputs = "".join(
        v2.bilingual_html(value["ar"], value["en"], "li")
        for value in item["outputs"]
    )
    failures = "".join(
        v2.bilingual_html(value["ar"], value["en"], "li")
        for value in item["failure_modes"]
    )
    protected = "".join(f"<li><code>{v2.escape(value)}</code></li>" for value in item["protected_elements"])
    handoff = "".join(f"<li><code>{v2.escape(value)}</code></li>" for value in item["handoff_to"])
    overlap = "".join(f"<li><code>{v2.escape(value)}</code></li>" for value in item["overlap_with"])
    return f"""
      <article class="insight-panel">
        <div class="tag-row">
          {v2.code_tag(item["skill_id"])}
          {v2.inline_tag(item["layer"]["ar"], item["layer"]["en"], "accent")}
        </div>
        <h3>{v2.escape(item["display_name"])}</h3>
        {v2.bilingual_text(item["primary_job"]["ar"], item["primary_job"]["en"], "p", "rail-copy")}
        {v2.bilingual_text("أول اختيار عندما: " + item["first_choice_when"]["ar"], "First choice when: " + item["first_choice_when"]["en"], "p", "dim-copy")}
        {v2.bilingual_text("لا تستخدمه عندما: " + item["do_not_use_when"]["ar"], "Do not use when: " + item["do_not_use_when"]["en"], "p", "dim-copy")}
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("المدخلات", "Inputs", "span")}</h3>
            <ul class="report-list">{inputs}</ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("المخرجات", "Outputs", "span")}</h3>
            <ul class="report-list">{outputs}</ul>
          </article>
        </div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("ما يجب حمايته", "Protected elements", "span")}</h3>
            <ul class="fact-list">{protected}</ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("حالات الفشل الشائعة", "Common failure modes", "span")}</h3>
            <ul class="report-list">{failures}</ul>
          </article>
        </div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("handoff_to", "handoff_to", "span")}</h3>
            <ul class="fact-list">{handoff}</ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("overlap_with", "overlap_with", "span")}</h3>
            <ul class="fact-list">{overlap}</ul>
          </article>
        </div>
      </article>
    """


def build_body() -> str:
    payload = base.build_ui_skill_guide_payload()
    generated_at = base.pretty_timestamp(
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    meta_html = "".join(
        [
            v2.metric_pill(len(payload["governance_overlay"]), "طبقة الحوكمة", "Governance overlay"),
            v2.metric_pill(len(payload["comparison_contract"]), "عقود UI", "UI contracts"),
            v2.metric_pill(len(payload["hud_contract"]["route_examples"]), "مسارات القرار", "Decision routes"),
            v2.metric_pill(generated_at, "تم التوليد", "Generated"),
        ]
    )

    topbar = build_topbar(meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Artifact واحد يحتوي كل الناتج", "One artifact containing the whole output", "span")}</p>
              <h1>{v2.bilingual_html("ملف <span class=\"accent\">Omega HUD</span> جامع لحدود منظومة UI", "A single <span class=\"accent\">Omega HUD</span> file for the UI skill boundaries", "span")}</h1>
              {v2.bilingual_text(payload["summary"]["ar"], payload["summary"]["en"], "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("Governance ليست UI peers", "Governance is not a UI peer layer", "accent")}
                {v2.inline_tag("source-of-truth واحد", "Single source of truth")}
                {v2.inline_tag("HUD + guide + contract", "HUD + guide + contract")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("الملف الناتج", "Output artifact", "accent")}
                  {v2.code_tag("omega-ui-skills-boundary-hud.html")}
                </div>
                <div class="poster-surface__score">
                  <strong>{len(payload["comparison_contract"])}</strong>
                  <span>{v2.bilingual_html("عقود UI", "UI contracts", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("كل ما تم بناؤه في ملف HTML واحد", "Everything implemented in one HTML file", "span")}</div>
                {v2.bilingual_text("الصفحة دي تجمع governance overlay، taxonomy، comparison contract الكامل، handoff order، route scenarios، والـartifacts المرجعية في سطح واحد.", "This page gathers the governance overlay, taxonomy, full comparison contract, handoff order, route scenarios, and canonical artifacts into a single surface.", "p", "poster-surface__summary")}
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  <span class="poster-meter"><span>overlay</span><strong>{len(payload["governance_overlay"])}</strong></span>
                  <span class="poster-meter"><span>contracts</span><strong>{len(payload["comparison_contract"])}</strong></span>
                  <span class="poster-meter"><span>routes</span><strong>{len(payload["hud_contract"]["route_examples"])}</strong></span>
                  <span class="poster-meter"><span>sources</span><strong>{len(payload["sources"])}</strong></span>
                </div>
                <p class="dim-copy">{v2.escape(generated_at)}</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    governance = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Governance overlay", "Governance overlay", "span")}</p>
          <h2>{v2.bilingual_html("طبقة الحوكمة فوق العنقود وليست داخله", "The governance layer sits above the cluster, not inside it", "span")}</h2>
          {v2.bilingual_text("الطبقة دي لا تُعرض كمهارات UI peers. دورها أن تغيّر الخطة أو التوثيق أو proof package عندما يلزم، ثم تترك مسار UI يكمل بوضوح.", "This layer is not presented as peer UI skills. Its role is to change the plan, documentation, or proof package when needed, then let the UI path continue clearly.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="stack-list">
          {"".join(render_governance_item(item) for item in payload["governance_overlay"])}
        </div>
      </section>
    """

    authority = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Authority + routing", "Authority + routing", "span")}</p>
          <h2>{v2.bilingual_html("قواعد السلطة وترتيب الـhandoff", "Authority rules and handoff order", "span")}</h2>
          {v2.bilingual_text(payload["hud_contract"]["authority_note"]["ar"], payload["hud_contract"]["authority_note"]["en"], "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {"".join(render_handoff_step(index, step) for index, step in enumerate(payload["hud_contract"]["handoff_order"], start=1))}
        </div>
        <div class="tag-row">
          {v2.inline_tag(payload["hud_contract"]["boundary_note"]["ar"], payload["hud_contract"]["boundary_note"]["en"], "accent")}
        </div>
      </section>
    """

    core_split = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Core split", "Core split", "span")}</p>
          <h2>{v2.bilingual_html("الفرق المركزي: المنسّق مقابل المهارة الذوقية السريعة", "The core split: orchestrator versus fast visual doctrine", "span")}</h2>
          {v2.bilingual_text("هذه هي النقطة التي كانت تسبب overlap: `omega_ui_product_brain` ينسّق ويحمي، بينما `frontend-skill` ينفذ pass ذوقي سريع عندما تكون الظروف مناسبة.", "`omega_ui_product_brain` coordinates and protects, while `frontend-skill` executes a fast taste-led pass when the conditions fit.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="story-stack">
          {v2.render_ui_contract_story(payload["comparison_contract"][0])}
          {v2.render_ui_contract_story(next(item for item in payload["comparison_contract"] if item["skill_id"] == "frontend-skill"))}
        </div>
      </section>
    """

    specialists = [
        item
        for item in payload["comparison_contract"]
        if item["skill_id"] not in {"omega_ui_product_brain", "frontend-skill"}
    ]
    specialist_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Specialist pack", "Specialist pack", "span")}</p>
          <h2>{v2.bilingual_html("المهارات التابعة التي تعمل تحت الحواجز الصحيحة", "The specialist skills operating under the right guardrails", "span")}</h2>
          {v2.bilingual_text("المهارات دي ليست interchangeable. كل واحدة تعالج محورًا محددًا: source، flow، taste، system، أو implementation.", "These skills are not interchangeable. Each one handles a distinct axis: source, flow, taste, system, or implementation.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="stack-list">
          {"".join(v2.render_ui_contract_stack(item) for item in specialists)}
        </div>
      </section>
    """

    routes = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Decision routes", "Decision routes", "span")}</p>
          <h2>{v2.bilingual_html("6 مسارات قرار جاهزة للاستعمال", "Six ready-to-use decision routes", "span")}</h2>
          {v2.bilingual_text("القسم ده يحوّل المقارنة إلى routing عملي: تبدأ بمين؟ والمسار يكمل إزاي؟ ومتى لا تستخدم `frontend-skill` كقائد؟", "This section turns the comparison into practical routing: who starts, how the path continues, and when `frontend-skill` must not lead.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {"".join(v2.render_ui_route_panel(route) for route in payload["hud_contract"]["route_examples"])}
        </div>
      </section>
    """

    ledger = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Full contract ledger", "Full contract ledger", "span")}</p>
          <h2>{v2.bilingual_html("العقد الكامل لكل skill في HTML واحد", "The full contract for every skill in one HTML file", "span")}</h2>
          {v2.bilingual_text("هنا كل ما في الـJSON والـguide متحوّل لسطح HUD قابل للقراءة المباشرة.", "Everything from the JSON contract and markdown guide is rendered here into a directly readable HUD surface.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="ledger-grid">
          {"".join(render_contract_ledger(item) for item in payload["comparison_contract"])}
        </div>
      </section>
    """

    artifacts = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Canonical artifacts", "Canonical artifacts", "span")}</p>
          <h2>{v2.bilingual_html("الملفات المرجعية التي خرجت من التنفيذ", "Canonical files produced by the implementation", "span")}</h2>
          {v2.bilingual_text("هذا الملف هو surface جامع. المرجع النصي والـcontract الخام ما زالا موجودين بجانبه كـsource-of-truth قابل لإعادة الاستهلاك.", "This file is the unified surface. The markdown guide and raw contract still exist beside it as reusable sources of truth.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Artifact paths", "Artifact paths", "span")}</h3>
            <ul class="fact-list">
              {v2.render_fact_list([
                  ("html_hud", str(OUTPUT_HTML.relative_to(ROOT))),
                  ("guide_markdown", payload["artifact_paths"]["guide_markdown"]),
                  ("contract_json", payload["artifact_paths"]["contract_json"]),
              ])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Official sources reviewed", "Official sources reviewed", "span")}</h3>
            <div class="source-list">
              {v2.render_custom_source_links(payload["sources"])}
            </div>
          </article>
        </div>
      </section>
    """

    return topbar + hero + governance + authority + core_split + specialist_section + routes + ledger + artifacts


def build_shell(body_html: str) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-ui-boundary-hud">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>Omega UI Boundary HUD | ملف حدود مهارات UI</title>
  <style>
{v5.V5_CSS}
  </style>
</head>
<body class="skills-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD / ui-boundary artifact / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def main():
    base.write_ui_skill_contract_artifacts(base.build_ui_skill_guide_payload())
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(build_shell(build_body()), encoding="utf-8")
    print("Wrote:")
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
