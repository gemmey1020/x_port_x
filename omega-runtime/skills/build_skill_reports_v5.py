#!/usr/bin/env python3

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2


ROOT = base.ROOT
OUTPUT_HTML_DIR = ROOT / "output/html"
SKILLS_OUTPUT = OUTPUT_HTML_DIR / "omega-skills-hud-v5.html"
MEMORY_OUTPUT = OUTPUT_HTML_DIR / "omega-memory-learning-report-v5.html"

V5_CSS = v2.SHARED_CSS + """

:root {
  --bg: #090907;
  --bg-soft: #14160f;
  --surface: rgba(24, 26, 20, 0.82);
  --surface-strong: rgba(30, 34, 26, 0.94);
  --surface-soft: rgba(120, 199, 173, 0.06);
  --line: rgba(120, 199, 173, 0.18);
  --line-strong: rgba(120, 199, 173, 0.38);
  --ink: #f3e7d0;
  --muted: rgba(243, 231, 208, 0.75);
  --dim: rgba(243, 231, 208, 0.48);
  --accent: #78c7ad;
  --accent-strong: #d7fff0;
  --accent-soft: rgba(120, 199, 173, 0.14);
  --success: #a7d9b2;
  --shadow: 0 36px 100px rgba(0, 0, 0, 0.4);
  --display-font: "Palatino Linotype", "Iowan Old Style", Georgia, serif;
  --body-font: "Segoe UI", Tahoma, Arial, sans-serif;
  --page-max: 1500px;
}

html[data-theme="light"] {
  --bg: #f6efe1;
  --bg-soft: #fcf7ef;
  --surface: rgba(255, 251, 244, 0.86);
  --surface-strong: rgba(255, 251, 244, 0.96);
  --surface-soft: rgba(59, 109, 92, 0.05);
  --line: rgba(59, 109, 92, 0.18);
  --line-strong: rgba(59, 109, 92, 0.34);
  --ink: #241e17;
  --muted: rgba(36, 30, 23, 0.74);
  --dim: rgba(36, 30, 23, 0.48);
  --accent: #3c7766;
  --accent-strong: #275346;
  --accent-soft: rgba(60, 119, 102, 0.12);
  --shadow: 0 28px 70px rgba(94, 73, 35, 0.13);
}

@keyframes candleBreath {
  0%,
  100% {
    opacity: 0.44;
    transform: scale(0.99);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.015);
  }
}

@keyframes inkDrift {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, 8px, 0);
  }
}

html {
  background:
    radial-gradient(circle at 18% 12%, rgba(120, 199, 173, 0.12), transparent 24%),
    radial-gradient(circle at 80% 14%, rgba(243, 231, 208, 0.07), transparent 24%),
    linear-gradient(180deg, #171912 0%, #090907 100%);
}

body::before {
  background:
    radial-gradient(circle at 78% 18%, rgba(120, 199, 173, 0.09), transparent 13%),
    repeating-linear-gradient(180deg, rgba(243, 231, 208, 0.025) 0, rgba(243, 231, 208, 0.025) 1px, transparent 1px, transparent 18px),
    repeating-linear-gradient(90deg, rgba(120, 199, 173, 0.02) 0, rgba(120, 199, 173, 0.02) 1px, transparent 1px, transparent 62px);
  background-size: auto, 100% 18px, 62px 62px;
  opacity: 0.24;
  mix-blend-mode: screen;
}

body::after {
  background:
    radial-gradient(circle at 50% -12%, rgba(120, 199, 173, 0.12), transparent 40%),
    radial-gradient(circle at 50% 118%, rgba(0, 0, 0, 0.48), transparent 46%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 28%);
  opacity: 0.92;
}

.page-shell::before {
  content: "";
  position: fixed;
  inset: 16px;
  border-radius: 28px;
  border: 1px solid rgba(120, 199, 173, 0.08);
  pointer-events: none;
  opacity: 0.5;
}

.utility-bar {
  top: 12px;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(243, 231, 208, 0.035), transparent 44%),
    linear-gradient(90deg, rgba(120, 199, 173, 0.06), transparent 22%),
    color-mix(in srgb, var(--surface-strong) 88%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    inset 0 0 0 1px rgba(120, 199, 173, 0.03),
    var(--shadow);
}

.brand-lockup strong {
  letter-spacing: 0.3em;
}

.brand-lockup span {
  letter-spacing: 0.08em;
}

.metric-pill,
.control-readout,
.inline-tag,
.score-chip,
.tier-token,
.tier-kicker {
  background:
    linear-gradient(180deg, rgba(243, 231, 208, 0.04), rgba(243, 231, 208, 0.015)),
    color-mix(in srgb, var(--surface-strong) 84%, transparent);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.045);
}

.control-button {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.07),
    0 8px 24px rgba(0, 0, 0, 0.12);
}

.hero-stage {
  min-height: clamp(620px, calc(100svh - 120px), 920px);
  border-bottom-color: color-mix(in srgb, var(--accent) 34%, transparent);
}

.hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.54) 12%, transparent 42%),
    radial-gradient(circle at 76% 28%, rgba(120, 199, 173, 0.15), transparent 32%),
    radial-gradient(circle at 76% 28%, rgba(243, 231, 208, 0.05), transparent 52%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.018), transparent 30%);
}

.hero-stage::after {
  background:
    repeating-linear-gradient(180deg, rgba(243, 231, 208, 0.03) 0, rgba(243, 231, 208, 0.03) 1px, transparent 1px, transparent 14px),
    radial-gradient(circle at 80% 24%, rgba(120, 199, 173, 0.12), transparent 18%);
  opacity: 0.56;
  animation: inkDrift 12s ease-in-out infinite;
}

.hero-kicker,
.section-kicker,
.eyebrow {
  letter-spacing: 0.22em;
}

.hero-copy h1 {
  text-shadow:
    0 12px 34px rgba(0, 0, 0, 0.32),
    0 0 28px rgba(120, 199, 173, 0.08);
}

.poster-surface {
  min-height: 460px;
  border-radius: 26px 26px 8px 26px;
  background:
    linear-gradient(160deg, rgba(120, 199, 173, 0.12), transparent 24%),
    linear-gradient(180deg, rgba(243, 231, 208, 0.045), transparent 46%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.028), transparent 70%),
    color-mix(in srgb, var(--surface-strong) 93%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.07),
    inset 0 0 0 1px rgba(120, 199, 173, 0.03),
    var(--shadow);
}

.poster-surface::before {
  inset: auto -8% -16% auto;
  width: 62%;
  background: radial-gradient(circle, rgba(120, 199, 173, 0.16), transparent 72%);
  animation: candleBreath 9s ease-in-out infinite;
}

.poster-surface::after {
  inset: 18px 18px auto auto;
  width: 180px;
  height: 180px;
  border: 1px solid rgba(120, 199, 173, 0.16);
  box-shadow: 0 0 0 12px rgba(120, 199, 173, 0.03);
}

.poster-surface__score strong,
.poster-surface__name {
  text-shadow:
    0 10px 22px rgba(0, 0, 0, 0.24),
    0 0 22px rgba(120, 199, 173, 0.06);
}

.section-head h2 {
  line-height: 0.96;
}

.section-divider {
  background: linear-gradient(90deg, transparent, rgba(120, 199, 173, 0.56), transparent);
}

.exception-strip,
.story-band,
.feature-row,
.dense-row,
.stack-item,
.insight-panel {
  padding-inline: 14px;
  border-radius: 18px;
  background:
    linear-gradient(90deg, rgba(120, 199, 173, 0.06), transparent 18%),
    linear-gradient(180deg, rgba(243, 231, 208, 0.018), transparent 72%);
}

.exception-strip,
.story-band,
.feature-row,
.dense-row,
.stack-item,
.insight-panel,
.fact-list li,
.report-list li,
.source-list a,
.fact-row {
  border-top-color: rgba(120, 199, 173, 0.12);
}

.exception-strip:hover,
.story-band:hover,
.feature-row:hover,
.dense-row:hover,
.stack-item:hover,
.insight-panel:hover {
  transform: translateY(-3px);
  border-color: rgba(120, 199, 173, 0.22);
}

.code-panel {
  background:
    linear-gradient(180deg, rgba(243, 231, 208, 0.03), transparent 30%),
    color-mix(in srgb, var(--surface-strong) 90%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    inset 0 0 0 1px rgba(120, 199, 173, 0.03);
}

.footer-note {
  letter-spacing: 0.14em;
}

.memory-page .hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.5) 12%, transparent 42%),
    radial-gradient(circle at 74% 28%, rgba(120, 199, 173, 0.11), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.016), transparent 28%);
}

@media (max-width: 900px) {
  .page-shell::before {
    display: none;
  }

  .hero-stage {
    min-height: auto;
    padding-block: 44px;
  }

  .poster-surface,
  .memory-page .poster-surface {
    min-height: auto;
  }
}

@media (max-width: 640px) {
  .exception-strip,
  .story-band,
  .feature-row,
  .dense-row,
  .stack-item,
  .insight-panel {
    padding-inline: 10px;
  }
}
"""

COMMON_REPLACEMENTS = [
    (
        "OMEGA HUD V2 / cinematic alternate artifact / local only / no external assets",
        "OMEGA HUD V5 / temple manuscript alternate artifact / local only / no external assets",
    ),
    ("OMEGA HUD V2", "OMEGA HUD V5"),
    ("omega-cinematic-v2", "omega-temple-manuscript-v5"),
    ("cinematic alternate artifact", "temple manuscript alternate artifact"),
]

SKILLS_REPLACEMENTS = [
    ("Omega Skills HUD V2", "Omega Skills HUD V5"),
    ("لوحة مهارات أوميجا V2", "لوحة مهارات أوميجا V5"),
    ("نسخة سينمائية بديلة", "نسخة مخطوطة معبدية"),
    ("Cinematic alternate edition", "Temple manuscript edition"),
    ("Taste Upgrade Mode / بلا source drift", "Temple Manuscript / بلا source drift"),
    ("Taste Upgrade Mode / no source drift", "Temple Manuscript / no source drift"),
    ("أفضل مهارة الآن تقود المشهد:", "في المخطوطة الخامسة ما زال الافتتاح باسم:"),
    ("One skill still leads the board:", "In the fifth manuscript, the opening still belongs to:"),
    (
        "النسخة دي تحافظ على نفس الحقيقة التشغيلية، لكن تقدمها كواجهة أقرب لغرفة تحكم أوميجا: hero أوضح، rails أنظف، وطبقات أقل تكرارًا من شكل الكروت المعتاد.",
        "النسخة دي تتعامل مع السجل كأنه مخطوطة تقنية مضيئة: نفس الحقائق محفوظة، لكن مكتوبة على رقّ أوميجا بدل سطح مراقبة مباشر.",
    ),
    (
        "This edition keeps the same operational truth, but stages it like an Omega control room: a stronger poster hero, cleaner rails, and less repeated card chrome.",
        "This edition treats the registry like an illuminated technical manuscript: the same facts preserved, but printed on Omega vellum instead of a live control surface.",
    ),
    ("شريط الاستثناءات", "هوامش الاستثناءات"),
    ("Exception strip", "Annotated exception margin"),
    ("العمود الفقري للترتيب", "هرمية مضيئة"),
    ("Editorial efficiency rails", "Illuminated hierarchy"),
    ("Consolidation map", "Merge annotations"),
    ("Cognitive load relief", "Dormant margins"),
    ("Forward pressure", "Restoration queue"),
    ("Ledger closeout", "Archive colophon"),
]

MEMORY_REPLACEMENTS = [
    ("Omega Memory Learning Report V2", "Omega Memory Learning Report V5"),
    ("تقرير ذاكرة وتعلّم أوميجا V2", "تقرير ذاكرة وتعلّم أوميجا V5"),
    ("نسخة تحليلية V2", "نسخة مخطوطة أرشيفية"),
    ("Forensic companion edition", "Archive manuscript edition"),
    ("Forensic companion / نفس pipeline", "Archive Manuscript / نفس pipeline"),
    ("Forensic companion / same pipeline", "Archive Manuscript / same pipeline"),
    (
        'الذاكرة <span class="accent">مستقرة</span>، والتعلّم <span class="accent">منضبط</span>، لكن لا يوجد auto-promotion.',
        'الذاكرة <span class="accent">محفوظة</span> في الرقّ، والتعلّم <span class="accent">منضبط</span>، ولا auto-promotion حتى الآن.',
    ),
    (
        'Memory is <span class="accent">stable</span>, learning is <span class="accent">disciplined</span>, and there is still no auto-promotion.',
        'Memory stays <span class="accent">preserved</span> in the manuscript, learning remains <span class="accent">disciplined</span>, and there is still no auto-promotion.',
    ),
    (
        "هذه النسخة تهدّي الصوت البصري، لكنها تبقي نفس الحقيقة: doctor سليم، backlog ما زال ephemeral بالكامل تقريبًا، وself-learn في وضع observe/report فقط.",
        "النسخة دي تقرأ الحالة كأنها folio محفوظة: نفس الحقيقة موجودة، doctor سليم، backlog ما زال شبه ephemeral بالكامل، وself-learn بقي داخل observe/report فقط.",
    ),
    (
        "This edition lowers the visual temperature, but keeps the same truth: doctor is healthy, the backlog is still effectively all-ephemeral, and self-learn stayed in observe/report mode only.",
        "This edition reads the state as a preserved folio: the same truth remains, doctor stays healthy, the backlog is still effectively all-ephemeral, and self-learn remained in observe/report only.",
    ),
    ("Durable profile", "Core manuscript profile"),
    ("Queue diagnosis", "Queue gloss"),
    ("Self-only boundary", "Sealed scholia"),
    ("Observed vs changed", "Observed vs restored"),
    ("Quality guardrails", "Preservation rules"),
    ("Evidence bundle", "Evidence folio"),
]


def apply_replacements(document: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        document = document.replace(old, new)
    return document


def restyle_document(document: str, page_kind: str) -> str:
    document = apply_replacements(document, COMMON_REPLACEMENTS)
    page_replacements = SKILLS_REPLACEMENTS if page_kind == "skills" else MEMORY_REPLACEMENTS
    return apply_replacements(document, page_replacements)


def main():
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    original_css = v2.SHARED_CSS
    try:
        v2.SHARED_CSS = V5_CSS
        skills = base.build_skill_index()
        snapshot = base.build_memory_snapshot()
        skills_html = restyle_document(v2.build_skills_page(skills), "skills")
        memory_html = restyle_document(v2.build_memory_page(skills, snapshot), "memory")
        SKILLS_OUTPUT.write_text(skills_html, encoding="utf-8")
        MEMORY_OUTPUT.write_text(memory_html, encoding="utf-8")
    finally:
        v2.SHARED_CSS = original_css

    print("Wrote:")
    print(SKILLS_OUTPUT)
    print(MEMORY_OUTPUT)


if __name__ == "__main__":
    main()
