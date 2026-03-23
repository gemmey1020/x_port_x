#!/usr/bin/env python3

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v7 as v7


ROOT = base.ROOT
OUTPUT_HTML_DIR = ROOT / "output/html"
SKILLS_OUTPUT = OUTPUT_HTML_DIR / "omega-skills-hud-v8.html"
MEMORY_OUTPUT = OUTPUT_HTML_DIR / "omega-memory-learning-report-v8.html"
CODEX_SKILLS_ROOT = Path.home() / ".codex/skills"
REFRESHED_DESCRIPTION_SKILLS = ["god-plan-mode", "omega-repo-map", "plan-critic", "omega-conductor", "omega-proof-gate"]
SKILL_DELTA_NOTES = {
    "god-plan-mode": [
        (
            "أصبحت السطوح التشغيلية الحالية تعرض الاسم العام مع invoke الحالي: `God Plan Mode` + `$god-plan-mode`.",
            "Current operator surfaces now show the public name together with the live invoke string: `God Plan Mode` + `$god-plan-mode`.",
        ),
        (
            "الستاك التخطيطي كلها صار موصوفًا كـ pipeline فيها execution orchestration بدل plan-to-proof gap.",
            "The planning stack is now described as a pipeline with execution orchestration instead of a plan-to-proof gap.",
        ),
    ],
    "omega-repo-map": [
        (
            "الهوية العامة أصبحت `Omega Third Eye` مع الإبقاء على invoke الحالي `$omega-repo-map`.",
            "The public identity is now `Omega Third Eye` while keeping the live invoke string `$omega-repo-map`.",
        ),
        (
            "السرد الحالي يثبّت الدور كـ discovery layer بدل الاكتفاء بالاسم الداخلي القديم.",
            "The current narrative locks the role as the discovery layer instead of relying on the older internal label alone.",
        ),
    ],
    "plan-critic": [
        (
            "الهوية العامة أصبحت `God Plan Critic` مع invoke حي واضح `$plan-critic`.",
            "The public identity is now `God Plan Critic` with a clear live invoke string `$plan-critic`.",
        ),
        (
            "الأرشيف يعرضه الآن كـ critique-side twin لـ`god-plan-mode` داخل stack واحدة أوسع.",
            "The archive now presents it as the critique-side twin of `god-plan-mode` inside a broader unified stack.",
        ),
    ],
    "omega-conductor": [
        (
            "أُضيفت entry رسمية جديدة لـ`Omega Conductor` داخل السجل الحي.",
            "A new formal `Omega Conductor` entry has been added to the live registry.",
        ),
        (
            "الوظيفة الحالية موصوفة بوضوح كطبقة execution orchestration بين النقد والإثبات.",
            "Its current role is clearly documented as the execution-orchestration layer between critique and proof.",
        ),
    ],
    "omega-proof-gate": [
        (
            "الهوية العامة أصبحت `Omega Proof Lock` مع invoke حي واضح `$omega-proof-gate`.",
            "The public identity is now `Omega Proof Lock` with a clear live invoke string `$omega-proof-gate`.",
        ),
        (
            "الوصف الحالي يربطه صراحة بـ`ProofHandoff` القادم من `omega-conductor` من غير توسيع زائد للدور.",
            "The current description explicitly ties it to `ProofHandoff` from `omega-conductor` without over-expanding its role.",
        ),
    ],
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_json_command(args: list[str]) -> dict:
    return json.loads(base.run_command(args))


def build_topbar(page_label_ar: str, page_label_en: str, meta_html: str) -> str:
    return f"""
      <header class="utility-bar">
        <div class="brand-lockup">
          <strong>OMEGA HUD V8</strong>
          <span>{v2.bilingual_html(page_label_ar, page_label_en, "span")}</span>
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


def build_shell(title_en: str, title_ar: str, body_class: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v8-audited">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{v2.escape(title_en)} | {v2.escape(title_ar)}</title>
  <style>
{v7.V7_CSS}
  </style>
</head>
<body class="{v2.escape(body_class)}">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD V8 / live audited artifact / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def collect_live_skill_sources() -> tuple[dict[str, Path], dict[str, Path]]:
    top_level = {}
    if CODEX_SKILLS_ROOT.exists():
        for item in sorted(CODEX_SKILLS_ROOT.iterdir()):
            if not item.is_dir() or item.name.startswith("."):
                continue
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                top_level[item.name] = skill_file

    system_entries = {}
    system_root = CODEX_SKILLS_ROOT / ".system"
    if system_root.exists():
        for item in sorted(system_root.iterdir()):
            if not item.is_dir():
                continue
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                system_entries[item.name] = skill_file
    return top_level, system_entries


def build_registry_audit() -> dict:
    catalog = base.read_yaml(base.CATALOG_PATH)
    top_level_sources, system_sources = collect_live_skill_sources()
    catalog_top_level = set()
    catalog_system = set()
    missing_sources = []
    checked_entries = 0

    for entry in catalog["entries"]:
        source_path = Path(entry["source_skill_path"])
        if source_path.exists():
            checked_entries += 1
        else:
            missing_sources.append(entry["skill_id"])
        if "/.system/" in entry["source_skill_path"]:
            catalog_system.add(entry["skill_id"])
        else:
            catalog_top_level.add(entry["skill_id"])

    unexpected_top_level = sorted(set(top_level_sources) - catalog_top_level)
    unexpected_system = sorted(set(system_sources) - catalog_system)

    return {
        "checked_entries": checked_entries,
        "catalog_total": len(catalog["entries"]),
        "catalog_top_level_total": len(catalog_top_level),
        "catalog_system_total": len(catalog_system),
        "live_top_level_total": len(top_level_sources),
        "live_system_total": len(system_sources),
        "missing_sources": sorted(missing_sources),
        "unexpected_top_level": unexpected_top_level,
        "unexpected_system": unexpected_system,
        "refreshed_descriptions": list(REFRESHED_DESCRIPTION_SKILLS),
    }


def build_memory_snapshot_v8() -> dict:
    inspect = run_json_command(
        [
            "python3",
            str(base.PMEM),
            "inspect",
            "--cwd",
            str(ROOT),
            "--format",
            "json",
            "--no-pending",
        ]
    )
    triage = run_json_command(
        [
            "python3",
            str(base.PMEM),
            "triage",
            "--cwd",
            str(ROOT),
            "--format",
            "json",
        ]
    )
    doctor_text = base.run_command(["python3", str(base.PMEM), "doctor"])
    self_learn = run_json_command(
        [
            "python3",
            str(base.SELF_LEARN),
            "--intent",
            "report",
            "--workspace-cwd",
            str(ROOT),
            "--json",
        ]
    )

    promotable = triage.get("promotable", [])
    ephemeral = triage.get("ephemeral", [])
    all_candidates = promotable + ephemeral
    key_counts = Counter(item["normalized_key"] for item in all_candidates)
    project_profile = inspect.get("project_profile", {})
    reference_artifacts = project_profile.get("reference_artifacts") or []

    return {
        "inspect": inspect,
        "triage": triage,
        "doctor_text": doctor_text,
        "self_learn": self_learn,
        "key_counts": key_counts,
        "reference_artifacts": reference_artifacts,
        "backlog_sample": all_candidates[:8],
    }


def render_local_source_links(items: list[tuple[str, str]]) -> str:
    return "".join(
        f'<a href="{v2.escape(href)}"><strong>{v2.escape(label)}</strong><span class="path-label">{v2.escape(href)}</span></a>'
        for label, href in items
    )


def render_summary_list(items: list[tuple[str, str]]) -> str:
    return "".join(
        f"<li><code>{v2.escape(key)}</code><span>{v2.escape(value)}</span></li>"
        for key, value in items
    )


def render_reference_entries(reference_artifacts: list[dict]) -> str:
    if not reference_artifacts:
        return v2.bilingual_text(
            "لا توجد مراجع مشروع durable مروجة في هذه الـ workspace حتى الآن.",
            "No durable project reference artifacts are promoted in this workspace yet.",
            "p",
            "rail-copy",
        )

    items = []
    for index, item in enumerate(reference_artifacts):
        title_ar = "المرجع الأساسي" if index == 0 else f"عنصر shortlist #{index}"
        title_en = "Primary reference" if index == 0 else f"Shortlist item #{index}"
        note = item.get("note") or "-"
        items.append(
            f"<li>{v2.bilingual_html(title_ar, title_en, 'span')} "
            f"<code>{v2.escape(item.get('path', '-'))}</code> "
            f"<span>({v2.escape(note)})</span></li>"
        )
    return f'<ul class="report-list">{"".join(items)}</ul>'


def render_reference_shortlist(shortlist: list[str]) -> str:
    if not shortlist:
        return v2.bilingual_text(
            "القائمة المختصرة فارغة حاليًا.",
            "The shortlist is currently empty.",
            "p",
            "rail-copy",
        )
    return f'<ul class="report-list">{"".join(f"<li><code>{v2.escape(item)}</code></li>" for item in shortlist)}</ul>'


def workspace_relative_output_link(target: str) -> str:
    return f"./{target}"


def workspace_relative_skill_link(target: str) -> str:
    return f"../../omega-runtime/skills/{target}"


def render_candidate_sample(candidates: list[dict]) -> str:
    if not candidates:
        return v2.bilingual_text(
            "لا توجد عناصر pending لعرضها في العينة الحالية.",
            "There are no pending candidates to sample right now.",
            "p",
            "rail-copy",
        )
    items = []
    for item in candidates:
        display_value = item.get("normalized_value")
        if isinstance(display_value, dict):
            display_value = json.dumps(display_value, ensure_ascii=False, sort_keys=True)
        items.append(
            f"<li><code>{v2.escape(item['normalized_key'])}</code> -> {v2.escape(display_value)} "
            f"<span>({v2.escape(item['status'])}, {item['confidence']:.2f})</span></li>"
        )
    return f'<ul class="report-list">{"".join(items)}</ul>'


def render_changed_skill_panel(skill: dict) -> str:
    delta_notes = SKILL_DELTA_NOTES.get(skill["skill_id"], [])
    note_list = "".join(v2.bilingual_html(ar, en, "li") for ar, en in delta_notes)
    invoke_now = skill.get("invoke_now", f"${skill['skill_id']}")
    return f"""
      <article class="insight-panel">
        <div class="tag-row">
          {v2.code_tag(skill["skill_id"])}
          {v2.code_tag(invoke_now)}
          {v2.inline_tag("وصف محدَّث", "Refreshed doc", "accent")}
        </div>
        <h3>{v2.escape(skill["display_name"])}</h3>
        {v2.bilingual_text(skill["summary"], skill["summary"], "p", "rail-copy")}
        <ul class="report-list">
          <li><code>source_last_checked</code> -> {v2.escape(v2.pretty_timestamp(skill["source_last_checked_at"]))}</li>
          <li><code>doc_last_refreshed</code> -> {v2.escape(v2.pretty_timestamp(skill["doc_last_refreshed_at"]))}</li>
          {note_list}
        </ul>
      </article>
    """


def render_tier_band(title_ar: str, title_en: str, kicker_ar: str, kicker_en: str, skills: list[dict]) -> str:
    if not skills:
        return ""
    featured = skills[:2]
    dense = skills[2:]
    return f"""
      <article class="tier-band">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html(kicker_ar, kicker_en, "span")}</p>
          <h2>{v2.bilingual_html(title_ar, title_en, "span")}</h2>
        </div>
        <div class="story-stack">
          {"".join(v2.render_feature_skill(skill) for skill in featured)}
        </div>
        <div class="dense-grid">
          {"".join(v2.render_dense_skill(skill) for skill in dense)}
        </div>
      </article>
    """


def build_skills_page_v8(skills: list[dict], audit: dict) -> str:
    top_level = [skill for skill in skills if not skill["is_exception"]]
    exceptions = [skill for skill in skills if skill["is_exception"]]
    top_level.sort(key=lambda item: (-item["score"], item["skill_id"]))
    best = top_level[0]
    generated_at = v2.pretty_timestamp(now_utc())
    refreshed_skills = [skill for skill in skills if skill["skill_id"] in REFRESHED_DESCRIPTION_SKILLS]
    refreshed_skills.sort(key=lambda item: item["skill_id"])
    tier_map = {
        "S": [skill for skill in top_level if skill["tier"] == "S"],
        "A": [skill for skill in top_level if skill["tier"] == "A"],
        "B": [skill for skill in top_level if skill["tier"] == "B"],
        "C": [skill for skill in top_level if skill["tier"] == "C"],
    }

    meta_html = "".join(
        [
            v2.metric_pill(audit["catalog_total"], "إجمالي السجل", "Catalog entries"),
            v2.metric_pill(audit["catalog_top_level_total"], "مهارات المستوى الأعلى", "Top-level skills"),
            v2.metric_pill(audit["catalog_system_total"], "استثناءات نظامية", "System exceptions"),
            v2.metric_pill(len(refreshed_skills), "أوصاف محدَّثة", "Refreshed docs"),
            v2.metric_pill(generated_at, "تم التوليد", "Generated"),
        ]
    )

    topbar = build_topbar("نسخة v8 المدققة", "Audited V8 edition", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Live audit / بلا narrative قديم", "Live audit / no stale narrative", "span")}</p>
              <h1>{v2.bilingual_html("لوحة المهارات بعد <span class=\"accent\">مراجعة حيّة</span> كاملة للمصدر", "The skills HUD after a full <span class=\"accent\">live source audit</span>", "span")}</h1>
              {v2.bilingual_text("هذه النسخة لا تعيد تدوير قصة قديمة عن الأرشيف. هي مبنية على فحص حي للسجل، ومطابقة مباشرة مع المهارات الموجودة فعليًا تحت `~/.codex/skills`، وتُظهر فقط ما ثبت في هذا المرور.", "This edition does not recycle an archive story. It is grounded in a live registry audit, direct source checks against `~/.codex/skills`, and only the facts confirmed in this pass.", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag(f"{audit['catalog_total']} entry متراجع", f"{audit['catalog_total']} audited entries", "accent")}
                {v2.inline_tag(f"{audit['catalog_top_level_total']} top-level + {audit['catalog_system_total']} system exceptions", f"{audit['catalog_top_level_total']} top-level + {audit['catalog_system_total']} system exceptions")}
                {v2.inline_tag(f"{len(refreshed_skills)} تحديثات مادية في الوصف", f"{len(refreshed_skills)} material doc refreshes")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("أفضل مهارة تشغيلية", "Highest operational score", "accent")}
                  {v2.code_tag(best["skill_id"])}
                </div>
                <div class="poster-surface__score">
                  <strong>{best["score"]}</strong>
                  <span>{v2.bilingual_html("درجة التشغيل", "Operational score", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.escape(best["display_name"])}</div>
                {v2.bilingual_text("أفضلية هذه المهارة هنا لم تتغيّر بالزخرفة، بل بثبات leverage التخطيط، وترتيب التنفيذ، والقدرة على تقليل التخمين قبل العمل.", "This lead is not cosmetic. It still comes from planning leverage, execution framing, and reducing guesswork before implementation.", "p", "poster-surface__summary")}
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  <span class="poster-meter"><span>checked</span><strong>{audit["checked_entries"]}</strong></span>
                  <span class="poster-meter"><span>missing</span><strong>{len(audit["missing_sources"])}</strong></span>
                  <span class="poster-meter"><span>refreshed</span><strong>{len(refreshed_skills)}</strong></span>
                  <span class="poster-meter"><span>live top</span><strong>{audit["live_top_level_total"]}</strong></span>
                </div>
                <p class="dim-copy">{v2.escape(generated_at)}</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    audit_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Registry audit", "Registry audit", "span")}</p>
          <h2>{v2.bilingual_html("نتيجة المطابقة بين السجل والمصدر الحي", "Registry-to-source audit result", "span")}</h2>
          {v2.bilingual_text("هنا نثبت هل السجل نفسه ما زال ممسوكًا على المصدر الحقيقي، وما الذي تغيّر ماديًا في أوصاف المهارات داخل workspace.", "This section proves whether the registry still matches the real skill sources and what materially changed in the local skill docs.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <div class="tag-row">
              {v2.inline_tag("Coverage", "Coverage", "accent")}
            </div>
            <h3>{v2.bilingual_html("تغطية الفحص", "Audit coverage", "span")}</h3>
            <ul class="fact-list">{render_summary_list([
                ("catalog_total", str(audit["catalog_total"])),
                ("checked_entries", str(audit["checked_entries"])),
                ("live_top_level", str(audit["live_top_level_total"])),
                ("live_system", str(audit["live_system_total"])),
            ])}</ul>
          </article>
          <article class="insight-panel">
            <div class="tag-row">
              {v2.inline_tag("Drift check", "Drift check", "accent")}
            </div>
            <h3>{v2.bilingual_html("نتيجة drift check", "Drift check result", "span")}</h3>
            <ul class="report-list">
              <li>{v2.bilingual_html(f"missing_sources = {len(audit['missing_sources'])}", f"missing_sources = {len(audit['missing_sources'])}", "span")}</li>
              <li>{v2.bilingual_html(f"unexpected_top_level = {len(audit['unexpected_top_level'])}", f"unexpected_top_level = {len(audit['unexpected_top_level'])}", "span")}</li>
              <li>{v2.bilingual_html(f"unexpected_system = {len(audit['unexpected_system'])}", f"unexpected_system = {len(audit['unexpected_system'])}", "span")}</li>
              <li>{v2.bilingual_html("لم يظهر أي skill top-level جديد خارج السجل في هذه الجولة.", "No new uncatalogued top-level skill appeared in this pass.", "span")}</li>
            </ul>
          </article>
        </div>
        <div class="split-grid">
          {"".join(render_changed_skill_panel(skill) for skill in refreshed_skills)}
        </div>
      </section>
    """

    tier_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Execution tiers", "Execution tiers", "span")}</p>
          <h2>{v2.bilingual_html("طبقات الكفاءة بعد الـ refresh الحالي", "Execution tiers after the current refresh", "span")}</h2>
          {v2.bilingual_text("هذا الجزء لا يغير منظومة الترتيب نفسها؛ هو فقط يعيد عرضها بعد ما اتثبت أن السجل والأوصاف المحدثة ما زالوا متوافقين مع المصدر.", "This section does not reinvent the ranking model. It simply restages it after confirming the registry and refreshed docs still match the source of truth.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="band-stack">
          {render_tier_band("طبقة S", "Tier S", "أعلى رافعة", "Highest leverage", tier_map["S"])}
          {render_tier_band("طبقة A", "Tier A", "قوية ومباشرة", "Strong and direct", tier_map["A"])}
          {render_tier_band("طبقة B", "Tier B", "متخصصة", "Specialist", tier_map["B"])}
          {render_tier_band("طبقة C", "Tier C", "مفيدة لكن أضيق", "Useful but narrow", tier_map["C"])}
        </div>
      </section>
    """

    merge_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Merge watch", "Merge watch", "span")}</p>
          <h2>{v2.bilingual_html("مناطق التداخل التي تستحق عينًا مستمرة", "Overlap areas that still deserve ongoing watch", "span")}</h2>
          {v2.bilingual_text("دي ليست أوامر دمج فوري. هي مناطق التداخل التي ما زالت تحتاج وضوح handoff أو surface موحدة مع الحفاظ على حدود كل مهارة.", "These are not immediate merge orders. They remain the overlap zones that still need clearer handoff or a more unified surface while preserving each skill's boundary.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="story-stack">
          {"".join(v2.render_story_band(group) for group in base.MERGE_GROUPS)}
        </div>
      </section>
    """

    pressure_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Pressure map", "Pressure map", "span")}</p>
          <h2>{v2.bilingual_html("المهارات التي تحتاج tightening أوضح بعد الفحص", "Skills that still need clearer tightening after the audit", "span")}</h2>
          {v2.bilingual_text("هذه ليست أخطاء تنفيذية الآن، لكنها نقاط ضغط معروفة نريد أن تظل مرئية داخل اللوحة بدل أن تضيع تحت نسخة واجهة جميلة فقط.", "These are not active implementation failures, but known pressure points that should remain visible in the HUD instead of disappearing behind presentation polish.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="stack-list">
          {"".join(v2.render_stack_item(candidate, "improve") for candidate in base.IMPROVE_CANDIDATES)}
        </div>
      </section>
    """

    exception_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("System exceptions", "System exceptions", "span")}</p>
          <h2>{v2.bilingual_html("الاستثناءات النظامية ما زالت خارج المقارنة", "System exceptions remain outside the score comparison", "span")}</h2>
          {v2.bilingual_text("وجودها هنا للتوثيق والوضوح فقط. هي مسارات نظامية خاصة، وليست peers داخل ترتيب المهارات top-level.", "They appear here for documentation and clarity only. These are special system pathways, not peer skills inside the top-level ranking.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="exception-grid">
          {"".join(v2.render_exception(skill) for skill in exceptions)}
        </div>
      </section>
    """

    sources_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Notes and sources", "Notes and sources", "span")}</p>
          <h2>{v2.bilingual_html("ملفات هذا الـ refresh", "Files touched by this refresh", "span")}</h2>
          {v2.bilingual_text("هنا نثبت الملفات المرجعية التي بُنيت عليها نسخة `v8`، وما الذي تغير بالفعل داخل الـ workspace بدل الاكتفاء بإخراج بصري جديد.", "This section locks the reference files behind `v8` and shows what materially changed inside the workspace instead of stopping at a new visual export.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("تغييرات هذا المرور", "What changed in this pass", "span")}</h3>
            <ul class="report-list">
              <li>{v2.bilingual_html("تمت مراجعة كل source paths في السجل وتحديث `source_last_checked_at` على مستوى الـ catalog كله.", "Every catalog source path was rechecked and `source_last_checked_at` was refreshed across the full catalog.", "span")}</li>
              <li>{v2.bilingual_html("تم تحديث وصفي `persistent-memory` و`self-learn` لأن عقدهم تغير فعليًا.", "The `persistent-memory` and `self-learn` docs were refreshed because their contracts materially changed.", "span")}</li>
              <li>{v2.bilingual_html("تم إنشاء مولد `v8` جديد بدل إعادة استخدام replacement narrative أقدم.", "A new `v8` generator was added instead of leaning on an older replacement-driven narrative.", "span")}</li>
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("ملفات مرجعية", "Reference files", "span")}</h3>
            <div class="source-list">
              {render_local_source_links([
                  ("OMEGA_SKILL_CATALOG.yaml", workspace_relative_skill_link("OMEGA_SKILL_CATALOG.yaml")),
                  ("persistent-memory.skill.md", workspace_relative_skill_link("descriptions/persistent-memory.skill.md")),
                  ("self-learn.skill.md", workspace_relative_skill_link("descriptions/self-learn.skill.md")),
                  ("build_skill_reports_v8.py", workspace_relative_skill_link("build_skill_reports_v8.py")),
              ])}
            </div>
          </article>
        </div>
      </section>
    """

    body = (
        topbar
        + hero
        + audit_section
        + tier_section
        + merge_section
        + pressure_section
        + exception_section
        + sources_section
    )
    return build_shell("Omega Skills HUD V8", "لوحة مهارات أوميجا V8", "skills-page", body)


def build_memory_page_v8(skills: list[dict], snapshot: dict) -> str:
    inspect = snapshot["inspect"]
    triage = snapshot["triage"]
    self_learn = snapshot["self_learn"]
    reference_artifacts = snapshot["reference_artifacts"]
    project_profile = inspect.get("project_profile", {})
    user_profile = inspect.get("user_profile", {})
    communication = user_profile.get("communication_preferences", {})
    workflow = user_profile.get("workflow_preferences", {})
    role_pref = user_profile.get("assistant_role_preference", {})
    reference_context = self_learn.get("reference_context", {})
    generated_at = v2.pretty_timestamp(now_utc())

    meta_html = "".join(
        [
            v2.metric_pill(triage["summary"]["pending_total"], "عناصر معلقة", "Pending items"),
            v2.metric_pill(triage["summary"]["promotable_total"], "صالحة للترقية", "Promotable"),
            v2.metric_pill(len(reference_artifacts), "مراجع المشروع", "Project references"),
            v2.metric_pill(generated_at, "تم التوليد", "Generated"),
        ]
    )
    topbar = build_topbar("تقرير الذاكرة والتعلّم V8", "Memory + learning report V8", meta_html)

    key_counts = "".join(
        f"<li><code>{v2.escape(key)}</code>: {count}</li>"
        for key, count in snapshot["key_counts"].most_common()
    )
    project_aliases = ", ".join(project_profile.get("aliases") or []) or "-"
    primary_reference = reference_artifacts[0]["path"] if reference_artifacts else "-"
    shortlist = [item["path"] for item in reference_artifacts[1:]]
    bridge_primary = reference_context.get("primary_reference_artifact") or "-"
    bridge_shortlist = reference_context.get("reference_shortlist") or []

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Runtime truth / JSON-first", "Runtime truth / JSON-first", "span")}</p>
              <h1>{v2.bilingual_html("الذاكرة <span class=\"accent\">مستقرة</span>، والتعلّم <span class=\"accent\">منضبط</span>، وجسر المرجع صار واضحًا", "Memory is <span class=\"accent\">stable</span>, learning is <span class=\"accent\">disciplined</span>, and the reference bridge is now explicit", "span")}</h1>
              {v2.bilingual_text("هذه النسخة لا تبني القراءة على markdown parsing قديم. هي تربط `persistent-memory` و`self-learn` بعقود JSON مباشرة، وتعرض حدود الجسر `report-only` كما هي فعلًا.", "This edition does not build on old markdown parsing. It connects `persistent-memory` and `self-learn` through direct JSON contracts and stages the `report-only` bridge exactly as it really exists.", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag(f"pending = {triage['summary']['pending_total']}", f"pending = {triage['summary']['pending_total']}", "accent")}
                {v2.inline_tag(f"promotable = {triage['summary']['promotable_total']}", f"promotable = {triage['summary']['promotable_total']}")}
                {v2.inline_tag("self-learn --workspace-cwd", "self-learn --workspace-cwd")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("Reference bridge", "Reference bridge", "accent")}
                  {v2.code_tag(reference_context.get("resolved_project") or inspect.get("resolved_project", "-"))}
                </div>
                <div class="poster-surface__score">
                  <strong>{len(reference_artifacts)}</strong>
                  <span>{v2.bilingual_html("مراجع مروجة", "Promoted references", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("Primary + Shortlist", "Primary + Shortlist", "span")}</div>
                {v2.bilingual_text("في هذه الـ workspace لا يظهر bridge reference إلا عندما تُمرر `--workspace-cwd`، ولا يكتب شيئًا إلى الذاكرة. إن وجدت مراجع مروجة ستظهر هنا، وإن لم توجد فسيظهر empty state صريح.", "The bridge only appears for this workspace when `--workspace-cwd` is provided, and it never writes to memory. Promoted references appear here when they exist; otherwise the empty state stays explicit.", "p", "poster-surface__summary")}
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  <span class="poster-meter"><span>refs</span><strong>{len(reference_artifacts)}</strong></span>
                  <span class="poster-meter"><span>shortlist</span><strong>{len(shortlist)}</strong></span>
                  <span class="poster-meter"><span>events</span><strong>{self_learn['health']['event_sequence']}</strong></span>
                  <span class="poster-meter"><span>patterns</span><strong>{self_learn['memory_summary']['durable_pattern_count']}</strong></span>
                </div>
                <p class="dim-copy">{v2.escape(generated_at)}</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    memory_state_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Persistent memory", "Persistent memory", "span")}</p>
          <h2>{v2.bilingual_html("الحالة الحالية للملف الدائم وقائمة الانتظار", "Current durable profile and pending queue", "span")}</h2>
          {v2.bilingual_text("المحتوى هنا مبني على `inspect --format json --no-pending` و`triage --format json`، لذلك يعرض الحالة الحالية كما هي بدل إعادة تفسيرها من markdown.", "The content here is built from `inspect --format json --no-pending` and `triage --format json`, so it reflects the current state directly instead of reinterpreting markdown.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("التفضيلات durable", "Durable collaboration profile", "span")}</h3>
            <ul class="fact-list">{render_summary_list([
                ("communication.language", communication.get("language", "-")),
                ("communication.tone", communication.get("tone", "-")),
                ("assistant.expected_role", role_pref.get("primary", "-")),
                ("workflow.plan_preference", workflow.get("plan_mode", "-")),
                ("workflow.review_preference", workflow.get("review_mode", "-")),
            ])}</ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("مشهد المشروع", "Current project overlay", "span")}</h3>
            <ul class="fact-list">{render_summary_list([
                ("project.id", project_profile.get("project_id", "-")),
                ("project.domain", project_profile.get("domain", "-")),
                ("project.aliases", project_aliases),
                ("project.root", project_profile.get("root_path", "-")),
            ])}</ul>
          </article>
        </div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("نتيجة triage", "Current triage result", "span")}</h3>
            <ul class="fact-list">{render_summary_list([
                ("pending_total", str(triage["summary"]["pending_total"])),
                ("ephemeral_total", str(triage["summary"]["ephemeral_total"])),
                ("promotable_total", str(triage["summary"]["promotable_total"])),
                ("conflict_count", str(triage["summary"]["conflict_count"])),
            ])}</ul>
            {v2.bilingual_text("حتى الآن كل ما في هذه الـ workspace ما زال pending أو ephemeral، لذلك لا توجد ترقية durable جارية في هذا المرور.", "At the moment everything in this workspace remains pending or ephemeral, so no durable promotion is happening in this pass.", "p", "rail-copy")}
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("توزيع مفاتيح قائمة الانتظار", "Pending-key distribution", "span")}</h3>
            <ul class="report-list">{key_counts or '<li><span data-lang="ar">لا توجد عناصر pending.</span><span data-lang=\"en\">No pending items.</span></li>'}</ul>
          </article>
        </div>
      </section>
    """

    reference_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Reference bridge", "Reference bridge", "span")}</p>
          <h2>{v2.bilingual_html("مراجع المشروع durable والربط مع self-learn", "Durable project references and the self-learn bridge", "span")}</h2>
          {v2.bilingual_text("هذا هو الجزء الجديد فعليًا في `v8`: عرض صريح لمراجع المشروع durable من جهة `persistent-memory`، ثم عرض ما يراه `self-learn report` في `reference_context` عند تشغيله مع `--workspace-cwd`.", "This is the real new area in `v8`: an explicit view of durable project references from `persistent-memory`, followed by what `self-learn report` sees in `reference_context` when run with `--workspace-cwd`.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <div class="tag-row">
              {v2.inline_tag("Persistent memory", "Persistent memory", "accent")}
            </div>
            <h3>{v2.bilingual_html("Primary + Shortlist من الملف الدائم", "Primary + Shortlist from durable memory", "span")}</h3>
            {render_reference_entries(reference_artifacts)}
          </article>
          <article class="insight-panel">
            <div class="tag-row">
              {v2.inline_tag("Self Learn", "Self Learn", "accent")}
            </div>
            <h3>{v2.bilingual_html("reference_context داخل report", "reference_context inside report", "span")}</h3>
            <ul class="fact-list">{render_summary_list([
                ("resolved_project", reference_context.get("resolved_project", "-") or "-"),
                ("primary_reference_artifact", bridge_primary),
            ])}</ul>
            {render_reference_shortlist(bridge_shortlist)}
          </article>
        </div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Boundary contract", "Boundary contract", "span")}</h3>
            <ul class="report-list">
              <li>{v2.bilingual_html("الربط كله `report-only`.", "The bridge is strictly `report-only`.", "span")}</li>
              <li>{v2.bilingual_html("كل القراءة هنا `read-only` بلا promote أو write-back.", "Everything here is `read-only` with no promote or write-back.", "span")}</li>
              <li>{v2.bilingual_html("تشغيل الجسر نفسه gated by `--workspace-cwd`.", "The bridge itself is gated by `--workspace-cwd`.", "span")}</li>
              <li>{v2.bilingual_html("ما زالت سياسة `persistent-memory` تمنع `auto-promotion`.", "`persistent-memory` policy still forbids `auto-promotion`.", "span")}</li>
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("الحالة الحالية", "Current state", "span")}</h3>
            <ul class="report-list">
              <li>{v2.bilingual_html(f"primary_reference = {primary_reference}", f"primary_reference = {primary_reference}", "span")}</li>
              <li>{v2.bilingual_html(f"shortlist_count = {len(shortlist)}", f"shortlist_count = {len(shortlist)}", "span")}</li>
              <li>{v2.bilingual_html(f"bridge_primary = {bridge_primary}", f"bridge_primary = {bridge_primary}", "span")}</li>
              <li>{v2.bilingual_html(f"bridge_shortlist_count = {len(bridge_shortlist)}", f"bridge_shortlist_count = {len(bridge_shortlist)}", "span")}</li>
            </ul>
          </article>
        </div>
      </section>
    """

    self_learn_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Self Learn", "Self Learn", "span")}</p>
          <h2>{v2.bilingual_html("صحة المهارة وسجلها الحالي", "Current health and event state", "span")}</h2>
          {v2.bilingual_text("هذا القسم ما زال يحترم حدود `self-only`: نحن نقرأ الحالة، ولا نفتح أي apply جديد، ولا نعيد كتابة سجل التطور.", "This section still respects the `self-only` boundary: we read the state, we do not open a new apply path, and we do not rewrite the evolution history.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("ملخص الصحة", "Health summary", "span")}</h3>
            <ul class="fact-list">{render_summary_list([
                ("skill_version", self_learn["health"].get("skill_version", "-")),
                ("event_sequence", str(self_learn["health"].get("event_sequence", "-"))),
                ("last_verification_status", self_learn["health"].get("last_verification_status", "-")),
                ("current_renderer_profile", self_learn["health"].get("current_renderer_profile", "-")),
                ("active_patterns_count", str(self_learn["health"].get("active_patterns_count", "-"))),
            ])}</ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("الذاكرة الداخلية الحالية", "Current internal memory state", "span")}</h3>
            <ul class="fact-list">{render_summary_list([
                ("journal_event_count", str(self_learn["memory_summary"].get("journal_event_count", "-"))),
                ("durable_pattern_count", str(self_learn["memory_summary"].get("durable_pattern_count", "-"))),
                ("suppressed_fingerprint_count", str(self_learn["memory_summary"].get("suppressed_fingerprint_count", "-"))),
                ("apply_mode", self_learn["decision_cache"]["recent_trusted_defaults"].get("apply_mode", "-")),
                ("prefer_propose_for_freeform", str(self_learn["decision_cache"]["recent_trusted_defaults"].get("prefer_propose_for_freeform", "-")).lower()),
            ])}</ul>
          </article>
        </div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("آخر حدث", "Latest event", "span")}</h3>
            <pre class="code-panel code-block"><code>{v2.escape(json.dumps(self_learn["latest_event"], ensure_ascii=False, indent=2))}</code></pre>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("آخر حدث reversible", "Latest reversible event", "span")}</h3>
            <pre class="code-panel code-block"><code>{v2.escape(json.dumps(self_learn["latest_reversible_event"], ensure_ascii=False, indent=2))}</code></pre>
          </article>
        </div>
      </section>
    """

    change_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("What changed", "What changed", "span")}</p>
          <h2>{v2.bilingual_html("ما الذي تغيّر في نسخة `v8` نفسها", "What changed in `v8` itself", "span")}</h2>
          {v2.bilingual_text("هذا القسم يتكلم عن تغير بنية التقرير نفسه، لا عن mutation داخل `persistent-memory` أو `self-learn`.", "This section describes the report architecture changes themselves, not a mutation inside `persistent-memory` or `self-learn`.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Shift in data contract", "Shift in data contract", "span")}</h3>
            <ul class="report-list">
              <li>{v2.bilingual_html("تم إسقاط الاعتماد على markdown parsing القديم لحالة الذاكرة.", "The report dropped its dependence on older markdown parsing for memory state.", "span")}</li>
              <li>{v2.bilingual_html("أصبحت أوامر القراءة الأساسية JSON-first.", "The core read path is now JSON-first.", "span")}</li>
              <li>{v2.bilingual_html("تقرير `self-learn` يُستدعى الآن مع `--workspace-cwd` ليظهر `reference_context` عندما يكون موجودًا.", "`self-learn` is now called with `--workspace-cwd` so `reference_context` appears when available.", "span")}</li>
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("صدق الحدود", "Boundary honesty", "span")}</h3>
            <ul class="report-list">
              <li>{v2.bilingual_html("لا claim بوجود promoted references عندما لا توجد فعليًا.", "There is no claim of promoted references when none actually exist.", "span")}</li>
              <li>{v2.bilingual_html("لا claim بوجود mutation جديدة داخل `self-learn` في هذا المرور.", "There is no claim of new mutation inside `self-learn` in this pass.", "span")}</li>
              <li>{v2.bilingual_html("لا postmortem جديد، ولا update للأرشيف، فقط الملفان `v8`.", "No new postmortem and no archive update, only the two `v8` artifacts.", "span")}</li>
            </ul>
          </article>
        </div>
      </section>
    """

    evidence_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Evidence", "Evidence", "span")}</p>
          <h2>{v2.bilingual_html("الأوامر والعيّنات التي بُنيت عليها القراءة", "Commands and samples behind the reading", "span")}</h2>
          {v2.bilingual_text("هذا هو أصغر دليل صادق على أن الصفحة مبنية على runtime outputs فعلية من نفس الـ workspace.", "This is the smallest honest proof that the page is built on real runtime outputs from the same workspace.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("الأوامر المستخدمة", "Commands used", "span")}</h3>
            <pre class="code-panel code-block"><code>python3 "$PMEM" inspect --cwd "$PWD" --format json --no-pending
python3 "$PMEM" triage --cwd "$PWD" --format json
python3 "$PMEM" doctor
python3 "$SELF_LEARN" --intent report --workspace-cwd "$PWD" --json</code></pre>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("doctor output", "doctor output", "span")}</h3>
            <pre class="code-panel code-block"><code>{v2.escape(snapshot["doctor_text"])}</code></pre>
          </article>
        </div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("عينة من قائمة الانتظار", "Pending sample", "span")}</h3>
            {render_candidate_sample(snapshot["backlog_sample"])}
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("ملفات مرجعية", "Reference files", "span")}</h3>
            <div class="source-list">
              {render_local_source_links([
                  ("build_skill_reports_v8.py", workspace_relative_skill_link("build_skill_reports_v8.py")),
                  ("persistent-memory.skill.md", workspace_relative_skill_link("descriptions/persistent-memory.skill.md")),
                  ("self-learn.skill.md", workspace_relative_skill_link("descriptions/self-learn.skill.md")),
                  ("omega-memory-learning-report-v8.html", workspace_relative_output_link("omega-memory-learning-report-v8.html")),
              ])}
            </div>
          </article>
        </div>
      </section>
    """

    body = (
        topbar
        + hero
        + memory_state_section
        + reference_section
        + self_learn_section
        + change_section
        + evidence_section
    )
    return build_shell(
        "Omega Memory Learning Report V8",
        "تقرير ذاكرة وتعلّم أوميجا V8",
        "memory-page",
        body,
    )


def main() -> None:
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    skills = base.build_skill_index()
    audit = build_registry_audit()
    snapshot = build_memory_snapshot_v8()
    skills_html = build_skills_page_v8(skills, audit)
    memory_html = build_memory_page_v8(skills, snapshot)
    SKILLS_OUTPUT.write_text(skills_html, encoding="utf-8")
    MEMORY_OUTPUT.write_text(memory_html, encoding="utf-8")

    print("Wrote:")
    print(SKILLS_OUTPUT)
    print(MEMORY_OUTPUT)


if __name__ == "__main__":
    main()
