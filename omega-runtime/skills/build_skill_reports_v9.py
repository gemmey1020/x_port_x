#!/usr/bin/env python3

from __future__ import annotations

import difflib
import hashlib
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v7 as v7


ROOT = base.ROOT
OUTPUT_PATH = ROOT / "output/html/omega-skills-hud-v9.html"
SKILLS_ROOT = Path.home() / ".codex" / "skills"


CLUSTERS = [
    {
        "id": "figma_stack",
        "title_ar": "عنقود Figma",
        "title_en": "Figma Stack",
        "skills": ["figma", "figma-implement-design", "figma_mcp_operator"],
        "why_ar": "عندك 3 مهارات تدور حول نفس السورس نفسه: setup + implement + operator governance.",
        "action_ar": "الأنسب حاليًا دمج `figma` مع `figma-implement-design`، والإبقاء على `figma_mcp_operator` فقط كطبقة حوكمة اختيارية.",
        "tier": "merge-now",
    },
    {
        "id": "ui_stack",
        "title_ar": "عنقود UI / Product",
        "title_en": "UI / Product Stack",
        "skills": [
            "frontend-skill",
            "premium_ui_generator",
            "ui_taste_critic",
            "product_flow_architect",
            "design_system_enforcer",
            "omega_ui_product_brain",
        ],
        "why_ar": "هذا أكثر عنقود يخلق إحساس الزحمة: generation وcritique وflow وsystem enforcement ومعهم orchestrator أعلى.",
        "action_ar": "ادمج `frontend-skill` داخل `premium_ui_generator`، واحتفظ بـ `ui_taste_critic` و`product_flow_architect` و`design_system_enforcer` كأدوار مستقلة، مع إبقاء `omega_ui_product_brain` كطبقة orchestration فقط.",
        "tier": "tighten",
    },
    {
        "id": "planning_stack",
        "title_ar": "عنقود Planning / Proof",
        "title_en": "Planning / Proof Stack",
        "skills": [
            "god-plan-mode",
            "plan-critic",
            "omega-conductor",
            "omega-repo-map",
            "omega-proof-gate",
            "omega-ai-runtime",
        ],
        "why_ar": "عنقود قوي لكنه ثقيل ذهنيًا. القوة هنا في الـ pipeline، لكن عدد السطوح الظاهرة أعلى من اللازم.",
        "action_ar": "لا تدمجه كله. احتفظ بـ `plan-critic` و`omega-proof-gate` و`omega-repo-map`، وفكر في طي `omega-conductor` داخل `god-plan-mode` لو multi-agent orchestration ليس مسارًا يوميًا.",
        "tier": "group-dont-flatten",
    },
    {
        "id": "portfolio_pipeline",
        "title_ar": "سلسلة Portfolio Pipeline",
        "title_en": "Portfolio Pipeline",
        "skills": [
            "portfolio-spectrum-builder",
            "schema-mapper",
            "jsonld-generator",
            "landing-generator",
            "seo-artifact-generator",
            "render-artifact-generator",
        ],
        "why_ar": "الست مهارات deterministic ومترابطة جدًا. مفيدة كستيجات، لكنها مرهقة كـ user-facing entrypoints منفصلة.",
        "action_ar": "مرشحة بقوة للتحويل إلى 2 أو 3 مراحل كبيرة بدل 6 نقاط دخول منفصلة.",
        "tier": "group-now",
    },
    {
        "id": "docs_output_stack",
        "title_ar": "مسارات المستندات والإخراج",
        "title_en": "Documents / Output",
        "skills": ["doc", "pdf", "spreadsheet", "speech", "omega-html"],
        "why_ar": "مش زائدة؛ هي low-frequency specialists. المشكلة أنها قد تبدو كثيرة رغم أنها لا تتفعل إلا في سياقات واضحة جدًا.",
        "action_ar": "اتركها كما هي، لكن صنفها داخليًا كـ artifact specialists لا كمهارات يومية في التفكير.",
        "tier": "keep-specialists",
    },
    {
        "id": "ops_stack",
        "title_ar": "عمليات وتشغيل",
        "title_en": "Ops / Automation",
        "skills": ["playwright", "sentry", "vercel-deploy", "yeet", "persistent-memory", "omega-format", "teach_me"],
        "why_ar": "ده عنقود غير متجانس لكنه عملي. بعضه core overlays، وبعضه مجرد operator macros عند الطلب.",
        "action_ar": "اخفِ `yeet` و`vercel-deploy` و`self-learn` من السطح الذهني العام، واترك `persistent-memory` و`omega-format` كـ core overlays.",
        "tier": "hide-low-frequency",
    },
    {
        "id": "security_stack",
        "title_ar": "عنقود Security",
        "title_en": "Security Stack",
        "skills": ["security-best-practices", "security-ownership-map", "security-threat-model"],
        "why_ar": "ليس متكررًا بقدر ما هو متفاوت الكثافة: `security-best-practices` ضخم جدًا في المراجع مقارنة بباقي العنقود.",
        "action_ar": "لا تدمج العنقود. الأفضل split/tighten لـ `security-best-practices` حسب اللغة أو الإطار.",
        "tier": "split-heavy-guidance",
    },
]


CATEGORY_BY_SKILL = {
    ".system/openai-docs": "system",
    ".system/skill-creator": "system",
    ".system/skill-installer": "system",
    "figma": "figma",
    "figma-implement-design": "figma",
    "figma_mcp_operator": "figma",
    "frontend-skill": "ui",
    "premium_ui_generator": "ui",
    "ui_taste_critic": "ui",
    "product_flow_architect": "ui",
    "design_system_enforcer": "ui",
    "omega_ui_product_brain": "ui",
    "god-plan-mode": "planning",
    "plan-critic": "planning",
    "omega-conductor": "planning",
    "omega-repo-map": "planning",
    "omega-proof-gate": "planning",
    "omega-ai-runtime": "planning",
    "openai-docs": "runtime",
    "portfolio-spectrum-builder": "portfolio",
    "schema-mapper": "portfolio",
    "jsonld-generator": "portfolio",
    "landing-generator": "portfolio",
    "seo-artifact-generator": "portfolio",
    "render-artifact-generator": "portfolio",
    "doc": "artifact",
    "pdf": "artifact",
    "spreadsheet": "artifact",
    "speech": "artifact",
    "omega-html": "artifact",
    "security-best-practices": "security",
    "security-ownership-map": "security",
    "security-threat-model": "security",
    "playwright": "ops",
    "sentry": "ops",
    "vercel-deploy": "ops",
    "yeet": "ops",
    "persistent-memory": "core",
    "omega-format": "core",
    "teach_me": "core",
    "self-learn": "internal",
}


CATEGORY_LABELS = {
    "system": "System",
    "figma": "Figma",
    "ui": "UI/Product",
    "planning": "Planning",
    "runtime": "OpenAI Runtime",
    "portfolio": "Portfolio",
    "artifact": "Artifact",
    "security": "Security",
    "ops": "Ops",
    "core": "Core Overlay",
    "internal": "Internal",
    "other": "Other",
}


STANCE_BY_SKILL = {
    ".system/openai-docs": ("duplicate", "مكرر مع نسخة user-level"),
    ".system/skill-creator": ("hide", "system-only"),
    ".system/skill-installer": ("hide", "system-only"),
    "openai-docs": ("dedupe", "احتفظ بنسخة واحدة"),
    "figma": ("merge", "ادمجها مع implement"),
    "figma-implement-design": ("merge", "ادمجها مع figma"),
    "figma_mcp_operator": ("tighten", "حوكمة اختيارية"),
    "frontend-skill": ("merge", "ادمجها داخل premium UI"),
    "premium_ui_generator": ("keep", "تبقى نقطة التنفيذ الأساسية"),
    "ui_taste_critic": ("keep", "نقد بصري مستقل"),
    "product_flow_architect": ("keep", "منطق flow مستقل"),
    "design_system_enforcer": ("keep", "انضباط نظام التصميم"),
    "omega_ui_product_brain": ("keep", "orchestrator واضح"),
    "god-plan-mode": ("keep", "الـ planner الأساسي"),
    "plan-critic": ("keep", "تمييز واضح"),
    "omega-conductor": ("tighten", "فكر في طيه داخل planner"),
    "omega-repo-map": ("keep", "discovery distinct"),
    "omega-proof-gate": ("keep", "proof distinct"),
    "omega-ai-runtime": ("keep", "AI system design distinct"),
    "portfolio-spectrum-builder": ("group", "اجمعها ضمن pipeline"),
    "schema-mapper": ("group", "اجمعها ضمن pipeline"),
    "jsonld-generator": ("group", "اجمعها ضمن pipeline"),
    "landing-generator": ("group", "اجمعها ضمن pipeline"),
    "seo-artifact-generator": ("group", "اجمعها ضمن pipeline"),
    "render-artifact-generator": ("group", "اجمعها ضمن pipeline"),
    "doc": ("macro", "specialist عند الطلب"),
    "pdf": ("keep", "distinct downstream"),
    "spreadsheet": ("macro", "specialist عند الطلب"),
    "speech": ("macro", "specialist عند الطلب"),
    "omega-html": ("keep", "distinct report artifact"),
    "security-best-practices": ("split", "قسّم guidance حسب اللغة/الإطار"),
    "security-ownership-map": ("macro", "audit specialist"),
    "security-threat-model": ("keep", "distinct AppSec path"),
    "playwright": ("keep", "browser automation distinct"),
    "sentry": ("keep", "workspace capability distinct"),
    "vercel-deploy": ("macro", "deploy specialist"),
    "yeet": ("hide", "operator macro صريح"),
    "persistent-memory": ("keep", "core overlay"),
    "omega-format": ("keep", "core overlay"),
    "teach_me": ("keep", "understanding-first distinct"),
    "self-learn": ("hide", "internal فقط"),
}


EXTRA_CSS = """
.audit-page .page-shell {
  padding-bottom: 120px;
}

.audit-page .hero-copy h1 {
  max-width: 13ch;
}

.audit-page .hero-copy .muted-copy {
  max-width: 70ch;
}

.audit-page .hero-grid {
  grid-template-columns: minmax(0, 1.18fr) minmax(360px, 0.82fr);
}

.audit-page .hero-brief,
.audit-page .compact-list,
.audit-page .signal-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.audit-page .hero-brief {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}

.audit-page .hero-brief li,
.audit-page .compact-list li,
.audit-page .signal-list li {
  display: grid;
  gap: 8px;
}

.audit-page .compact-list li,
.audit-page .signal-list li {
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
}

.audit-page .poster-surface__summary strong,
.audit-page .section-copy strong,
.audit-page .rail-copy strong {
  color: var(--accent-strong);
}

.audit-page .section-block {
  margin-top: 26px;
}

.audit-page .stats-grid,
.audit-page .matrix-grid,
.audit-page .cluster-grid,
.audit-page .hotspot-grid,
.audit-page .duplicate-grid {
  display: grid;
  gap: 22px;
}

.audit-page .stats-grid,
.audit-page .duplicate-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.audit-page .cluster-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.audit-page .hotspot-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.audit-page .matrix-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.audit-page .cluster-card,
.audit-page .matrix-card,
.audit-page .hotspot-card,
.audit-page .duplicate-card {
  position: relative;
  display: grid;
  gap: 16px;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 34%),
    color-mix(in srgb, var(--surface-strong) 94%, transparent);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.18);
  overflow: hidden;
}

.audit-page .cluster-card::after,
.audit-page .matrix-card::after,
.audit-page .hotspot-card::after,
.audit-page .duplicate-card::after {
  content: "";
  position: absolute;
  inset: auto -24% 0 auto;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 194, 117, 0.14), transparent 70%);
  pointer-events: none;
}

.audit-page .card-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.audit-page .card-head h3 {
  margin: 0;
  font-size: 22px;
  line-height: 1.35;
}

.audit-page .card-body {
  display: grid;
  gap: 12px;
}

.audit-page .micro-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.audit-page .micro-metric {
  min-width: 110px;
  padding: 10px 12px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
}

.audit-page .micro-metric strong {
  display: block;
  font-size: 18px;
}

.audit-page .micro-metric span {
  display: block;
  margin-top: 4px;
  color: var(--muted);
  font-size: 12px;
}

.audit-page .matrix-card {
  align-content: start;
}

.audit-page .matrix-card[data-tone="merge"] {
  border-color: rgba(255, 194, 117, 0.32);
}

.audit-page .matrix-card[data-tone="hide"] {
  border-color: rgba(233, 139, 120, 0.32);
}

.audit-page .matrix-card[data-tone="keep"] {
  border-color: rgba(158, 212, 176, 0.26);
}

.audit-page .matrix-card[data-tone="split"] {
  border-color: rgba(183, 216, 255, 0.28);
}

.audit-page .stack-bullets {
  display: grid;
  gap: 10px;
}

.audit-page .stack-bullets li {
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
}

.audit-page .list-kicker {
  color: var(--muted);
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.audit-page .filter-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 12px;
  align-items: center;
}

.audit-page .hud-input {
  width: 100%;
  min-height: 48px;
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface-strong) 90%, transparent);
  color: var(--ink);
  font: inherit;
}

.audit-page .filter-note {
  color: var(--muted);
  font-size: 13px;
}

.audit-page .audit-table {
  display: grid;
  gap: 10px;
  margin-top: 20px;
}

.audit-page .audit-row,
.audit-page .audit-head {
  display: grid;
  grid-template-columns: minmax(240px, 1.4fr) minmax(92px, 0.7fr) minmax(110px, 0.72fr) repeat(4, minmax(78px, 0.5fr)) minmax(280px, 1.5fr);
  gap: 12px;
  align-items: start;
}

.audit-page .audit-head {
  padding: 0 14px 10px;
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.audit-page .audit-row {
  padding: 16px 14px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.03), transparent 20%),
    rgba(255, 255, 255, 0.015);
}

.audit-page .audit-row.is-hidden {
  display: none;
}

.audit-page .audit-row[data-stance="merge"],
.audit-page .audit-row[data-stance="dedupe"],
.audit-page .audit-row[data-stance="group"] {
  border-color: rgba(255, 194, 117, 0.26);
}

.audit-page .audit-row[data-stance="hide"],
.audit-page .audit-row[data-stance="duplicate"] {
  border-color: rgba(233, 139, 120, 0.28);
}

.audit-page .audit-row[data-stance="split"],
.audit-page .audit-row[data-stance="tighten"] {
  border-color: rgba(183, 216, 255, 0.24);
}

.audit-page .audit-cell {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.audit-page .audit-skill-name {
  font-size: 18px;
  line-height: 1.35;
  margin: 0;
}

.audit-page .path-label {
  word-break: break-word;
}

.audit-page .audit-number {
  font-size: 18px;
  font-weight: 700;
}

.audit-page .audit-number-label {
  color: var(--muted);
  font-size: 12px;
}

.audit-page .description-block {
  color: var(--muted);
  font-size: 14px;
  line-height: 1.7;
}

.audit-page .stance-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  width: fit-content;
  font-size: 12px;
  color: var(--muted);
  background: rgba(255, 255, 255, 0.03);
}

.audit-page .stance-chip[data-tone="keep"] {
  border-color: rgba(158, 212, 176, 0.36);
  color: var(--success);
}

.audit-page .stance-chip[data-tone="merge"],
.audit-page .stance-chip[data-tone="dedupe"],
.audit-page .stance-chip[data-tone="group"] {
  border-color: rgba(255, 194, 117, 0.38);
  color: var(--accent-strong);
}

.audit-page .stance-chip[data-tone="hide"],
.audit-page .stance-chip[data-tone="duplicate"] {
  border-color: rgba(233, 139, 120, 0.38);
  color: var(--danger);
}

.audit-page .stance-chip[data-tone="split"],
.audit-page .stance-chip[data-tone="tighten"] {
  border-color: rgba(183, 216, 255, 0.42);
  color: #b7d8ff;
}

.audit-page .source-note {
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
  color: var(--muted);
  line-height: 1.8;
}

.audit-page .footer-note {
  margin-top: 26px;
}

@media (max-width: 1240px) {
  .audit-page .cluster-grid,
  .audit-page .stats-grid,
  .audit-page .duplicate-grid,
  .audit-page .hotspot-grid,
  .audit-page .matrix-grid {
    grid-template-columns: 1fr 1fr;
  }

  .audit-page .audit-head,
  .audit-page .audit-row {
    grid-template-columns: minmax(220px, 1.4fr) minmax(90px, 0.7fr) minmax(110px, 0.8fr) repeat(4, minmax(72px, 0.55fr));
  }

  .audit-page .audit-cell--description {
    grid-column: 1 / -1;
  }
}

@media (max-width: 920px) {
  .audit-page .hero-grid,
  .audit-page .stats-grid,
  .audit-page .cluster-grid,
  .audit-page .duplicate-grid,
  .audit-page .hotspot-grid,
  .audit-page .matrix-grid,
  .audit-page .filter-bar {
    grid-template-columns: 1fr;
  }

  .audit-page .audit-head {
    display: none;
  }

  .audit-page .audit-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .audit-page .audit-cell--skill,
  .audit-page .audit-cell--description {
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .audit-page .audit-row {
    grid-template-columns: 1fr;
  }
}
"""


SCRIPT_JS = """
(function () {
  const root = document.documentElement;
  const langKey = 'omega.v9.lang';
  const themeKey = 'omega.v9.theme';
  const filterInput = document.getElementById('skill-filter');
  const rows = Array.from(document.querySelectorAll('.audit-row'));
  const filterCount = document.getElementById('filter-count');
  const themeToggle = document.getElementById('theme-toggle');
  const themeState = document.getElementById('theme-state');
  const langToggle = document.getElementById('lang-toggle');
  const langState = document.getElementById('lang-state');

  function safeGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function safeSet(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      // Ignore storage failures in restrictive previews.
    }
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    if (themeState) {
      themeState.textContent = theme === 'light' ? 'Light' : 'Dark';
    }
  }

  function applyLang(lang) {
    const next = lang === 'en' ? 'en' : 'ar';
    root.setAttribute('data-ui-lang', next);
    root.setAttribute('lang', next);
    root.setAttribute('dir', next === 'en' ? 'ltr' : 'rtl');
    if (langState) {
      langState.textContent = next === 'en' ? 'EN' : 'AR';
    }
  }

  function syncTheme() {
    const saved = safeGet(themeKey);
    applyTheme(saved === 'light' ? 'light' : 'dark');
  }

  function syncLang() {
    const saved = safeGet(langKey);
    applyLang(saved === 'en' ? 'en' : 'ar');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      safeSet(themeKey, next);
      applyTheme(next);
    });
  }

  if (langToggle) {
    langToggle.addEventListener('click', function () {
      const next = root.getAttribute('data-ui-lang') === 'en' ? 'ar' : 'en';
      safeSet(langKey, next);
      applyLang(next);
    });
  }

  function applyFilter(value) {
    const query = value.trim().toLowerCase();
    let visible = 0;
    rows.forEach(function (row) {
      const haystack = (row.getAttribute('data-search') || '').toLowerCase();
      const show = !query || haystack.indexOf(query) !== -1;
      row.classList.toggle('is-hidden', !show);
      if (show) {
        visible += 1;
      }
    });
    if (filterCount) {
      filterCount.textContent = String(visible);
    }
  }

  if (filterInput) {
    filterInput.addEventListener('input', function (event) {
      applyFilter(event.target.value || '');
    });
  }

  if (document.body) {
    document.body.classList.add('is-ready');
  }

  syncLang();
  syncTheme();
  applyFilter('');
})();
"""


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def walk_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    files: list[Path] = []
    for root, _, names in os.walk(directory):
        for name in names:
            files.append(Path(root) / name)
    return sorted(files)


def text_bundle_stats(directory: Path) -> dict[str, int]:
    files = walk_files(directory)
    total_bytes = 0
    for file_path in files:
        total_bytes += file_path.stat().st_size
    return {
        "count": len(files),
        "bytes": total_bytes,
        "est_tokens": round(total_bytes / 4),
    }


def parse_skill_markdown(text: str) -> tuple[str, str]:
    name_match = re.search(r'^name:\s*"?(?P<value>[^"\n]+)"?', text, re.M)
    description_match = re.search(r'^description:\s*"?(?P<value>.+?)"?$', text, re.M)
    name = name_match.group("value").strip() if name_match else "unknown"
    description = description_match.group("value").strip() if description_match else ""
    return name, description


def category_for(skill_key: str) -> str:
    return CATEGORY_BY_SKILL.get(skill_key, "other")


def stance_for(skill_key: str) -> tuple[str, str]:
    return STANCE_BY_SKILL.get(skill_key, ("keep", "لا يحتاج دمجًا حاليًا"))


def scan_skills() -> list[dict]:
    rows: list[dict] = []
    for root, _, files in os.walk(SKILLS_ROOT):
        if "SKILL.md" not in files:
            continue
        skill_dir = Path(root)
        rel = skill_dir.relative_to(SKILLS_ROOT).as_posix()
        skill_md_path = skill_dir / "SKILL.md"
        skill_md_text = read_text(skill_md_path)
        skill_name, description = parse_skill_markdown(skill_md_text)
        refs = text_bundle_stats(skill_dir / "references")
        scripts = text_bundle_stats(skill_dir / "scripts")
        assets = text_bundle_stats(skill_dir / "assets")
        all_files = walk_files(skill_dir)
        stance, stance_note = stance_for(rel)
        rows.append(
            {
                "skill_key": rel,
                "path": str(skill_md_path),
                "name": skill_name,
                "description": description,
                "is_system": rel.startswith(".system/"),
                "category": category_for(rel),
                "category_label": CATEGORY_LABELS.get(category_for(rel), CATEGORY_LABELS["other"]),
                "stance": stance,
                "stance_note": stance_note,
                "skill_words": len(re.findall(r"\S+", skill_md_text)),
                "skill_chars": len(skill_md_text),
                "baseline_tokens": estimate_tokens(description) if description else 0,
                "activation_tokens": estimate_tokens(skill_md_text),
                "refs_files": refs["count"],
                "refs_tokens": refs["est_tokens"],
                "scripts_files": scripts["count"],
                "scripts_tokens": scripts["est_tokens"],
                "assets_files": assets["count"],
                "assets_bytes": assets["bytes"],
                "file_count": len(all_files),
                "dir_bytes": sum(path.stat().st_size for path in all_files),
                "sha1": hashlib.sha1(skill_md_text.encode("utf-8")).hexdigest()[:12],
                "skill_md_text": skill_md_text,
            }
        )
    rows.sort(key=lambda item: item["skill_key"])
    return rows


def build_duplicates(rows: list[dict]) -> list[dict]:
    by_name: defaultdict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_name[row["name"]].append(row)

    duplicate_families: list[dict] = []
    for name, family in sorted(by_name.items()):
        if len(family) < 2:
            continue
        family = sorted(family, key=lambda item: item["skill_key"])
        texts = [item["skill_md_text"] for item in family]
        descriptions = {item["description"] for item in family}
        identical_full = len(set(texts)) == 1
        identical_desc = len(descriptions) == 1
        primary = family[0]
        secondary = family[1]
        diff_lines = list(
            difflib.unified_diff(
                primary["skill_md_text"].splitlines(),
                secondary["skill_md_text"].splitlines(),
                fromfile=primary["skill_key"],
                tofile=secondary["skill_key"],
                lineterm="",
            )
        )
        changed_lines = [line for line in diff_lines if line.startswith("+") or line.startswith("-")]
        excerpt = []
        for line in changed_lines:
            if line.startswith("---") or line.startswith("+++"):
                continue
            excerpt.append(line)
            if len(excerpt) == 6:
                break
        duplicate_families.append(
            {
                "name": name,
                "items": family,
                "identical_full": identical_full,
                "identical_desc": identical_desc,
                "changed_line_count": len(changed_lines),
                "diff_excerpt": excerpt,
            }
        )
    return duplicate_families


def cluster_payload(rows: list[dict]) -> list[dict]:
    by_key = {row["skill_key"]: row for row in rows}
    payload = []
    for cluster in CLUSTERS:
        members = [by_key[skill] for skill in cluster["skills"] if skill in by_key]
        activation_total = sum(item["activation_tokens"] for item in members)
        refs_total = sum(item["refs_tokens"] for item in members)
        scripts_total = sum(item["scripts_tokens"] for item in members)
        baseline_total = sum(item["baseline_tokens"] for item in members)
        heaviest = max(members, key=lambda item: item["activation_tokens"]) if members else None
        payload.append(
            {
                **cluster,
                "count": len(members),
                "baseline_total": baseline_total,
                "activation_total": activation_total,
                "refs_total": refs_total,
                "scripts_total": scripts_total,
                "possible_with_refs": activation_total + refs_total,
                "heaviest": heaviest["skill_key"] if heaviest else None,
                "members": members,
            }
        )
    return payload


def generated_at() -> str:
    value = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return base.pretty_timestamp(value)


def bilingual(ar: str, en: str, tag: str = "span", cls: str = "") -> str:
    cls_attr = f' class="{escape(cls)}"' if cls else ""
    return f'<{tag}{cls_attr}><span data-lang="ar">{escape(ar)}</span><span data-lang="en">{escape(en)}</span></{tag}>'


def topbar(meta_html: str) -> str:
    return f"""
      <header class="utility-bar">
        <div class="brand-lockup">
          <strong>OMEGA HUD V9</strong>
          {bilingual("تدقيق المهارات / التوكن / الدمج", "Skills Audit / Token / Merge Deep Dive", "span")}
        </div>
        <div class="metric-strip">
          {meta_html}
        </div>
        <div class="control-cluster">
          <span class="control-readout" id="lang-state">AR</span>
          <button class="control-button" id="lang-toggle">{bilingual("تبديل اللغة", "Switch Lang", "span")}</button>
          <span class="control-readout" id="theme-state">Dark</span>
          <button class="control-button" id="theme-toggle">{bilingual("تبديل الثيم", "Switch Theme", "span")}</button>
        </div>
      </header>
    """


def pill(value: str | int, label: str, tone: str = "") -> str:
    tone_cls = f" metric-pill--{tone}" if tone else ""
    return f'<span class="metric-pill{tone_cls}"><strong>{escape(str(value))}</strong><span class="metric-pill__label">{escape(label)}</span></span>'


def inline_tag(label: str, tone: str = "") -> str:
    tone_cls = f" inline-tag--{tone}" if tone else ""
    return f'<span class="inline-tag{tone_cls}">{escape(label)}</span>'


def code_tag(label: str) -> str:
    return f'<span class="inline-tag code-tag">{escape(label)}</span>'


def list_items(items: list[str]) -> str:
    return "".join(f"<li>{item}</li>" for item in items)


def tone_label(stance: str) -> str:
    labels = {
        "keep": "Keep",
        "merge": "Merge",
        "dedupe": "Deduplicate",
        "group": "Group",
        "hide": "Hide",
        "duplicate": "Duplicate",
        "split": "Split",
        "tighten": "Tighten",
        "macro": "On-demand",
    }
    return labels.get(stance, stance.title())


def stance_chip(stance: str) -> str:
    return f'<span class="stance-chip" data-tone="{escape(stance)}">{escape(tone_label(stance))}</span>'


def format_num(value: int) -> str:
    return f"{value:,}"


def render_cluster_cards(clusters: list[dict]) -> str:
    parts = []
    for cluster in clusters:
        members = "".join(code_tag(item["skill_key"]) for item in cluster["members"])
        parts.append(
            f"""
            <article class="cluster-card">
              <div class="card-head">
                <h3>{escape(cluster["title_ar"])}</h3>
                {inline_tag(cluster["tier"], "accent")}
              </div>
              <div class="micro-metrics">
                <div class="micro-metric"><strong>{format_num(cluster["count"])}</strong><span>عدد المهارات</span></div>
                <div class="micro-metric"><strong>{format_num(cluster["baseline_total"])}</strong><span>baseline</span></div>
                <div class="micro-metric"><strong>{format_num(cluster["activation_total"])}</strong><span>activation</span></div>
                <div class="micro-metric"><strong>{format_num(cluster["possible_with_refs"])}</strong><span>activation + refs</span></div>
              </div>
              <div class="card-body">
                <p class="rail-copy">{escape(cluster["why_ar"])}</p>
                <p class="dim-copy">{escape(cluster["action_ar"])}</p>
                <div class="token-row">{members}</div>
                <p class="path-label">heaviest: {escape(cluster["heaviest"] or "n/a")}</p>
              </div>
            </article>
            """
        )
    return "".join(parts)


def render_matrix() -> str:
    cards = [
        {
            "tone": "merge",
            "title": "ادمج الآن",
            "summary": "تقليل نقاط الدخول المتشابهة من غير خسارة الوظيفة.",
            "items": [
                "`figma` + `figma-implement-design`",
                "`frontend-skill` داخل `premium_ui_generator`",
                "نسخة واحدة فقط من `openai-docs`",
            ],
        },
        {
            "tone": "keep",
            "title": "احتفظ بها منفصلة",
            "summary": "هذه مهارات أدوارها مختلفة فعلًا حتى لو كانت متجاورة.",
            "items": [
                "`plan-critic`",
                "`omega-proof-gate`",
                "`ui_taste_critic`",
                "`product_flow_architect`",
                "`design_system_enforcer`",
                "`security-threat-model`",
            ],
        },
        {
            "tone": "hide",
            "title": "اخفِ من السطح العام",
            "summary": "ليست عديمة القيمة، لكنها low-frequency أو internal.",
            "items": [
                "`self-learn`",
                "`yeet`",
                "`vercel-deploy`",
                "system helpers مثل `skill-creator` و`skill-installer`",
            ],
        },
        {
            "tone": "split",
            "title": "قسّم أو شدّد الحدود",
            "summary": "المشكلة هنا ليست التكرار بل الكثافة أو تسييل الحدود.",
            "items": [
                "`security-best-practices` حسب اللغة/الإطار",
                "`omega-conductor` كـ appendix أو sub-mode",
                "واجهة مجمعة للـ portfolio pipeline بدل 6 entrypoints",
            ],
        },
    ]

    return "".join(
        f"""
        <article class="matrix-card" data-tone="{escape(card["tone"])}">
          <div class="card-head">
            <h3>{escape(card["title"])}</h3>
            {inline_tag(tone_label(card["tone"]), "accent")}
          </div>
          <p class="rail-copy">{escape(card["summary"])}</p>
          <ul class="stack-bullets">{list_items(card["items"])}</ul>
        </article>
        """
        for card in cards
    )


def render_hotspots(rows: list[dict]) -> str:
    rankings = [
        ("أعلى baseline", "كل ما يثقل قائمة المهارات حتى قبل التفعيل", sorted(rows, key=lambda item: item["baseline_tokens"], reverse=True)[:6], "baseline_tokens"),
        ("أعلى activation", "تكلفة فتح `SKILL.md` عند التفعيل", sorted(rows, key=lambda item: item["activation_tokens"], reverse=True)[:6], "activation_tokens"),
        ("أعلى refs ممكنة", "حمولة إضافية إذا فتحت المراجع النصية", sorted(rows, key=lambda item: item["refs_tokens"], reverse=True)[:6], "refs_tokens"),
        ("أعلى scripts ممكنة", "حمولة إضافية فقط إذا قرأت السكربتات نفسها", sorted(rows, key=lambda item: item["scripts_tokens"], reverse=True)[:6], "scripts_tokens"),
    ]
    cards = []
    for title, summary, items, key in rankings:
        rows_html = "".join(
            f'<li><strong>{escape(item["skill_key"])}</strong><span>{format_num(item[key])}</span></li>'
            for item in items
        )
        cards.append(
            f"""
            <article class="hotspot-card">
              <div class="card-head">
                <h3>{escape(title)}</h3>
                {inline_tag("top 6", "accent")}
              </div>
              <p class="rail-copy">{escape(summary)}</p>
              <ul class="signal-list">{rows_html}</ul>
            </article>
            """
        )
    return "".join(cards)


def render_duplicate_section(duplicates: list[dict]) -> str:
    if not duplicates:
        return """
          <article class="duplicate-card">
            <div class="card-head"><h3>لا توجد duplicate families</h3></div>
            <p class="rail-copy">المسح الحي لم يكشف أي اسم مهارة مكرر.</p>
          </article>
        """

    cards = []
    for duplicate in duplicates:
        items = duplicate["items"]
        paths = "".join(
            f'<li><strong>{escape(item["skill_key"])}</strong><span>{escape(item["path"])}</span></li>'
            for item in items
        )
        diff_excerpt = "".join(f"<li><code>{escape(line)}</code></li>" for line in duplicate["diff_excerpt"]) or "<li>no diff excerpt</li>"
        special_note = ""
        if duplicate["name"] == "openai-docs":
            special_note = (
                "<p class=\"dim-copy\">النسختان تتفقان في الاسم والوصف العام تقريبًا، لكن نسخة user-level تحتوي سطورًا إضافية خاصة بتنسيق السطح العربي وملاحظة HTML، بينما النسخة النظامية أنظف وأضيق.</p>"
            )
        cards.append(
            f"""
            <article class="duplicate-card">
              <div class="card-head">
                <h3>{escape(duplicate["name"])}</h3>
                {inline_tag("duplicate family", "accent")}
              </div>
              <div class="micro-metrics">
                <div class="micro-metric"><strong>{len(items)}</strong><span>نسخ</span></div>
                <div class="micro-metric"><strong>{'yes' if duplicate['identical_desc'] else 'no'}</strong><span>same description</span></div>
                <div class="micro-metric"><strong>{'yes' if duplicate['identical_full'] else 'no'}</strong><span>same full text</span></div>
                <div class="micro-metric"><strong>{duplicate['changed_line_count']}</strong><span>diff lines</span></div>
              </div>
              <div class="card-body">
                <ul class="signal-list">{paths}</ul>
                {special_note}
                <div class="source-note">
                  <div class="list-kicker">diff excerpt</div>
                  <ul class="compact-list">{diff_excerpt}</ul>
                </div>
              </div>
            </article>
            """
        )
    return "".join(cards)


def render_table(rows: list[dict]) -> str:
    sorted_rows = sorted(rows, key=lambda item: (item["activation_tokens"], item["baseline_tokens"]), reverse=True)
    rendered = []
    for row in sorted_rows:
        search_blob = " ".join(
            [
                row["skill_key"],
                row["name"],
                row["category_label"],
                row["stance"],
                row["stance_note"],
            ]
        )
        rendered.append(
            f"""
            <div class="audit-row" data-stance="{escape(row["stance"])}" data-search="{escape(search_blob)}">
              <div class="audit-cell audit-cell--skill">
                <div class="card-head">
                  <h3 class="audit-skill-name">{escape(row["skill_key"])}</h3>
                  {stance_chip(row["stance"])}
                </div>
                <div class="token-row">
                  {inline_tag(row["category_label"], "accent")}
                  {code_tag(row["name"])}
                  {code_tag(row["sha1"])}
                </div>
                <div class="path-label">{escape(row["path"])}</div>
              </div>
              <div class="audit-cell">
                <div class="audit-number">{escape(row["category_label"])}</div>
                <div class="audit-number-label">Category</div>
              </div>
              <div class="audit-cell">
                {stance_chip(row["stance"])}
                <div class="audit-number-label">{escape(row["stance_note"])}</div>
              </div>
              <div class="audit-cell">
                <div class="audit-number">{format_num(row["baseline_tokens"])}</div>
                <div class="audit-number-label">Baseline</div>
              </div>
              <div class="audit-cell">
                <div class="audit-number">{format_num(row["activation_tokens"])}</div>
                <div class="audit-number-label">Activation</div>
              </div>
              <div class="audit-cell">
                <div class="audit-number">{format_num(row["refs_tokens"])}</div>
                <div class="audit-number-label">Refs if opened</div>
              </div>
              <div class="audit-cell">
                <div class="audit-number">{format_num(row["scripts_tokens"])}</div>
                <div class="audit-number-label">Scripts if read</div>
              </div>
              <div class="audit-cell audit-cell--description">
                <div class="description-block">{escape(row["description"])}</div>
                <div class="token-row">
                  {inline_tag(f'files {row["file_count"]}')}
                  {inline_tag(f'refs {row["refs_files"]}')}
                  {inline_tag(f'scripts {row["scripts_files"]}')}
                  {inline_tag(f'assets {row["assets_files"]}')}
                  {inline_tag(f'chars {row["skill_chars"]}')}
                </div>
              </div>
            </div>
            """
        )
    return "".join(rendered)


def build_body(rows: list[dict]) -> str:
    duplicates = build_duplicates(rows)
    clusters = cluster_payload(rows)

    totals = {
        "all": len(rows),
        "top_level": sum(0 if row["is_system"] else 1 for row in rows),
        "system": sum(1 if row["is_system"] else 0 for row in rows),
        "baseline": sum(row["baseline_tokens"] for row in rows),
        "activation": sum(row["activation_tokens"] for row in rows),
        "refs": sum(row["refs_tokens"] for row in rows),
        "scripts": sum(row["scripts_tokens"] for row in rows),
    }

    meta_html = "".join(
        [
            pill(totals["all"], "مهارات مثبتة"),
            pill(totals["top_level"], "top-level"),
            pill(len(duplicates), "duplicate families", "accent" if duplicates else ""),
            pill(format_num(totals["baseline"]), "baseline total"),
            pill(format_num(totals["activation"]), "activation total"),
            pill(generated_at(), "تم التوليد"),
        ]
    )

    heaviest_cluster = max(clusters, key=lambda item: item["possible_with_refs"])
    largest_baseline = max(rows, key=lambda item: item["baseline_tokens"])
    largest_activation = max(rows, key=lambda item: item["activation_tokens"])
    largest_refs = max(rows, key=lambda item: item["refs_tokens"])
    largest_scripts = max(rows, key=lambda item: item["scripts_tokens"])

    return f"""
      {topbar(meta_html)}

      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{bilingual("تقرير HUD عميق", "Skills Audit / Deep HUD", "span")}</p>
              <h1>لوحة <span class="accent">المهارات</span> بعد فحص حي للتكرار واستهلاك التوكن</h1>
              <p class="muted-copy">
                هذا الملف يجمع <strong>كل النتيجة السابقة</strong> ويضيف طبقة أعمق: duplicate families،
                baseline مقابل activation، حمولة المراجع الممكنة، تحليل العناقيد، ومصفوفة عملية توضح
                ماذا نُبقي، ماذا ندمج، ماذا نُخفي، وماذا نُقسِّمه.
              </p>
              <div class="tag-row">
                {inline_tag("live scan", "accent")}
                {inline_tag("token estimate = chars / 4")}
                {inline_tag("no tiktoken installed")}
                {inline_tag("Arabic-first HUD")}
              </div>
              <ul class="hero-brief">
                <li>
                  <span class="list-kicker">أهم نتيجة</span>
                  <span>أوضح duplicate حقيقي هو <code>openai-docs</code> بين نسخة user-level ونسخة system.</span>
                </li>
                <li>
                  <span class="list-kicker">أكثر عنقود يخلق الإحساس بالزحمة</span>
                  <span>UI / Product ثم Planning / Proof ثم Portfolio pipeline.</span>
                </li>
                <li>
                  <span class="list-kicker">التوصية الأسرع أثرًا</span>
                  <span>ابدأ بالـ dedupe ثم merge صغيرين: <code>figma + figma-implement-design</code> و<code>frontend-skill → premium_ui_generator</code>.</span>
                </li>
              </ul>
            </div>

            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {inline_tag("deep verdict", "accent")}
                  {code_tag("omega-skills-hud-v9.html")}
                </div>
                <div class="poster-surface__score">
                  <strong>{format_num(totals["activation"])}</strong>
                  <span>إجمالي activation التقريبي</span>
                </div>
                <div class="poster-surface__name">أين السخونة الحقيقية؟</div>
                <p class="poster-surface__summary">
                  السخونة ليست في عدد المهارات وحده، بل في <strong>تكتلات تتفعل معًا</strong>.
                  أثقل عنقود عند تحميل المراجع هو <strong>{escape(heaviest_cluster["title_ar"])}</strong>.
                </p>
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  <span class="poster-meter"><span>أعلى baseline</span><strong>{escape(largest_baseline["skill_key"])}</strong></span>
                  <span class="poster-meter"><span>أعلى activation</span><strong>{escape(largest_activation["skill_key"])}</strong></span>
                  <span class="poster-meter"><span>أعلى refs</span><strong>{escape(largest_refs["skill_key"])}</strong></span>
                  <span class="poster-meter"><span>أعلى scripts</span><strong>{escape(largest_scripts["skill_key"])}</strong></span>
                </div>
                <p class="dim-copy">baseline = description surface / activation = opening SKILL.md / refs & scripts = possible extra load only if explicitly opened</p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{bilingual("كيف تقرأ الملف", "How to read this file", "span")}</p>
          <h2>كيف تقرأ أرقام التوكن هنا</h2>
          <p class="section-copy">
            هذه الأرقام <strong>تقديرية للمقارنة</strong> وليست billing-exact، لأن مكتبة <code>tiktoken</code> غير مثبتة هنا.
            اعتمدت على النص الفعلي لكل <code>SKILL.md</code> ووصفتين أساسيتين:
            <strong>baseline</strong> لما يوضع في سطح الاكتشاف، و<strong>activation</strong> لما تفتح المهارة نفسها.
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="stats-grid">
          <article class="duplicate-card">
            <div class="card-head"><h3>Baseline</h3>{inline_tag("fixed-ish", "accent")}</div>
            <div class="card-body">
              <p class="rail-copy">تكلفة تقريبية لوصف المهارة نفسه في registry أو surfaces التي تعرّف Codex بالمهارات المتاحة.</p>
              <div class="micro-metrics">
                <div class="micro-metric"><strong>{format_num(totals["baseline"])}</strong><span>إجمالي baseline</span></div>
                <div class="micro-metric"><strong>{escape(largest_baseline["skill_key"])}</strong><span>أعلى baseline</span></div>
              </div>
            </div>
          </article>

          <article class="duplicate-card">
            <div class="card-head"><h3>Activation</h3>{inline_tag("real cost", "accent")}</div>
            <div class="card-body">
              <p class="rail-copy">تكلفة تقريبية عند قراءة <code>SKILL.md</code> نفسها. هذه أهم طبقة عندما تشتغل المهارة فعلًا.</p>
              <div class="micro-metrics">
                <div class="micro-metric"><strong>{format_num(totals["activation"])}</strong><span>إجمالي activation</span></div>
                <div class="micro-metric"><strong>{escape(largest_activation["skill_key"])}</strong><span>أعلى activation</span></div>
              </div>
            </div>
          </article>

          <article class="duplicate-card">
            <div class="card-head"><h3>Refs / Scripts</h3>{inline_tag("possible extra", "accent")}</div>
            <div class="card-body">
              <p class="rail-copy">ليست تكلفة افتراضية. هي حمولة إضافية تقريبية فقط إذا فتحت المراجع أو السكربتات النصية نفسها أثناء التنفيذ.</p>
              <div class="micro-metrics">
                <div class="micro-metric"><strong>{format_num(totals["refs"])}</strong><span>refs possible</span></div>
                <div class="micro-metric"><strong>{format_num(totals["scripts"])}</strong><span>scripts possible</span></div>
              </div>
            </div>
          </article>

          <article class="duplicate-card">
            <div class="card-head"><h3>Important nuance</h3>{inline_tag("do not over-read", "accent")}</div>
            <div class="card-body">
              <p class="rail-copy">وجود skill كبيرة لا يعني أنها سيئة. أحيانًا تكون <strong>specialist</strong> ممتازة لكن low-frequency، والمشكلة فقط أنها ظاهرة كأنها peer يومي لباقي النظام.</p>
            </div>
          </article>
        </div>
      </section>

      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{bilingual("قراءة العناقيد", "Cluster reading", "span")}</p>
          <h2>العناقيد التي تفسر إحساس الزحمة</h2>
          <p class="section-copy">
            بدل سؤال “أي مهارة ملهاش لازمة؟” السؤال الأدق هو: <strong>أي stack يتفعل معًا فيخلق surface أعرض من اللازم؟</strong>
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="cluster-grid">
          {render_cluster_cards(clusters)}
        </div>
      </section>

      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{bilingual("مصفوفة القرار", "Immediate matrix", "span")}</p>
          <h2>مصفوفة القرار: keep / merge / hide / split</h2>
          <p class="section-copy">
            هذه ليست إعادة تصميم شاملة للمنظومة. هي أقرب إلى <strong>أول pass عملي</strong> لتخفيف الزحمة مع الحفاظ على القيمة العالية.
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="matrix-grid">
          {render_matrix()}
        </div>
      </section>

      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{bilingual("مراجعة التكرار", "Duplicate review", "span")}</p>
          <h2>العائلات المكررة</h2>
          <p class="section-copy">
            التكرار الحقيقي أخطر من overlap الصحي، لأنه يدفع baseline للأعلى من غير مكسب تشغيل واضح.
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="duplicate-grid">
          {render_duplicate_section(duplicates)}
        </div>
      </section>

      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{bilingual("النقاط الساخنة", "Hotspots", "span")}</p>
          <h2>أثقل النقاط في السطح الحالي</h2>
          <p class="section-copy">
            الأرقام هنا توضح من يثقل الـ registry، ومن يثقل activation، ومن يحمل مراجع أو سكربتات ضخمة إذا فُتحت.
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="hotspot-grid">
          {render_hotspots(rows)}
        </div>
      </section>

      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{bilingual("الجرد الكامل", "Full inventory", "span")}</p>
          <h2>الجرد الكامل لكل مهارة</h2>
          <p class="section-copy">
            الترتيب هنا افتراضيًا حسب activation الأعلى. استخدم البحث للفلترة بالاسم أو الفئة أو الـ stance.
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="filter-bar">
          <input id="skill-filter" class="hud-input" type="search" placeholder="ابحث باسم المهارة أو الفئة أو الـ stance...">
          <span class="filter-note">النتائج الظاهرة: <strong id="filter-count">0</strong></span>
          <span class="filter-note">الترتيب: الأعلى activation أولًا</span>
        </div>
        <div class="audit-table">
          <div class="audit-head">
            <div>Skill</div>
            <div>Category</div>
            <div>Stance</div>
            <div>Baseline</div>
            <div>Activation</div>
            <div>Refs</div>
            <div>Scripts</div>
            <div>Details</div>
          </div>
          {render_table(rows)}
        </div>
      </section>

      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{bilingual("الخلاصة التشغيلية", "Operator closeout", "span")}</p>
          <h2>الخلاصة التنفيذية</h2>
          <p class="section-copy">
            لو هتعمل pass واحد فقط هذا الأسبوع، فالأولوية المنطقية هي: <strong>dedupe</strong> ثم <strong>two merges</strong> ثم <strong>surface cleanup</strong>.
          </p>
        </div>
        <div class="section-divider"></div>
        <div class="stats-grid">
          <article class="duplicate-card">
            <div class="card-head"><h3>Step 1</h3>{inline_tag("dedupe", "accent")}</div>
            <p class="rail-copy">احذف أو أخفِ إحدى نسختي <code>openai-docs</code> أولًا. هذا أنظف مكسب سريع بلا مخاطرة منطقية تقريبًا.</p>
          </article>
          <article class="duplicate-card">
            <div class="card-head"><h3>Step 2</h3>{inline_tag("small merges", "accent")}</div>
            <p class="rail-copy">ادمج <code>figma</code> مع <code>figma-implement-design</code>، وادمج <code>frontend-skill</code> داخل <code>premium_ui_generator</code>.</p>
          </article>
          <article class="duplicate-card">
            <div class="card-head"><h3>Step 3</h3>{inline_tag("surface cleanup", "accent")}</div>
            <p class="rail-copy">اخفِ low-frequency macros مثل <code>self-learn</code> و<code>yeet</code> و<code>vercel-deploy</code> من surface التفكير اليومي.</p>
          </article>
          <article class="duplicate-card">
            <div class="card-head"><h3>Step 4</h3>{inline_tag("phase 2", "accent")}</div>
            <p class="rail-copy">بعدها فقط ارجع لعنقود planning وportfolio pipeline لتقرير هل تحتاج grouped entrypoints أو مجرد handoff boundaries أوضح.</p>
          </article>
        </div>
      </section>
    """


def build_shell(body_html: str) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-theme="dark" data-ui-lang="ar">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-v9-skills-audit">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl">
  <link rel="icon" href="data:,">
  <title>Omega Skills HUD V9 | تدقيق المهارات واستهلاك التوكن</title>
  <style>
{v7.V7_CSS}
{EXTRA_CSS}
  </style>
</head>
<body class="audit-page is-ready">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD V9 / live local audit / no remote assets / token figures are comparative estimates, not billing-exact</div>
  </div>
  <script>
{SCRIPT_JS}
  </script>
</body>
</html>
"""


def main() -> None:
    rows = scan_skills()
    html = build_shell(build_body(rows))
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
