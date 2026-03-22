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
SKILLS_OUTPUT = OUTPUT_HTML_DIR / "omega-skills-hud-v4.html"
MEMORY_OUTPUT = OUTPUT_HTML_DIR / "omega-memory-learning-report-v4.html"

V4_CSS = v2.SHARED_CSS + """

:root {
  --bg: #06080c;
  --bg-soft: #11151c;
  --surface: rgba(16, 20, 28, 0.8);
  --surface-strong: rgba(22, 26, 36, 0.94);
  --surface-soft: rgba(183, 216, 255, 0.05);
  --line: rgba(183, 216, 255, 0.16);
  --line-strong: rgba(183, 216, 255, 0.34);
  --ink: #f4eee2;
  --muted: rgba(244, 238, 226, 0.74);
  --dim: rgba(244, 238, 226, 0.46);
  --accent: #b7d8ff;
  --accent-strong: #edf7ff;
  --accent-soft: rgba(183, 216, 255, 0.13);
  --success: #9fcfc3;
  --shadow: 0 40px 110px rgba(0, 0, 0, 0.42);
  --display-font: "Palatino Linotype", "Book Antiqua", Georgia, serif;
  --body-font: "Segoe UI", Tahoma, Arial, sans-serif;
  --page-max: 1500px;
}

html[data-theme="light"] {
  --bg: #f1ece2;
  --bg-soft: #faf6ef;
  --surface: rgba(255, 252, 247, 0.84);
  --surface-strong: rgba(255, 252, 247, 0.96);
  --surface-soft: rgba(66, 89, 114, 0.05);
  --line: rgba(77, 102, 129, 0.18);
  --line-strong: rgba(77, 102, 129, 0.34);
  --ink: #211d19;
  --muted: rgba(33, 29, 25, 0.74);
  --dim: rgba(33, 29, 25, 0.48);
  --accent: #4b6f93;
  --accent-strong: #345671;
  --accent-soft: rgba(75, 111, 147, 0.12);
  --shadow: 0 28px 72px rgba(72, 58, 37, 0.14);
}

@keyframes archivePulse {
  0%,
  100% {
    opacity: 0.46;
    transform: scale(0.98);
  }
  50% {
    opacity: 0.82;
    transform: scale(1.02);
  }
}

@keyframes scanDrift {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, 10px, 0);
  }
}

html {
  background:
    radial-gradient(circle at 18% 12%, rgba(183, 216, 255, 0.12), transparent 24%),
    radial-gradient(circle at 78% 16%, rgba(183, 216, 255, 0.08), transparent 24%),
    linear-gradient(180deg, #171c25 0%, #06080c 100%);
}

body::before {
  background:
    radial-gradient(circle at 74% 18%, rgba(183, 216, 255, 0.08), transparent 13%),
    repeating-linear-gradient(90deg, rgba(183, 216, 255, 0.028) 0, rgba(183, 216, 255, 0.028) 1px, transparent 1px, transparent 46px),
    repeating-linear-gradient(180deg, rgba(183, 216, 255, 0.024) 0, rgba(183, 216, 255, 0.024) 1px, transparent 1px, transparent 46px);
  background-size: auto, 46px 46px, 46px 46px;
  opacity: 0.26;
  mix-blend-mode: screen;
}

body::after {
  background:
    radial-gradient(circle at 50% -8%, rgba(183, 216, 255, 0.11), transparent 40%),
    radial-gradient(circle at 50% 120%, rgba(0, 0, 0, 0.46), transparent 44%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 30%);
  opacity: 0.92;
}

.page-shell::before {
  content: "";
  position: fixed;
  inset: 18px;
  border-radius: 28px;
  border: 1px solid rgba(183, 216, 255, 0.08);
  pointer-events: none;
  opacity: 0.5;
}

.utility-bar {
  top: 12px;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.038), transparent 44%),
    linear-gradient(90deg, rgba(183, 216, 255, 0.05), transparent 24%),
    color-mix(in srgb, var(--surface-strong) 88%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    inset 0 0 0 1px rgba(183, 216, 255, 0.03),
    var(--shadow);
}

.brand-lockup strong {
  letter-spacing: 0.34em;
}

.brand-lockup span {
  letter-spacing: 0.06em;
}

.metric-pill,
.control-readout,
.inline-tag,
.score-chip,
.tier-token,
.tier-kicker {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.015)),
    color-mix(in srgb, var(--surface-strong) 84%, transparent);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.control-button {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.07),
    0 8px 24px rgba(0, 0, 0, 0.12);
}

.hero-stage {
  min-height: clamp(620px, calc(100svh - 116px), 920px);
  border-bottom-color: color-mix(in srgb, var(--accent) 34%, transparent);
}

.hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.58) 12%, transparent 42%),
    radial-gradient(circle at 76% 28%, rgba(183, 216, 255, 0.16), transparent 30%),
    radial-gradient(circle at 76% 28%, rgba(255, 255, 255, 0.04), transparent 52%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.022), transparent 30%);
}

.hero-stage::after {
  background:
    repeating-linear-gradient(180deg, rgba(183, 216, 255, 0.03) 0, rgba(183, 216, 255, 0.03) 1px, transparent 1px, transparent 12px),
    radial-gradient(circle at 80% 24%, rgba(183, 216, 255, 0.12), transparent 18%);
  opacity: 0.64;
  animation: scanDrift 12s ease-in-out infinite;
}

.hero-kicker,
.section-kicker,
.eyebrow {
  letter-spacing: 0.2em;
}

.hero-copy h1 {
  text-shadow:
    0 12px 36px rgba(0, 0, 0, 0.32),
    0 0 34px rgba(183, 216, 255, 0.08);
}

.poster-surface {
  min-height: 460px;
  border-radius: 28px 28px 8px 28px;
  background:
    linear-gradient(162deg, rgba(183, 216, 255, 0.12), transparent 24%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), transparent 44%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.03), transparent 68%),
    color-mix(in srgb, var(--surface-strong) 93%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    inset 0 0 0 1px rgba(183, 216, 255, 0.03),
    var(--shadow);
}

.poster-surface::before {
  inset: auto -6% -14% auto;
  width: 60%;
  background: radial-gradient(circle, rgba(183, 216, 255, 0.16), transparent 72%);
  animation: archivePulse 9s ease-in-out infinite;
}

.poster-surface::after {
  inset: 18px 18px auto auto;
  width: 188px;
  height: 188px;
  border: 1px solid rgba(183, 216, 255, 0.16);
  box-shadow: 0 0 0 14px rgba(183, 216, 255, 0.03);
}

.poster-surface__score strong,
.poster-surface__name {
  text-shadow:
    0 10px 24px rgba(0, 0, 0, 0.24),
    0 0 28px rgba(183, 216, 255, 0.06);
}

.section-head h2 {
  line-height: 0.96;
}

.section-divider {
  background: linear-gradient(90deg, transparent, rgba(183, 216, 255, 0.56), transparent);
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
    linear-gradient(90deg, rgba(183, 216, 255, 0.06), transparent 18%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.018), transparent 70%);
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
  border-top-color: rgba(183, 216, 255, 0.12);
}

.exception-strip:hover,
.story-band:hover,
.feature-row:hover,
.dense-row:hover,
.stack-item:hover,
.insight-panel:hover {
  transform: translateY(-3px);
  border-color: rgba(183, 216, 255, 0.22);
}

.code-panel {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 30%),
    color-mix(in srgb, var(--surface-strong) 90%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    inset 0 0 0 1px rgba(183, 216, 255, 0.03);
}

.footer-note {
  letter-spacing: 0.14em;
}

.memory-page .hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.52) 12%, transparent 42%),
    radial-gradient(circle at 74% 28%, rgba(183, 216, 255, 0.12), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.018), transparent 28%);
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
        "OMEGA HUD V4 / future relic alternate artifact / local only / no external assets",
    ),
    ("OMEGA HUD V2", "OMEGA HUD V4"),
    ("omega-cinematic-v2", "omega-future-relic-v4"),
    ("cinematic alternate artifact", "future relic alternate artifact"),
]

SKILLS_REPLACEMENTS = [
    ("Omega Skills HUD V2", "Omega Skills HUD V4"),
    ("لوحة مهارات أوميجا V2", "لوحة مهارات أوميجا V4"),
    ("نسخة سينمائية بديلة", "نسخة أثرية مستقبلية"),
    ("Cinematic alternate edition", "Future relic edition"),
    ("Taste Upgrade Mode / بلا source drift", "Recovered Relic / بلا source drift"),
    ("Taste Upgrade Mode / no source drift", "Recovered Relic / no source drift"),
    ("أفضل مهارة الآن تقود المشهد:", "اللوح المستعاد من المستقبل ما زال يتوّج:"),
    ("One skill still leads the board:", "Recovered from a future archive, one skill still crowns the slab:"),
    (
        "النسخة دي تحافظ على نفس الحقيقة التشغيلية، لكن تقدمها كواجهة أقرب لغرفة تحكم أوميجا: hero أوضح، rails أنظف، وطبقات أقل تكرارًا من شكل الكروت المعتاد.",
        "هذه النسخة لا تدّعي أنها واجهة جديدة، بل artifact تم فكّه من أرشيف مستقبلي: نفس الحقيقة محفوظة، لكن بسطح أقرب إلى لوح مُكتشف ومُرمَّم.",
    ),
    (
        "This edition keeps the same operational truth, but stages it like an Omega control room: a stronger poster hero, cleaner rails, and less repeated card chrome.",
        "This edition does not pretend to be a new truth. It reads like a recovered artifact from a future Omega archive: the same facts preserved, but staged as a restored slab instead of a control-room screen.",
    ),
    ("شريط الاستثناءات", "طبقة الاستثناءات المحفوظة"),
    ("Exception strip", "Preserved exception layer"),
    ("العمود الفقري للترتيب", "طبقات الكفاءة المنقوشة"),
    ("Editorial efficiency rails", "Inscribed efficiency strata"),
    ("Consolidation map", "Excavated overlap map"),
    ("Cognitive load relief", "Dormant tools registry"),
    ("Forward pressure", "Fragments needing restoration"),
    ("Ledger closeout", "Archive ledger"),
]

MEMORY_REPLACEMENTS = [
    ("Omega Memory Learning Report V2", "Omega Memory Learning Report V4"),
    ("تقرير ذاكرة وتعلّم أوميجا V2", "تقرير ذاكرة وتعلّم أوميجا V4"),
    ("نسخة تحليلية V2", "نسخة أرشيفية مستقبلية"),
    ("Forensic companion edition", "Recovered archive edition"),
    ("Forensic companion / نفس pipeline", "Recovered Archive / نفس pipeline"),
    ("Forensic companion / same pipeline", "Recovered Archive / same pipeline"),
    (
        'الذاكرة <span class="accent">مستقرة</span>، والتعلّم <span class="accent">منضبط</span>، لكن لا يوجد auto-promotion.',
        'الذاكرة خرجت من الحفريات <span class="accent">مستقرة</span>، والتعلّم بقي <span class="accent">منضبطًا</span>، ولا auto-promotion حتى الآن.',
    ),
    (
        'Memory is <span class="accent">stable</span>, learning is <span class="accent">disciplined</span>, and there is still no auto-promotion.',
        'Memory emerged from excavation <span class="accent">stable</span>, learning remained <span class="accent">disciplined</span>, and there is still no auto-promotion.',
    ),
    (
        "هذه النسخة تهدّي الصوت البصري، لكنها تبقي نفس الحقيقة: doctor سليم، backlog ما زال ephemeral بالكامل تقريبًا، وself-learn في وضع observe/report فقط.",
        "النسخة دي تُقرأ كأنها سجل تم اكتشافه لاحقًا: الحقيقة نفسها محفوظة، الطبيب سليم، backlog ما زال شبه ephemeral بالكامل، وself-learn بقي داخل observe/report فقط.",
    ),
    (
        "This edition lowers the visual temperature, but keeps the same truth: doctor is healthy, the backlog is still effectively all-ephemeral, and self-learn stayed in observe/report mode only.",
        "This edition reads like a recovered archive plate from the future: the same truth is preserved, doctor stays healthy, the backlog remains effectively all-ephemeral, and self-learn remained in observe/report only.",
    ),
    ("Durable profile", "Recovered core profile"),
    ("Queue diagnosis", "Excavation queue"),
    ("Self-only boundary", "Sealed self-only boundary"),
    ("Observed vs changed", "Recovered vs rewritten"),
    ("Quality guardrails", "Preservation rules"),
    ("Evidence bundle", "Excavation evidence"),
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
        v2.SHARED_CSS = V4_CSS
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
