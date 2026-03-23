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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
SURFACE_IDS = {"skills-review", "memory"}
NONCE_HEADER = "X-Omega-Session-Nonce"

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
    }


def metric_strip(items: list[tuple[Any, str, str, str]]) -> str:
    return "".join(v2.metric_pill(value, ar, en, tone) for value, ar, en, tone in items)


def cockpit_topbar(page_label_ar: str, page_label_en: str, meta_html: str) -> str:
    return f"""
      <header class="utility-bar">
        <div class="brand-lockup">
          <strong>OMEGA COCKPIT V1</strong>
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
  <meta name="omega:brand_profile" content="omega-cockpit-v1">
  <meta name="omega:handoff:lang" content="ar,en">
  <meta name="omega:handoff:dir" content="rtl,ltr">
  <link rel="icon" href="data:,">
  <title>{escape(title_en)} | {escape(title_ar)}</title>
  <style>
{v7.V7_CSS}
{APP_CSS}
  </style>
</head>
<body class="{escape(body_class)}">
  <div class="page-shell">
    {body_html}
    <div class="footer-note">OMEGA COCKPIT V1 / live local app / local-only truth / exported snapshots follow `omega-hud-{'{filename}'}.html`</div>
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
      <article class="surface-card">
        <div class="surface-card__header">
          <div class="stack-column">
            <h3>{escape(skill["display_name"])}</h3>
            <span class="path-label">{escape(skill["source_path"])}</span>
          </div>
          <div class="tag-row">
            {v2.code_tag(skill["skill_id"])}
            {v2.code_tag(skill["invoke"])}
            {v2.inline_tag("system" if skill["scope"] == "system" else "top-level", skill["scope"], "accent" if skill["scope"] == "top-level" else "")}
          </div>
        </div>
        <p class="muted-copy">{escape(skill["description"] or "No description.")}</p>
        <div class="tag-row">
          {v2.inline_tag("scripts" if skill["has_scripts"] else "no scripts", "scripts" if skill["has_scripts"] else "no scripts")}
          {v2.inline_tag("assets" if skill["has_assets"] else "no assets", "assets" if skill["has_assets"] else "no assets")}
          {v2.inline_tag("refs" if skill["has_references"] else "no refs", "refs" if skill["has_references"] else "no refs")}
        </div>
      </article>
    """


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
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Live skill truth", "Live skill truth", "span")}</p>
              <h1>{v2.bilingual_html('مراجعة المهارات من المصدر الحي تحت <span class="accent">~/.codex/skills</span>', 'Skill review staged directly from <span class="accent">~/.codex/skills</span>', "span")}</h1>
              {v2.bilingual_text("هذا التصدير يثبت أن الحقيقة تأتي من ملفات المهارات الحية نفسها، بينما الكتالوج مجرد طبقة مقارنة وتشخيص drift.", "This export proves that truth comes from the live skill files themselves, while the catalog stays a comparison and drift-detection overlay.", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("live truth", "live truth", "accent")}
                {v2.inline_tag("catalog overlay", "catalog overlay")}
                {v2.inline_tag("readonly surface", "readonly surface")}
              </div>
            </div>
            <article class="poster-surface hero-panel">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("source root", "source root", "accent")}
                  {v2.code_tag(str(config.skills_root))}
                </div>
                <div class="poster-surface__score">
                  <strong>{audit["summary"]["live_total"]}</strong>
                  <span>{v2.bilingual_html("مهارة live", "Live skills", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("Audit + diff snapshot", "Audit + diff snapshot", "span")}</div>
              </div>
              {kv_fact_list([
                  ("catalog_total", str(audit["summary"]["catalog_total"])),
                  ("missing_from_catalog", str(audit["summary"]["missing_from_catalog"])),
                  ("missing_on_disk", str(audit["summary"]["missing_on_disk"])),
                  ("stale_docs", str(audit["summary"]["stale_docs"])),
              ])}
            </article>
          </div>
        </div>
      </section>
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Audit summary", "Audit summary", "span")}</p>
          <h2>{v2.bilingual_html("نتيجة المقارنة مع الكتالوج", "Catalog comparison result", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="panel-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Drift summary", "Drift summary", "span")}</h3>
            {kv_fact_list([
                ("live_total", str(audit["summary"]["live_total"])),
                ("metadata_drift", str(audit["summary"]["metadata_drift"])),
                ("fresh_docs", str(audit["summary"]["fresh_docs"])),
                ("missing_docs", str(audit["summary"]["missing_docs"])),
            ])}
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Open findings", "Open findings", "span")}</h3>
            {report_list([
                escape(item["skill_key"]) for item in audit["missing_from_catalog"][:12]
            ] or ["No uncatalogued live skills detected in this pass."])}
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Stale docs", "Stale docs", "span")}</h3>
            {report_list([
                f"<code>{escape(item['skill_key'])}</code> — {escape(item['doc_path'] or '-')}" for item in audit["stale_docs"][:12]
            ] or ["No stale docs detected in this pass."])}
          </article>
        </div>
      </section>
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Live inventory", "Live inventory", "span")}</p>
          <h2>{v2.bilingual_html("كل المهارات الحية", "All live skills", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="card-grid">
          {cards}
        </div>
      </section>
    """
    return render_shell(title_en="Omega HUD Skills Review", title_ar="تصدير مراجعة المهارات", body_class="skills-page", body_html=body)


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
    history_items = "".join(
        f"<li><code>{escape(item['event_type'])}</code> — {escape(item['event_id'])} — {escape(pretty_timestamp(item['created_at']))}</li>"
        for item in history["items"][:12]
    )
    queue_cards = "".join(
        f"""
          <article class="insight-panel">
            <div class="tag-row">
              {v2.code_tag(queue['id'])}
              {v2.inline_tag(str(queue['actionable_total']), "actionable", "accent" if queue['actionable_total'] else "")}
            </div>
            <h3>{v2.bilingual_html(queue['label_ar'], queue['label_en'], "span")}</h3>
            <p class="muted-copy">{v2.bilingual_html(queue['description_ar'], queue['description_en'], "span")}</p>
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
    body = f"""
      {cockpit_topbar("تصدير الميموري", "Memory export", meta)}
      <section class="hero-stage memory-page" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{v2.bilingual_html("Tool-enabled memory surface", "Tool-enabled memory surface", "span")}</p>
              <h1>{v2.bilingual_html('سطح تشغيل الميموري بعد التحويل إلى <span class="accent">SQLite-first</span>', 'The memory control surface after the <span class="accent">SQLite-first</span> shift', "span")}</h1>
              {v2.bilingual_text("هذا التصدير snapshot لصفحة التحكم في الميموري، بما فيها queue diagnosis وcleanup preview وmutation history.", "This export is a snapshot of the memory control surface, including queue diagnosis, cleanup preview, and mutation history.", "p", "muted-copy")}
              <div class="tag-row">
                {v2.inline_tag("tool-enabled", "tool-enabled", "accent")}
                {v2.inline_tag("manual approvals", "manual approvals")}
                {v2.inline_tag("smart cleanup", "smart cleanup")}
              </div>
            </div>
            <article class="poster-surface hero-panel">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {v2.inline_tag("state db", "state db", "accent")}
                  {v2.code_tag(str(doctor["state_db"]))}
                </div>
                <div class="poster-surface__score">
                  <strong>{triage["summary"]["pending_total"]}</strong>
                  <span>{v2.bilingual_html("pending", "Pending", "span")}</span>
                </div>
                <div class="poster-surface__name">{v2.bilingual_html("Memory operator snapshot", "Memory operator snapshot", "span")}</div>
              </div>
              {kv_fact_list([
                  ("resolved_project", str(doctor["resolved_project"] or "-")),
                  ("doctor_issues", str(len(doctor["issues"]))),
                  ("event_history", str(history["total"])),
                  ("oldest_pending_at", pretty_timestamp(analytics["oldest_pending_at"])),
              ])}
            </article>
          </div>
        </div>
      </section>
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Current truth", "Current truth", "span")}</p>
          <h2>{v2.bilingual_html("Doctor + triage + analytics", "Doctor + triage + analytics", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="panel-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Doctor", "Doctor", "span")}</h3>
            {kv_fact_list([
                ("memory_root", str(doctor["memory_root"])),
                ("issues", str(len(doctor["issues"]))),
                ("project_slug", str(doctor["resolved_project"] or "-")),
            ])}
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Triage summary", "Triage summary", "span")}</h3>
            {kv_fact_list([
                ("pending_total", str(triage["summary"]["pending_total"])),
                ("promotable_total", str(triage["summary"]["promotable_total"])),
                ("ephemeral_total", str(triage["summary"]["ephemeral_total"])),
                ("conflict_count", str(triage["summary"]["conflict_count"])),
            ])}
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Age bands", "Age bands", "span")}</h3>
            {kv_fact_list([
                ("0-24h", str(analytics["age_bands"]["0-24h"])),
                ("24-72h", str(analytics["age_bands"]["24-72h"])),
                ("72h+", str(analytics["age_bands"]["72h+"])),
            ])}
          </article>
        </div>
      </section>
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("Cleanup preview", "Cleanup preview", "span")}</p>
          <h2>{v2.bilingual_html("الـ queues الذكية", "Smart cleanup queues", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="panel-grid">
          {queue_cards}
        </div>
      </section>
      <section class="section-block">
        <div class="section-head">
          <p class="section-kicker">{v2.bilingual_html("History + cost", "History + cost", "span")}</p>
          <h2>{v2.bilingual_html("التاريخ والتكلفة", "History and token cost", "span")}</h2>
        </div>
        <div class="section-divider"></div>
        <div class="panel-grid">
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Recent events", "Recent events", "span")}</h3>
            <ul class="report-list">{history_items or '<li>No events</li>'}</ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Token cost", "Token cost", "span")}</h3>
            <ul class="report-list">{token_rows or '<li>No token metrics</li>'}</ul>
          </article>
          <article class="insight-panel">
            <h3>{v2.bilingual_html("Inspect snapshot", "Inspect snapshot", "span")}</h3>
            <pre class="code-panel">{escape(json.dumps({
                "user_profile": inspect.get("user_profile", {}),
                "project_profile": inspect.get("project_profile", {}),
            }, ensure_ascii=False, indent=2))}</pre>
          </article>
        </div>
      </section>
    """
    return render_shell(title_en="Omega HUD Memory", title_ar="تصدير الميموري", body_class="memory-page", body_html=body)


def safe_export_filename(surface_id: str) -> str:
    normalized = HTML_FILENAME_RE.sub("-", surface_id.lower()).strip("-")
    return f"omega-hud-{normalized}.html"


def export_surface(config: CockpitConfig, surface_id: str) -> Path:
    if surface_id not in SURFACE_IDS:
        raise ValueError(f"Unsupported surface id: {surface_id}")
    config.output_dir.mkdir(parents=True, exist_ok=True)
    target = config.output_dir / safe_export_filename(surface_id)
    if surface_id == "skills-review":
        html_text = render_skills_export(config)
    else:
        html_text = render_memory_export(config)
    target.write_text(html_text, encoding="utf-8")
    return target
