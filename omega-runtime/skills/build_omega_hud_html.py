#!/usr/bin/env python3

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v8 as v8


ROOT = base.ROOT
OUTPUT_PATH = ROOT / "output/html/omega-hud-html.html"
SAMPLE_PATH = ROOT / "output/html/omega-hud-html-sample.html"

CODEX_ROOT = Path.home() / ".codex"
PERSISTENT_MEMORY_ROOT = CODEX_ROOT / "skills" / "persistent-memory"
SELF_LEARN_ROOT = CODEX_ROOT / "skills" / "self-learn"

MEMORY_CLI = PERSISTENT_MEMORY_ROOT / "scripts/memory_cli.py"
MIGRATION_HELPER = PERSISTENT_MEMORY_ROOT / "scripts/migrate_sqlite_first.py"
PERSISTENT_MEMORY_SKILL = PERSISTENT_MEMORY_ROOT / "SKILL.md"
SELF_LEARN_RUNNER = SELF_LEARN_ROOT / "scripts/run_self_learn.py"
SELF_LEARN_SKILL = SELF_LEARN_ROOT / "SKILL.md"


def run_json(script_path: Path, *args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)


def collect_runtime_payload() -> dict:
    doctor = run_json(MEMORY_CLI, "doctor", "--cwd", str(ROOT), "--json")
    inspect_payload = run_json(MEMORY_CLI, "inspect", "--cwd", str(ROOT), "--format", "json")
    triage_payload = run_json(MEMORY_CLI, "triage", "--cwd", str(ROOT), "--format", "json")
    self_learn_report = run_json(
        SELF_LEARN_RUNNER,
        "--intent",
        "report",
        "--workspace-cwd",
        str(ROOT),
        "--json",
    )
    migration_summary = run_json(MIGRATION_HELPER)

    db_metrics: dict[str, int] = {}
    connection = sqlite3.connect(doctor["state_db"])
    try:
        for label, query in (
            ("global_profile_rows", "SELECT COUNT(*) FROM global_profile_state"),
            ("project_profile_rows", "SELECT COUNT(*) FROM project_profile_state"),
            ("reference_artifact_rows", "SELECT COUNT(*) FROM project_reference_artifacts"),
            ("candidate_rows", "SELECT COUNT(*) FROM candidate_items"),
            ("pending_candidate_rows", "SELECT COUNT(*) FROM candidate_items WHERE status = 'pending'"),
            ("snapshot_event_rows", "SELECT COUNT(*) FROM mutation_snapshot_events"),
        ):
            db_metrics[label] = int(connection.execute(query).fetchone()[0])
    finally:
        connection.close()

    return {
        "doctor": doctor,
        "inspect": inspect_payload,
        "triage": triage_payload,
        "self_learn_report": self_learn_report,
        "migration_summary": migration_summary,
        "db_metrics": db_metrics,
    }


def build_topbar(meta_html: str) -> str:
    return v8.build_topbar("ملف معمارية الميموري", "Memory Architecture Artifact", meta_html)


def report_list(items: list[tuple[str, str]]) -> str:
    return (
        '<ul class="report-list">'
        + "".join(v2.bilingual_html(ar, en, "li") for ar, en in items)
        + "</ul>"
    )


def fact_list(items: list[tuple[str, str]]) -> str:
    return (
        '<ul class="fact-list">'
        + "".join(f"<li><code>{escape(label)}</code><span>{escape(value)}</span></li>" for label, value in items)
        + "</ul>"
    )


def bilingual_fact_list(items: list[tuple[tuple[str, str], str]]) -> str:
    return (
        '<ul class="fact-list">'
        + "".join(
            (
                "<li>"
                f"<span>{v2.bilingual_html(ar, en, 'span')}</span>"
                f"<span>{escape(value)}</span>"
                "</li>"
            )
            for (ar, en), value in items
        )
        + "</ul>"
    )


def source_list(items: list[tuple[str, str]]) -> str:
    return (
        '<ul class="fact-list">'
        + "".join(f"<li><code>{escape(label)}</code><span>{escape(path)}</span></li>" for label, path in items)
        + "</ul>"
    )


def insight_panel(title_ar: str, title_en: str, body_html: str, tags: str = "") -> str:
    return f"""
      <article class="insight-panel">
        {f'<div class="tag-row">{tags}</div>' if tags else ""}
        <h3>{v2.bilingual_html(title_ar, title_en, "span")}</h3>
        {body_html}
      </article>
    """


def meter(value: str | int, ar: str, en: str) -> str:
    rendered_value = escape(str(value))
    return (
        '<span class="poster-meter">'
        f"{v2.bilingual_html(ar, en, 'span')}"
        f"<strong>{rendered_value}</strong>"
        "</span>"
    )


def build_body(payload: dict) -> str:
    doctor = payload["doctor"]
    inspect_payload = payload["inspect"]
    triage_payload = payload["triage"]
    self_learn_report = payload["self_learn_report"]
    migration_summary = payload["migration_summary"]
    db_metrics = payload["db_metrics"]
    generated_at = base.pretty_timestamp(
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )

    triage_summary = triage_payload["summary"]
    memory_summary = self_learn_report["memory_summary"]
    meta_html = "".join(
        [
            v2.metric_pill("OK" if not doctor["issues"] else "WARN", "حالة doctor", "Doctor status", "accent"),
            v2.metric_pill(triage_summary["pending_total"], "مرشحات pending", "Pending candidates"),
            v2.metric_pill(db_metrics["project_profile_rows"], "ملفات مشروع DB", "Project profile rows"),
            v2.metric_pill(memory_summary["journal_event_count"], "أحداث self-learn", "Self-learn events"),
            v2.metric_pill(generated_at, "تم التوليد", "Generated"),
        ]
    )

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Architecture HUD", "Architecture HUD", "span")}</p>
              <h1>{v2.bilingual_html("ترقية <span class=\"accent\">persistent-memory</span> إلى SQLite-first من غير كسر حدود <span class=\"accent\">self-learn</span>", "Promoting <span class=\"accent\">persistent-memory</span> to SQLite-first without breaking <span class=\"accent\">self-learn</span> boundaries", "span")}</h1>
              {v2.bilingual_text(
                  "الملف ده لا يعمل كـ live dashboard. هو artifact معماري مرجعي يشرح ماذا يحدث الآن، أين SQLite موجودة بالفعل، وما الذي تغيّر كي تصبح canonical داخل `persistent-memory` فقط.",
                  "This file is not a live admin dashboard. It is an architecture artifact that explains the current state, where SQLite already exists, and what changed to make it canonical inside `persistent-memory` only.",
                  "p",
                  "muted-copy",
              )}
              <div class="tag-row">
                {v2.inline_tag("SQLite-first", "SQLite-first", "accent")}
                {v2.inline_tag("persistent-memory only", "persistent-memory only")}
                {v2.inline_tag("self-learn stays self-only", "self-learn stays self-only")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("الملف الناتج", "Output artifact", "accent")}
                  {v2.code_tag("omega-hud-html.html")}
                </div>
                <div class="poster-surface__score">
                  <strong>{db_metrics["pending_candidate_rows"]}</strong>
                  <span>{v2.bilingual_html("pending حاليًا", "Pending now", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("الحقيقة التشغيلية بعد الترقية", "Operational truth after the upgrade", "span")}</div>
                {v2.bilingual_text(
                    "القراءة هنا مبنية على `doctor` و`inspect` و`triage` و`self-learn report` وملخص migration helper من نفس البيئة.",
                    "This reading is grounded in `doctor`, `inspect`, `triage`, `self-learn report`, and the migration helper summary from the same environment.",
                    "p",
                    "poster-surface__summary",
                )}
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  {meter(db_metrics["global_profile_rows"], "صفوف global", "Global rows")}
                  {meter(db_metrics["project_profile_rows"], "صفوف المشاريع", "Project rows")}
                  {meter(db_metrics["reference_artifact_rows"], "مراجع المشاريع", "Project references")}
                  {meter(db_metrics["snapshot_event_rows"], "أحداث snapshots", "Snapshot events")}
                </div>
                <p class="dim-copy">{escape(generated_at)}</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    current_state = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Current truth", "Current truth", "span")}</p>
          <h2>{v2.bilingual_html("ماذا تفعل كل طبقة الآن", "What each layer does right now", "span")}</h2>
          {v2.bilingual_text(
              "القسم ده يثبت الفرق بين المهارتين كما هي فعليًا بعد التنفيذ، بدل وصف عام أو نية مستقبلية.",
              "This section locks the actual split between the two skills after implementation, not a generic or future-facing description.",
              "p",
              "section-copy",
          )}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {insight_panel(
              "persistent-memory الآن",
              "persistent-memory now",
              bilingual_fact_list(
                  [
                      (("المشروع المحلول", "Resolved project"), str(doctor["resolved_project"] or "None")),
                      (("ملف قاعدة الحالة", "State DB path"), str(doctor["state_db"])),
                      (("إجمالي pending", "Pending total"), str(triage_summary["pending_total"])),
                      (("مرشحات قابلة للترقية", "Promotable total"), str(triage_summary["promotable_total"])),
                      (("مرشحات ephemeral", "Ephemeral total"), str(triage_summary["ephemeral_total"])),
                  ]
              )
              + v2.bilingual_text(
                  "تخزن الـ profile state الآن داخل SQLite نفسها، ثم تصدر YAML/Markdown كطبقة توافق بشرية. الـ CLI العامة لم تتغير.",
                  "Profile state now lives inside SQLite itself, while YAML/Markdown remain compatibility exports. The public CLI contract did not change.",
                  "p",
                  "rail-copy",
              ),
              tags="".join([v2.code_tag("doctor"), v2.code_tag("inspect"), v2.code_tag("triage"), v2.inline_tag("SQLite-first", "SQLite-first", "accent")]),
          )}
          {insight_panel(
              "self-learn الآن",
              "self-learn now",
              bilingual_fact_list(
                  [
                      (("أحداث journal", "Journal events"), str(memory_summary["journal_event_count"])),
                      (("أنماط durable", "Durable patterns"), str(memory_summary["durable_pattern_count"])),
                      (("بصمات suppressed", "Suppressed fingerprints"), str(memory_summary["suppressed_fingerprint_count"])),
                      (("renderer الحالي", "Current renderer"), str((self_learn_report.get("health") or {}).get("current_renderer_profile") or "None")),
                  ]
              )
              + v2.bilingual_text(
                  "ما زالت self-learn file-backed بالكامل داخل skill نفسها: journal, proposals, snapshots, rollback. التكامل الوحيد هنا هو read-only reference context من `persistent-memory`.",
                  "Self-learn remains fully file-backed inside its own skill: journal, proposals, snapshots, and rollback. The only integration here is read-only reference context from `persistent-memory`.",
                  "p",
                  "rail-copy",
              ),
              tags="".join([v2.code_tag("report"), v2.code_tag("rollback"), v2.inline_tag("self-only", "self-only", "accent")]),
          )}
        </div>
      </section>
    """

    storage_split = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("SQLite boundary", "SQLite boundary", "span")}</p>
          <h2>{v2.bilingual_html("أين كانت SQLite وأين أصبحت canonical", "Where SQLite existed and where it became canonical", "span")}</h2>
          {v2.bilingual_text(
              "بدل greenfield rewrite، الترقية هنا رفعت SQLite من state/index layer إلى source-of-truth داخل `persistent-memory` نفسها.",
              "Instead of a greenfield rewrite, this upgrade promotes SQLite from a state/index layer into the source of truth inside `persistent-memory` itself.",
              "p",
              "section-copy",
          )}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {insight_panel(
              "قبل الترقية",
              "Before the upgrade",
              report_list(
                  [
                      ("SQLite موجودة للحالة التشغيلية فقط", "SQLite existed mainly for operational state"),
                      ("profiles كانت تُقرأ وتُكتب من YAML مباشرة", "Profiles were read from and written to YAML directly"),
                      ("rollback كان يعيد الملفات، لا الـ DB كمصدر canonical", "Rollback restored files, not the DB as the canonical source"),
                      ("caches البشرية كانت تعتمد على ملفات متفرقة", "Human-readable caches depended on scattered files"),
                  ]
              ),
              tags="".join([v2.inline_tag("hybrid", "hybrid"), v2.code_tag("memory_state.sqlite")]),
          )}
          {insight_panel(
              "بعد الترقية",
              "After the upgrade",
              report_list(
                  [
                      ("`global_profile_state` و`project_profile_state` داخل SQLite", "`global_profile_state` and `project_profile_state` now live in SQLite"),
                      ("`project_reference_artifacts` و`candidate_evidence` موجودتان للاستعلام المباشر", "`project_reference_artifacts` and `candidate_evidence` are available for direct querying"),
                      ("YAML وMarkdown بقيا compatibility exports فقط", "YAML and Markdown remain compatibility exports only"),
                      ("rollback يعيد الملف ثم يزامن الـ DB من snapshot المسترجعة", "Rollback restores the file and then resynchronizes the DB from the restored snapshot"),
                  ]
              ),
              tags="".join([v2.inline_tag("canonical DB", "canonical DB", "accent"), v2.code_tag("mutation_snapshot_events")]),
          )}
        </div>
      </section>
    """

    boundaries = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Boundaries", "Boundaries", "span")}</p>
          <h2>{v2.bilingual_html("الحدود التي لا يجب كسرها", "The boundaries that must stay intact", "span")}</h2>
          {v2.bilingual_text(
              "القيمة هنا ليست في دمج الطبقتين، بل في إبقاء كل واحدة صادقة في مسؤوليتها.",
              "The value here is not merging the two layers, but keeping each one honest about its responsibility.",
              "p",
              "section-copy",
          )}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {insight_panel(
              "ما يكتبه `persistent-memory`",
              "What `persistent-memory` writes",
              report_list(
                  [
                      ("profile state الدائمة", "Durable profile state"),
                      ("candidate state + evidence lineage", "Candidate state and evidence lineage"),
                      ("promotion / reject / forget / rollback events", "Promotion / reject / forget / rollback events"),
                      ("bootstrap caches وproject caches كـ exports", "Bootstrap caches and project caches as exports"),
                  ]
              ),
              tags="".join([v2.code_tag("promote"), v2.code_tag("forget"), v2.code_tag("rollback")]),
          )}
          {insight_panel(
              "ما لا يُسمح لـ `self-learn` بكتابته",
              "What `self-learn` must not write",
              report_list(
                  [
                      ("لا تشارك نفس SQLite DB في هذه المرحلة", "It does not share the same SQLite DB in this phase"),
                      ("لا تروّج candidates ولا تعدّل profile state", "It does not promote candidates or mutate profile state"),
                      ("تقرأ `reference_context` فقط عند report", "It only reads `reference_context` during report"),
                      ("تحتفظ بـ journal/proposals/snapshots داخل skill نفسها", "It keeps journal/proposals/snapshots inside its own skill"),
                  ]
              ),
              tags="".join([v2.inline_tag("read-only bridge", "read-only bridge", "accent"), v2.code_tag("report")]),
          )}
        </div>
      </section>
    """

    migration_path = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Migration path", "Migration path", "span")}</p>
          <h2>{v2.bilingual_html("مسار الترقية والرجوع الآمن", "The upgrade path and safe rollback", "span")}</h2>
          {v2.bilingual_text(
              "الترقية اتبنت كـ bounded refactor: نفس الـ CLI، نفس الـ exports، لكن storage adapter واحد وSQLite canonical.",
              "The upgrade was built as a bounded refactor: same CLI, same exports, but one storage adapter and SQLite as canonical storage.",
              "p",
              "section-copy",
          )}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {insight_panel(
              "خطوات التنفيذ",
              "Execution steps",
              report_list(
                  [
                      ("إضافة profile tables وreference/candidate evidence tables", "Add profile tables plus reference/candidate evidence tables"),
                      ("تحميل legacy YAML مرة أولى إلى DB عند الحاجة", "Seed legacy YAML into the DB when needed"),
                      ("توحيد `inspect` و`doctor` و`promote` و`forget` و`rollback` حول storage adapter واحد", "Unify `inspect`, `doctor`, `promote`, `forget`, and `rollback` around one storage adapter"),
                      ("الإبقاء على YAML/Markdown كـ exports متوافقة", "Keep YAML/Markdown as compatibility exports"),
                  ]
              ),
              tags="".join([v2.code_tag("migrate_sqlite_first.py"), v2.inline_tag("bounded repair", "bounded repair", "accent")]),
          )}
          {insight_panel(
              "الرجوع الآمن",
              "Safe rollback",
              report_list(
                  [
                      ("snapshot للملف قبل mutation", "Snapshot the file before mutation"),
                      ("استعادة الملف من snapshot عند rollback", "Restore the file from the snapshot during rollback"),
                      ("إعادة مزامنة DB من الملف المسترجع", "Resynchronize the DB from the restored file"),
                      ("إعادة بناء caches من الحالة canonical بعد rollback", "Rebuild caches from canonical state after rollback"),
                  ]
              ),
              tags="".join([v2.code_tag("mutation_snapshot_events"), v2.inline_tag("rollback-safe", "rollback-safe", "accent")]),
          )}
        </div>
      </section>
    """

    proof_matrix = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Proof matrix", "Proof matrix", "span")}</p>
          <h2>{v2.bilingual_html("ما الذي تم إثباته بعد التنفيذ", "What was proved after implementation", "span")}</h2>
          {v2.bilingual_text(
              "التحقق هنا مربوط بخطوات الخطة نفسها: parity، mutation safety، bridge integrity، وHUD generation.",
              "Verification here is tied to the plan itself: parity, mutation safety, bridge integrity, and HUD generation.",
              "p",
              "section-copy",
          )}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {insight_panel(
              "Parity + DB proof",
              "Parity + DB proof",
              bilingual_fact_list(
                  [
                      (("إجمالي pending", "Pending total"), str(triage_summary["pending_total"])),
                      (("قابلة للترقية", "Promotable total"), str(triage_summary["promotable_total"])),
                      (("ephemeral", "Ephemeral total"), str(triage_summary["ephemeral_total"])),
                      (("صفوف global", "Global profile rows"), str(db_metrics["global_profile_rows"])),
                      (("صفوف المشاريع", "Project profile rows"), str(db_metrics["project_profile_rows"])),
                  ]
              )
              + v2.bilingual_text(
                  "الاختبارات تؤكد أن promote/forget/rollback تُحدّث DB-backed profile state وتبقي الـ YAML exports متسقة.",
                  "The tests confirm that promote/forget/rollback update DB-backed profile state while keeping YAML exports consistent.",
                  "p",
                  "rail-copy",
              ),
              tags="".join([v2.inline_tag("15 tests", "15 tests", "accent"), v2.code_tag("test_memory_system.py")]),
          )}
          {insight_panel(
              "Bridge + health",
              "Bridge + health",
              bilingual_fact_list(
                  [
                      (("المشروع المحلول", "Resolved project"), str((self_learn_report.get("reference_context") or {}).get("resolved_project") or "None")),
                      (("المرجع الأساسي", "Primary reference artifact"), str((self_learn_report.get("reference_context") or {}).get("primary_reference_artifact") or "None")),
                      (("renderer الحالي", "Current renderer"), str((self_learn_report.get("health") or {}).get("current_renderer_profile") or "None")),
                      (("صفوف migration للمشاريع", "Migration project rows"), str(migration_summary["project_profile_rows"])),
                  ]
              )
              + v2.bilingual_text(
                  "جسر `self-learn report` ما زال read-only، ويقرأ context من `persistent-memory` من غير أي write path عكسي.",
                  "The `self-learn report` bridge remains read-only and continues to read context from `persistent-memory` with no reverse write path.",
                  "p",
                  "rail-copy",
              ),
              tags="".join([v2.code_tag("report"), v2.inline_tag("read-only", "read-only", "accent")]),
          )}
        </div>
      </section>
    """

    risks = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Non-goals + risks", "Non-goals + risks", "span")}</p>
          <h2>{v2.bilingual_html("ما الذي لم نحاوله وما الذي ما زال يحتاج Phase لاحقة", "What we did not attempt and what still belongs to a later phase", "span")}</h2>
          {v2.bilingual_text(
              "الترقية دي مقصود بها إقفال المصدر canonical داخل `persistent-memory` فقط. أي توحيد أوسع ما زال خارج النطاق الحالي عمدًا.",
              "This upgrade is meant to lock the canonical source inside `persistent-memory` only. Any wider unification remains deliberately out of scope.",
              "p",
              "section-copy",
          )}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          {insight_panel(
              "Non-goals",
              "Non-goals",
              report_list(
                  [
                      ("عدم تحويل الصفحة إلى live admin dashboard", "Do not turn this page into a live admin dashboard"),
                      ("عدم نقل `self-learn` إلى SQLite مشتركة", "Do not move `self-learn` into a shared SQLite store"),
                      ("عدم تغيير أسماء أو semantics الـ CLI الحالية", "Do not change public CLI names or semantics"),
                      ("عدم بناء memory bus موحدة للمنظومة كلها الآن", "Do not build a platform-wide memory bus yet"),
                  ]
              ),
              tags="".join([v2.inline_tag("scope locked", "scope locked", "accent")]),
          )}
          {insight_panel(
              "Residual risks",
              "Residual risks",
              report_list(
                  [
                      ("أي تعديل يدوي مباشر في YAML بعد الآن لن يكون المصدر canonical", "Direct manual edits to YAML are no longer canonical"),
                      ("الـ UI الحالي يشرح المعمارية لكنه لا يراقب live mutations لحظيًا", "The current UI explains the architecture but does not live-monitor mutations"),
                      ("shared DB مع `self-learn` يحتاج phase مستقلة إن قررناها لاحقًا", "A shared DB with `self-learn` would need a dedicated later phase"),
                      ("الـ compatibility exports يجب أن تظل متزامنة عبر `doctor` أو مسارات الكتابة الرسمية", "Compatibility exports must stay synchronized through `doctor` or official write paths"),
                  ]
              ),
              tags="".join([v2.inline_tag("phase 2 later", "phase 2 later", "accent")]),
          )}
        </div>
      </section>
    """

    sources = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Sources", "Sources", "span")}</p>
          <h2>{v2.bilingual_html("المصادر التي بُني منها هذا الـ HUD", "The sources used to build this HUD", "span")}</h2>
          {v2.bilingual_text(
              "المقصود هنا إظهار canonical sources والـ artifacts المرجعية التي استخدمها builder، لا سرد كل ملف في المشروع.",
              "The point here is to show the canonical sources and reference artifacts used by the builder, not to enumerate every file in the repo.",
              "p",
              "section-copy",
          )}
        </div>
        <div class="section-divider"></div>
        {insight_panel(
            "Source map",
            "Source map",
            source_list(
                [
                    ("builder", str(Path(__file__).resolve())),
                    ("sample HUD", str(SAMPLE_PATH)),
                    ("persistent-memory / SKILL", str(PERSISTENT_MEMORY_SKILL)),
                    ("persistent-memory / CLI", str(MEMORY_CLI)),
                    ("persistent-memory / migration helper", str(MIGRATION_HELPER)),
                    ("self-learn / SKILL", str(SELF_LEARN_SKILL)),
                    ("self-learn / runner", str(SELF_LEARN_RUNNER)),
                    ("output", str(OUTPUT_PATH)),
                ]
            ),
            tags="".join([v2.inline_tag("local-only", "local-only", "accent"), v2.code_tag("omega-hud-html.html")]),
        )}
      </section>
    """

    return "\n".join([build_topbar(meta_html), hero, current_state, storage_split, boundaries, migration_path, proof_matrix, risks, sources])


def build_shell(body_html: str) -> str:
    shell = v8.build_shell("Omega HUD HTML", "ملف معمارية الميموري", "memory-page", body_html)
    return shell.replace("OMEGA HUD V8 / live audited artifact / local only / no external assets", "OMEGA HUD HTML / v8-derived memory-architecture artifact / local only / no external assets")


def main() -> None:
    payload = collect_runtime_payload()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_shell(build_body(payload)), encoding="utf-8")
    print("Wrote:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
