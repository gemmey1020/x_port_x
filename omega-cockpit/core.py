#!/usr/bin/env python3

from __future__ import annotations

import html
import json
import os
import re
import secrets
import sqlite3
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import quote

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
SKILL_HELPERS_DIR = ROOT / "omega-runtime" / "skills"
if str(SKILL_HELPERS_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_HELPERS_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2
import build_skill_reports_v7 as v7


REAL_CODEX_HOME = Path.home() / ".codex"
DEFAULT_CODEX_HOME = REAL_CODEX_HOME
DEFAULT_SKILLS_ROOT = DEFAULT_CODEX_HOME / "skills"
DEFAULT_MEMORY_CLI = REAL_CODEX_HOME / "skills" / "persistent-memory" / "scripts" / "memory_cli.py"
DEFAULT_CATALOG_PATH = ROOT / "omega-runtime" / "skills" / "OMEGA_SKILL_CATALOG.yaml"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "html"
WORKSPACE_ROOT = ROOT
SURFACE_IDS = {"skills-review", "memory", "artifacts", "runtime"}
NONCE_HEADER = "X-Omega-Session-Nonce"
ADMIN_PASSCODE_ENV = "OMEGA_COCKPIT_ADMIN_PASSCODE"
IMPLEMENTATION_REPORT_NAME = "omega-hud-admin-v2-implementation-report.html"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
PUBLIC_NAME_RE = re.compile(r"Its public(?:/operator)? name is `([^`]+)`\.", re.IGNORECASE)
INVOKE_RE = re.compile(r"Invoke now with `([^`]+)`\.", re.IGNORECASE)
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
HTML_FILENAME_RE = re.compile(r"[^a-z0-9-]+")


APP_CSS = """
.cockpit-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}

.nav-button,
.action-button {
  cursor: pointer;
  min-height: 42px;
  padding: 10px 14px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface-strong) 82%, transparent);
  color: var(--ink);
  font: inherit;
  transition: transform 180ms ease, border-color 200ms ease, background 200ms ease;
}

.nav-button:hover,
.action-button:hover {
  transform: translateY(-1px);
  border-color: var(--line-strong);
}

.nav-button.is-active,
.action-button.is-accent {
  background: var(--accent-soft);
  border-color: var(--line-strong);
}

.action-button.is-danger {
  border-color: rgba(233, 139, 120, 0.4);
  color: var(--danger);
}

.action-button.is-success {
  border-color: rgba(158, 212, 176, 0.4);
  color: var(--success);
}

.surface-header {
  display: grid;
  gap: 12px;
  margin-bottom: 16px;
}

.surface-header h2,
.surface-header h3,
.surface-header p {
  margin: 0;
}

.surface-grid {
  display: grid;
  gap: 18px;
}

.panel-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.card-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.surface-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 30%),
    color-mix(in srgb, var(--surface-strong) 94%, transparent);
  box-shadow: 0 20px 44px rgba(0, 0, 0, 0.18);
}

.surface-card h3,
.surface-card h4,
.surface-card p {
  margin: 0;
}

.surface-card .path-label {
  word-break: break-word;
}

.surface-card__header,
.toolbar-line,
.row-inline,
.action-row,
.form-row,
.detail-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.surface-card__header {
  justify-content: space-between;
}

.stack-column {
  display: grid;
  gap: 10px;
}

.table-list,
.code-list {
  display: grid;
  gap: 10px;
}

.table-row,
.ledger-row {
  display: grid;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
}

.table-row__meta,
.ledger-row__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 30px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
  color: var(--muted);
  font-size: 12px;
}

.status-pill--danger {
  border-color: rgba(233, 139, 120, 0.4);
  color: var(--danger);
}

.status-pill--success {
  border-color: rgba(158, 212, 176, 0.4);
  color: var(--success);
}

.status-pill--accent {
  border-color: var(--line-strong);
  background: var(--accent-soft);
}

.field-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.field {
  display: grid;
  gap: 8px;
}

.field label {
  color: var(--muted);
  font-size: 13px;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  min-height: 44px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface-strong) 82%, transparent);
  color: var(--ink);
  font: inherit;
}

.field textarea {
  min-height: 92px;
  resize: vertical;
}

.detail-drawer {
  position: fixed;
  top: 0;
  bottom: 0;
  right: 0;
  width: min(560px, 96vw);
  transform: translateX(104%);
  transition: transform 220ms ease;
  z-index: 40;
  padding: 16px;
  pointer-events: none;
}

.detail-drawer.is-open {
  transform: translateX(0);
  pointer-events: auto;
}

.detail-drawer__panel,
.modal-card {
  max-height: calc(100vh - 32px);
  overflow: auto;
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 24px;
  border: 1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 28%),
    color-mix(in srgb, var(--surface-strong) 96%, transparent);
  box-shadow: var(--shadow);
}

.detail-drawer__scrim,
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(5, 7, 11, 0.56);
  backdrop-filter: blur(8px);
  opacity: 0;
  pointer-events: none;
  transition: opacity 180ms ease;
  z-index: 35;
}

.detail-drawer__scrim.is-open,
.modal-backdrop.is-open {
  opacity: 1;
  pointer-events: auto;
}

.modal-layer {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 16px;
  pointer-events: none;
}

.modal-layer.is-open {
  pointer-events: auto;
}

.modal-card {
  width: min(560px, 96vw);
  transform: translateY(12px);
  opacity: 0;
  transition: transform 180ms ease, opacity 180ms ease;
}

.modal-layer.is-open .modal-card {
  transform: translateY(0);
  opacity: 1;
}

.toast-stack {
  position: fixed;
  left: 16px;
  bottom: 16px;
  z-index: 60;
  display: grid;
  gap: 10px;
  width: min(420px, calc(100vw - 32px));
}

.toast {
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface-strong) 92%, transparent);
  box-shadow: 0 18px 34px rgba(0, 0, 0, 0.18);
}

.toast--danger {
  border-color: rgba(233, 139, 120, 0.4);
}

.toast--success {
  border-color: rgba(158, 212, 176, 0.4);
}

.empty-state {
  padding: 16px;
  border-radius: 16px;
  border: 1px dashed var(--line);
  color: var(--muted);
}

.hero-copy .workspace-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 36px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.03);
}

.hero-panel {
  display: grid;
  gap: 12px;
}

.hero-panel pre,
.code-panel {
  margin: 0;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(3, 5, 8, 0.44);
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.snapshot-note {
  color: var(--dim);
  font-size: 12px;
}

.fact-list li > span:first-child {
  color: var(--muted);
}

.route-anchor {
  text-decoration: none;
}

@media (max-width: 860px) {
  .detail-drawer {
    width: 100vw;
    padding: 10px;
  }
}
"""


COMMAND_DECK_CSS = """
body.cockpit-admin-v2 {
  background:
    radial-gradient(circle at top right, rgba(88, 190, 255, 0.14), transparent 26%),
    radial-gradient(circle at 15% 20%, rgba(255, 184, 77, 0.08), transparent 20%),
    linear-gradient(180deg, #05080d 0%, #091019 44%, #05080c 100%);
}

.page-shell.command-deck-shell {
  max-width: none;
  padding: 18px;
  gap: 18px;
}

.cockpit-admin-v2 .utility-bar {
  position: sticky;
  top: 0;
  z-index: 25;
  backdrop-filter: blur(18px);
  background:
    linear-gradient(180deg, rgba(4, 10, 17, 0.92), rgba(4, 10, 17, 0.78)),
    rgba(4, 10, 17, 0.82);
  border: 1px solid rgba(126, 179, 216, 0.18);
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.28);
}

.command-deck-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 18px;
  min-height: calc(100vh - 150px);
}

.deck-sidebar,
.deck-main {
  min-width: 0;
}

.deck-sidebar {
  display: grid;
  gap: 14px;
  align-content: start;
}

.sidebar-card,
.route-shell,
.summary-panel,
.stream-panel,
.operator-frame {
  border-radius: 24px;
  border: 1px solid rgba(126, 179, 216, 0.16);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 30%),
    rgba(8, 13, 21, 0.88);
  box-shadow: 0 20px 38px rgba(0, 0, 0, 0.22);
}

.sidebar-card {
  display: grid;
  gap: 12px;
  padding: 16px;
}

.sidebar-card h3,
.sidebar-card p,
.sidebar-card ul,
.route-shell h2,
.route-shell p,
.summary-panel h3,
.summary-panel p,
.stream-panel h3,
.stream-panel p,
.operator-frame h3,
.operator-frame p {
  margin: 0;
}

.deck-nav {
  display: grid;
  gap: 10px;
}

.deck-nav .route-anchor {
  justify-content: space-between;
  min-height: 50px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
}

.deck-nav .route-anchor.is-active {
  border-color: rgba(127, 205, 255, 0.34);
  box-shadow: inset 0 0 0 1px rgba(127, 205, 255, 0.08);
}

.deck-main {
  display: grid;
  gap: 16px;
}

.route-shell {
  display: grid;
  gap: 16px;
  padding: 18px;
}

.route-shell__head {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: space-between;
  align-items: flex-start;
}

.route-shell__intro {
  display: grid;
  gap: 8px;
}

.route-shell__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.summary-band {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
}

.summary-panel {
  display: grid;
  gap: 10px;
  padding: 16px;
}

.summary-panel__value {
  font-size: clamp(24px, 4vw, 36px);
  font-weight: 700;
  letter-spacing: -0.03em;
}

.summary-panel__label {
  color: var(--muted);
  font-size: 13px;
}

.stream-panel,
.operator-frame {
  display: grid;
  gap: 14px;
  padding: 18px;
}

.surface-stream {
  display: grid;
  gap: 10px;
}

.stream-row {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(126, 179, 216, 0.12);
  background: rgba(255, 255, 255, 0.02);
}

.stream-row__meta,
.stream-row__actions,
.toolbar-cluster {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.stream-row__headline {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-between;
  align-items: baseline;
}

.stream-row__title {
  font-size: 17px;
  font-weight: 600;
  line-height: 1.3;
}

.stream-row__subtitle {
  color: var(--muted);
  font-size: 13px;
}

.stream-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
}

.toolbar-stack,
.field-stack {
  display: grid;
  gap: 10px;
}

.field-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.field-inline > * {
  flex: 1 1 160px;
}

.search-input {
  min-height: 44px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(126, 179, 216, 0.16);
  background: rgba(255, 255, 255, 0.03);
  color: var(--ink);
  font: inherit;
}

.sidebar-kpi {
  display: grid;
  gap: 4px;
}

.sidebar-kpi strong {
  font-size: 20px;
  line-height: 1;
}

.session-lock-slot {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
}

.lock-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 34px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(126, 179, 216, 0.18);
  background: rgba(255, 255, 255, 0.03);
  font-size: 12px;
}

.lock-chip--armed {
  border-color: rgba(158, 212, 176, 0.38);
  color: var(--success);
}

.lock-chip--locked {
  border-color: rgba(255, 184, 77, 0.34);
  color: #ffd48d;
}

.lock-chip--disabled {
  border-color: rgba(233, 139, 120, 0.32);
  color: var(--danger);
}

.action-button:disabled {
  cursor: not-allowed;
  opacity: 0.44;
  transform: none;
}

.command-note {
  color: var(--muted);
  font-size: 13px;
}

.artifact-family-tag {
  font-size: 12px;
  color: var(--muted);
}

.code-block {
  margin: 0;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(126, 179, 216, 0.12);
  background: rgba(2, 6, 10, 0.52);
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 1080px) {
  .command-deck-layout,
  .stream-grid {
    grid-template-columns: 1fr;
  }

  .deck-sidebar {
    order: 2;
  }
}

@media (max-width: 720px) {
  .page-shell.command-deck-shell {
    padding: 10px;
  }

  .route-shell,
  .summary-panel,
  .stream-panel,
  .operator-frame,
  .sidebar-card {
    border-radius: 18px;
  }
}
"""


@dataclass
class CockpitConfig:
    workspace_root: Path = WORKSPACE_ROOT
    codex_home: Path = DEFAULT_CODEX_HOME
    catalog_path: Path = DEFAULT_CATALOG_PATH
    output_dir: Path = DEFAULT_OUTPUT_DIR
    memory_cli_path: Path = DEFAULT_MEMORY_CLI
    host: str = "127.0.0.1"
    port: int = 8765
    session_nonce: str | None = None
    admin_passcode: str | None = None

    @property
    def skills_root(self) -> Path:
        return self.codex_home / "skills"

    @property
    def state_db_path(self) -> Path:
        return self.codex_home / "memory" / "state" / "memory_state.sqlite"

    def normalized(self) -> "CockpitConfig":
        return CockpitConfig(
            workspace_root=self.workspace_root.expanduser().resolve(),
            codex_home=self.codex_home.expanduser().resolve(),
            catalog_path=self.catalog_path.expanduser().resolve(),
            output_dir=self.output_dir.expanduser().resolve(),
            memory_cli_path=self.memory_cli_path.expanduser().resolve(),
            host=self.host,
            port=self.port,
            session_nonce=self.session_nonce or secrets.token_hex(16),
            admin_passcode=self.admin_passcode if self.admin_passcode is not None else os.environ.get(ADMIN_PASSCODE_ENV),
        )


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def age_hours(value: str | None) -> float | None:
    parsed = parse_iso(value)
    if parsed is None:
        return None
    delta = datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)
    return round(delta.total_seconds() / 3600, 2)


def pretty_timestamp(value: str | None) -> str:
    return base.pretty_timestamp(value) if value else "-"


def format_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def token_estimate(char_count: int) -> dict[str, int]:
    return {
        "low": (char_count + 3) // 4,
        "high": (char_count + 2) // 3,
    }


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw_frontmatter, body = match.groups()
    return yaml.safe_load(raw_frontmatter) or {}, body


def strip_code_fences(text: str) -> str:
    return FENCE_RE.sub("", text)


def first_paragraph(text: str) -> str:
    cleaned = strip_code_fences(text)
    lines = [line.strip() for line in cleaned.splitlines()]
    buffer: list[str] = []
    for line in lines:
        if not line:
            if buffer:
                break
            continue
        if line.startswith("#"):
            continue
        buffer.append(line)
    return " ".join(buffer).strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_catalog(catalog_path: Path) -> dict[str, Any]:
    payload = base.read_yaml(catalog_path)
    return payload or {"entries": []}


def catalog_source_index(catalog_path: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for entry in load_catalog(catalog_path).get("entries", []):
        source_path = Path(str(entry["source_skill_path"])).expanduser().resolve()
        index[str(source_path)] = entry
    return index


def catalog_entries(catalog_path: Path) -> list[dict[str, Any]]:
    return list(load_catalog(catalog_path).get("entries", []))


def detect_public_name(body: str, fallback: str) -> str:
    match = PUBLIC_NAME_RE.search(body)
    return match.group(1).strip() if match else fallback


def detect_invoke(body: str, skill_id: str) -> str:
    match = INVOKE_RE.search(body)
    if match:
        return match.group(1).strip()
    return f"${skill_id}"


def doc_status(skill_path: Path, doc_path: Path | None) -> tuple[str, str | None]:
    if doc_path is None:
        return "missing", None
    if not doc_path.exists():
        return "missing", None
    skill_mtime = skill_path.stat().st_mtime
    doc_mtime = doc_path.stat().st_mtime
    return ("stale", pretty_timestamp(datetime.fromtimestamp(doc_mtime, timezone.utc).isoformat().replace("+00:00", "Z"))) if doc_mtime < skill_mtime else (
        "fresh",
        pretty_timestamp(datetime.fromtimestamp(doc_mtime, timezone.utc).isoformat().replace("+00:00", "Z")),
    )


def skill_key(skill_id: str, scope: str) -> str:
    return skill_id if scope == "top-level" else f"{skill_id}@system"


def collect_skill_record(skill_path: Path, scope: str, catalog_path: Path) -> dict[str, Any]:
    text = read_text(skill_path)
    frontmatter, body = split_frontmatter(text)
    folder_name = skill_path.parent.name
    source_key = str(skill_path.expanduser().resolve())
    catalog_entry = catalog_source_index(catalog_path).get(source_key)
    fallback_name = str(frontmatter.get("name") or folder_name)
    public_name = detect_public_name(body, fallback_name)
    invoke_token = detect_invoke(body, folder_name)
    description = str(frontmatter.get("description") or first_paragraph(body) or "").strip()
    actual_doc_path = None
    if catalog_entry and catalog_entry.get("doc_path"):
        actual_doc_path = (ROOT / str(catalog_entry["doc_path"])).resolve()
    doc_state, doc_state_timestamp = doc_status(skill_path, actual_doc_path)

    drift_flags: list[str] = []
    if catalog_entry is None:
        drift_flags.append("missing-from-catalog")
    else:
        if str(catalog_entry.get("display_name") or "").strip() and str(catalog_entry["display_name"]).strip() != public_name:
            drift_flags.append("display-name-drift")
        if actual_doc_path is not None and not actual_doc_path.exists():
            drift_flags.append("missing-doc")
        elif doc_state == "stale":
            drift_flags.append("stale-doc")

    return {
        "skill_id": folder_name,
        "skill_key": skill_key(folder_name, scope),
        "scope": scope,
        "source_path": source_key,
        "relative_source_path": str(skill_path.resolve().relative_to(skill_path.parents[2])),
        "display_name": public_name,
        "invoke": invoke_token,
        "description": description,
        "has_scripts": (skill_path.parent / "scripts").exists(),
        "has_assets": (skill_path.parent / "assets").exists(),
        "has_references": (skill_path.parent / "references").exists(),
        "mtime": pretty_timestamp(datetime.fromtimestamp(skill_path.stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z")),
        "catalog_present": catalog_entry is not None,
        "catalog_category": str(catalog_entry.get("category") or "") if catalog_entry else "",
        "catalog_status": str(catalog_entry.get("status") or "") if catalog_entry else "",
        "catalog_display_name": str(catalog_entry.get("display_name") or "") if catalog_entry else "",
        "doc_path": str(actual_doc_path) if actual_doc_path else None,
        "doc_status": doc_state,
        "doc_timestamp": doc_state_timestamp,
        "drift_flags": drift_flags,
    }


def scan_live_skills(skills_root: Path, catalog_path: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if skills_root.exists():
        for item in sorted(skills_root.iterdir()):
            if item.name.startswith(".") or not item.is_dir():
                continue
            skill_path = item / "SKILL.md"
            if skill_path.exists():
                results.append(collect_skill_record(skill_path, "top-level", catalog_path))

        system_root = skills_root / ".system"
        if system_root.exists():
            for item in sorted(system_root.iterdir()):
                if not item.is_dir():
                    continue
                skill_path = item / "SKILL.md"
                if skill_path.exists():
                    results.append(collect_skill_record(skill_path, "system", catalog_path))

    return sorted(results, key=lambda item: (item["scope"], item["skill_id"]))


def build_skill_audit(live_skills: list[dict[str, Any]], catalog_path: Path) -> dict[str, Any]:
    catalog = load_catalog(catalog_path)
    entries = list(catalog.get("entries", []))
    live_sources = {item["source_path"] for item in live_skills}
    missing_from_catalog = [item for item in live_skills if not item["catalog_present"]]
    missing_on_disk = [
        {
            "skill_id": str(entry["skill_id"]),
            "source_path": str(entry["source_skill_path"]),
            "doc_path": str(entry.get("doc_path") or ""),
        }
        for entry in entries
        if not Path(str(entry["source_skill_path"])).expanduser().exists()
    ]
    metadata_drift = [item for item in live_skills if item["drift_flags"]]
    stale_docs = [item for item in live_skills if item["doc_status"] == "stale"]
    missing_docs = [item for item in live_skills if item["doc_status"] == "missing"]
    fresh_docs = [item for item in live_skills if item["doc_status"] == "fresh"]
    uncatalogued_sources = sorted(live_sources - {str(Path(str(entry["source_skill_path"])).expanduser().resolve()) for entry in entries})

    return {
        "generated_at": utc_now(),
        "summary": {
            "live_total": len(live_skills),
            "top_level_total": sum(1 for item in live_skills if item["scope"] == "top-level"),
            "system_total": sum(1 for item in live_skills if item["scope"] == "system"),
            "catalog_total": len(entries),
            "missing_from_catalog": len(missing_from_catalog),
            "missing_on_disk": len(missing_on_disk),
            "metadata_drift": len(metadata_drift),
            "stale_docs": len(stale_docs),
            "missing_docs": len(missing_docs),
            "fresh_docs": len(fresh_docs),
        },
        "missing_from_catalog": missing_from_catalog,
        "missing_on_disk": missing_on_disk,
        "metadata_drift": metadata_drift,
        "stale_docs": stale_docs,
        "missing_docs": missing_docs,
        "uncatalogued_sources": uncatalogued_sources,
    }


def get_skill_detail(skill_ref: str, skills_root: Path, catalog_path: Path) -> dict[str, Any] | None:
    for item in scan_live_skills(skills_root, catalog_path):
        if item["skill_key"] == skill_ref or item["skill_id"] == skill_ref:
            return item
    return None


def command_env(codex_home: Path | None) -> dict[str, str]:
    env = os.environ.copy()
    if codex_home:
        env["CODEX_HOME"] = str(codex_home)
    return env


def run_command(
    args: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path = ROOT,
    expect_json: bool = False,
) -> Any:
    completed = subprocess.run(
        args,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if completed.returncode != 0:
        raise RuntimeError(stderr or stdout or f"Command failed: {' '.join(args)}")
    if expect_json:
        return json.loads(stdout or "{}")
    return stdout


def run_memory(
    config: CockpitConfig,
    *command: str,
    json_output: bool = False,
    cwd: Path | None = None,
) -> Any:
    args = [sys.executable, str(config.memory_cli_path), *command]
    return run_command(args, env=command_env(config.codex_home), cwd=cwd or config.workspace_root, expect_json=json_output)


def doctor_payload(config: CockpitConfig) -> dict[str, Any]:
    return run_memory(config, "doctor", "--cwd", str(config.workspace_root), "--json", json_output=True)


def inspect_payload(config: CockpitConfig, no_pending: bool = False) -> dict[str, Any]:
    args = ["inspect", "--cwd", str(config.workspace_root), "--format", "json"]
    if no_pending:
        args.append("--no-pending")
    return run_memory(config, *args, json_output=True)


def triage_payload(config: CockpitConfig) -> dict[str, Any]:
    return run_memory(config, "triage", "--cwd", str(config.workspace_root), "--format", "json", json_output=True)


def suggest_payload(config: CockpitConfig) -> list[dict[str, Any]]:
    return run_memory(config, "suggest", "--cwd", str(config.workspace_root), "--format", "json", json_output=True)


def memory_state_db(config: CockpitConfig) -> Path:
    doctor = doctor_payload(config)
    return Path(str(doctor["state_db"]))


def sqlite_rows(state_db: Path, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    connection = sqlite3.connect(state_db)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(query, params).fetchall()
    finally:
        connection.close()
    return rows


def load_memory_history(config: CockpitConfig, limit: int = 24) -> dict[str, Any]:
    rows = sqlite_rows(
        memory_state_db(config),
        """
        SELECT event_id, event_type, candidate_id, target_path, snapshot_path, created_at, payload_json
        FROM promotion_events
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    items = []
    for row in rows:
        payload = json.loads(str(row["payload_json"])) if row["payload_json"] else {}
        items.append(
            {
                "event_id": str(row["event_id"]),
                "event_type": str(row["event_type"]),
                "candidate_id": str(row["candidate_id"]) if row["candidate_id"] else None,
                "target_path": str(row["target_path"]) if row["target_path"] else None,
                "snapshot_path": str(row["snapshot_path"]) if row["snapshot_path"] else None,
                "created_at": str(row["created_at"]),
                "payload": payload,
            }
        )
    return {"items": items, "total": len(items)}


def load_memory_analytics(config: CockpitConfig) -> dict[str, Any]:
    state_db = memory_state_db(config)
    triage = triage_payload(config)
    project_slug = triage.get("resolved_project")
    pending_scope = (project_slug,)
    key_rows = sqlite_rows(
        state_db,
        """
        SELECT normalized_key, COUNT(*) AS count
        FROM candidate_items
        WHERE status = 'pending' AND (project_slug = ? OR scope = 'global')
        GROUP BY normalized_key
        ORDER BY count DESC, normalized_key ASC
        """,
        pending_scope,
    )
    event_rows = sqlite_rows(
        state_db,
        """
        SELECT event_type, COUNT(*) AS count
        FROM promotion_events
        GROUP BY event_type
        ORDER BY count DESC, event_type ASC
        """,
    )
    pending_rows = sqlite_rows(
        state_db,
        """
        SELECT candidate_id, normalized_key, normalized_value_json, confidence, created_at
        FROM candidate_items
        WHERE status = 'pending' AND (project_slug = ? OR scope = 'global')
        ORDER BY created_at ASC
        """,
        pending_scope,
    )

    bands = {"0-24h": 0, "24-72h": 0, "72h+": 0}
    oldest = None
    newest = None
    pending_items = []
    for row in pending_rows:
        created_at = str(row["created_at"])
        created_dt = parse_iso(created_at)
        hours = age_hours(created_at) or 0
        if hours <= 24:
            bands["0-24h"] += 1
        elif hours <= 72:
            bands["24-72h"] += 1
        else:
            bands["72h+"] += 1
        if oldest is None or (created_dt and created_dt < oldest):
            oldest = created_dt
        if newest is None or (created_dt and created_dt > newest):
            newest = created_dt
        pending_items.append(
            {
                "candidate_id": str(row["candidate_id"]),
                "normalized_key": str(row["normalized_key"]),
                "normalized_value": json.loads(str(row["normalized_value_json"])),
                "confidence": float(row["confidence"]),
                "created_at": created_at,
                "age_hours": hours,
            }
        )

    return {
        "project_slug": project_slug,
        "pending_total": len(pending_items),
        "pending_by_key": [dict(row) for row in key_rows],
        "age_bands": bands,
        "oldest_pending_at": oldest.isoformat().replace("+00:00", "Z") if oldest else None,
        "newest_pending_at": newest.isoformat().replace("+00:00", "Z") if newest else None,
        "event_types": [dict(row) for row in event_rows],
        "pending_items": pending_items,
    }


def load_token_cost(config: CockpitConfig) -> dict[str, Any]:
    commands = {
        "doctor_json": [sys.executable, str(config.memory_cli_path), "doctor", "--cwd", str(config.workspace_root), "--json"],
        "inspect_json_no_pending": [
            sys.executable,
            str(config.memory_cli_path),
            "inspect",
            "--cwd",
            str(config.workspace_root),
            "--format",
            "json",
            "--no-pending",
        ],
        "triage_json": [sys.executable, str(config.memory_cli_path), "triage", "--cwd", str(config.workspace_root), "--format", "json"],
        "suggest_json": [sys.executable, str(config.memory_cli_path), "suggest", "--cwd", str(config.workspace_root), "--format", "json"],
    }
    rows = []
    env = command_env(config.codex_home)
    for name, args in commands.items():
        completed = subprocess.run(args, cwd=str(config.workspace_root), env=env, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            rows.append({"command": name, "error": completed.stderr.strip() or completed.stdout.strip()})
            continue
        chars = len(completed.stdout)
        words = len(completed.stdout.split())
        estimate = token_estimate(chars)
        rows.append(
            {
                "command": name,
                "chars": chars,
                "words": words,
                "approx_tokens_low": estimate["low"],
                "approx_tokens_high": estimate["high"],
            }
        )
    return {"generated_at": utc_now(), "commands": rows}


def cleanup_item(candidate: dict[str, Any], *, recommended_action: str, queue_id: str, executable: bool) -> dict[str, Any]:
    return {
        "candidate_id": str(candidate["candidate_id"]),
        "normalized_key": str(candidate["normalized_key"]),
        "normalized_value": format_value(candidate["normalized_value"]),
        "confidence": float(candidate["confidence"]),
        "created_at": str(candidate["created_at"]),
        "age_hours": age_hours(str(candidate["created_at"])),
        "recommended_action": recommended_action,
        "queue_id": queue_id,
        "executable": executable,
    }


def build_cleanup_preview(config: CockpitConfig) -> dict[str, Any]:
    triage = triage_payload(config)
    suggest = suggest_payload(config)
    promotable_ids = {item["candidate_id"] for item in triage.get("promotable", [])}

    ephemeral_artifacts = [
        cleanup_item(item, recommended_action="reject", queue_id="ephemeral-artifacts", executable=True)
        for item in suggest
        if item["normalized_key"] == "project.active_artifact"
    ]

    stale_pending = []
    for item in suggest:
        stale_hours = age_hours(str(item["created_at"])) or 0
        if stale_hours <= 72:
            continue
        stale_pending.append(
            cleanup_item(
                item,
                recommended_action="reject" if item["normalized_key"] == "project.active_artifact" else "review",
                queue_id="stale-pending",
                executable=item["normalized_key"] == "project.active_artifact",
            )
        )

    review_attention_map: dict[str, dict[str, Any]] = {}
    for item in suggest:
        if item["candidate_id"] in promotable_ids or item["normalized_key"] in {"project.domain", "project.reference_artifacts"}:
            review_attention_map[item["candidate_id"]] = cleanup_item(
                item,
                recommended_action="promote" if item["candidate_id"] in promotable_ids else "review",
                queue_id="review-attention",
                executable=False,
            )

    queues = [
        {
            "id": "ephemeral-artifacts",
            "label_ar": "ephemeral artifacts",
            "label_en": "ephemeral artifacts",
            "description_ar": "عناصر `project.active_artifact` منخفضة القيمة ويمكن تنظيفها بالجملة.",
            "description_en": "Low-value `project.active_artifact` items that are safe cleanup candidates.",
            "recommended_action": "reject",
            "executable": True,
            "items": ephemeral_artifacts,
        },
        {
            "id": "stale-pending",
            "label_ar": "stale pending > 72h",
            "label_en": "stale pending > 72h",
            "description_ar": "العناصر القديمة تحتاج إما رفضًا سريعًا أو مراجعة يدوية إذا كانت durable.",
            "description_en": "Older pending items should be rejected quickly or manually reviewed if durable.",
            "recommended_action": "mixed",
            "executable": True,
            "items": stale_pending,
        },
        {
            "id": "review-attention",
            "label_ar": "review attention",
            "label_en": "review attention",
            "description_ar": "العناصر التي تستحق مراجعة بشرية لأنها promotable أو تمس domain/reference state.",
            "description_en": "Items that deserve manual review because they are promotable or touch domain/reference state.",
            "recommended_action": "review",
            "executable": False,
            "items": list(review_attention_map.values()),
        },
    ]

    for queue in queues:
        queue["total"] = len(queue["items"])
        queue["actionable_total"] = sum(1 for item in queue["items"] if item["executable"])

    return {"generated_at": utc_now(), "queues": queues}


def extract_event_id(output: str) -> str | None:
    match = re.search(r"with event (\S+)", output)
    return match.group(1) if match else None


def backfill_memory(config: CockpitConfig) -> dict[str, Any]:
    return run_memory(config, "backfill", "--json", json_output=True)


def promote_candidate(config: CockpitConfig, candidate_id: str) -> dict[str, Any]:
    output = run_memory(config, "promote", "--candidate-id", candidate_id, json_output=False)
    return {"message": output, "event_id": extract_event_id(output)}


def reject_candidate(config: CockpitConfig, candidate_id: str, reason: str = "") -> dict[str, Any]:
    output = run_memory(config, "reject", "--candidate-id", candidate_id, "--reason", reason, json_output=False)
    return {"message": output, "event_id": extract_event_id(output)}


def forget_memory(
    config: CockpitConfig,
    *,
    scope: str,
    key: str,
    value: str | None = None,
    project_slug: str | None = None,
) -> dict[str, Any]:
    args = ["forget", "--scope", scope, "--key", key, "--cwd", str(config.workspace_root)]
    if value:
        args.extend(["--value", value])
    if project_slug:
        args.extend(["--project-slug", project_slug])
    output = run_memory(config, *args, json_output=False)
    return {"message": output, "event_id": extract_event_id(output)}


def rollback_event(config: CockpitConfig, event_id: str) -> dict[str, Any]:
    output = run_memory(config, "rollback", "--event-id", event_id, json_output=False)
    return {"message": output, "event_id": extract_event_id(output)}


def execute_cleanup(config: CockpitConfig, queue_id: str, candidate_ids: list[str] | None, reason: str = "") -> dict[str, Any]:
    preview = build_cleanup_preview(config)
    queue = next((item for item in preview["queues"] if item["id"] == queue_id), None)
    if queue is None:
        raise ValueError(f"Unknown cleanup queue: {queue_id}")

    eligible = {item["candidate_id"]: item for item in queue["items"] if item["executable"]}
    selected_ids = candidate_ids or list(eligible)
    ledger = []

    for candidate_id in selected_ids:
        item = eligible.get(candidate_id)
        if item is None:
            ledger.append({"candidate_id": candidate_id, "status": "skipped", "reason": "not-actionable"})
            continue
        try:
            result = reject_candidate(config, candidate_id, reason or f"omega-cockpit cleanup:{queue_id}")
            ledger.append({"candidate_id": candidate_id, "status": "succeeded", "event_id": result.get("event_id"), "message": result["message"]})
        except Exception as exc:  # noqa: BLE001
            ledger.append({"candidate_id": candidate_id, "status": "failed", "reason": str(exc)})

    return {
        "queue_id": queue_id,
        "summary": {
            "requested": len(selected_ids),
            "succeeded": sum(1 for row in ledger if row["status"] == "succeeded"),
            "failed": sum(1 for row in ledger if row["status"] == "failed"),
            "skipped": sum(1 for row in ledger if row["status"] == "skipped"),
        },
        "ledger": ledger,
    }


def serialize_health(config: CockpitConfig) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "workspace_root": str(config.workspace_root),
        "codex_home": str(config.codex_home),
        "skills_root": str(config.skills_root),
        "catalog_path": str(config.catalog_path),
        "output_dir": str(config.output_dir),
        "session_nonce": config.session_nonce,
        "allowed_surfaces": sorted(SURFACE_IDS),
        "host": config.host,
        "port": config.port,
        "ui_version": "omega-cockpit-admin-v2",
        "passcode_env": ADMIN_PASSCODE_ENV,
        "passcode_configured": bool(config.admin_passcode),
    }


def default_session_payload(config: CockpitConfig) -> dict[str, Any]:
    configured = bool(config.admin_passcode)
    return {
        "mode": "mutations-only",
        "passcode_configured": configured,
        "unlocked": False,
        "writes_available": False,
        "lock_reason": "locked" if configured else "passcode-missing",
        "unlock_count": 0,
        "last_unlock_at": None,
        "last_lock_at": None,
    }


def metric_strip(items: list[tuple[Any, str, str, str]]) -> str:
    return "".join(v2.metric_pill(value, ar, en, tone) for value, ar, en, tone in items)


def cockpit_topbar(page_label_ar: str, page_label_en: str, meta_html: str, *, session_slot: bool = False) -> str:
    session_html = '<div id="session-lock-slot" class="session-lock-slot"></div>' if session_slot else ""
    return f"""
      <header class="utility-bar">
        <div class="brand-lockup">
          <strong>OMEGA COCKPIT ADMIN V2</strong>
          <span>{v2.bilingual_html(page_label_ar, page_label_en, "span")}</span>
        </div>
        <div class="metric-strip">
          {meta_html}
        </div>
        <div class="control-cluster">
          {session_html}
          {v2.state_readout("lang-state")}
          {v2.control_button("lang-toggle", "تبديل اللغة", "Switch Lang")}
          {v2.state_readout("theme-state")}
          {v2.control_button("theme-toggle", "تبديل الثيم", "Switch Theme")}
        </div>
      </header>
    """


def render_shell(
    *,
    title_en: str,
    title_ar: str,
    body_class: str,
    body_html: str,
    extra_js: str = "",
) -> str:
    return f"""<!doctype html>
<html lang="ar" dir="rtl" data-ui-lang="ar" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="omega:brand_profile" content="omega-cockpit-admin-v2">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{escape(title_en)} | {escape(title_ar)}</title>
  <style>
{v7.V7_CSS}
{APP_CSS}
{COMMAND_DECK_CSS}
  </style>
</head>
<body class="{escape(body_class)}">
  <div class="page-shell command-deck-shell">
    {body_html}
    <div class="footer-note">OMEGA COCKPIT ADMIN V2 / local control plane / local-only truth / omega-hud-{'{filename}'}.html</div>
  </div>
  <script>
{v2.SHARED_JS}
  </script>
  {extra_js}
</body>
</html>
"""


def route_button(href: str, current: str, label_ar: str, label_en: str) -> str:
    active = " is-active" if href == current else ""
    return f'<a class="route-anchor nav-button{active}" href="#/{escape(href)}">{v2.bilingual_html(label_ar, label_en, "span")}</a>'


def kv_fact_list(items: list[tuple[str, str]]) -> str:
    return '<ul class="fact-list">' + "".join(f"<li><span>{escape(k)}</span><span>{escape(v)}</span></li>" for k, v in items) + "</ul>"


def report_list(items: list[str]) -> str:
    if not items:
        return '<div class="empty-state">No items</div>'
    return '<ul class="report-list">' + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def compact_skill_card(skill: dict[str, Any]) -> str:
    return f"""
      <article class="stream-row">
        <div class="stream-row__headline">
          <div>
            <div class="stream-row__title">{escape(skill["display_name"])}</div>
            <div class="stream-row__subtitle">{escape(skill["source_path"])}</div>
          </div>
          <div class="stream-row__meta">
            {v2.code_tag(skill["skill_id"])}
            {v2.code_tag(skill["invoke"])}
            {v2.inline_tag("system" if skill["scope"] == "system" else "top-level", skill["scope"], "accent" if skill["scope"] == "top-level" else "")}
          </div>
        </div>
        <p class="muted-copy">{escape(skill["description"] or "No description.")}</p>
      </article>
    """


def artifact_family(name: str) -> tuple[str, str, str]:
    if name == IMPLEMENTATION_REPORT_NAME:
        return "omega-admin-report", "تقرير التنفيذ", "Implementation report"
    if name == "omega-hud-html.html":
        return "omega-hud-legacy", "أرشيف HUD قديم", "Legacy HUD archive"
    if name.startswith("omega-hud-"):
        return "omega-hud", "Omega HUD", "Omega HUD"
    if name.startswith("omega-planning-"):
        return "omega-planning", "Omega Planning", "Omega Planning"
    if name.startswith("omega-memory-"):
        return "omega-memory", "Omega Memory", "Omega Memory"
    if name.startswith("omega-skills-"):
        return "omega-skills", "Omega Skills", "Omega Skills"
    return "other", "أخرى", "Other"


def artifact_record(path: Path) -> dict[str, Any]:
    family_id, family_ar, family_en = artifact_family(path.name)
    pdf_path = path.with_suffix(".pdf")
    qa_path = path.with_suffix(".qa")
    return {
        "artifact_name": path.name,
        "stem": path.stem,
        "absolute_path": str(path.resolve()),
        "relative_path": str(path),
        "public_path": f"/exports/{quote(path.name)}",
        "family_id": family_id,
        "family_label_ar": family_ar,
        "family_label_en": family_en,
        "size_bytes": path.stat().st_size,
        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
        "has_pdf_companion": pdf_path.exists(),
        "pdf_companion": pdf_path.name if pdf_path.exists() else None,
        "has_qa_companion": qa_path.exists(),
        "qa_companion": qa_path.name if qa_path.exists() else None,
        "is_legacy": path.name == "omega-hud-html.html",
        "is_report": path.name == IMPLEMENTATION_REPORT_NAME,
    }


def load_artifacts_index(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    items = [artifact_record(path) for path in sorted(output_dir.glob("*.html"), key=lambda item: item.stat().st_mtime, reverse=True)]
    family_counts = Counter(item["family_id"] for item in items)
    summary = {
        "total_html": len(items),
        "with_pdf_companion": sum(1 for item in items if item["has_pdf_companion"]),
        "with_qa_companion": sum(1 for item in items if item["has_qa_companion"]),
        "legacy_total": sum(1 for item in items if item["is_legacy"]),
        "report_total": sum(1 for item in items if item["is_report"]),
        "families": [
            {
                "family_id": family_id,
                "count": count,
            }
            for family_id, count in sorted(family_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
    }
    return {"generated_at": utc_now(), "summary": summary, "items": items}


def get_artifact_detail(config: CockpitConfig, artifact_name: str) -> dict[str, Any] | None:
    for item in load_artifacts_index(config.output_dir)["items"]:
        if item["artifact_name"] == artifact_name:
            return item
    return None


def timed_probe(callback: Any) -> tuple[Any | None, float, str | None]:
    started = perf_counter()
    try:
        result = callback()
    except Exception as exc:  # noqa: BLE001
        return None, round((perf_counter() - started) * 1000, 2), str(exc)
    return result, round((perf_counter() - started) * 1000, 2), None


def build_runtime_overview(
    config: CockpitConfig,
    session_state: dict[str, Any] | None = None,
    export_ledger: list[dict[str, Any]] | None = None,
    mutation_ledger: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    session = session_state or default_session_payload(config)
    health = serialize_health(config)
    skills, skills_ms, skills_error = timed_probe(lambda: scan_live_skills(config.skills_root, config.catalog_path))
    audit = build_skill_audit(skills or [], config.catalog_path) if skills is not None else {"summary": {}}
    doctor, doctor_ms, doctor_error = timed_probe(lambda: doctor_payload(config))
    analytics, analytics_ms, analytics_error = timed_probe(lambda: load_memory_analytics(config))
    artifacts, artifacts_ms, artifacts_error = timed_probe(lambda: load_artifacts_index(config.output_dir))

    notices = []
    for label, error in (
        ("skills", skills_error),
        ("memory_doctor", doctor_error),
        ("memory_analytics", analytics_error),
        ("artifacts", artifacts_error),
    ):
        if error:
            notices.append({"probe": label, "message": error})

    return {
        "generated_at": utc_now(),
        "session": session,
        "health": health,
        "skills": {
            "summary": audit.get("summary", {}),
            "top_skill_names": [item["display_name"] for item in (skills or [])[:6]],
        },
        "memory": {
            "doctor": doctor or {},
            "analytics": analytics or {},
            "summary": {
                "issues": len((doctor or {}).get("issues", [])) if doctor else None,
                "resolved_project": (doctor or {}).get("resolved_project"),
                "pending_total": (analytics or {}).get("pending_total"),
                "older_than_72h": ((analytics or {}).get("age_bands") or {}).get("72h+"),
            },
        },
        "artifacts": artifacts or {"summary": {"total_html": 0}, "items": []},
        "runtime": {
            "implementation_report_present": (config.output_dir / IMPLEMENTATION_REPORT_NAME).exists(),
            "recent_exports_total": len(export_ledger or []),
            "recent_mutations_total": len(mutation_ledger or []),
            "passcode_env": ADMIN_PASSCODE_ENV,
        },
        "latencies_ms": {
            "skills_scan": skills_ms,
            "memory_doctor": doctor_ms,
            "memory_analytics": analytics_ms,
            "artifacts_index": artifacts_ms,
        },
        "notices": notices,
    }


def render_skills_export(config: CockpitConfig) -> str:
    skills = scan_live_skills(config.skills_root, config.catalog_path)
    audit = build_skill_audit(skills, config.catalog_path)
    meta = metric_strip(
        [
            (audit["summary"]["live_total"], "مهارات live", "Live skills", ""),
            (audit["summary"]["missing_from_catalog"], "خارج الكتالوج", "Missing in catalog", "accent"),
            (audit["summary"]["metadata_drift"], "drift", "Drift", ""),
            (pretty_timestamp(utc_now()), "تم التوليد", "Generated", ""),
        ]
    )
    cards = "".join(compact_skill_card(skill) for skill in skills)
    body = f"""
      {cockpit_topbar("تصدير مراجعة المهارات", "Skills review export", meta)}
      <section class="route-shell">
        <div class="route-shell__head">
          <div class="route-shell__intro">
            <p class="section-kicker">{v2.bilingual_html("Readonly live source", "Readonly live source", "span")}</p>
            <h2>{v2.bilingual_html("المهارات الحية من المصدر الفعلي", "Live skills from the actual source", "span")}</h2>
            <p class="muted-copy">{v2.bilingual_html("الحقيقة هنا تأتي من `~/.codex/skills` مباشرة، والكتالوج يظل طبقة مقارنة فقط.", "Truth here comes directly from `~/.codex/skills`, while the catalog stays comparison-only.", "span")}</p>
          </div>
        </div>
        <div class="summary-band">
          <article class="summary-panel"><div class="summary-panel__value">{audit["summary"]["live_total"]}</div><div class="summary-panel__label">{v2.bilingual_html("إجمالي live", "Live total", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{audit["summary"]["missing_from_catalog"]}</div><div class="summary-panel__label">{v2.bilingual_html("خارج الكتالوج", "Missing in catalog", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{audit["summary"]["metadata_drift"]}</div><div class="summary-panel__label">{v2.bilingual_html("drift metadata", "Metadata drift", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{audit["summary"]["stale_docs"]}</div><div class="summary-panel__label">{v2.bilingual_html("docs stale", "Stale docs", "span")}</div></article>
        </div>
        <div class="stream-grid">
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Catalog findings", "Catalog findings", "span")}</h3>
            {report_list([escape(item["skill_key"]) for item in audit["missing_from_catalog"][:10]] or ["No uncatalogued live skills detected."])}
          </article>
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Stale docs", "Stale docs", "span")}</h3>
            {report_list([f"<code>{escape(item['skill_key'])}</code> — {escape(item['doc_path'] or '-')}" for item in audit["stale_docs"][:10]] or ["No stale docs detected."])}
          </article>
        </div>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("Live inventory", "Live inventory", "span")}</h3>
          <div class="surface-stream">{cards}</div>
        </article>
      </section>
    """
    return render_shell(title_en="Omega HUD Skills Review", title_ar="تصدير مراجعة المهارات", body_class="cockpit-admin-v2 skills-page", body_html=body)


def render_memory_export(config: CockpitConfig) -> str:
    doctor = doctor_payload(config)
    inspect = inspect_payload(config, no_pending=False)
    triage = triage_payload(config)
    analytics = load_memory_analytics(config)
    history = load_memory_history(config, limit=16)
    token_cost = load_token_cost(config)
    cleanup = build_cleanup_preview(config)
    meta = metric_strip(
        [
            (triage["summary"]["pending_total"], "pending", "Pending", "accent"),
            (triage["summary"]["promotable_total"], "promotable", "Promotable", ""),
            (analytics["age_bands"]["72h+"], "أقدم من 72h", "Older than 72h", ""),
            (pretty_timestamp(utc_now()), "تم التوليد", "Generated", ""),
        ]
    )
    queue_cards = "".join(
        f"""
          <article class="stream-row">
            <div class="stream-row__headline">
              <div>
                <div class="stream-row__title">{v2.bilingual_html(queue['label_ar'], queue['label_en'], "span")}</div>
                <div class="stream-row__subtitle">{v2.bilingual_html(queue['description_ar'], queue['description_en'], "span")}</div>
              </div>
              <div class="stream-row__meta">
                {v2.code_tag(queue['id'])}
                {v2.inline_tag(str(queue['actionable_total']), "actionable", "accent" if queue['actionable_total'] else "")}
              </div>
            </div>
            {kv_fact_list([
                ("total", str(queue["total"])),
                ("actionable", str(queue["actionable_total"])),
                ("recommended_action", str(queue["recommended_action"])),
            ])}
          </article>
        """
        for queue in cleanup["queues"]
    )
    token_rows = "".join(
        f"<li><code>{escape(item['command'])}</code> — {escape(str(item.get('approx_tokens_low', '-')))}..{escape(str(item.get('approx_tokens_high', '-')))} tokens</li>"
        for item in token_cost["commands"]
        if "error" not in item
    )
    history_rows = "".join(
        f"<li><code>{escape(item['event_type'])}</code> — {escape(item['event_id'])} — {escape(pretty_timestamp(item['created_at']))}</li>"
        for item in history["items"][:12]
    )
    body = f"""
      {cockpit_topbar("تصدير الميموري", "Memory export", meta)}
      <section class="route-shell">
        <div class="route-shell__head">
          <div class="route-shell__intro">
            <p class="section-kicker">{v2.bilingual_html("Tool-enabled surface", "Tool-enabled surface", "span")}</p>
            <h2>{v2.bilingual_html("سطح الميموري داخل الكوكبيت الإدارية", "The memory surface inside the admin cockpit", "span")}</h2>
            <p class="muted-copy">{v2.bilingual_html("هذا snapshot تشغيلي للميموري مع triage, analytics, cleanup, history, والتكلفة التقريبية.", "This is an operational memory snapshot with triage, analytics, cleanup, history, and token cost.", "span")}</p>
          </div>
        </div>
        <div class="summary-band">
          <article class="summary-panel"><div class="summary-panel__value">{triage["summary"]["pending_total"]}</div><div class="summary-panel__label">{v2.bilingual_html("pending", "Pending", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{triage["summary"]["promotable_total"]}</div><div class="summary-panel__label">{v2.bilingual_html("promotable", "Promotable", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{analytics["age_bands"]["72h+"]}</div><div class="summary-panel__label">{v2.bilingual_html("older than 72h", "Older than 72h", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{len(history["items"])}</div><div class="summary-panel__label">{v2.bilingual_html("recent events", "Recent events", "span")}</div></article>
        </div>
        <div class="stream-grid">
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Doctor + analytics", "Doctor + analytics", "span")}</h3>
            {kv_fact_list([
                ("memory_root", str(doctor["memory_root"])),
                ("resolved_project", str(doctor["resolved_project"] or "-")),
                ("issues", str(len(doctor["issues"]))),
                ("pending_total", str(analytics["pending_total"])),
            ])}
          </article>
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Token cost", "Token cost", "span")}</h3>
            <ul class="report-list">{token_rows or '<li>No token metrics</li>'}</ul>
          </article>
        </div>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("Smart cleanup queues", "Smart cleanup queues", "span")}</h3>
          <div class="surface-stream">{queue_cards}</div>
        </article>
        <div class="stream-grid">
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Recent events", "Recent events", "span")}</h3>
            <ul class="report-list">{history_rows or '<li>No events</li>'}</ul>
          </article>
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Inspect snapshot", "Inspect snapshot", "span")}</h3>
            <pre class="code-block">{escape(json.dumps({
                "user_profile": inspect.get("user_profile", {}),
                "project_profile": inspect.get("project_profile", {}),
            }, ensure_ascii=False, indent=2))}</pre>
          </article>
        </div>
      </section>
    """
    return render_shell(title_en="Omega HUD Memory", title_ar="تصدير الميموري", body_class="cockpit-admin-v2 memory-page", body_html=body)


def render_artifacts_export(config: CockpitConfig) -> str:
    artifacts = load_artifacts_index(config.output_dir)
    rows = "".join(
        f"""
          <article class="stream-row">
            <div class="stream-row__headline">
              <div>
                <div class="stream-row__title">{escape(item["artifact_name"])}</div>
                <div class="stream-row__subtitle">{escape(item["absolute_path"])}</div>
              </div>
              <div class="stream-row__meta">
                {v2.inline_tag(item["family_label_ar"], item["family_label_en"], "accent" if item["family_id"] == "omega-hud" else "")}
                {v2.inline_tag("pdf" if item["has_pdf_companion"] else "no pdf", "pdf" if item["has_pdf_companion"] else "no pdf")}
                {v2.inline_tag("qa" if item["has_qa_companion"] else "no qa", "qa" if item["has_qa_companion"] else "no qa")}
              </div>
            </div>
            {kv_fact_list([
                ("modified_at", pretty_timestamp(item["modified_at"])),
                ("size_bytes", str(item["size_bytes"])),
                ("public_path", item["public_path"]),
            ])}
          </article>
        """
        for item in artifacts["items"][:20]
    )
    meta = metric_strip(
        [
            (artifacts["summary"]["total_html"], "ملفات HTML", "HTML files", "accent"),
            (artifacts["summary"]["with_pdf_companion"], "with pdf", "With PDF", ""),
            (artifacts["summary"]["with_qa_companion"], "with qa", "With QA", ""),
            (pretty_timestamp(utc_now()), "تم التوليد", "Generated", ""),
        ]
    )
    body = f"""
      {cockpit_topbar("تصدير الـ Artifacts", "Artifacts export", meta)}
      <section class="route-shell">
        <div class="route-shell__head">
          <div class="route-shell__intro">
            <p class="section-kicker">{v2.bilingual_html("Live output inventory", "Live output inventory", "span")}</p>
            <h2>{v2.bilingual_html("أرشيف الـ HTML المحلي داخل الكوكبيت", "The local HTML archive inside the cockpit", "span")}</h2>
            <p class="muted-copy">{v2.bilingual_html("هذا التصدير يفهرس كل ملفات `output/html` مع companions والـ family grouping.", "This export indexes all `output/html` files with companion detection and family grouping.", "span")}</p>
          </div>
        </div>
        <div class="summary-band">
          <article class="summary-panel"><div class="summary-panel__value">{artifacts["summary"]["total_html"]}</div><div class="summary-panel__label">{v2.bilingual_html("html files", "HTML files", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{artifacts["summary"]["with_pdf_companion"]}</div><div class="summary-panel__label">{v2.bilingual_html("with pdf", "With PDF", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{artifacts["summary"]["with_qa_companion"]}</div><div class="summary-panel__label">{v2.bilingual_html("with qa", "With QA", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{artifacts["summary"]["report_total"]}</div><div class="summary-panel__label">{v2.bilingual_html("reports", "Reports", "span")}</div></article>
        </div>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("Latest inventory", "Latest inventory", "span")}</h3>
          <div class="surface-stream">{rows}</div>
        </article>
      </section>
    """
    return render_shell(title_en="Omega HUD Artifacts", title_ar="تصدير الـ Artifacts", body_class="cockpit-admin-v2 artifacts-page", body_html=body)


def render_runtime_export(
    config: CockpitConfig,
    session_state: dict[str, Any] | None = None,
    export_ledger: list[dict[str, Any]] | None = None,
    mutation_ledger: list[dict[str, Any]] | None = None,
) -> str:
    overview = build_runtime_overview(config, session_state, export_ledger, mutation_ledger)
    meta = metric_strip(
        [
            ("loopback", "محلي", "Local", "accent"),
            ("mutations-only", "gating", "Gating", ""),
            (overview["runtime"]["recent_exports_total"], "exports", "Exports", ""),
            (pretty_timestamp(utc_now()), "تم التوليد", "Generated", ""),
        ]
    )
    body = f"""
      {cockpit_topbar("تصدير الـ Runtime", "Runtime export", meta)}
      <section class="route-shell">
        <div class="route-shell__head">
          <div class="route-shell__intro">
            <p class="section-kicker">{v2.bilingual_html("Operator runtime", "Operator runtime", "span")}</p>
            <h2>{v2.bilingual_html("صورة تشغيلية للكوكبيت الإدارية", "An operational picture of the admin cockpit", "span")}</h2>
            <p class="muted-copy">{v2.bilingual_html("هذا snapshot يثبت health, session gate, latencies, live skills, memory, وartifact inventory.", "This snapshot proves health, session gate, latencies, live skills, memory, and artifact inventory.", "span")}</p>
          </div>
        </div>
        <div class="summary-band">
          <article class="summary-panel"><div class="summary-panel__value">{'yes' if overview['session']['passcode_configured'] else 'no'}</div><div class="summary-panel__label">{v2.bilingual_html("passcode configured", "Passcode configured", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{'armed' if overview['session']['writes_available'] else 'locked'}</div><div class="summary-panel__label">{v2.bilingual_html("write state", "Write state", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{overview['memory']['summary'].get('pending_total') or 0}</div><div class="summary-panel__label">{v2.bilingual_html("pending memory", "Pending memory", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{overview['artifacts']['summary'].get('total_html') or 0}</div><div class="summary-panel__label">{v2.bilingual_html("html artifacts", "HTML artifacts", "span")}</div></article>
        </div>
        <div class="stream-grid">
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Health + session", "Health + session", "span")}</h3>
            {kv_fact_list([
                ("workspace_root", overview["health"]["workspace_root"]),
                ("host", overview["health"]["host"]),
                ("port", str(overview["health"]["port"])),
                ("lock_reason", str(overview["session"]["lock_reason"])),
            ])}
          </article>
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Latency snapshot", "Latency snapshot", "span")}</h3>
            {kv_fact_list([
                ("skills_scan", f"{overview['latencies_ms']['skills_scan']} ms"),
                ("memory_doctor", f"{overview['latencies_ms']['memory_doctor']} ms"),
                ("memory_analytics", f"{overview['latencies_ms']['memory_analytics']} ms"),
                ("artifacts_index", f"{overview['latencies_ms']['artifacts_index']} ms"),
            ])}
          </article>
        </div>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("Runtime notices", "Runtime notices", "span")}</h3>
          {report_list([f"<code>{escape(item['probe'])}</code> — {escape(item['message'])}" for item in overview["notices"]] or ["No runtime notices in this export."])}
        </article>
      </section>
    """
    return render_shell(title_en="Omega HUD Runtime", title_ar="تصدير الـ Runtime", body_class="cockpit-admin-v2 runtime-page", body_html=body)


def default_proof_ledger() -> dict[str, list[str]]:
    return {
        "ran": ["Implementation artifact generated from the current local cockpit state."],
        "manual": ["No explicit post-implementation proof supplied in this generation context."],
        "not_run": [],
        "blocked": [],
    }


def render_implementation_report(
    config: CockpitConfig,
    *,
    proof_ledger: dict[str, list[str]] | None = None,
    runtime_overview: dict[str, Any] | None = None,
) -> str:
    proof = proof_ledger or default_proof_ledger()
    overview = runtime_overview or build_runtime_overview(config, default_session_payload(config), [], [])
    artifacts = load_artifacts_index(config.output_dir)
    meta = metric_strip(
        [
            ("V2", "الإصدار", "Version", "accent"),
            (len(SURFACE_IDS), "سطوح حيّة", "Live surfaces", ""),
            (artifacts["summary"]["total_html"], "artifacts", "Artifacts", ""),
            (pretty_timestamp(utc_now()), "تم التوليد", "Generated", ""),
        ]
    )
    body = f"""
      {cockpit_topbar("تقرير تنفيذ Omega HUD", "Omega HUD implementation report", meta)}
      <section class="route-shell">
        <div class="route-shell__head">
          <div class="route-shell__intro">
            <p class="section-kicker">{v2.bilingual_html("Implementation dossier", "Implementation dossier", "span")}</p>
            <h2>{v2.bilingual_html("ماذا حدث أثناء بناء Omega Cockpit Admin V2", "What happened while building Omega Cockpit Admin V2", "span")}</h2>
            <p class="muted-copy">{v2.bilingual_html("هذا الملف يوثّق ما بُني، ما تغيّر من V1، ما الذي تم الحفاظ عليه، وما الذي تم التحقق منه بعد التنفيذ.", "This file documents what was built, what changed from V1, what was protected, and what was verified after implementation.", "span")}</p>
          </div>
        </div>
        <div class="summary-band">
          <article class="summary-panel"><div class="summary-panel__value">4</div><div class="summary-panel__label">{v2.bilingual_html("surfaces", "Surfaces", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{'local'}</div><div class="summary-panel__label">{v2.bilingual_html("deployment", "Deployment", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{'mutations-only'}</div><div class="summary-panel__label">{v2.bilingual_html("gate mode", "Gate mode", "span")}</div></article>
          <article class="summary-panel"><div class="summary-panel__value">{artifacts["summary"]["total_html"]}</div><div class="summary-panel__label">{v2.bilingual_html("html artifacts", "HTML artifacts", "span")}</div></article>
        </div>
        <div class="stream-grid">
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Before / after", "Before / after", "span")}</h3>
            {report_list([
                "V1 had two live routes: <code>skills</code> and <code>memory</code>; V2 expands to <code>skills</code>, <code>memory</code>, <code>artifacts</code>, and <code>runtime</code>.",
                "V1 used a simpler surface shell; V2 introduces a command-deck layout with left rail, top command strip, shared drawer, and operator workspace.",
                "V1 relied on nonce only; V2 adds an in-memory admin passcode gate for mutating actions only.",
            ])}
          </article>
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Locked decisions", "Locked decisions", "span")}</h3>
            {report_list([
                "Local-first loopback runtime stays the deployment model.",
                "Live skill truth remains <code>~/.codex/skills</code>; the catalog remains comparison-only.",
                "Dangerous writes stay gated and <code>omega-hud-html.html</code> remains a legacy artifact.",
            ])}
          </article>
        </div>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("What was built", "What was built", "span")}</h3>
          {report_list([
              "A command-deck shell with sidebar navigation, lock slot, route workspace, and shared evidence drawer.",
              "A mutation gate based on <code>OMEGA_COCKPIT_ADMIN_PASSCODE</code> with unlock/lock session semantics held only in memory.",
              "Two new read-heavy surfaces: <code>Artifacts Hub</code> and <code>Runtime</code>.",
              "Extended exports for <code>omega-hud-artifacts.html</code> and <code>omega-hud-runtime.html</code>.",
              "An implementation dossier artifact under the Omega HUD HTML identity.",
          ])}
        </article>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("Public interface changes", "Public interface changes", "span")}</h3>
          {report_list([
              "<code>GET /api/session/state</code>",
              "<code>POST /api/session/unlock</code> and <code>POST /api/session/lock</code>",
              "<code>GET /api/artifacts/index</code> and <code>GET /api/artifacts/{artifact_name}</code>",
              "<code>GET /api/runtime/overview</code> and <code>GET /api/runtime/ledger</code>",
              "<code>GET /exports/{artifact_name}</code> for local artifact viewing",
          ])}
        </article>
        <div class="stream-grid">
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Artifact inventory", "Artifact inventory", "span")}</h3>
            {kv_fact_list([
                ("total_html", str(artifacts["summary"]["total_html"])),
                ("with_pdf_companion", str(artifacts["summary"]["with_pdf_companion"])),
                ("with_qa_companion", str(artifacts["summary"]["with_qa_companion"])),
                ("implementation_report_present", "yes" if (config.output_dir / IMPLEMENTATION_REPORT_NAME).exists() else "no"),
            ])}
          </article>
          <article class="stream-panel">
            <h3>{v2.bilingual_html("Runtime snapshot", "Runtime snapshot", "span")}</h3>
            {kv_fact_list([
                ("passcode_configured", str(overview["session"]["passcode_configured"])),
                ("writes_available", str(overview["session"]["writes_available"])),
                ("pending_memory", str(overview["memory"]["summary"].get("pending_total"))),
                ("recent_exports_total", str(overview["runtime"]["recent_exports_total"])),
            ])}
          </article>
        </div>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("Proof ledger", "Proof ledger", "span")}</h3>
          <div class="stream-grid">
            <div>{report_list(proof.get("ran", []))}</div>
            <div>{report_list(proof.get("manual", []))}</div>
          </div>
          <div class="stream-grid">
            <div>{report_list(proof.get("not_run", []))}</div>
            <div>{report_list(proof.get("blocked", []))}</div>
          </div>
        </article>
        <article class="stream-panel">
          <h3>{v2.bilingual_html("Deferred in this phase", "Deferred in this phase", "span")}</h3>
          {report_list([
              "No multi-user roles or remote hosting were added in V2.",
              "Artifacts Hub remains inventory/open/inspect only; no bulk delete/regenerate flows were added.",
              "Runtime remains read-only and diagnostic rather than becoming a new orchestration surface.",
          ])}
        </article>
      </section>
    """
    return render_shell(
        title_en="Omega HUD Admin V2 Implementation Report",
        title_ar="تقرير تنفيذ Omega Cockpit Admin V2",
        body_class="cockpit-admin-v2 implementation-report-page",
        body_html=body,
    )


def safe_export_filename(surface_id: str) -> str:
    normalized = HTML_FILENAME_RE.sub("-", surface_id.lower()).strip("-")
    return f"omega-hud-{normalized}.html"


def export_surface(
    config: CockpitConfig,
    surface_id: str,
    *,
    session_state: dict[str, Any] | None = None,
    export_ledger: list[dict[str, Any]] | None = None,
    mutation_ledger: list[dict[str, Any]] | None = None,
) -> Path:
    if surface_id not in SURFACE_IDS:
        raise ValueError(f"Unsupported surface id: {surface_id}")
    config.output_dir.mkdir(parents=True, exist_ok=True)
    target = config.output_dir / safe_export_filename(surface_id)
    if surface_id == "skills-review":
        html_text = render_skills_export(config)
    elif surface_id == "memory":
        html_text = render_memory_export(config)
    elif surface_id == "artifacts":
        html_text = render_artifacts_export(config)
    else:
        html_text = render_runtime_export(config, session_state, export_ledger, mutation_ledger)
    target.write_text(html_text, encoding="utf-8")
    return target


def write_implementation_report(
    config: CockpitConfig,
    *,
    proof_ledger: dict[str, list[str]] | None = None,
    runtime_overview: dict[str, Any] | None = None,
) -> Path:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    target = config.output_dir / IMPLEMENTATION_REPORT_NAME
    html_text = render_implementation_report(config, proof_ledger=proof_ledger, runtime_overview=runtime_overview)
    target.write_text(html_text, encoding="utf-8")
    return target
