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
SKILLS_OUTPUT = OUTPUT_HTML_DIR / "omega-skills-hud-v6.html"
MEMORY_OUTPUT = OUTPUT_HTML_DIR / "omega-memory-learning-report-v6.html"

V6_CSS = v2.SHARED_CSS + """

:root {
  --bg: #050814;
  --bg-soft: #0d1428;
  --surface: rgba(13, 20, 38, 0.82);
  --surface-strong: rgba(18, 28, 52, 0.94);
  --surface-soft: rgba(158, 211, 255, 0.06);
  --line: rgba(158, 211, 255, 0.18);
  --line-strong: rgba(158, 211, 255, 0.42);
  --ink: #edf5ff;
  --muted: rgba(237, 245, 255, 0.76);
  --dim: rgba(237, 245, 255, 0.48);
  --accent: #9ed3ff;
  --accent-strong: #ffffff;
  --accent-soft: rgba(158, 211, 255, 0.14);
  --success: #93d8c7;
  --shadow: 0 42px 110px rgba(0, 4, 16, 0.42);
  --display-font: "Baskerville", "Palatino Linotype", Georgia, serif;
  --body-font: "Segoe UI", Tahoma, Arial, sans-serif;
  --page-max: 1500px;
}

html[data-theme="light"] {
  --bg: #eef3fb;
  --bg-soft: #f8fbff;
  --surface: rgba(255, 255, 255, 0.86);
  --surface-strong: rgba(255, 255, 255, 0.95);
  --surface-soft: rgba(41, 82, 137, 0.05);
  --line: rgba(41, 82, 137, 0.18);
  --line-strong: rgba(41, 82, 137, 0.34);
  --ink: #162033;
  --muted: rgba(22, 32, 51, 0.74);
  --dim: rgba(22, 32, 51, 0.48);
  --accent: #355f9b;
  --accent-strong: #1c3860;
  --accent-soft: rgba(53, 95, 155, 0.12);
  --shadow: 0 28px 72px rgba(38, 55, 92, 0.13);
}

@keyframes vaultBreath {
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

@keyframes naveDrift {
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
    radial-gradient(circle at 18% 12%, rgba(158, 211, 255, 0.14), transparent 24%),
    radial-gradient(circle at 82% 14%, rgba(210, 233, 255, 0.08), transparent 26%),
    linear-gradient(180deg, #121a31 0%, #050814 100%);
}

body::before {
  background:
    linear-gradient(to right, rgba(158, 211, 255, 0.022) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(158, 211, 255, 0.014) 1px, transparent 1px),
    radial-gradient(circle at 78% 18%, rgba(158, 211, 255, 0.08), transparent 14%);
  background-size: 84px 84px, 84px 84px, auto;
  opacity: 0.28;
  mix-blend-mode: screen;
}

body::after {
  background:
    radial-gradient(circle at 50% -10%, rgba(158, 211, 255, 0.12), transparent 42%),
    radial-gradient(circle at 50% 118%, rgba(0, 0, 0, 0.48), transparent 46%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.022), transparent 30%);
  opacity: 0.92;
}

.page-shell::before {
  content: "";
  position: fixed;
  inset: 16px;
  border-radius: 28px;
  border: 1px solid rgba(158, 211, 255, 0.08);
  pointer-events: none;
  opacity: 0.5;
}

.utility-bar {
  top: 12px;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.038), transparent 44%),
    linear-gradient(90deg, rgba(158, 211, 255, 0.06), transparent 22%),
    color-mix(in srgb, var(--surface-strong) 88%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    inset 0 0 0 1px rgba(158, 211, 255, 0.03),
    var(--shadow);
}

.brand-lockup strong {
  letter-spacing: 0.34em;
}

.brand-lockup span {
  letter-spacing: 0.07em;
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
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.045);
}

.control-button {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.07),
    0 8px 24px rgba(0, 0, 0, 0.12);
}

.hero-stage {
  min-height: clamp(640px, calc(100svh - 118px), 940px);
  border-bottom-color: color-mix(in srgb, var(--accent) 34%, transparent);
}

.hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.56) 12%, transparent 42%),
    radial-gradient(circle at 76% 28%, rgba(158, 211, 255, 0.16), transparent 32%),
    linear-gradient(90deg, transparent 0, transparent 44%, rgba(158, 211, 255, 0.08) 50%, transparent 56%, transparent 100%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.018), transparent 30%);
}

.hero-stage::after {
  background:
    repeating-linear-gradient(90deg, rgba(158, 211, 255, 0.028) 0, rgba(158, 211, 255, 0.028) 1px, transparent 1px, transparent 120px),
    repeating-linear-gradient(180deg, rgba(255, 255, 255, 0.022) 0, rgba(255, 255, 255, 0.022) 1px, transparent 1px, transparent 18px),
    radial-gradient(circle at 80% 24%, rgba(158, 211, 255, 0.12), transparent 18%);
  opacity: 0.6;
  animation: naveDrift 12s ease-in-out infinite;
}

.hero-kicker,
.section-kicker,
.eyebrow {
  letter-spacing: 0.24em;
}

.hero-copy h1 {
  text-shadow:
    0 12px 34px rgba(0, 0, 0, 0.32),
    0 0 30px rgba(158, 211, 255, 0.1);
}

.poster-surface {
  min-height: 480px;
  border-radius: 28px 28px 10px 28px;
  background:
    linear-gradient(160deg, rgba(158, 211, 255, 0.12), transparent 24%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.045), transparent 46%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.028), transparent 70%),
    color-mix(in srgb, var(--surface-strong) 93%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.07),
    inset 0 0 0 1px rgba(158, 211, 255, 0.03),
    var(--shadow);
}

.poster-surface::before {
  inset: auto -10% -18% auto;
  width: 66%;
  background: radial-gradient(circle, rgba(158, 211, 255, 0.16), transparent 72%);
  animation: vaultBreath 9s ease-in-out infinite;
}

.poster-surface::after {
  inset: 18px 18px auto auto;
  width: 168px;
  height: 220px;
  border: 1px solid rgba(158, 211, 255, 0.16);
  border-radius: 999px 999px 22px 22px;
  box-shadow: 0 0 0 12px rgba(158, 211, 255, 0.03);
}

.poster-surface__score strong,
.poster-surface__name {
  text-shadow:
    0 10px 22px rgba(0, 0, 0, 0.24),
    0 0 24px rgba(158, 211, 255, 0.08);
}

.section-head h2 {
  line-height: 0.96;
}

.section-divider {
  background: linear-gradient(90deg, transparent, rgba(158, 211, 255, 0.56), transparent);
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
    linear-gradient(90deg, rgba(158, 211, 255, 0.06), transparent 18%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.018), transparent 72%);
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
  border-top-color: rgba(158, 211, 255, 0.12);
}

.exception-strip:hover,
.story-band:hover,
.feature-row:hover,
.dense-row:hover,
.stack-item:hover,
.insight-panel:hover {
  transform: translateY(-3px);
  border-color: rgba(158, 211, 255, 0.22);
}

.code-panel {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 30%),
    color-mix(in srgb, var(--surface-strong) 90%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    inset 0 0 0 1px rgba(158, 211, 255, 0.03);
}

.footer-note {
  letter-spacing: 0.14em;
}

.memory-page .hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.5) 12%, transparent 42%),
    radial-gradient(circle at 74% 28%, rgba(158, 211, 255, 0.11), transparent 30%),
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
        "OMEGA HUD V6 / cathedral terminal alternate artifact / local only / no external assets",
    ),
    ("OMEGA HUD V2", "OMEGA HUD V6"),
    ("omega-cinematic-v2", "omega-cathedral-terminal-v6"),
    ("cinematic alternate artifact", "cathedral terminal alternate artifact"),
]

SKILLS_REPLACEMENTS = [
    ("Omega Skills HUD V2", "Omega Skills HUD V6"),
    ("لوحة مهارات أوميجا V2", "لوحة مهارات أوميجا V6"),
    ("نسخة سينمائية بديلة", "نسخة كاتدرائية تشغيلية"),
    ("Cinematic alternate edition", "Cathedral terminal edition"),
    ("Taste Upgrade Mode / بلا source drift", "Cathedral Signal / بلا source drift"),
    ("Taste Upgrade Mode / no source drift", "Cathedral Signal / no source drift"),
    ("أفضل مهارة الآن تقود المشهد:", "في الكاتدرائية السادسة يظل المذبح التشغيلي باسم:"),
    ("One skill still leads the board:", "In the sixth cathedral, the operational altar still names:"),
    (
        "النسخة دي تحافظ على نفس الحقيقة التشغيلية، لكن تقدمها كواجهة أقرب لغرفة تحكم أوميجا: hero أوضح، rails أنظف، وطبقات أقل تكرارًا من شكل الكروت المعتاد.",
        "النسخة دي تتعامل مع السجل كأنه nave تشغيلية مضيئة: نفس الحقائق محفوظة، لكن متقدمة داخل معمار رأسي أهدى وأفخم من كل الإصدارات السابقة.",
    ),
    (
        "This edition keeps the same operational truth, but stages it like an Omega control room: a stronger poster hero, cleaner rails, and less repeated card chrome.",
        "This edition treats the registry like a luminous operational nave: the same facts preserved, but staged inside a vaulted terminal rather than a flat control surface.",
    ),
    ("شريط الاستثناءات", "ممر الاستثناءات"),
    ("Exception strip", "Exception aisle"),
    ("العمود الفقري للترتيب", "هرمية القبو"),
    ("Editorial efficiency rails", "Vaulted efficiency lanes"),
    ("Consolidation map", "Choir of merges"),
    ("Cognitive load relief", "Dormant side chapels"),
    ("Forward pressure", "Repair nave"),
    ("Ledger closeout", "Terminal colophon"),
]

MEMORY_REPLACEMENTS = [
    ("Omega Memory Learning Report V2", "Omega Memory Learning Report V6"),
    ("تقرير ذاكرة وتعلّم أوميجا V2", "تقرير ذاكرة وتعلّم أوميجا V6"),
    ("نسخة تحليلية V2", "نسخة قدّاس تشغيلي"),
    ("Forensic companion edition", "Cathedral ledger edition"),
    ("Forensic companion / نفس pipeline", "Sanctum Ledger / نفس pipeline"),
    ("Forensic companion / same pipeline", "Sanctum Ledger / same pipeline"),
    (
        'الذاكرة <span class="accent">مستقرة</span>، والتعلّم <span class="accent">منضبط</span>، لكن لا يوجد auto-promotion.',
        'الذاكرة <span class="accent">محروسة</span> داخل القبو، والتعلّم <span class="accent">منضبط</span>، ولا auto-promotion حتى الآن.',
    ),
    (
        'Memory is <span class="accent">stable</span>, learning is <span class="accent">disciplined</span>, and there is still no auto-promotion.',
        'Memory stays <span class="accent">guarded</span> in the vault, learning remains <span class="accent">disciplined</span>, and there is still no auto-promotion.',
    ),
    (
        "هذه النسخة تهدّي الصوت البصري، لكنها تبقي نفس الحقيقة: doctor سليم، backlog ما زال ephemeral بالكامل تقريبًا، وself-learn في وضع observe/report فقط.",
        "النسخة دي تقرأ الحالة كأنها ledger مضيء داخل sanctum: الحقيقة نفسها موجودة، doctor سليم، backlog ما زال شبه ephemeral بالكامل، وself-learn بقي داخل observe/report فقط.",
    ),
    (
        "This edition lowers the visual temperature, but keeps the same truth: doctor is healthy, the backlog is still effectively all-ephemeral, and self-learn stayed in observe/report mode only.",
        "This edition reads the state like a luminous ledger in the sanctum: the same truth remains, doctor stays healthy, the backlog is still effectively all-ephemeral, and self-learn remained in observe/report only.",
    ),
    ("Durable profile", "Vault memory profile"),
    ("Queue diagnosis", "Queue nave"),
    ("Self-only boundary", "Sealed sanctum"),
    ("Observed vs changed", "Observed vs inscribed"),
    ("Quality guardrails", "Preservation rules"),
    ("Evidence bundle", "Proof vault"),
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
        v2.SHARED_CSS = V6_CSS
        skills = base.build_skill_index()
        snapshot = base.build_memory_snapshot()
        base.write_ui_skill_contract_artifacts(base.build_ui_skill_guide_payload())
        skills_html = restyle_document(v2.build_skills_page(skills), "skills")
        memory_html = restyle_document(v2.build_memory_page(skills, snapshot), "memory")
        SKILLS_OUTPUT.write_text(skills_html, encoding="utf-8")
        MEMORY_OUTPUT.write_text(memory_html, encoding="utf-8")
    finally:
        v2.SHARED_CSS = original_css

    print("Wrote:")
    print(SKILLS_OUTPUT)
    print(MEMORY_OUTPUT)
    print(base.UI_SKILLS_BOUNDARY_GUIDE_MD)
    print(base.UI_SKILLS_BOUNDARY_CONTRACT_JSON)


if __name__ == "__main__":
    main()
