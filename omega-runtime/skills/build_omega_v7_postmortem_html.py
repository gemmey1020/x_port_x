#!/usr/bin/env python3

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v7 as v7


ROOT = base.ROOT
OUTPUT_HTML = ROOT / "output/html/omega-v7-hero-layout-postmortem.html"
SOURCE_MD = ROOT / "output/reports/omega-v7-hero-layout-postmortem.md"

POSTMORTEM_CSS = v7.V7_CSS + """

.postmortem-page .hero-copy h1 {
  max-width: 13ch;
}

.postmortem-page .poster-surface {
  min-height: 520px;
}

.postmortem-page .poster-surface__name {
  max-width: 10ch;
}

.postmortem-page .hero-copy .muted-copy {
  max-width: 54ch;
}

.postmortem-meters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.postmortem-meters .mini-meter {
  min-height: 62px;
  align-content: start;
}

.kpi-ribbon {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.kpi-ribbon .insight-panel {
  padding-top: 0;
  border-top: none;
}

.postmortem-page .code-panel {
  max-height: none;
}

.postmortem-page .insight-panel h3,
.postmortem-page .story-band h3,
.postmortem-page .stack-item h3 {
  font-size: 1.45rem;
}

.status-mark {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid rgba(183, 216, 255, 0.18);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 80%),
    rgba(183, 216, 255, 0.05);
  color: var(--ink);
  font-size: 13px;
}

.status-mark strong {
  color: var(--accent-strong);
  font-family: var(--display-font);
  font-size: 1.05rem;
}

.section-block + .section-block {
  margin-top: 10px;
}

@media (max-width: 1080px) {
  .postmortem-meters,
  .kpi-ribbon {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .postmortem-meters,
  .kpi-ribbon {
    grid-template-columns: 1fr;
  }

  .postmortem-page .poster-surface {
    min-height: auto;
  }
}
"""


def escape(value: object) -> str:
    return base.escape(str(value))


def bilingual_text(ar: str, en: str, tag: str = "div", cls: str = "") -> str:
    return v2.bilingual_text(ar, en, tag, cls)


def bilingual_html(ar: str, en: str, tag: str = "div", cls: str = "") -> str:
    return v2.bilingual_html(ar, en, tag, cls)


def pretty_timestamp(value: str) -> str:
    return base.pretty_timestamp(value)


def state_readout(readout_id: str) -> str:
    return f'<span class="control-readout" id="{escape(readout_id)}"></span>'


def control_button(button_id: str, ar: str, en: str) -> str:
    return f'<button class="control-button" id="{escape(button_id)}">{bilingual_html(ar, en, "span")}</button>'


def topbar(page_label_ar: str, page_label_en: str, meta_html: str) -> str:
    return f"""
      <header class="utility-bar">
        <div class="brand-lockup">
          <strong>OMEGA HUD V7</strong>
          <span>{bilingual_html(page_label_ar, page_label_en, "span")}</span>
        </div>
        <div class="metric-strip">
          {meta_html}
        </div>
        <div class="control-cluster">
          {state_readout("lang-state")}
          {control_button("lang-toggle", "تبديل اللغة", "Switch Lang")}
          {state_readout("theme-state")}
          {control_button("theme-toggle", "تبديل الثيم", "Switch Theme")}
        </div>
      </header>
    """


def metric_pill(value: object, ar: str, en: str, tone: str = "") -> str:
    tone_cls = f" metric-pill--{tone}" if tone else ""
    return (
        f'<span class="metric-pill{tone_cls}">'
        f"<strong>{escape(value)}</strong>"
        f'{bilingual_text(ar, en, "span", "metric-pill__label")}'
        f"</span>"
    )


def inline_tag(ar: str, en: str, tone: str = "") -> str:
    tone_cls = f" inline-tag--{tone}" if tone else ""
    return f'<span class="inline-tag{tone_cls}">{bilingual_html(ar, en, "span")}</span>'


def code_tag(value: str) -> str:
    return f'<span class="inline-tag code-tag">{escape(value)}</span>'


def story_band(
    token: str,
    title_ar: str,
    title_en: str,
    body_ar: str,
    body_en: str,
    detail_ar: str,
    detail_en: str,
    codes: list[str] | None = None,
) -> str:
    codes = codes or []
    tokens_html = ""
    if codes:
        tokens_html = f'<div class="token-row story-band__tokens">{"".join(code_tag(code) for code in codes)}</div>'
    return f"""
      <article class="story-band">
        <div>
          <span class="tier-token">{escape(token)}</span>
        </div>
        <div class="story-band__content">
          {bilingual_html(title_ar, title_en, "h3")}
          {bilingual_text(body_ar, body_en, "p", "rail-copy")}
          {bilingual_text(detail_ar, detail_en, "p", "dim-copy")}
          {tokens_html}
        </div>
      </article>
    """


def insight_panel(title_ar: str, title_en: str, body_html: str, kicker_ar: str = "", kicker_en: str = "") -> str:
    kicker_html = ""
    if kicker_ar or kicker_en:
        kicker_html = f'<div class="tag-row">{inline_tag(kicker_ar, kicker_en, "accent")}</div>'
    return f"""
      <article class="insight-panel">
        {kicker_html}
        {bilingual_html(title_ar, title_en, "h3")}
        {body_html}
      </article>
    """


def report_list(items: list[tuple[str, str]]) -> str:
    return f'<ul class="report-list">{"".join(bilingual_html(ar, en, "li") for ar, en in items)}</ul>'


def fact_list(items: list[tuple[str, str]]) -> str:
    rows = "".join(f"<li><code>{escape(key)}</code><span>{escape(value)}</span></li>" for key, value in items)
    return f'<ul class="fact-list">{rows}</ul>'


def source_links(links: list[dict[str, str]]) -> str:
    rows = "".join(
        f'<a href="{escape(link["href"])}"><strong>{escape(link["label"])}</strong><span class="path-label">{escape(link["path"])}</span></a>'
        for link in links
    )
    return f'<div class="source-list">{rows}</div>'


def shell(title_en: str, title_ar: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v7-postmortem-artifact">
  <meta name="omega:page_intent" content="interactive_postmortem">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{escape(title_en)} | {escape(title_ar)}</title>
  <style>
{POSTMORTEM_CSS}
  </style>
</head>
<body class="postmortem-page">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD V7 POSTMORTEM / future relic learning artifact / local only / no external assets</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
</body>
</html>
"""


def build_page() -> str:
    generated_at = pretty_timestamp(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    meta_html = "".join(
        [
            metric_pill(2, "ملفان مقبولان", "Accepted outputs", "accent"),
            metric_pill(1, "سبب جذري واحد", "Single root cause"),
            metric_pill(6, "قواعد منع التكرار", "Recurrence locks"),
            metric_pill(generated_at, "تم التوليد", "Generated"),
        ]
    )

    body_html = f"""
    {topbar("نسخة تعلّم مرجعية", "Learning reference artifact", meta_html)}

    <section class="hero-stage" data-parallax>
      <div class="hero-inner">
        <div class="hero-grid">
          <div class="hero-copy">
            <p class="hero-kicker">{bilingual_html("تعلم مثبت / بلا drift جديد", "Proven learning / no new drift", "span")}</p>
            <h1>{bilingual_html("العطل كان في <span class=\"accent\">تموضع الـ Hero</span> لا في الترجمة", "The failure lived in <span class=\"accent\">hero geometry</span>, not translation", "span")}</h1>
            {bilingual_text("النسخة دي تحوّل الخطأ الذي حصل في V7 إلى artifact مرجعي واضح: ماذا انكسر، لماذا بدا كأنه bug لغة، كيف أثبتنا السبب الحقيقي، وكيف قفلنا المسار حتى لا تتكرر نفس النسخ البايظة.", "This artifact turns the V7 failure into a reusable reference: what broke, why it initially looked like a language bug, how we proved the real cause, and how we locked the route against recurrence.", "p", "muted-copy")}
            <div class="tag-row">
              {inline_tag("اللغة لم تكن السبب", "Language was not the cause", "accent")}
              {inline_tag("الثيم كان سليمًا", "Theme switching was healthy")}
              {inline_tag("الهندسة أثبتت الحقيقة", "Geometry exposed the truth")}
            </div>
          </div>
          <article class="poster-surface">
            <div class="poster-surface__headline">
              <div class="tag-row">
                {inline_tag("الحالة النهائية", "Final state", "accent")}
                {code_tag("hero-stage")}
              </div>
              <div class="poster-surface__score">
                <strong>01</strong>
                <span>{bilingual_html("سبب جذري", "root cause", "span")}</span>
              </div>
              <div class="poster-surface__name">{bilingual_html("Full-Bleed Geometry Drift", "Full-Bleed Geometry Drift", "span")}</div>
              {bilingual_text("العرض لم ينهَر لأن النص اختفى، بل لأن `.hero-copy` انزلق خارج الـ viewport. هذه كانت مشكلة shell وتموضع، لا مشكلة ترجمة أو data toggles.", "The page did not fail because the text disappeared. It failed because `.hero-copy` slid outside the viewport. This was a shell and positioning bug, not a translation or toggle-data bug.", "p", "poster-surface__summary")}
            </div>
            <div class="poster-surface__meta">
              <div class="tag-row">
                {inline_tag("مقبول الآن", "Accepted now", "accent")}
                {inline_tag("RTL كشف الدين", "RTL exposed the debt")}
                {inline_tag("V7 shell محفوظ", "V7 shell preserved")}
              </div>
              <div class="meter-row postmortem-meters">
                <span class="mini-meter"><span>broken x</span><strong>2476.5</strong></span>
                <span class="mini-meter"><span>fixed x</span><strong>972.5</strong></span>
                <span class="mini-meter"><span>stage x</span><strong>0</strong></span>
              </div>
              <div class="meta-inline">
                <span class="status-mark"><strong>{bilingual_html("مقبول", "Accepted", "span")}</strong><span>{bilingual_html("الملفان اتقفلوا بنجاح", "Both outputs are now stable", "span")}</span></span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="section-block" data-parallax>
      <div class="section-head">
        <p class="section-kicker">{bilingual_html("الصورة الأولى للمشكلة", "First read of the failure", "span")}</p>
        <h2>{bilingual_html("ما الذي ظهر للمستخدم وما الذي لم يكن مكسورًا", "What the user saw versus what was actually healthy", "span")}</h2>
        {bilingual_text("هذا القسم مهم لأنه يشرح لماذا كان من السهل سوء تشخيص المشكلة: بعض الطبقات كانت سليمة فعلًا، وبعضها فقط جعل العطل يبدو كلغوي بدل أن يكون layout bug.", "This section matters because it explains why the failure was easy to misdiagnose: some layers were genuinely healthy, while others made the issue look linguistic instead of structural.", "p", "section-copy")}
      </div>
      <div class="section-divider"></div>
      <div class="story-stack">
        {story_band("SYMPTOM", "ما الذي رآه المستخدم", "What the user saw", "الـ top bar ظاهر، الـ controls شغالة، والثيم يبدّل عادي، لكن الـ hero نفسه يبدو فاضيًا أو منزلقًا.", "The top bar was visible, the controls worked, and theme switching behaved, but the hero itself looked empty or displaced.", "الانطباع الطبيعي هنا: اللغة بوّظت الـ hero. لكن الانطباع كان ناقصًا.", "The natural impression was that language switching broke the hero. That impression was incomplete.", ["omega-skills-hud-v7.html", "omega-memory-learning-report-v7.html"])}
        {story_band("HEALTHY", "ما الذي كان سليمًا فعلًا", "What was actually healthy", "منطق `Switch Lang` نفسه كان يغيّر `html lang` و`dir` بشكل صحيح. ومنطق `Switch Theme` كان سليمًا، وحفظ `localStorage` كان صحيحًا.", "The `Switch Lang` logic correctly changed `html lang` and `dir`. `Switch Theme` was healthy, and `localStorage` persistence was correct.", "يعني الـ bug لم يكن في event wiring ولا في state persistence.", "So the bug did not live in event wiring or state persistence.", ["omega.ui.lang", "omega.ui.theme"])}
        {story_band("FALSE LEAD", "لماذا بدا التشخيص الأول مضللًا", "Why the first diagnosis was misleading", "الـ accessibility snapshot رأى النصوص داخل الـ DOM بشكل طبيعي، فبدا كأن الصفحة سليمة أو أن المشكلة مجرد labels.", "The accessibility snapshot could still see the text in the DOM, so the page initially looked healthy or merely mislabeled.", "وجود النص في الـ DOM لا يساوي ظهوره داخل viewport.", "DOM presence is not the same as on-screen geometry.", ["getBoundingClientRect()", "accessibility snapshot"])}
      </div>
    </section>

    <section class="section-block" data-parallax>
      <div class="section-head">
        <p class="section-kicker">{bilingual_html("الدليل الهندسي", "Geometry proof", "span")}</p>
        <h2>{bilingual_html("السبب الجذري كما أثبتته القياسات", "Root cause as proven by layout measurements", "span")}</h2>
        {bilingual_text("بدل الاكتفاء بالإحساس البصري أو قراءة الـ DOM، القياسات وضعت يدنا على الحقيقة: العنصر نفسه كان خارج viewport.", "Instead of relying on visual intuition or DOM presence alone, the measurements proved the truth: the element itself had moved outside the viewport.", "p", "section-copy")}
      </div>
      <div class="section-divider"></div>
      <div class="split-grid">
        {insight_panel("الحالة المكسورة", "Broken state", fact_list([("page", "omega-skills-hud-v7.html"), ("viewport", "1881 x 950"), ("lang / dir", "ar / rtl"), ("hero-stage.x", "1504"), ("hero-copy.x", "2476.5"), ("viewport width", "1881")]), "قبل الإصلاح", "Before fix")}
        {insight_panel("المرجع السليم", "Healthy reference", fact_list([("page", "omega-skills-hud-v4.html"), ("viewport", "1881 x 950"), ("lang / dir", "ar / rtl"), ("hero-stage.x", "0"), ("hero-copy.x", "1021.14"), ("poster.x", "407.82")]), "نسخة مرجعية", "Reference version")}
        {insight_panel("بعد الإصلاح", "After fix", fact_list([("skills / stage.x", "0"), ("skills / copy.x / rtl", "972.5"), ("skills / copy.x / ltr", "188.5"), ("memory / stage.x", "0"), ("memory / copy.x / rtl", "972.5"), ("memory / copy.x / ltr", "188.5")]), "مقفل بنجاح", "Locked successfully")}
        {insight_panel("الاستنتاج", "Inference", report_list([("المشكلة كانت في shell وتموضع الـ full-bleed، لا في النصوص نفسها.", "The bug lived in the shell and full-bleed positioning, not the text itself."), ("`rtl` لم يصنع الخطأ من الصفر، لكنه كشف debt كان موجودًا في التمركز.", "`rtl` did not create the bug from nothing; it exposed existing centering debt."), ("أفضل proof هنا كان: screenshot + geometry + current toggle state.", "The best proof here was: screenshot + geometry + current toggle state.")]), "الخلاصة", "Bottom line")}
      </div>
    </section>

    <section class="section-block" data-parallax>
      <div class="section-head">
        <p class="section-kicker">{bilingual_html("الإصلاح نفسه", "The fix itself", "span")}</p>
        <h2>{bilingual_html("ما الذي كان بايظ وما الذي غيّرناه", "What was broken and what changed", "span")}</h2>
        {bilingual_text("المهم هنا أننا لم نكسر shell أو theme أو toggles لكي نصلح الـ hero. الإصلاح كان صغيرًا ومحددًا ومثبتًا بالاختبار.", "What matters here is that we did not break the shell, theme, or toggles to repair the hero. The fix stayed small, specific, and test-backed.", "p", "section-copy")}
      </div>
      <div class="section-divider"></div>
      <div class="split-grid">
        {insight_panel("النمط الذي صنع العطل", "Pattern that caused the bug", f'<pre class="code-panel">{escape(""".hero-stage {\n  left: 50%;\n  width: 100vw;\n  margin-left: -50vw;\n  margin-right: -50vw;\n}""")}</pre>', "النسخة المكسورة", "Broken pattern")}
        {insight_panel("الـ override الذي قفل المسار", "Override that locked the route", f'<pre class="code-panel">{escape(""".hero-stage {\n  left: auto;\n  right: auto;\n  margin-left: calc(50% - 50vw);\n  margin-right: calc(50% - 50vw);\n}""")}</pre>', "الإصلاح النهائي", "Final fix")}
        {insight_panel("لماذا نجح", "Why it worked", report_list([("ألغى الحساسية المرتبطة بـ `left: 50%` داخل shell الصفحة.", "It removed the sensitivity tied to `left: 50%` inside the page shell."), ("أبقى تأثير الـ full-bleed بصريًا من غير أن يدفع الـ hero خارج viewport.", "It preserved the full-bleed look without pushing the hero outside the viewport."), ("حافظ على نفس `Switch Lang`, `Switch Theme`, و`localStorage` keys بدون تغيير.", "It preserved `Switch Lang`, `Switch Theme`, and the same `localStorage` keys unchanged.")]), "لماذا نجح", "Why it worked")}
        {insight_panel("التثبيت النهائي", "Final acceptance", report_list([("أعيد توليد الملفين من الـ builder نفسه بدل ترقيع HTML يدوي.", "Both outputs were regenerated from the builder rather than patched by hand."), ("تم اختبار `skills` و`memory` على desktop مع تبديل اللغة والثيم.", "Both `skills` and `memory` were tested on desktop with language and theme switching."), ("لا توجد `console errors` ولا external network requests.", "There are no console errors and no external network requests.")]), "Proof gate", "Proof gate")}
      </div>
    </section>

    <section class="section-block" data-parallax>
      <div class="section-head">
        <p class="section-kicker">{bilingual_html("قفل التكرار", "Recurrence lock", "span")}</p>
        <h2>{bilingual_html("قواعد تمنع خروج نسخ بايظة مرة ثانية", "Rules that prevent broken versions next time", "span")}</h2>
        {bilingual_text("هذه ليست ملاحظات عامة فقط. هي checklist عملية قابلة للتطبيق على أي `v8+` أو أي alternate edition لاحقة.", "These are not generic notes. They form a practical checklist for any `v8+` or later alternate edition.", "p", "section-copy")}
      </div>
      <div class="section-divider"></div>
      <div class="split-grid">
        {insight_panel("قواعد التصميم والتنفيذ", "Build rules", report_list([("لا نستخدم `left: 50%` مع `-50vw` في sections حرجة قبل geometry test فعلي.", "Do not use `left: 50%` with `-50vw` in critical sections without a real geometry test."), ("في صفحات bilingual، لا نكتفي بفحص النص داخل الـ DOM.", "In bilingual pages, do not stop at DOM text presence."), ("أي shell جديد يرث من نسخة سليمة ومختبرة بدل إعادة اختراع التموضع من الصفر.", "Any new shell should inherit from a proven version instead of reinventing positioning from scratch.")]), "قواعد البناء", "Build discipline")}
        {insight_panel("Regression Checklist", "Regression Checklist", report_list([("اختبر `ar + dark`", "Test `ar + dark`"), ("اختبر `ar + light`", "Test `ar + light`"), ("اختبر `en + dark`", "Test `en + dark`"), ("اختبر `en + light`", "Test `en + light`"), ("افحص `getBoundingClientRect()` للـ hero بعد التبديل.", "Inspect `getBoundingClientRect()` for the hero after switching."), ("خذ screenshot على desktop wide viewport، لا mobile فقط.", "Take a screenshot on a wide desktop viewport, not mobile only.")]), "قفل تراجعي", "Regression lock")}
      </div>
      <div class="kpi-ribbon">
        {insight_panel("أهم تعلّم", "Key learning", bilingual_text("ليس كل bug يظهر مع تبديل اللغة يكون bug ترجمة. أحيانًا `rtl` يكشف layout debt كان موجودًا بالفعل.", "Not every bug that appears during language switching is a translation bug. Sometimes `rtl` simply exposes layout debt that already existed.", "p", "rail-copy"), "تعلم", "Learning")}
        {insight_panel("أهم أداة إثبات", "Best proving tool", bilingual_text("أفضل proof هنا كان: screenshot + geometry + actual toggle state. هذا الثلاثي أقوى من DOM presence وحده.", "The strongest proof here was: screenshot + geometry + actual toggle state. That trio is stronger than DOM presence alone.", "p", "rail-copy"), "Proof", "Proof")}
        {insight_panel("الحالة النهائية", "Final status", bilingual_text("الملفان `omega-skills-hud-v7.html` و`omega-memory-learning-report-v7.html` مقبولان الآن بنجاح، والتقرير هذا هو المرجع الذي نتعلم منه قبل أي نسخ جديدة.", "Both `omega-skills-hud-v7.html` and `omega-memory-learning-report-v7.html` are now accepted, and this report is the reference we learn from before producing future versions.", "p", "rail-copy"), "Accepted", "Accepted")}
      </div>
    </section>

    <section class="section-block" data-parallax>
      <div class="section-head">
        <p class="section-kicker">{bilingual_html("المراجع والآثار", "Artifacts and references", "span")}</p>
        <h2>{bilingual_html("الملفات المرجعية المرتبطة بالتعلّم", "Reference artifacts tied to this learning", "span")}</h2>
        {bilingual_text("هذه الروابط تجمع النسختين المقبولتين، التقرير النصي، والـ builder الذي حوى الإصلاح النهائي.", "These links gather the accepted outputs, the markdown report, and the builder that carried the final fix.", "p", "section-copy")}
      </div>
      <div class="section-divider"></div>
      <div class="split-grid">
        {insight_panel("Artifacts التشغيل", "Operational artifacts", source_links([
            {"href": "./omega-skills-hud-v7.html", "label": "omega-skills-hud-v7.html", "path": "output/html/omega-skills-hud-v7.html"},
            {"href": "./omega-memory-learning-report-v7.html", "label": "omega-memory-learning-report-v7.html", "path": "output/html/omega-memory-learning-report-v7.html"},
            {"href": "./omega-v7-hero-layout-postmortem.html", "label": "omega-v7-hero-layout-postmortem.html", "path": "output/html/omega-v7-hero-layout-postmortem.html"},
        ]), "HTML", "HTML")}
        {insight_panel("المصدر المرجعي", "Canonical source", source_links([
            {"href": "../reports/omega-v7-hero-layout-postmortem.md", "label": "omega-v7-hero-layout-postmortem.md", "path": "output/reports/omega-v7-hero-layout-postmortem.md"},
            {"href": "../../omega-runtime/skills/build_skill_reports_v7.py", "label": "build_skill_reports_v7.py", "path": "omega-runtime/skills/build_skill_reports_v7.py"},
            {"href": "../../omega-runtime/skills/build_omega_v7_postmortem_html.py", "label": "build_omega_v7_postmortem_html.py", "path": "omega-runtime/skills/build_omega_v7_postmortem_html.py"},
        ]), "Source", "Source")}
      </div>
    </section>
    """

    return shell("Omega V7 Hero Layout Postmortem", "تقرير ما بعد العطل لتموضع Hero في V7", body_html)


def main() -> None:
    if not SOURCE_MD.exists():
        raise FileNotFoundError(f"Missing canonical source markdown: {SOURCE_MD}")

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(build_page(), encoding="utf-8")
    print(f"Wrote: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
