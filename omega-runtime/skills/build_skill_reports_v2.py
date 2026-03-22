#!/usr/bin/env python3

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base


ROOT = base.ROOT
OUTPUT_HTML_DIR = ROOT / "output/html"
SKILLS_OUTPUT = OUTPUT_HTML_DIR / "omega-skills-hud-v2.html"
MEMORY_OUTPUT = OUTPUT_HTML_DIR / "omega-memory-learning-report-v2.html"

SHARED_CSS = """
:root {
  --bg: #05070b;
  --bg-soft: #0f141c;
  --surface: rgba(12, 16, 21, 0.74);
  --surface-strong: rgba(18, 24, 31, 0.9);
  --surface-soft: rgba(255, 255, 255, 0.03);
  --line: rgba(255, 194, 117, 0.18);
  --line-strong: rgba(255, 194, 117, 0.38);
  --ink: #f6efe5;
  --muted: rgba(246, 239, 229, 0.74);
  --dim: rgba(246, 239, 229, 0.48);
  --accent: #ffc275;
  --accent-strong: #ffe0ad;
  --accent-soft: rgba(255, 194, 117, 0.12);
  --success: #9ed4b0;
  --danger: #e98b78;
  --page-max: 1480px;
  --page-pad: 18px;
  --radius-xl: 32px;
  --radius-lg: 24px;
  --radius-md: 18px;
  --radius-sm: 12px;
  --shadow: 0 30px 80px rgba(0, 0, 0, 0.34);
  --body-font: "Segoe UI", Tahoma, Arial, sans-serif;
  --display-font: Georgia, "Times New Roman", serif;
  --mono-font: "Cascadia Mono", "DejaVu Sans Mono", "Liberation Mono", monospace;
}

html[data-theme="light"] {
  --bg: #f4eee5;
  --bg-soft: #fbf7f1;
  --surface: rgba(255, 252, 247, 0.82);
  --surface-strong: rgba(255, 252, 247, 0.94);
  --surface-soft: rgba(76, 53, 18, 0.04);
  --line: rgba(146, 103, 33, 0.16);
  --line-strong: rgba(146, 103, 33, 0.34);
  --ink: #1f1a16;
  --muted: rgba(31, 26, 22, 0.74);
  --dim: rgba(31, 26, 22, 0.48);
  --accent: #b56d1d;
  --accent-strong: #8d5512;
  --accent-soft: rgba(181, 109, 29, 0.12);
  --shadow: 0 26px 70px rgba(62, 41, 15, 0.12);
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  min-height: 100%;
}

html {
  background:
    radial-gradient(circle at 16% 12%, rgba(255, 194, 117, 0.14), transparent 30%),
    radial-gradient(circle at 82% 10%, rgba(255, 194, 117, 0.08), transparent 28%),
    linear-gradient(180deg, var(--bg-soft) 0%, var(--bg) 100%);
  color: var(--ink);
  font-family: var(--body-font);
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  scroll-behavior: smooth;
}

body {
  position: relative;
  overflow-x: clip;
}

body::before,
body::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
}

body::before {
  background:
    linear-gradient(to right, rgba(255, 194, 117, 0.06) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 194, 117, 0.06) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.22;
  mix-blend-mode: screen;
}

body::after {
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 194, 117, 0.09), transparent 46%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 32%);
  opacity: 0.8;
}

a {
  color: inherit;
  text-decoration-color: var(--line-strong);
  text-decoration-thickness: 1px;
}

code,
pre {
  font-family: var(--mono-font);
}

[data-ui-lang="ar"] [data-lang="en"],
[data-ui-lang="en"] [data-lang="ar"] {
  display: none !important;
}

.page-shell {
  width: min(100%, var(--page-max));
  margin: 0 auto;
  padding: 16px var(--page-pad) 96px;
  position: relative;
  z-index: 1;
}

.utility-bar {
  position: sticky;
  top: 10px;
  z-index: 30;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: 22px;
  background: color-mix(in srgb, var(--surface-strong) 84%, transparent);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow);
}

.brand-lockup {
  display: grid;
  gap: 4px;
}

.brand-lockup strong {
  font-size: 13px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
}

.brand-lockup span {
  color: var(--muted);
  font-size: 12px;
}

.metric-strip,
.control-cluster,
.tag-row,
.token-row,
.meter-row,
.meta-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.metric-strip {
  justify-content: center;
}

.metric-pill,
.control-readout,
.inline-tag,
.score-chip,
.tier-token,
.tier-kicker {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 36px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
}

.metric-pill strong,
.score-chip strong {
  font-size: 15px;
  color: var(--ink);
}

.metric-pill__label,
.control-readout,
.inline-tag,
.score-chip span,
.tier-kicker,
.tier-token {
  color: var(--muted);
  font-size: 12px;
}

.metric-pill--warn,
.inline-tag--warn {
  border-color: rgba(233, 139, 120, 0.38);
  color: var(--danger);
}

.metric-pill--accent,
.score-chip,
.tier-token,
.inline-tag--accent {
  border-color: var(--line-strong);
  background: var(--accent-soft);
}

.code-tag {
  font-family: var(--mono-font);
  font-size: 11px;
}

.control-button {
  cursor: pointer;
  min-height: 42px;
  padding: 10px 14px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface-strong) 78%, transparent);
  color: var(--ink);
  font: inherit;
  transition: transform 180ms ease, border-color 220ms ease, background 220ms ease;
}

.control-button:hover {
  transform: translateY(-1px);
  border-color: var(--line-strong);
  background: color-mix(in srgb, var(--surface-strong) 92%, transparent);
}

.hero-stage {
  position: relative;
  left: 50%;
  width: 100vw;
  margin-left: -50vw;
  margin-right: -50vw;
  min-height: clamp(560px, calc(100svh - 126px), 860px);
  display: flex;
  align-items: end;
  overflow: hidden;
  margin-top: 18px;
  padding-block: clamp(54px, 7vw, 86px);
  border-bottom: 1px solid var(--line);
}

.hero-stage::before,
.hero-stage::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-stage::before {
  background:
    linear-gradient(120deg, rgba(0, 0, 0, 0.32) 8%, transparent 46%),
    radial-gradient(circle at 78% 30%, rgba(255, 194, 117, 0.18), transparent 34%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 28%);
}

.hero-stage::after {
  background:
    repeating-linear-gradient(
      180deg,
      rgba(255, 255, 255, 0.035) 0,
      rgba(255, 255, 255, 0.035) 1px,
      transparent 1px,
      transparent 10px
    );
  opacity: 0.3;
}

.hero-inner {
  width: min(100%, var(--page-max));
  margin: 0 auto;
  padding-inline: var(--page-pad);
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(340px, 0.95fr);
  gap: clamp(24px, 3vw, 48px);
  align-items: end;
}

.hero-copy {
  max-width: 620px;
}

.hero-kicker,
.section-kicker,
.eyebrow {
  margin: 0;
  color: var(--accent);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 12px;
}

.hero-copy h1,
.poster-surface__name,
.section-head h2,
.story-band h3,
.feature-row h3,
.dense-row h3,
.stack-item h3,
.insight-panel h3 {
  margin: 0;
  font-family: var(--display-font);
  font-weight: 700;
  line-height: 0.94;
}

.hero-copy h1 {
  margin-top: 14px;
  font-size: clamp(3.4rem, 8vw, 7rem);
  letter-spacing: -0.04em;
  text-wrap: balance;
}

.hero-copy p,
.section-copy,
.rail-copy,
.muted-copy {
  margin: 0;
  font-size: 15px;
  line-height: 1.75;
  color: var(--muted);
}

.hero-copy .muted-copy {
  max-width: 48ch;
  margin-top: 16px;
}

.poster-surface {
  position: relative;
  overflow: hidden;
  padding: clamp(24px, 3vw, 34px);
  min-height: 430px;
  border: 1px solid var(--line);
  border-radius: 32px 32px 0 32px;
  background:
    linear-gradient(165deg, rgba(255, 194, 117, 0.16), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 50%),
    color-mix(in srgb, var(--surface-strong) 92%, transparent);
  box-shadow: var(--shadow);
  display: grid;
  align-content: space-between;
  gap: 24px;
}

.poster-surface::before,
.poster-surface::after {
  content: "";
  position: absolute;
  pointer-events: none;
}

.poster-surface::before {
  inset: auto -10% -18% auto;
  width: 62%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 194, 117, 0.18), transparent 70%);
}

.poster-surface::after {
  inset: 16px 18px auto auto;
  width: 160px;
  height: 160px;
  border: 1px solid rgba(255, 194, 117, 0.18);
  border-radius: 50%;
}

.poster-surface > * {
  position: relative;
  z-index: 1;
}

.poster-surface__headline {
  display: grid;
  gap: 14px;
}

.poster-surface__score {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.poster-surface__score strong {
  font-family: var(--display-font);
  font-size: clamp(4rem, 9vw, 7.6rem);
  line-height: 0.86;
  letter-spacing: -0.06em;
}

.poster-surface__score span {
  color: var(--muted);
  font-size: 14px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.poster-surface__name {
  font-size: clamp(2.4rem, 5vw, 4rem);
  letter-spacing: -0.04em;
}

.poster-surface__summary {
  max-width: 34ch;
}

.poster-surface__meta,
.poster-surface__meters {
  display: grid;
  gap: 12px;
}

.poster-meter,
.mini-meter {
  display: inline-grid;
  gap: 4px;
  min-width: 110px;
}

.poster-meter span,
.mini-meter span {
  color: var(--dim);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.poster-meter strong,
.mini-meter strong {
  font-size: 14px;
}

.section-block {
  position: relative;
  padding-top: 34px;
}

.section-block[data-parallax] {
  transform: translate3d(0, calc(var(--parallax, 0) * -16px), 0);
  will-change: transform;
}

.section-head {
  display: grid;
  gap: 12px;
  margin-bottom: 18px;
}

.section-head h2 {
  font-size: clamp(2rem, 3.6vw, 3.2rem);
  letter-spacing: -0.04em;
}

.section-copy {
  max-width: 62ch;
}

.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--line-strong), transparent);
  margin-top: 18px;
}

.exception-grid,
.insight-grid,
.split-grid,
.ledger-grid {
  display: grid;
  gap: 24px;
}

.exception-grid,
.insight-grid,
.split-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.ledger-grid {
  grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
}

.exception-strip,
.story-band,
.feature-row,
.dense-row,
.stack-item,
.fact-row,
.insight-panel {
  position: relative;
  transition: transform 220ms ease, border-color 220ms ease, background 220ms ease;
}

.exception-strip {
  padding: 18px 0;
  border-top: 1px solid var(--line);
}

.exception-strip:hover,
.story-band:hover,
.feature-row:hover,
.dense-row:hover,
.stack-item:hover,
.insight-panel:hover {
  transform: translateY(-2px);
}

.exception-strip h3,
.story-band h3,
.feature-row h3,
.dense-row h3,
.stack-item h3,
.insight-panel h3 {
  font-size: 1.6rem;
  letter-spacing: -0.03em;
}

.path-label,
.dim-copy,
.meta-copy {
  color: var(--dim);
  font-size: 12px;
  line-height: 1.65;
}

.band-stack,
.stack-list,
.story-stack,
.dense-list,
.feature-list {
  display: grid;
}

.tier-band {
  padding-top: 10px;
  border-top: 1px solid var(--line);
}

.tier-band + .tier-band {
  margin-top: 24px;
}

.tier-band__intro {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: end;
  gap: 12px;
  margin-bottom: 8px;
}

.feature-row {
  display: grid;
  grid-template-columns: 90px minmax(0, 1fr) auto;
  gap: 18px;
  padding: 20px 0;
  border-top: 1px solid rgba(255, 194, 117, 0.1);
}

.feature-row:first-child,
.dense-row:first-child,
.stack-item:first-child {
  border-top: none;
}

.feature-rank {
  display: grid;
  gap: 8px;
  align-content: start;
}

.feature-rank strong {
  font-family: var(--display-font);
  font-size: 2.4rem;
  line-height: 0.9;
  letter-spacing: -0.04em;
}

.feature-tail {
  display: grid;
  gap: 8px;
  justify-items: end;
  align-content: start;
  text-align: end;
}

.dense-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
  margin-top: 18px;
}

.dense-cluster {
  padding-top: 10px;
  border-top: 1px solid var(--line);
}

.dense-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  padding: 14px 0;
  border-top: 1px solid rgba(255, 194, 117, 0.1);
}

.dense-row__side {
  display: grid;
  gap: 8px;
  justify-items: end;
  align-content: start;
  text-align: end;
}

.story-stack {
  border-top: 1px solid var(--line);
}

.story-band {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 16px;
  padding: 18px 0;
  border-top: 1px solid rgba(255, 194, 117, 0.1);
}

.story-band:first-child {
  border-top: none;
}

.story-band__content {
  display: grid;
  gap: 10px;
}

.story-band__tokens {
  grid-column: 2;
}

.stack-list {
  border-top: 1px solid var(--line);
}

.stack-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 14px;
  padding: 16px 0;
  border-top: 1px solid rgba(255, 194, 117, 0.1);
}

.insight-panel {
  padding: 18px 0;
  border-top: 1px solid var(--line);
  display: grid;
  gap: 14px;
}

.insight-panel:first-child {
  border-top: none;
}

.fact-list,
.report-list,
.source-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0;
}

.fact-list li,
.report-list li,
.source-list a,
.fact-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  padding: 12px 0;
  border-top: 1px solid rgba(255, 194, 117, 0.1);
  align-items: start;
}

.report-list li,
.source-list a {
  grid-template-columns: minmax(0, 1fr);
}

.fact-list li:first-child,
.report-list li:first-child,
.source-list a:first-child {
  border-top: none;
}

.fact-list code,
.report-list code,
.source-list code,
.code-panel code {
  color: var(--accent-strong);
  font-size: 12px;
}

.code-panel {
  margin: 0;
  max-height: 320px;
  overflow: auto;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface-strong) 88%, transparent);
  color: var(--muted);
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

.source-list a:hover,
.source-list a:focus-visible {
  border-color: var(--line-strong);
  background: var(--accent-soft);
  outline: none;
}

.footer-note {
  margin-top: 34px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  color: var(--dim);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.accent {
  color: var(--accent);
}

body:not(.is-ready) .hero-copy > *,
body:not(.is-ready) .poster-surface,
body:not(.is-ready) .section-block {
  opacity: 0;
  transform: translate3d(0, 24px, 0);
}

body.is-ready .hero-copy > *,
body.is-ready .poster-surface,
body.is-ready .section-block {
  opacity: 1;
  transform: translate3d(0, 0, 0);
  transition:
    opacity 520ms ease,
    transform 620ms cubic-bezier(0.22, 1, 0.36, 1),
    border-color 220ms ease,
    background 220ms ease;
}

body.is-ready .hero-copy > *:nth-child(1) { transition-delay: 60ms; }
body.is-ready .hero-copy > *:nth-child(2) { transition-delay: 140ms; }
body.is-ready .hero-copy > *:nth-child(3) { transition-delay: 220ms; }
body.is-ready .hero-copy > *:nth-child(4) { transition-delay: 300ms; }
body.is-ready .poster-surface { transition-delay: 220ms; }

.memory-page .hero-stage::before {
  background:
    linear-gradient(120deg, rgba(0, 0, 0, 0.24) 10%, transparent 42%),
    radial-gradient(circle at 76% 28%, rgba(255, 194, 117, 0.14), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.015), transparent 28%);
}

.memory-page .poster-surface {
  min-height: 380px;
}

@media (max-width: 1180px) {
  .utility-bar {
    grid-template-columns: 1fr;
    justify-items: stretch;
  }

  .metric-strip {
    justify-content: start;
  }

  .hero-grid,
  .ledger-grid {
    grid-template-columns: 1fr;
  }

  .feature-row {
    grid-template-columns: 80px minmax(0, 1fr);
  }

  .feature-tail,
  .dense-row__side {
    justify-items: start;
    text-align: start;
  }

  .feature-tail {
    grid-column: 2;
  }
}

@media (max-width: 900px) {
  .utility-bar {
    position: static;
  }

  .hero-stage {
    min-height: auto;
    padding-block: 44px;
  }

  .exception-grid,
  .insight-grid,
  .split-grid,
  .dense-grid {
    grid-template-columns: 1fr;
  }

  .story-band,
  .stack-item {
    grid-template-columns: 1fr;
  }

  .story-band__tokens {
    grid-column: auto;
  }
}

@media (max-width: 640px) {
  :root {
    --page-pad: 14px;
  }

  .page-shell {
    padding-bottom: 70px;
  }

  .control-cluster {
    width: 100%;
  }

  .control-button {
    flex: 1 1 0;
  }

  .hero-copy h1 {
    font-size: clamp(2.5rem, 13vw, 4rem);
  }

  .poster-surface__name {
    font-size: clamp(2rem, 10vw, 3rem);
  }

  .feature-row,
  .dense-row,
  .fact-list li,
  .story-band,
  .stack-item {
    grid-template-columns: 1fr;
  }

  .feature-tail,
  .dense-row__side {
    grid-column: auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }

  *,
  *::before,
  *::after {
    animation: none !important;
    transition: none !important;
  }

  .section-block[data-parallax] {
    transform: none !important;
  }
}
"""

SHARED_JS = """
(function () {
  const root = document.documentElement;
  const langState = document.getElementById('lang-state');
  const themeState = document.getElementById('theme-state');
  const langButton = document.getElementById('lang-toggle');
  const themeButton = document.getElementById('theme-toggle');
  const langKey = 'omega.ui.lang';
  const themeKey = 'omega.ui.theme';
  const langLabels = {
    ar: { lang: 'AR / RTL', themeDark: 'داكن', themeLight: 'فاتح' },
    en: { lang: 'EN / LTR', themeDark: 'Dark', themeLight: 'Light' }
  };

  function loadSetting(key, fallback) {
    try {
      return localStorage.getItem(key) || fallback;
    } catch (error) {
      return fallback;
    }
  }

  function saveSetting(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      void error;
    }
  }

  function applyLanguage(lang) {
    root.setAttribute('data-ui-lang', lang);
    root.lang = lang;
    root.dir = lang === 'ar' ? 'rtl' : 'ltr';
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
  }

  function refreshStateLabels() {
    const lang = root.getAttribute('data-ui-lang');
    const theme = root.getAttribute('data-theme');
    if (langState) {
      langState.textContent = langLabels[lang].lang;
    }
    if (themeState) {
      themeState.textContent = theme === 'dark' ? langLabels[lang].themeDark : langLabels[lang].themeLight;
    }
  }

  const initialLang = loadSetting(langKey, 'ar');
  const initialTheme = loadSetting(themeKey, 'dark');
  applyLanguage(initialLang);
  applyTheme(initialTheme);
  refreshStateLabels();

  if (langButton) {
    langButton.addEventListener('click', function () {
      const next = root.getAttribute('data-ui-lang') === 'ar' ? 'en' : 'ar';
      applyLanguage(next);
      saveSetting(langKey, next);
      refreshStateLabels();
    });
  }

  if (themeButton) {
    themeButton.addEventListener('click', function () {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      saveSetting(themeKey, next);
      refreshStateLabels();
    });
  }

  const depthNodes = Array.from(document.querySelectorAll('[data-parallax]'));
  let scheduled = false;

  function updateDepth() {
    const viewport = window.innerHeight || 1;
    depthNodes.forEach(function (node) {
      const rect = node.getBoundingClientRect();
      const center = rect.top + rect.height / 2;
      const delta = Math.max(-1, Math.min(1, (center - viewport / 2) / (viewport / 2)));
      node.style.setProperty('--parallax', delta.toFixed(3));
    });
    scheduled = false;
  }

  function requestDepth() {
    if (scheduled || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    scheduled = true;
    window.requestAnimationFrame(updateDepth);
  }

  window.addEventListener('scroll', requestDepth, { passive: true });
  window.addEventListener('resize', requestDepth);
  window.addEventListener('load', function () {
    document.body.classList.add('is-ready');
    requestDepth();
  });
  requestDepth();
})();
"""


def escape(value):
    return base.escape(str(value))


def bilingual_text(ar: str, en: str, tag: str = "div", cls: str = "") -> str:
    return base.bilingual_text(ar, en, tag, cls)


def bilingual_html(ar: str, en: str, tag: str = "div", cls: str = "") -> str:
    return base.bilingual_html(ar, en, tag, cls)


def pretty_timestamp(value: str) -> str:
    return base.pretty_timestamp(value)


def metric_pill(value, ar: str, en: str, tone: str = "") -> str:
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


def state_readout(readout_id: str) -> str:
    return f'<span class="control-readout" id="{escape(readout_id)}"></span>'


def control_button(button_id: str, ar: str, en: str) -> str:
    return f'<button class="control-button" id="{escape(button_id)}">{bilingual_html(ar, en, "span")}</button>'


def advice_tags(skill_id: str) -> str:
    return "".join(inline_tag(ar, en) for en, ar in base.advice_flags(skill_id))


def category_tag(category: str) -> str:
    ar, en = base.category_labels(category)
    return inline_tag(ar, en, "accent")


def component_meters(skill: dict) -> str:
    labels = [
        ("E", "execution", 40),
        ("U", "uniqueness", 20),
        ("C", "clarity", 15),
        ("M", "maintenance", 15),
        ("G", "evidence", 10),
    ]
    return "".join(
        f'<span class="mini-meter"><span>{label}</span><strong>{skill["components"][key]}/{max_value}</strong></span>'
        for label, key, max_value in labels
    )


def feature_tail(skill: dict) -> str:
    return f"""
      <div class="feature-tail">
        <span class="score-chip"><strong>{skill["score"]}</strong><span>/100</span></span>
        <span class="dim-copy">{escape(pretty_timestamp(skill["source_last_checked_at"]))}</span>
        <span class="dim-copy">{escape(pretty_timestamp(skill["doc_last_refreshed_at"]))}</span>
      </div>
    """


def render_feature_skill(skill: dict) -> str:
    return f"""
      <article class="feature-row">
        <div class="feature-rank">
          <span class="tier-token">{escape(skill["tier"])}</span>
          <strong>{skill["score"]}</strong>
        </div>
        <div class="feature-body">
          <div class="tag-row">
            {code_tag(skill["skill_id"])}
            {category_tag(skill["category"])}
            {advice_tags(skill["skill_id"])}
          </div>
          <h3>{escape(skill["display_name"])}</h3>
          {bilingual_text(skill["summary"], skill["summary"], "p", "rail-copy")}
          <div class="meter-row">{component_meters(skill)}</div>
          {bilingual_text(skill["tier_blurb_ar"], skill["tier_blurb_en"], "p", "dim-copy")}
        </div>
        {feature_tail(skill)}
      </article>
    """


def render_dense_skill(skill: dict) -> str:
    return f"""
      <article class="dense-row">
        <div class="dense-row__body">
          <div class="tag-row">
            {code_tag(skill["skill_id"])}
            {category_tag(skill["category"])}
          </div>
          <h3>{escape(skill["display_name"])}</h3>
          {bilingual_text(skill["summary"], skill["summary"], "p", "rail-copy")}
        </div>
        <div class="dense-row__side">
          <span class="tier-token">{escape(skill["tier"])}</span>
          <span class="score-chip"><strong>{skill["score"]}</strong><span>/100</span></span>
          {bilingual_text(skill["tier_blurb_ar"], skill["tier_blurb_en"], "span", "dim-copy")}
        </div>
      </article>
    """


def render_exception(skill: dict) -> str:
    return f"""
      <article class="exception-strip">
        <div class="tag-row">
          {inline_tag("استثناء نظامي", "System Exception", "warn")}
          {category_tag(skill["category"])}
        </div>
        <h3>{escape(skill["display_name"])}</h3>
        {bilingual_text(skill["summary"], skill["summary"], "p", "rail-copy")}
        <p class="path-label">{escape(skill["source_path"])}</p>
      </article>
    """


def render_story_band(group: dict) -> str:
    return f"""
      <article class="story-band">
        <div>
          <span class="tier-token">{escape(group["tier"])}</span>
        </div>
        <div class="story-band__content">
          {bilingual_text(group["label_ar"], group["label_en"], "h3")}
          {bilingual_text(group["why_ar"], group["why_en"], "p", "rail-copy")}
          {bilingual_text(group["action_ar"], group["action_en"], "p", "dim-copy")}
          <div class="token-row story-band__tokens">
            {"".join(code_tag(skill_id) for skill_id in group["skills"])}
          </div>
        </div>
      </article>
    """


def render_stack_item(candidate: dict, kind: str) -> str:
    title = candidate["skill"]
    detail_ar = candidate["instead_ar"] if kind == "retire" else candidate["next_ar"]
    detail_en = candidate["instead_en"] if kind == "retire" else candidate["next_en"]
    return f"""
      <article class="stack-item">
        <div>
          <span class="tier-token">{escape(candidate["tier"])}</span>
        </div>
        <div>
          <h3>{escape(title)}</h3>
          {bilingual_text(candidate["reason_ar"], candidate["reason_en"], "p", "rail-copy")}
          {bilingual_text(detail_ar, detail_en, "p", "dim-copy")}
        </div>
      </article>
    """


def render_fact_list(items: list[tuple[str, str]]) -> str:
    return "".join(
        f"<li><code>{escape(key)}</code><span>{escape(value)}</span></li>" for key, value in items
    )


def render_report_list(items: list[tuple[str, str]]) -> str:
    return "".join(bilingual_html(ar, en, "li") for ar, en in items)


def render_source_links() -> str:
    return "".join(
        f'<a href="{escape(link["url"])}"><strong>{escape(link["label"])}</strong><span class="path-label">{escape(link["url"])}</span></a>'
        for link in base.OPENAI_DOC_LINKS
    )


def build_topbar(page_label_ar: str, page_label_en: str, meta_html: str) -> str:
    return f"""
      <header class="utility-bar">
        <div class="brand-lockup">
          <strong>OMEGA HUD V2</strong>
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


def build_shell(title_en: str, title_ar: str, body_class: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-cinematic-v2">
  <meta name="omega:page_intent" content="interactive_hud">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{escape(title_en)} | {escape(title_ar)}</title>
  <style>
{SHARED_CSS}
  </style>
</head>
<body class="{escape(body_class)}">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA HUD V2 / cinematic alternate artifact / local only / no external assets</div>
  </div>
  <script>
{SHARED_JS}
  </script>
</body>
</html>
"""


def build_skills_page(skills: list[dict]) -> str:
    top_level = [skill for skill in skills if not skill["is_exception"]]
    exceptions = [skill for skill in skills if skill["is_exception"]]
    top_level.sort(key=lambda item: (-item["score"], item["skill_id"]))
    best = top_level[0]
    tier_groups = {tier: [skill for skill in top_level if skill["tier"] == tier] for tier in ("S", "A", "B", "C")}
    generated_at = pretty_timestamp(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))

    meta_html = "".join(
        [
            metric_pill(len(skills), "إجمالي السجل", "Catalog entries"),
            metric_pill(len(top_level), "مهارات Top-Level", "Top-level skills"),
            metric_pill(len(exceptions), "استثناءات نظامية", "System exceptions"),
            metric_pill(generated_at, "تم التوليد", "Generated"),
        ]
    )

    topbar = build_topbar("نسخة سينمائية بديلة", "Cinematic alternate edition", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{bilingual_html("Taste Upgrade Mode / بلا source drift", "Taste Upgrade Mode / no source drift", "span")}</p>
              <h1>{bilingual_html("أفضل مهارة الآن تقود المشهد: <span class=\"accent\">God Plan Mode</span>", "One skill still leads the board: <span class=\"accent\">God Plan Mode</span>", "span")}</h1>
              {bilingual_text("النسخة دي تحافظ على نفس الحقيقة التشغيلية، لكن تقدمها كواجهة أقرب لغرفة تحكم أوميجا: hero أوضح، rails أنظف، وطبقات أقل تكرارًا من شكل الكروت المعتاد.", "This edition keeps the same operational truth, but stages it like an Omega control room: a stronger poster hero, cleaner rails, and less repeated card chrome.", "p", "muted-copy")}
              <div class="tag-row">
                {inline_tag("معنى S هنا: أعلى كفاءة تشغيلية", "S here means highest operational efficiency", "accent")}
                {inline_tag("الاستثناءات النظامية خارج المقارنة", "System exceptions stay outside comparative scoring")}
                {inline_tag("نفس مفاتيح التخزين المحلي", "Same localStorage keys")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {inline_tag("الأفضل حاليًا", "Best overall", "accent")}
                  {code_tag(best["skill_id"])}
                </div>
                <div class="poster-surface__score">
                  <strong>{best["score"]}</strong>
                  <span>/ 100</span>
                </div>
                <div class="poster-surface__name">{escape(best["display_name"])}</div>
                {bilingual_text("قوة المهارة هنا جاية من leverage كبير في التخطيط، صياغة المسار، وتقليل التخمين قبل التنفيذ.", "Its edge comes from high leverage in planning, path framing, and reducing guesswork before execution.", "p", "poster-surface__summary")}
              </div>
              <div class="poster-surface__meta">
                <div class="tag-row">
                  {category_tag(best["category"])}
                  {advice_tags(best["skill_id"])}
                </div>
                <div class="meter-row poster-surface__meters">
                  {component_meters(best)}
                </div>
                <div class="meta-inline">
                  {inline_tag("فحص المصدر: " + pretty_timestamp(best["source_last_checked_at"]), "Source check: " + pretty_timestamp(best["source_last_checked_at"]))}
                  {inline_tag("تحديث الوصف: " + pretty_timestamp(best["doc_last_refreshed_at"]), "Doc refresh: " + pretty_timestamp(best["doc_last_refreshed_at"]))}
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    system_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("شريط الاستثناءات", "Exception strip", "span")}</p>
          <h2>{bilingual_html("System Exceptions خارج المقارنة", "System Exceptions outside comparison", "span")}</h2>
          {bilingual_text("المهارات دي موثقة لأن لها مصدرًا صالحًا داخل `.system`، لكنها لا تدخل tier ranking. الاستثناء المكسور `arabic-output-guard` يظل خارج النسخة الحالية لأنه لم يعد يملك مصدرًا فعليًا.", "These skills remain documented because they still have valid `.system` sources, but they stay outside the tier ranking. The broken `arabic-output-guard` exception remains excluded because its real source no longer exists.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="exception-grid">
          {"".join(render_exception(skill) for skill in exceptions)}
        </div>
      </section>
    """

    efficiency_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("العمود الفقري للترتيب", "Editorial efficiency rails", "span")}</p>
          <h2>{bilingual_html("Efficiency Tiers كسكك تشغيلية", "Efficiency Tiers as operating rails", "span")}</h2>
          {bilingual_text("Tier S و Tier A يظهران كمسارات مميزة عالية التأثير. Tier B و Tier C يتحولان إلى operator lists أكثر كثافة وأقل ضجيجًا بصريًا.", "Tier S and Tier A appear as featured high-impact rails. Tier B and Tier C collapse into denser operator lists with lighter visual treatment.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="band-stack">
          <section class="tier-band">
            <div class="tier-band__intro">
              <div>
                <span class="tier-kicker">{bilingual_html("Tier S / الأعلى كفاءة", "Tier S / highest efficiency", "span")}</span>
              </div>
              <div class="tag-row">
                {inline_tag("4 مهارات في القمة", "4 skills at the top")}
              </div>
            </div>
            <div class="feature-list">
              {"".join(render_feature_skill(skill) for skill in tier_groups["S"])}
            </div>
          </section>
          <section class="tier-band">
            <div class="tier-band__intro">
              <div>
                <span class="tier-kicker">{bilingual_html("Tier A / قوي جدًا", "Tier A / strong", "span")}</span>
              </div>
              <div class="tag-row">
                {inline_tag("5 مهارات رافعتها عالية", "5 high-leverage skills")}
              </div>
            </div>
            <div class="feature-list">
              {"".join(render_feature_skill(skill) for skill in tier_groups["A"])}
            </div>
          </section>
        </div>
        <div class="dense-grid">
          <section class="dense-cluster">
            <div class="tier-band__intro">
              <span class="tier-kicker">{bilingual_html("Tier B / مفيد", "Tier B / useful", "span")}</span>
              {inline_tag("15 skill", "15 skills")}
            </div>
            <div class="dense-list">
              {"".join(render_dense_skill(skill) for skill in tier_groups["B"])}
            </div>
          </section>
          <section class="dense-cluster">
            <div class="tier-band__intro">
              <span class="tier-kicker">{bilingual_html("Tier C / تخصصي أو منخفض التكرار", "Tier C / specialist", "span")}</span>
              {inline_tag("13 skill", "13 skills")}
            </div>
            <div class="dense-list">
              {"".join(render_dense_skill(skill) for skill in tier_groups["C"])}
            </div>
          </section>
        </div>
      </section>
    """

    merge_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Consolidation map", "Consolidation map", "span")}</p>
          <h2>{bilingual_html("Merge Candidates كحكايات دمج", "Merge Candidates as consolidation stories", "span")}</h2>
          {bilingual_text("المقصود هنا ليس تشغيل المهارات معًا دائمًا، بل تحديد المجموعات التي فيها overlap أو handoff يمكن تقليله بواجهة أو contract أوضح.", "This is not a recommendation to always call these skills together. It identifies clusters where overlap or handoff cost could be reduced with a clearer surface or contract.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="story-stack">
          {"".join(render_story_band(group) for group in base.MERGE_GROUPS)}
        </div>
      </section>
    """

    retire_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Cognitive load relief", "Cognitive load relief", "span")}</p>
          <h2>{bilingual_html("Retire / Skip Candidates كقائمة تخفيف", "Retire / Skip Candidates as a relief list", "span")}</h2>
          {bilingual_text("هذه ليست دعوة لحذف المهارات من المصدر. هي فقط قائمة بالقدرات التي يفضّل تصنيفها كمسارات عند الطلب بدل الاحتفاظ بها ذهنيًا طوال الوقت.", "This is not a deletion list. It is a recommendation to classify certain capabilities as on-demand paths instead of carrying them mentally by default.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="stack-list">
          {"".join(render_stack_item(item, "retire") for item in base.RETIRE_CANDIDATES)}
        </div>
      </section>
    """

    improve_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Forward pressure", "Forward pressure", "span")}</p>
          <h2>{bilingual_html("Improve Next كخريطة ضغط", "Improve Next as a pressure map", "span")}</h2>
          {bilingual_text("هنا معنى S ليس الأفضل، بل الأعلى احتياجًا إلى tightening أو تحديث أو وضوح إضافي في النسخ القادمة.", "Here, S does not mean best. It marks the skills that deserve the most tightening, freshness, or clarity in upcoming revisions.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="stack-list">
          {"".join(render_stack_item(item, "improve") for item in base.IMPROVE_CANDIDATES)}
        </div>
      </section>
    """

    registry_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Ledger closeout", "Ledger closeout", "span")}</p>
          <h2>{bilingual_html("Registry Notes And Sources", "Registry Notes And Sources", "span")}</h2>
          {bilingual_text("النسخة البديلة دي لا تغيّر الحقيقة، لكنها تعيد تمثيلها بصريًا. نفس الروابط الرسمية والنتائج التشغيلية ما زالت هي المرجع.", "This alternate edition does not change the truth. It only stages it differently. The same official links and operational results remain authoritative.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{bilingual_html("ما الذي تغيّر في السجل؟", "What changed in the registry?", "span")}</h3>
            <ul class="report-list">
              {render_report_list([
                  ("تمت إضافة 5 أوصاف ناقصة: frontend-skill, omega-ai-runtime, omega-format, omega-proof-gate, omega-repo-map", "Added 5 missing descriptions: frontend-skill, omega-ai-runtime, omega-format, omega-proof-gate, omega-repo-map"),
                  ("إجمالي السجل الحالي 39 entry = 37 top-level + 2 system exceptions", "Current registry total is 39 entries = 37 top-level skills + 2 system exceptions"),
                  ("العنصر broken القديم `arabic-output-guard` يظل خارج السجل لأنه بلا مصدر فعلي", "The old broken `arabic-output-guard` entry remains out because it has no real source"),
              ])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("الروابط الرسمية المراجعة", "Official links reviewed", "span")}</h3>
            <div class="source-list">
              {render_source_links()}
            </div>
          </article>
        </div>
      </section>
    """

    body = topbar + hero + system_section + efficiency_section + merge_section + retire_section + improve_section + registry_section
    return build_shell("Omega Skills HUD V2", "لوحة مهارات أوميجا V2", "skills-page", body)


def build_memory_page(skills: list[dict], snapshot: dict) -> str:
    inspect = snapshot["inspect"]
    triage = snapshot["triage"]
    suggest_entries = snapshot["suggest_entries"]
    key_counts = snapshot["key_counts"]
    self_learn = snapshot["self_learn"]
    baseline = snapshot["baseline"] or {}
    generated_at = pretty_timestamp(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    latest_event = self_learn["latest_event"]
    latest_reversible = self_learn["latest_reversible_event"]
    delta_pending = triage["pending_total"] - baseline.get("pending_total", triage["pending_total"])
    doctor_excerpt = " / ".join(snapshot["doctor_text"].splitlines()[:2])
    backlog_sample = suggest_entries[:8]

    meta_html = "".join(
        [
            metric_pill(triage["pending_total"], "Pending backlog", "Pending backlog"),
            metric_pill(self_learn["health"]["event_sequence"], "أحداث self-learn", "Self-learn events"),
            metric_pill(self_learn["health"]["active_patterns_count"], "أنماط durable", "Durable patterns"),
            metric_pill(generated_at, "تم التوليد", "Generated"),
        ]
    )

    topbar = build_topbar("نسخة تحليلية V2", "Forensic companion edition", meta_html)

    hero = f"""
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{bilingual_html("Forensic companion / نفس pipeline", "Forensic companion / same pipeline", "span")}</p>
              <h1>{bilingual_html("الذاكرة <span class=\"accent\">مستقرة</span>، والتعلّم <span class=\"accent\">منضبط</span>، لكن لا يوجد auto-promotion.", "Memory is <span class=\"accent\">stable</span>, learning is <span class=\"accent\">disciplined</span>, and there is still no auto-promotion.", "span")}</h1>
              {bilingual_text("هذه النسخة تهدّي الصوت البصري، لكنها تبقي نفس الحقيقة: doctor سليم، backlog ما زال ephemeral بالكامل تقريبًا، وself-learn في وضع observe/report فقط.", "This edition lowers the visual temperature, but keeps the same truth: doctor is healthy, the backlog is still effectively all-ephemeral, and self-learn stayed in observe/report mode only.", "p", "muted-copy")}
              <div class="tag-row">
                {inline_tag("doctor صالح", "Doctor healthy", "accent")}
                {inline_tag("pending لا يزال 40", "Pending still 40")}
                {inline_tag("لا يوجد promotable durable", "No promotable durable candidate")}
              </div>
            </div>
            <article class="poster-surface">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {inline_tag("حقيقة التشغيل الحالية", "Current operational truth", "accent")}
                  {inline_tag("لا auto-promotion", "No auto-promotion")}
                </div>
                <div class="poster-surface__score">
                  <strong>{triage["pending_total"]}</strong>
                  <span>{bilingual_html("pending", "pending", "span")}</span>
                </div>
                <div class="poster-surface__name">{bilingual_html("backlog قابل للقراءة، لكنه غير قابل للترقية", "Readable backlog, but not promotable", "span")}</div>
                {bilingual_text("القراءة الحالية مبنية على inspect / triage / suggest / doctor / self-learn report من نفس جلسة التوليد.", "This reading is grounded in inspect / triage / suggest / doctor / self-learn report from the same generation pass.", "p", "poster-surface__summary")}
              </div>
              <div class="poster-surface__meta">
                <div class="meter-row poster-surface__meters">
                  <span class="poster-meter"><span>doctor</span><strong>OK</strong></span>
                  <span class="poster-meter"><span>promotable</span><strong>{triage["promotable_total"]}</strong></span>
                  <span class="poster-meter"><span>events</span><strong>{self_learn["health"]["event_sequence"]}</strong></span>
                  <span class="poster-meter"><span>patterns</span><strong>{self_learn["health"]["active_patterns_count"]}</strong></span>
                </div>
                <p class="dim-copy">{escape(doctor_excerpt)}</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    """

    profile_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Durable profile", "Durable profile", "span")}</p>
          <h2>{bilingual_html("Persistent Memory / الملف durable", "Persistent Memory / durable profile", "span")}</h2>
          {bilingual_text("الذاكرة الدائمة ما زالت تحتفظ بقواعد التعاون الأساسية والمشهد الحالي للمشروع، بدون أي ادعاء بترقية backlog غير صالح.", "Durable memory still holds the core collaboration defaults and the current project overlay, without pretending the backlog is promotable.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="insight-grid">
          <article class="insight-panel">
            <h3>{bilingual_html("تفضيلات التعاون durable", "Durable collaboration profile", "span")}</h3>
            <ul class="fact-list">
              {render_fact_list([
                  ("communication.language", inspect["language"]),
                  ("communication.tone", inspect["tone"]),
                  ("assistant.expected_role", inspect["role"]),
                  ("workflow.plan_preference", inspect["plan"]),
                  ("workflow.review_preference", inspect["review"]),
              ])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("مشهد المشروع الحالي", "Current project overlay", "span")}</h3>
            <ul class="fact-list">
              {render_fact_list([
                  ("project.id", inspect["project_id"]),
                  ("project.domain", inspect["domain"]),
                  ("project.aliases", inspect["aliases"]),
                  ("root", inspect["root_path"]),
              ])}
            </ul>
          </article>
        </div>
      </section>
    """

    triage_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Queue diagnosis", "Queue diagnosis", "span")}</p>
          <h2>{bilingual_html("Triage + Backlog Distribution", "Triage + backlog distribution", "span")}</h2>
          {bilingual_text("القسم ده يوضح لماذا backlog ما زال غير قابل للترقية: no conflicts، لكن no promotable durable candidate أيضًا.", "This section explains why the backlog remains non-promotable: there are no conflicts, but there is also no promotable durable candidate.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{bilingual_html("نتيجة triage الحالية", "Current triage result", "span")}</h3>
            <ul class="fact-list">
              {render_fact_list([
                  ("pending_total", triage["pending_total"]),
                  ("ephemeral_total", triage["ephemeral_total"]),
                  ("promotable_total", triage["promotable_total"]),
                  ("conflict_count", triage["conflict_count"]),
                  ("delta_vs_baseline", f"{delta_pending:+d}"),
              ])}
            </ul>
            {bilingual_text("خلاصة القراءة: كل ما تبقى تقريبًا ephemeral، لذلك الترقية غير مبررة ضمن policy الحالية.", "Bottom line: what remains is effectively all-ephemeral, so promotion is not justified under the current policy.", "p", "dim-copy")}
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("توزيع مفاتيح الـ backlog", "Backlog key distribution", "span")}</h3>
            <ul class="fact-list">
              {render_fact_list([(key, count) for key, count in key_counts.most_common()])}
            </ul>
          </article>
        </div>
      </section>
    """

    self_learn_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Self-only boundary", "Self-only boundary", "span")}</p>
          <h2>{bilingual_html("Self Learn / health + event ledger", "Self Learn / health + event ledger", "span")}</h2>
          {bilingual_text("في هذه المهمة لم يحدث apply جديد داخل self-learn. المطلوب كان قراءة الحالة الحالية وعرضها بوضوح فقط.", "No new apply happened inside self-learn for this task. The job here was to read the current state and stage it clearly.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="ledger-grid">
          <div>
            <article class="insight-panel">
              <h3>{bilingual_html("صحة المهارة", "Skill health", "span")}</h3>
              <ul class="fact-list">
                {render_fact_list([
                    ("skill_version", self_learn["health"]["skill_version"]),
                    ("event_sequence", self_learn["health"]["event_sequence"]),
                    ("successful_evolutions", self_learn["health"]["successful_evolutions"]),
                    ("failed_evolutions", self_learn["health"]["failed_evolutions"]),
                    ("last_verification_status", self_learn["health"]["last_verification_status"]),
                    ("current_renderer_profile", self_learn["health"]["current_renderer_profile"]),
                    ("active_patterns_count", self_learn["health"]["active_patterns_count"]),
                ])}
              </ul>
            </article>
            <article class="insight-panel">
              <h3>{bilingual_html("الذاكرة الداخلية الحالية", "Current internal memory state", "span")}</h3>
              <ul class="fact-list">
                {render_fact_list([
                    ("journal_event_count", self_learn["memory_summary"]["journal_event_count"]),
                    ("durable_pattern_count", self_learn["memory_summary"]["durable_pattern_count"]),
                    ("suppressed_fingerprint_count", self_learn["memory_summary"]["suppressed_fingerprint_count"]),
                    ("apply_mode", self_learn["decision_cache"]["recent_trusted_defaults"]["apply_mode"]),
                    ("prefer_propose_for_freeform", str(self_learn["decision_cache"]["recent_trusted_defaults"]["prefer_propose_for_freeform"]).lower()),
                ])}
              </ul>
            </article>
          </div>
          <div>
            <article class="insight-panel">
              <h3>{bilingual_html("آخر حدث", "Latest event", "span")}</h3>
              <pre class="code-panel">{escape(json.dumps(latest_event, ensure_ascii=False, indent=2))}</pre>
            </article>
            <article class="insight-panel">
              <h3>{bilingual_html("آخر حدث reversible", "Latest reversible event", "span")}</h3>
              <pre class="code-panel">{escape(json.dumps(latest_reversible, ensure_ascii=False, indent=2))}</pre>
            </article>
          </div>
        </div>
      </section>
    """

    changes_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Observed vs changed", "Observed vs changed", "span")}</p>
          <h2>{bilingual_html("What Changed", "What Changed", "span")}</h2>
          {bilingual_text("القسم ده يفصل بين ما تم تحديثه فعليًا في workspace، وما تم رصده فقط بدون mutation إضافي.", "This section separates what was materially updated in the workspace from what was only observed without extra mutation.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{bilingual_html("تحديث السجل", "Registry refresh", "span")}</h3>
            <ul class="report-list">
              {render_report_list([
                  ("تمت إضافة 5 أوصاف ناقصة إلى السجل", "Added 5 missing descriptions to the registry"),
                  (f"إجمالي السجل الآن {len(skills)} entry منها {len([skill for skill in skills if not skill['is_exception']])} top-level", f"Registry now tracks {len(skills)} entries, including {len([skill for skill in skills if not skill['is_exception']])} top-level skills"),
                  ("تمت إزالة الاستثناء المكسور `arabic-output-guard` من النسخة التشغيلية لأنه بلا مصدر", "Removed the broken `arabic-output-guard` exception from the operational view because it has no source"),
              ])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("تحديث الذاكرة", "Memory refresh", "span")}</h3>
            <ul class="report-list">
              {render_report_list([
                  (f"الـ pending الحالي = {triage['pending_total']} والفرق مقابل آخر baseline محفوظ = {delta_pending:+d}", f"Current pending count = {triage['pending_total']} and delta vs the last saved baseline = {delta_pending:+d}"),
                  ("لم يتم promote أو forget أو rollback على ذاكرة المشروع في هذا pass", "No promote, forget, or rollback was applied to project memory in this pass"),
                  ("سبب عدم الترقية: لا يوجد durable candidate صالح أو خالٍ من المخاطر يستحق promotion", "Why no promotion: there is no valid low-risk durable candidate worth promoting"),
              ])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("تحديث self-learn", "Self-learn refresh", "span")}</h3>
            <ul class="report-list">
              {render_report_list([
                  (f"event_sequence وصل إلى {self_learn['health']['event_sequence']} بعد observe-only event جديد", f"event_sequence reached {self_learn['health']['event_sequence']} after a new observe-only event"),
                  ("لم يتم استخدام apply احترامًا لحدود self-only", "No apply was used to respect the self-only boundary"),
                  ("آخر verification status ما زال rolled-back من حدث أقدم ولم يتم تغيير التاريخ السابق", "The last verification status still reads rolled-back from an older event and that historical state was not rewritten"),
              ])}
            </ul>
          </article>
        </div>
      </section>
    """

    boundaries_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Quality guardrails", "Quality guardrails", "span")}</p>
          <h2>{bilingual_html("Boundaries", "Boundaries", "span")}</h2>
          {bilingual_text("هنا الحدود ليست نقصًا في القدرات، بل جزء من الصدق. هي التي تمنع التقرير من إدعاء شيء لم يحدث فعلاً.", "These boundaries are not a lack of capability. They are part of the report's honesty, preventing it from claiming work that did not actually happen.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{bilingual_html("لماذا self-learn لم يحدّث باقي المهارات؟", "Why self-learn did not update other skills", "span")}</h3>
            <ul class="report-list">
              {render_report_list([
                  ("العقد الحالي لـ self-learn محلي داخل مجلده فقط", "The current self-learn contract is local to its own skill directory"),
                  ("هذه المهمة استخدمت observe/report كطبقة evidence لا كطبقة mutation", "This task used observe/report as an evidence layer, not a mutation layer"),
                  ("تحديث السجل تم في workspace نفسه لأنه النطاق الصحيح هنا", "The registry update happened in the workspace itself because that is the correct scope here"),
              ])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("لماذا persistent-memory لم يروّج backlog تلقائيًا؟", "Why persistent-memory did not auto-promote the backlog", "span")}</h3>
            <ul class="report-list">
              {render_report_list([
                  ("سياسة الذاكرة تمنع auto-promotion من الأساس", "The memory policy forbids auto-promotion in the first place"),
                  ("المتبقي كله تقريبًا مفاتيح ephemeral مثل project.active_artifact", "What remains is effectively all ephemeral keys such as project.active_artifact"),
                  ("حتى بعد backfill، لا يوجد durable candidate صالح يستحق promotion", "Even after backfill, there is still no valid durable candidate worth promoting"),
              ])}
            </ul>
          </article>
        </div>
      </section>
    """

    evidence_section = f"""
      <section class="section-block" data-parallax>
        <div class="section-head">
          <p class="section-kicker">{bilingual_html("Evidence bundle", "Evidence bundle", "span")}</p>
          <h2>{bilingual_html("Evidence Ledger", "Evidence Ledger", "span")}</h2>
          {bilingual_text("كل ما يظهر هنا ناتج عن مخرجات محلية مباشرة، مع مراجعة رسمية إضافية لروابط OpenAI الحساسة زمنيًا.", "Everything shown here comes from direct local outputs, with an additional official review pass for time-sensitive OpenAI links.", "p", "section-copy")}
        </div>
        <div class="section-divider"></div>
        <div class="split-grid">
          <article class="insight-panel">
            <h3>{bilingual_html("الأوامر المستخدمة", "Commands used", "span")}</h3>
            <pre class="code-panel">python3 "$PMEM" inspect --cwd "$PWD" --format markdown
python3 "$PMEM" triage --cwd "$PWD" --format markdown
python3 "$PMEM" suggest --cwd "$PWD"
python3 "$PMEM" doctor
python3 "$SELF_LEARN" --intent report --json</pre>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("عيّنة من الـ backlog", "Backlog sample", "span")}</h3>
            <ul class="fact-list">
              {render_fact_list([(entry["key"], entry["value"]) for entry in backlog_sample])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("ملفات مرجعية", "Reference files", "span")}</h3>
            <ul class="fact-list">
              {render_fact_list([
                  ("omega-runtime/skills/OMEGA_SKILL_CATALOG.yaml", "catalog"),
                  ("output/reports/persistent-memory-status-report.md", "previous baseline"),
                  ("~/.codex/skills/self-learn/SKILL.md", "self-learn contract"),
                  ("~/.codex/skills/persistent-memory/SKILL.md", "memory contract"),
              ])}
            </ul>
          </article>
          <article class="insight-panel">
            <h3>{bilingual_html("روابط OpenAI الرسمية", "Official OpenAI links", "span")}</h3>
            <div class="source-list">
              {render_source_links()}
            </div>
          </article>
        </div>
      </section>
    """

    body = topbar + hero + profile_section + triage_section + self_learn_section + changes_section + boundaries_section + evidence_section
    return build_shell("Omega Memory Learning Report V2", "تقرير ذاكرة وتعلّم أوميجا V2", "memory-page", body)


def main():
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    skills = base.build_skill_index()
    snapshot = base.build_memory_snapshot()
    SKILLS_OUTPUT.write_text(build_skills_page(skills), encoding="utf-8")
    MEMORY_OUTPUT.write_text(build_memory_page(skills, snapshot), encoding="utf-8")
    print("Wrote:")
    print(SKILLS_OUTPUT)
    print(MEMORY_OUTPUT)


if __name__ == "__main__":
    main()
