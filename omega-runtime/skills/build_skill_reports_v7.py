#!/usr/bin/env python3

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v4 as v4


ROOT = base.ROOT
OUTPUT_HTML_DIR = ROOT / "output/html"
SKILLS_OUTPUT = OUTPUT_HTML_DIR / "omega-skills-hud-v7.html"
MEMORY_OUTPUT = OUTPUT_HTML_DIR / "omega-memory-learning-report-v7.html"

V7_CSS = v4.V4_CSS + """

:root {
  --page-max: 1540px;
  --accent-veil: rgba(183, 216, 255, 0.11);
  --accent-veil-strong: rgba(183, 216, 255, 0.18);
  --brass: rgba(214, 190, 147, 0.16);
}

html[data-theme="light"] {
  --accent-veil: rgba(75, 111, 147, 0.10);
  --accent-veil-strong: rgba(75, 111, 147, 0.16);
  --brass: rgba(132, 107, 74, 0.10);
}

html[data-theme="light"] {
  background:
    radial-gradient(circle at 14% 12%, rgba(75, 111, 147, 0.18), transparent 24%),
    radial-gradient(circle at 82% 12%, rgba(132, 107, 74, 0.10), transparent 30%),
    linear-gradient(180deg, #f7f2ea 0%, #ebe3d6 100%);
}

html[data-theme="light"] body::before {
  opacity: 0.14;
  mix-blend-mode: multiply;
}

html[data-theme="light"] body::after {
  background:
    radial-gradient(circle at 50% -8%, rgba(75, 111, 147, 0.16), transparent 38%),
    radial-gradient(circle at 50% 112%, rgba(132, 107, 74, 0.08), transparent 44%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.32), transparent 34%);
}

html[data-theme="light"] .utility-bar {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 255, 255, 0.42)),
    linear-gradient(90deg, rgba(75, 111, 147, 0.08), transparent 24%),
    color-mix(in srgb, var(--surface-strong) 94%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.88),
    inset 0 0 0 1px rgba(75, 111, 147, 0.05),
    0 20px 56px rgba(77, 60, 35, 0.14);
}

html[data-theme="light"] .utility-bar::after {
  background: linear-gradient(110deg, transparent 0%, transparent 38%, rgba(75, 111, 147, 0.12) 50%, transparent 62%, transparent 100%);
  opacity: 0.44;
}

html[data-theme="light"] .hero-stage::before {
  background:
    linear-gradient(132deg, rgba(255, 255, 255, 0.34) 6%, transparent 40%),
    radial-gradient(circle at 74% 24%, rgba(75, 111, 147, 0.20), transparent 26%),
    radial-gradient(circle at 76% 26%, rgba(132, 107, 74, 0.08), transparent 42%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.26), transparent 34%);
}

html[data-theme="light"] .hero-stage::after {
  background:
    repeating-linear-gradient(180deg, rgba(75, 111, 147, 0.04) 0, rgba(75, 111, 147, 0.04) 1px, transparent 1px, transparent 12px),
    repeating-linear-gradient(90deg, rgba(132, 107, 74, 0.025) 0, rgba(132, 107, 74, 0.025) 1px, transparent 1px, transparent 72px),
    radial-gradient(circle at 80% 22%, rgba(75, 111, 147, 0.14), transparent 19%);
  opacity: 0.58;
}

html[data-theme="light"] .hero-copy h1,
html[data-theme="light"] .poster-surface__score strong,
html[data-theme="light"] .poster-surface__name {
  text-shadow:
    0 10px 24px rgba(255, 255, 255, 0.35),
    0 0 18px rgba(75, 111, 147, 0.08);
}

html[data-theme="light"] .poster-surface {
  background:
    linear-gradient(162deg, rgba(75, 111, 147, 0.12), transparent 24%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.62), transparent 44%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.4), transparent 68%),
    color-mix(in srgb, var(--surface-strong) 97%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.84),
    inset 0 0 0 1px rgba(75, 111, 147, 0.05),
    0 28px 60px rgba(77, 60, 35, 0.14);
}

html[data-theme="light"] .poster-surface::before {
  background:
    radial-gradient(circle, rgba(75, 111, 147, 0.18), transparent 68%),
    radial-gradient(circle at 28% 36%, rgba(132, 107, 74, 0.08), transparent 36%);
}

html[data-theme="light"] .poster-surface::after {
  border-color: rgba(75, 111, 147, 0.20);
  box-shadow:
    0 0 0 14px rgba(75, 111, 147, 0.04),
    0 0 0 38px rgba(132, 107, 74, 0.03);
}

html[data-theme="light"] .section-block::before {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.28), transparent 26%),
    radial-gradient(circle at 10% 8%, var(--accent-veil), transparent 24%);
}

html[data-theme="light"] .tier-band,
html[data-theme="light"] .dense-cluster {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.44), transparent 30%),
    linear-gradient(90deg, rgba(75, 111, 147, 0.08), transparent 18%);
  border-color: rgba(75, 111, 147, 0.11);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    0 12px 28px rgba(77, 60, 35, 0.06);
}

html[data-theme="light"] .exception-strip,
html[data-theme="light"] .story-band,
html[data-theme="light"] .feature-row,
html[data-theme="light"] .dense-row,
html[data-theme="light"] .stack-item,
html[data-theme="light"] .insight-panel {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.7),
    0 18px 38px rgba(77, 60, 35, 0.08);
}

html[data-theme="light"] .story-band::after,
html[data-theme="light"] .insight-panel::after,
html[data-theme="light"] .code-panel::before {
  background: linear-gradient(90deg, transparent, rgba(75, 111, 147, 0.28), transparent);
}

html[data-theme="light"] .source-list a,
html[data-theme="light"] .fact-list li,
html[data-theme="light"] .report-list li,
html[data-theme="light"] .fact-row {
  background:
    linear-gradient(90deg, rgba(75, 111, 147, 0.05), transparent 24%);
}

html[data-theme="light"] .memory-page .hero-stage::before {
  background:
    linear-gradient(132deg, rgba(255, 255, 255, 0.30) 6%, transparent 40%),
    radial-gradient(circle at 74% 24%, rgba(75, 111, 147, 0.16), transparent 28%),
    radial-gradient(circle at 74% 24%, rgba(132, 107, 74, 0.05), transparent 44%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.26), transparent 30%);
}

@keyframes relicLift {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, -8px, 0);
  }
}

@keyframes relicSweep {
  0% {
    transform: translateX(-20%);
    opacity: 0;
  }
  20% {
    opacity: 0.18;
  }
  80% {
    opacity: 0.08;
  }
  100% {
    transform: translateX(20%);
    opacity: 0;
  }
}

html {
  background:
    radial-gradient(circle at 14% 12%, rgba(183, 216, 255, 0.14), transparent 22%),
    radial-gradient(circle at 82% 12%, rgba(214, 190, 147, 0.08), transparent 28%),
    linear-gradient(180deg, #171d27 0%, #06080c 100%);
}

body::before {
  opacity: 0.22;
}

body::after {
  background:
    radial-gradient(circle at 50% -8%, rgba(183, 216, 255, 0.14), transparent 36%),
    radial-gradient(circle at 50% 112%, rgba(214, 190, 147, 0.06), transparent 42%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 34%);
}

.utility-bar {
  overflow: hidden;
}

.utility-bar::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, transparent 38%, rgba(183, 216, 255, 0.10) 50%, transparent 62%, transparent 100%);
  pointer-events: none;
  opacity: 0.5;
  animation: relicSweep 11s linear infinite;
}

.brand-lockup strong {
  font-size: 13px;
}

.hero-stage {
  left: auto;
  right: auto;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  min-height: clamp(660px, calc(100svh - 108px), 960px);
}

.hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.60) 10%, transparent 42%),
    radial-gradient(circle at 74% 24%, rgba(183, 216, 255, 0.19), transparent 26%),
    radial-gradient(circle at 76% 26%, rgba(214, 190, 147, 0.08), transparent 42%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.022), transparent 34%);
}

.hero-stage::after {
  background:
    repeating-linear-gradient(180deg, rgba(183, 216, 255, 0.03) 0, rgba(183, 216, 255, 0.03) 1px, transparent 1px, transparent 12px),
    repeating-linear-gradient(90deg, rgba(214, 190, 147, 0.02) 0, rgba(214, 190, 147, 0.02) 1px, transparent 1px, transparent 72px),
    radial-gradient(circle at 80% 22%, rgba(183, 216, 255, 0.13), transparent 19%);
  opacity: 0.68;
}

.hero-copy {
  max-width: 720px;
}

.hero-copy h1 {
  max-width: 11ch;
  font-size: clamp(3.2rem, 6vw, 6.2rem);
}

.muted-copy {
  max-width: 64ch;
}

.poster-surface,
.memory-page .poster-surface {
  min-height: 510px;
  overflow: hidden;
  isolation: isolate;
}

.poster-surface::before {
  background:
    radial-gradient(circle, rgba(183, 216, 255, 0.20), transparent 68%),
    radial-gradient(circle at 28% 36%, rgba(214, 190, 147, 0.08), transparent 36%);
}

.poster-surface::after {
  width: 198px;
  height: 198px;
  border-color: rgba(183, 216, 255, 0.22);
  box-shadow:
    0 0 0 14px rgba(183, 216, 255, 0.03),
    0 0 0 38px rgba(214, 190, 147, 0.02);
}

.poster-surface__headline,
.poster-surface__meta {
  position: relative;
  z-index: 1;
}

.poster-surface__score {
  padding-block: 4px;
}

.section-block {
  position: relative;
  overflow: clip;
}

.section-block::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.016), transparent 26%),
    radial-gradient(circle at 10% 8%, var(--accent-veil), transparent 24%);
  opacity: 0.9;
  pointer-events: none;
}

.section-head,
.section-divider,
.band-stack,
.dense-grid,
.story-stack,
.split-grid,
.stack-list,
.exception-grid,
.insight-grid {
  position: relative;
  z-index: 1;
}

.section-head h2 {
  max-width: 12ch;
}

.section-copy,
.rail-copy {
  max-width: 72ch;
}

.section-divider {
  height: 2px;
  background:
    linear-gradient(90deg, transparent, rgba(183, 216, 255, 0.56), rgba(214, 190, 147, 0.22), transparent);
}

.tier-band,
.dense-cluster {
  border-radius: 24px;
  padding: 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 30%),
    linear-gradient(90deg, var(--accent-veil), transparent 18%);
  border: 1px solid rgba(183, 216, 255, 0.09);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.exception-strip,
.story-band,
.feature-row,
.dense-row,
.stack-item,
.insight-panel {
  backdrop-filter: blur(14px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 22px 42px rgba(0, 0, 0, 0.18);
}

.exception-strip:hover,
.story-band:hover,
.feature-row:hover,
.dense-row:hover,
.stack-item:hover,
.insight-panel:hover {
  transform: translateY(-4px);
  border-color: rgba(183, 216, 255, 0.28);
}

.story-band {
  position: relative;
}

.story-band::after,
.insight-panel::after {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(183, 216, 255, 0.28), transparent);
  pointer-events: none;
}

.tag-row,
.meta-inline,
.token-row {
  row-gap: 8px;
}

.metric-pill,
.control-readout,
.inline-tag,
.score-chip,
.tier-token,
.tier-kicker,
.code-tag {
  backdrop-filter: blur(10px);
}

.control-button {
  min-width: 124px;
}

.control-button:hover {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 12px 28px rgba(0, 0, 0, 0.16);
}

.source-list a,
.fact-list li,
.report-list li,
.fact-row {
  background:
    linear-gradient(90deg, rgba(183, 216, 255, 0.035), transparent 24%);
}

.code-panel {
  position: relative;
}

.code-panel::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(183, 216, 255, 0.32), transparent);
}

.footer-note {
  padding-top: 12px;
  opacity: 0.82;
}

.memory-page .hero-stage::before {
  background:
    linear-gradient(132deg, rgba(0, 0, 0, 0.54) 10%, transparent 40%),
    radial-gradient(circle at 74% 24%, rgba(183, 216, 255, 0.14), transparent 28%),
    radial-gradient(circle at 74% 24%, rgba(214, 190, 147, 0.05), transparent 44%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.018), transparent 30%);
}

.memory-page .poster-surface {
  animation: relicLift 12s ease-in-out infinite;
}

@media (max-width: 1080px) {
  .hero-copy h1 {
    max-width: none;
  }

  .poster-surface,
  .memory-page .poster-surface {
    min-height: 460px;
  }
}

@media (max-width: 900px) {
  .utility-bar::after,
  .section-block::before,
  .memory-page .poster-surface {
    animation: none;
  }
}

@media (max-width: 640px) {
  .hero-stage {
    min-height: auto;
  }

  .hero-copy h1 {
    font-size: clamp(2.5rem, 13vw, 3.7rem);
  }

  .tier-band,
  .dense-cluster {
    padding: 12px;
  }

  .control-button {
    min-width: 0;
    width: 100%;
  }
}
"""

COMMON_REPLACEMENTS = [
    (
        "OMEGA HUD V4 / future relic alternate artifact / local only / no external assets",
        "OMEGA HUD V7 / future relic mastered artifact / local only / no external assets",
    ),
    ("OMEGA HUD V4", "OMEGA HUD V7"),
    ("omega-future-relic-v4", "omega-future-relic-v7"),
    ("future relic alternate artifact", "future relic mastered artifact"),
]

SKILLS_REPLACEMENTS = [
    ("Omega Skills HUD V4", "Omega Skills HUD V7"),
    ("لوحة مهارات أوميجا V4", "لوحة مهارات أوميجا V7"),
    ("نسخة أثرية مستقبلية", "نسخة أثرية مستقبلية مُحكمة"),
    ("Future relic edition", "Mastered future relic edition"),
    ("Recovered Relic / بلا source drift", "Recovered Relic Prime / بلا source drift"),
    ("Recovered Relic / no source drift", "Recovered Relic Prime / no source drift"),
    ("اللوح المستعاد من المستقبل ما زال يتوّج:", "اللوح المستعاد بعد الترميم الكامل ما زال يتوّج:"),
    ("Recovered from a future archive, one skill still crowns the slab:", "After full restoration, one skill still crowns the slab:"),
    (
        "هذه النسخة لا تدّعي أنها واجهة جديدة، بل artifact تم فكّه من أرشيف مستقبلي: نفس الحقيقة محفوظة، لكن بسطح أقرب إلى لوح مُكتشف ومُرمَّم.",
        "هذه النسخة تعود إلى اللوح الذي أثبت نفسه: نفس الحقيقة محفوظة، لكن بعد ترميم كامل وضمّ أحدث العقود والتحديثات من دون كسر العربي أو سلوك التحويل.",
    ),
    (
        "This edition does not pretend to be a new truth. It reads like a recovered artifact from a future Omega archive: the same facts preserved, but staged as a restored slab instead of a control-room screen.",
        "This edition returns to the slab that proved itself: the same facts preserved, now fully restored and updated with the latest contracts without breaking Arabic rendering or switch behavior.",
    ),
    ("طبقة الاستثناءات المحفوظة", "طبقة الاستثناءات المختومة"),
    ("Preserved exception layer", "Sealed exception layer"),
    ("Excavated overlap map", "Restored overlap map"),
    ("Dormant tools registry", "Dormant tools register"),
    ("Fragments needing restoration", "Pressure points still needing restoration"),
    ("Archive ledger", "Prime archive ledger"),
]

MEMORY_REPLACEMENTS = [
    ("Omega Memory Learning Report V4", "Omega Memory Learning Report V7"),
    ("تقرير ذاكرة وتعلّم أوميجا V4", "تقرير ذاكرة وتعلّم أوميجا V7"),
    ("نسخة أرشيفية مستقبلية", "نسخة أرشيفية مستقبلية مُحكمة"),
    ("Recovered archive edition", "Mastered archive edition"),
    ("Recovered Archive / نفس pipeline", "Recovered Archive Prime / نفس pipeline"),
    ("Recovered Archive / same pipeline", "Recovered Archive Prime / same pipeline"),
    (
        'الذاكرة خرجت من الحفريات <span class="accent">مستقرة</span>، والتعلّم بقي <span class="accent">منضبطًا</span>، ولا auto-promotion حتى الآن.',
        'الذاكرة بقيت <span class="accent">مستقرة</span> بعد الترميم، والتعلّم ظل <span class="accent">منضبطًا</span>، وما زال لا يوجد auto-promotion.',
    ),
    (
        'Memory emerged from excavation <span class="accent">stable</span>, learning remained <span class="accent">disciplined</span>, and there is still no auto-promotion.',
        'Memory stayed <span class="accent">stable</span> after restoration, learning remained <span class="accent">disciplined</span>, and there is still no auto-promotion.',
    ),
    (
        "النسخة دي تُقرأ كأنها سجل تم اكتشافه لاحقًا: الحقيقة نفسها محفوظة، الطبيب سليم، backlog ما زال شبه ephemeral بالكامل، وself-learn بقي داخل observe/report فقط.",
        "النسخة دي تأخذ السجل المستعاد وتثبّته: نفس الحقيقة التشغيلية، doctor سليم، backlog ما زال شبه ephemeral بالكامل، لكن العرض نفسه أصبح أوضح وأهدأ وأقرب للمرجع الموثوق.",
    ),
    (
        "This edition reads like a recovered archive plate from the future: the same truth is preserved, doctor stays healthy, the backlog remains effectively all-ephemeral, and self-learn remained in observe/report only.",
        "This edition stabilizes the recovered ledger: the same operational truth remains, doctor stays healthy, the backlog is still effectively all-ephemeral, and the presentation is calmer and more trustworthy.",
    ),
    ("Recovered core profile", "Restored core profile"),
    ("Excavation queue", "Restored queue state"),
    ("Sealed self-only boundary", "Sealed self-only contract"),
    ("Recovered vs rewritten", "Observed vs restored"),
    ("Preservation rules", "Preservation and proof rules"),
    ("Excavation evidence", "Restoration evidence"),
]

SKILLS_AR_SPAN_FIXES = {
    "مهارات Top-Level": "مهارات المستوى الأعلى",
    "Recovered Relic Prime / بلا source drift": "اللوح المستعاد المحكم / بلا انحراف عن المصدر",
    "قوة المهارة هنا جاية من leverage كبير في التخطيط، صياغة المسار، وتقليل التخمين قبل التنفيذ.": "قوة المهارة هنا جاية من رافعة كبيرة في التخطيط، وصياغة المسار، وتقليل التخمين قبل التنفيذ.",
    "System Exceptions خارج المقارنة": "الاستثناءات النظامية خارج المقارنة",
    "Efficiency Tiers كسكك تشغيلية": "طبقات الكفاءة كسكك تشغيلية",
    "15 skill": "15 مهارة",
    "13 skill": "13 مهارة",
    "Restored overlap map": "خريطة التداخل بعد الترميم",
    "Merge Candidates كحكايات دمج": "مرشحو الدمج كحكايات تداخل",
    "المقصود هنا ليس تشغيل المهارات معًا دائمًا، بل تحديد المجموعات التي فيها overlap أو handoff يمكن تقليله بواجهة أو contract أوضح.": "المقصود هنا ليس تشغيل المهارات معًا دائمًا، بل تحديد المجموعات التي فيها تداخل أو كلفة تمرير يمكن تقليلها بواجهة أو عقد أوضح.",
    "UI cluster contract": "عقد عنقود الواجهة",
    "هذا العنقود ليس stack إلزامي يمر عليه كل طلب. هو خريطة routing: من يبدأ، من يراجع، ومتى تتوقف passes حتى لا يحدث drift.": "هذا العنقود ليس مسارًا إلزاميًا يمر عليه كل طلب. هو خريطة توجيه: من يبدأ، ومن يراجع، ومتى تتوقف المراحل حتى لا يحدث انحراف.",
    "Governance overlay / ليست UI peers": "طبقة الحوكمة / ليست نظيرات واجهة",
    "هذه الطبقة تدخل فقط عندما تكون الخطة أو الوثائق أو proof package قادرة على تغيير القرار.": "هذه الطبقة تدخل فقط عندما تكون الخطة أو الوثائق أو حزمة الإثبات قادرة على تغيير القرار.",
    "Authority + handoff order": "تسلسل السلطة والتمرير",
    "في التعارض: user instruction ثم constraints ثم source truth ثم product flow ثم design system ثم visual taste.": "عند التعارض: تعليمات المستخدم ثم القيود ثم حقيقة المصدر ثم تدفق المنتج ثم نظام التصميم ثم الذوق البصري.",
    "Orchestration": "التنسيق القيادي",
    "يحدد mode التنفيذ، يحمي العناصر غير القابلة للكسر، ويرتّب المهارات الصحيحة بالترتيب الصحيح.": "يحدد نمط التنفيذ، ويحمي العناصر غير القابلة للكسر، ويرتّب المهارات الصحيحة بالترتيب الصحيح.",
    "أول اختيار: المهمة فيها أكثر من محور واحد: source + UX + taste + system أو فيها protected elements واضحة.": "أول اختيار: المهمة فيها أكثر من محور واحد مثل المصدر وUX والذوق والنظام، أو فيها عناصر محمية واضحة.",
    "لا تستخدمه عندما: الطلب narrow وواضح ويحتاج pass واحد مباشر مثل visual critique فقط أو landing execution فقط.": "لا تستخدمه عندما: الطلب ضيق وواضح ويحتاج تمريرة واحدة مباشرة مثل نقد بصري فقط أو تنفيذ صفحة فقط.",
    "ما يجب حمايته: user instruction, task constraints, source truth, cta intent, product-critical flow, information architecture": "ما يجب حمايته: تعليمات المستخدم، وقيود المهمة، وحقيقة المصدر، ونية CTA، والتدفق الحرج للمنتج، وبنية المعلومات.",
    "Single-pass visual doctrine": "عقيدة بصرية بتمريرة واحدة",
    "يدفع التنفيذ إلى composition أقوى، hierarchy أوضح، motion intentional، وواجهة غير generic.": "يدفع التنفيذ إلى تكوين أقوى، وتسلسل هرمي أوضح، وحركة مقصودة، وواجهة غير نمطية.",
    "أول اختيار: الطلب net-new branded landing أو demo أو surface ذوقي تقوده art direction وليس source/flow/system complexity.": "أول اختيار: الطلب صفحة جديدة بعلامة واضحة أو demo أو واجهة يقودها التوجه الفني أكثر من تعقيد المصدر أو التدفق أو النظام.",
    "لا تستخدمه عندما: المشكلة الأساسية Figma parity أو UX flow repair أو design-system drift أو protected elements معقدة.": "لا تستخدمه عندما: المشكلة الأساسية هي مطابقة فيجما أو إصلاح تدفق UX أو انحراف نظام التصميم أو عناصر محمية معقدة.",
    "ما يجب حمايته: visual anchor, brand-first hierarchy, sparse copy discipline, no-cards-by-default bias": "ما يجب حمايته: المرساة البصرية، وتسلسل العلامة أولًا، وانضباط النص المختصر، والانحياز لعدم استخدام الكروت افتراضيًا.",
    "Source governance": "حوكمة المصدر",
    "يقرأ Figma، يستخرج structure قابل للتنفيذ، يوسم deviations، ويتحقق من parity.": "يقرأ فيجما، ويستخرج بنية قابلة للتنفيذ، ويضع وسمًا للانحرافات، ويتحقق من المطابقة.",
    "ابدأ عندما: هناك Figma link أو frame أو node أو طلب parity source-based.": "ابدأ عندما: يوجد رابط فيجما أو frame أو node أو طلب مطابقة مبني على المصدر.",
    "فشل شائع: قراءة screenshot-only أو ادعاء parity بدون evidence.": "فشل شائع: الاعتماد على screenshot فقط أو ادعاء المطابقة بدون دليل.",
    "Product flow diagnosis": "تشخيص تدفق المنتج",
    "يفحص goal clarity، الأولوية بين الأفعال، friction، trust، والحالات الناقصة.": "يفحص وضوح الهدف، وأولوية الأفعال، والاحتكاك، والثقة، والحالات الناقصة.",
    "ابدأ عندما: المشكلة الأساسية ليست الشكل بل task path أو conversion أو next-step clarity.": "ابدأ عندما: المشكلة الأساسية ليست الشكل بل مسار المهمة أو التحويل أو وضوح الخطوة التالية.",
    "فشل شائع: حل بصري جميل لكن task path ما زال مكسورًا.": "فشل شائع: حل بصري جميل لكن مسار المهمة ما زال مكسورًا.",
    "Visual critique": "نقد بصري",
    "يرتّب مشاكل hierarchy وspacing وCTA emphasis وpolish حسب التأثير.": "يرتّب مشاكل التسلسل الهرمي، والمسافات، وتركيز CTA، والصقل البصري حسب التأثير.",
    "ابدأ عندما: الواجهة موجودة بالفعل والمطلوب sharper taste أو critique واضح لا إعادة هيكلة منتج كاملة.": "ابدأ عندما: الواجهة موجودة بالفعل والمطلوب ذوق أكثر حدة أو نقد واضح، لا إعادة هيكلة كاملة للمنتج.",
    "فشل شائع: مجاملة غامضة أو critique بلا ترتيب أولويات.": "فشل شائع: مجاملة غامضة أو نقد بلا ترتيب أولويات.",
    "System discipline": "انضباط النظام",
    "يعيد النظام إلى الواجهة: tokens، button roles، states، spacing scale، والـresponsive invariants.": "يعيد النظام إلى الواجهة: الـ tokens، وأدوار الأزرار، والحالات، ومقياس المسافات، وثوابت الـ responsive.",
    "ابدأ عندما: هناك drift في الأزرار أو الحقول أو المسافات أو الحالات أو قواعد الـresponsive.": "ابدأ عندما: يوجد انحراف في الأزرار أو الحقول أو المسافات أو الحالات أو قواعد الـ responsive.",
    "فشل شائع: اعتبار أي taste preference مشكلة نظام.": "فشل شائع: اعتبار أي تفضيل ذوقي مشكلة نظام.",
    "Guided implementation": "تنفيذ موجَّه",
    "ينفذ pass واجهة أقوى تحت mode واضح وقيود معلنة بدل premium decoration العشوائي.": "ينفذ تمريرة واجهة أقوى تحت نمط واضح وقيود معلنة بدل الزخرفة العشوائية.",
    "ابدأ عندما: نحتاج تنفيذ refinement أو redesign controlled بعد وجود source/flow/taste/system inputs.": "ابدأ عندما: نحتاج refinement أو redesign مضبوط بعد وجود مدخلات المصدر أو التدفق أو الذوق أو النظام.",
    "فشل شائع: premium شكلي بلا تحسن بنيوي.": "فشل شائع: مظهر فاخر بلا تحسن بنيوي.",
    "Figma parity": "مطابقة فيجما",
    "Visual cleanup only": "تنظيف بصري فقط",
    "UX / conversion issue": "مشكلة UX / التحويل",
    "Design-system drift": "انحراف نظام التصميم",
    "Net-new branded landing": "صفحة جديدة بعلامة واضحة",
    "Dashboard / task clarity weak": "لوحة / وضوح المهمة ضعيف",
    "Canonical artifacts": "الـ artifacts المرجعية",
    "الشرح الطويل يظل canonical في guide markdown، بينما الـHUD يعرض نسخة مكثفة منه فقط.": "الشرح الطويل يظل المرجع الأساسي في guide markdown، بينما يعرض الـ HUD نسخة مكثفة منه فقط.",
    "Why content is canonical and HUD is render": "لماذا المحتوى مرجعي والـ HUD مجرد عرض",
    "مراجعة OpenAI الرسمية هنا استخدمت فقط لتثبيت قاعدة فصل المحتوى المرجعي عن طبقة العرض، لا لتحويل `openai-docs` إلى UI skill داخل العنقود.": "مراجعة OpenAI الرسمية هنا استُخدمت فقط لتثبيت فصل المحتوى المرجعي عن طبقة العرض، لا لتحويل `openai-docs` إلى مهارة UI داخل العنقود.",
    "`frontend-skill` ليس orchestrator، وليس critique framework، وليس design-system enforcer. و`omega_ui_product_brain` ليس منفذ UI بحد ذاته.": "`frontend-skill` ليس منسقًا، وليس إطار نقد، وليس ضابط نظام تصميم. و`omega_ui_product_brain` ليس منفذ واجهة بحد ذاته.",
    "Dormant tools register": "سجل الأدوات الخاملة",
    "Retire / Skip Candidates كقائمة تخفيف": "مرشحو الاستبعاد / التجاوز كقائمة تخفيف",
    "خليها موجودة، لكن اعتبرها macro تشغيلية عند الطلب فقط.": "خليها موجودة، لكن اعتبرها ماكرو تشغيلية عند الطلب فقط.",
    "الأفضل اعتبارها endpoint متخصص وليس مسارًا نفكر فيه باستمرار.": "الأفضل اعتبارها نقطة نهاية متخصصة، لا مسارًا نفكر فيه باستمرار.",
    "تعامل معها كأداة audit متخصصة، لا كمهارة مراجعة افتراضية.": "تعامل معها كأداة تدقيق متخصصة، لا كمهارة مراجعة افتراضية.",
    "Pressure points still needing restoration": "نقاط الضغط التي ما زالت تحتاج ترميمًا",
    "Improve Next كخريطة ضغط": "التحسين القادم كخريطة ضغط",
    "تحتاج أمثلة failure modes أوضح وتحققًا أقوى للـ shared formatter.": "تحتاج أمثلة أوضح لحالات الفشل وتحققًا أقوى للمنسق المشترك.",
    "القدرة نفسها قوية، لكن اعتمادها على جودة MCP search وعلى docs سريعة التغير يستحق tightening مستمر.": "القدرة نفسها قوية، لكن اعتمادها على جودة بحث MCP وعلى docs سريعة التغير يستحق إحكامًا مستمرًا.",
    "الأولوية: تحسين جلب الـ canonical URLs وتثبيت fallback الرسمي بشكل أوضح.": "الأولوية: تحسين جلب الروابط المرجعية الأساسية وتثبيت fallback الرسمي بشكل أوضح.",
    "مهارة عالية الرافعة في تصميم أنظمة الذكاء، لكنها مبنية فوق guidance متغير في الموديلات والسطوح.": "مهارة عالية الرافعة في تصميم أنظمة الذكاء، لكنها مبنية فوق إرشادات متغيرة في الموديلات والسطوح.",
    "تحتاج تحديثًا مستمرًا للـ decision grid وربطًا أوضح بالـ docs الحالية.": "تحتاج تحديثًا مستمرًا لجدول القرار وربطًا أوضح بالـ docs الحالية.",
    "تحتاج reporting أوضح ومعايير ترقية أدق للتعلّمات القابلة لإعادة الاستخدام فعلًا.": "تحتاج reporting أوضح ومعايير ترقية أدق للتعلّمات القابلة لإعادة الاستخدام فعلًا.",
    "المطلوب: حدود أدق أمام orchestration والنقد وdesign-system enforcement.": "المطلوب: حدود أدق أمام التنسيق القيادي، والنقد، وضبط نظام التصميم.",
    "Prime archive ledger": "سجل الأرشيف المحكم",
    "Registry Notes And Sources": "ملاحظات السجل ومصادره",
    "تمت إضافة 5 أوصاف ناقصة: frontend-skill, omega-ai-runtime, omega-format, omega-proof-gate, omega-repo-map": "تمت إضافة 5 أوصاف ناقصة: frontend-skill وomega-ai-runtime وomega-format وomega-proof-gate وomega-repo-map",
    "إجمالي السجل الحالي 39 entry = 37 top-level + 2 system exceptions": "إجمالي السجل الحالي 39 عنصرًا = 37 مهارة مستوى أعلى + 2 استثناءين نظاميين",
}

MEMORY_AR_SPAN_FIXES = {
    "Pending backlog": "قائمة الانتظار المعلقة",
    "Recovered Archive Prime / نفس pipeline": "الأرشيف المستعاد المحكم / نفس المسار",
    "النسخة دي تأخذ السجل المستعاد وتثبّته: نفس الحقيقة التشغيلية، doctor سليم، backlog ما زال شبه ephemeral بالكامل، لكن العرض نفسه أصبح أوضح وأهدأ وأقرب للمرجع الموثوق.": "النسخة دي تأخذ السجل المستعاد وتثبّته: نفس الحقيقة التشغيلية، وحالة doctor سليمة، وقائمة الانتظار ما زالت شبه ephemeral بالكامل، لكن العرض نفسه أصبح أوضح وأهدأ وأقرب للمرجع الموثوق.",
    "doctor صالح": "حالة doctor سليمة",
    "pending لا يزال 40": "قائمة الانتظار ما زالت 40",
    "لا يوجد promotable durable": "لا يوجد عنصر durable صالح للترقية",
    "لا auto-promotion": "لا توجد ترقية تلقائية",
    "pending": "معلق",
    "backlog قابل للقراءة، لكنه غير قابل للترقية": "قائمة الانتظار قابلة للقراءة، لكنها غير قابلة للترقية",
    "القراءة الحالية مبنية على inspect / triage / suggest / doctor / self-learn report من نفس جلسة التوليد.": "القراءة الحالية مبنية على inspect وtriage وsuggest وdoctor وself-learn report من نفس جلسة التوليد.",
    "Restored core profile": "الملف الأساسي بعد الترميم",
    "Persistent Memory / الملف durable": "Persistent Memory / الملف الدائم",
    "تفضيلات التعاون durable": "تفضيلات التعاون الدائمة",
    "Restored queue state": "حالة الطابور بعد الترميم",
    "Triage + Backlog Distribution": "triage وتوزيع قائمة الانتظار",
    "القسم ده يوضح لماذا backlog ما زال غير قابل للترقية: no conflicts، لكن no promotable durable candidate أيضًا.": "القسم ده يوضح لماذا قائمة الانتظار ما زالت غير قابلة للترقية: لا توجد conflicts، لكن لا يوجد أيضًا عنصر durable صالح للترقية.",
    "نتيجة triage الحالية": "نتيجة triage الحالية",
    "خلاصة القراءة: كل ما تبقى تقريبًا ephemeral، لذلك الترقية غير مبررة ضمن policy الحالية.": "خلاصة القراءة: كل ما تبقى تقريبًا ephemeral، لذلك الترقية غير مبررة ضمن السياسة الحالية.",
    "توزيع مفاتيح الـ backlog": "توزيع مفاتيح قائمة الانتظار",
    "Sealed self-only contract": "عقد self-only المختوم",
    "Self Learn / health + event ledger": "Self Learn / الصحة وسجل الأحداث",
    "في هذه المهمة لم يحدث apply جديد داخل self-learn. المطلوب كان قراءة الحالة الحالية وعرضها بوضوح فقط.": "في هذه المهمة لم يحدث apply جديد داخل self-learn. المطلوب كان قراءة الحالة الحالية وعرضها بوضوح فقط.",
    "آخر حدث reversible": "آخر حدث قابل للعكس",
    "Observed vs restored": "المرصود مقابل المرمم",
    "What Changed": "ما الذي تغيّر",
    "القسم ده يفصل بين ما تم تحديثه فعليًا في workspace، وما تم رصده فقط بدون mutation إضافي.": "القسم ده يفصل بين ما تم تحديثه فعليًا في workspace، وما تم رصده فقط بدون أي mutation إضافية.",
    "إجمالي السجل الآن 39 entry منها 37 top-level": "إجمالي السجل الآن 39 عنصرًا، منها 37 مهارة من المستوى الأعلى",
    "تمت إزالة الاستثناء المكسور `arabic-output-guard` من النسخة التشغيلية لأنه بلا مصدر": "تمت إزالة الاستثناء المكسور `arabic-output-guard` من النسخة التشغيلية لأنه بلا مصدر فعلي",
    "الـ pending الحالي = 40 والفرق مقابل آخر baseline محفوظ = +32": "عدد العناصر المعلقة الحالي = 40 والفرق مقابل آخر baseline محفوظ = +32",
    "لم يتم promote أو forget أو rollback على ذاكرة المشروع في هذا pass": "لم يتم تنفيذ promote أو forget أو rollback على ذاكرة المشروع في هذا المرور",
    "سبب عدم الترقية: لا يوجد durable candidate صالح أو خالٍ من المخاطر يستحق promotion": "سبب عدم الترقية: لا يوجد عنصر durable صالح أو منخفض المخاطر يستحق promotion",
    "تحديث self-learn": "تحديث self-learn",
    "event_sequence وصل إلى 10 بعد observe-only event جديد": "وصل event_sequence إلى 10 بعد حدث جديد من نوع observe-only",
    "لم يتم استخدام apply احترامًا لحدود self-only": "لم يتم استخدام apply احترامًا لحدود self-only",
    "آخر verification status ما زال rolled-back من حدث أقدم ولم يتم تغيير التاريخ السابق": "آخر verification status ما زال rolled-back من حدث أقدم ولم يتم تغيير السجل التاريخي.",
    "Preservation and proof rules": "قواعد الحفظ والإثبات",
    "Boundaries": "الحدود",
    "هنا الحدود ليست نقصًا في القدرات، بل جزء من الصدق. هي التي تمنع التقرير من إدعاء شيء لم يحدث فعلاً.": "هنا الحدود ليست نقصًا في القدرات، بل جزء من الصدق. هي التي تمنع التقرير من ادعاء شيء لم يحدث فعلًا.",
    "لماذا self-learn لم يحدّث باقي المهارات؟": "لماذا لم يحدّث self-learn باقي المهارات؟",
    "العقد الحالي لـ self-learn محلي داخل مجلده فقط": "العقد الحالي لـ self-learn محلي داخل مجلده فقط",
    "هذه المهمة استخدمت observe/report كطبقة evidence لا كطبقة mutation": "هذه المهمة استخدمت observe/report كطبقة evidence لا كطبقة mutation",
    "لماذا persistent-memory لم يروّج backlog تلقائيًا؟": "لماذا لم يروّج persistent-memory قائمة الانتظار تلقائيًا؟",
    "سياسة الذاكرة تمنع auto-promotion من الأساس": "سياسة الذاكرة تمنع الترقية التلقائية من الأساس",
    "المتبقي كله تقريبًا مفاتيح ephemeral مثل project.active_artifact": "المتبقي كله تقريبًا مفاتيح ephemeral مثل project.active_artifact",
    "Restoration evidence": "أدلة الترميم",
    "Evidence Ledger": "سجل الأدلة",
    "كل ما يظهر هنا ناتج عن مخرجات محلية مباشرة، مع مراجعة رسمية إضافية لروابط OpenAI الحساسة زمنيًا.": "كل ما يظهر هنا ناتج عن مخرجات محلية مباشرة، مع مراجعة رسمية إضافية لروابط OpenAI الحساسة زمنيًا.",
    "عيّنة من الـ backlog": "عيّنة من قائمة الانتظار",
}


def apply_replacements(document: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        document = document.replace(old, new)
    return document


def fix_arabic_spans(document: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        document = document.replace(f'data-lang="ar">{old}<', f'data-lang="ar">{new}<')
    return document


def restyle_document(document: str, page_kind: str) -> str:
    document = v4.restyle_document(document, page_kind)
    document = apply_replacements(document, COMMON_REPLACEMENTS)
    page_replacements = SKILLS_REPLACEMENTS if page_kind == "skills" else MEMORY_REPLACEMENTS
    document = apply_replacements(document, page_replacements)
    ar_fixups = SKILLS_AR_SPAN_FIXES if page_kind == "skills" else MEMORY_AR_SPAN_FIXES
    return fix_arabic_spans(document, ar_fixups)


def main():
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    original_css = v2.SHARED_CSS
    try:
        v2.SHARED_CSS = V7_CSS
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
