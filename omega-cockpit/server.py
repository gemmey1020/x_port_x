#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hmac
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import unquote

import core


APP_JS_PATH = Path(__file__).resolve().parent / "app.js"
MUTATING_PATHS = {
    "/api/memory/backfill",
    "/api/memory/promote",
    "/api/memory/reject",
    "/api/memory/forget",
    "/api/memory/rollback",
    "/api/memory/cleanup/execute",
}


def json_envelope(data: object | None = None, error: object | None = None) -> dict[str, object | None]:
    return {"ok": error is None, "data": data, "error": error}


class CockpitServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], config: core.CockpitConfig):
        self.config = config.normalized()
        self.state_lock = Lock()
        self.session_state = core.default_session_payload(self.config)
        self.export_ledger: list[dict[str, object]] = []
        self.mutation_ledger: list[dict[str, object]] = []
        super().__init__(server_address, CockpitHandler)

    def snapshot_session(self) -> dict[str, object]:
        with self.state_lock:
            return dict(self.session_state)

    def writes_available(self) -> bool:
        with self.state_lock:
            return bool(self.session_state["writes_available"])

    def record_export(self, surface_id: str, target: Path, *, status: str, message: str = "") -> None:
        with self.state_lock:
            self.export_ledger.insert(
                0,
                {
                    "surface_id": surface_id,
                    "artifact_name": target.name,
                    "output_path": str(target),
                    "status": status,
                    "message": message,
                    "created_at": core.utc_now(),
                },
            )
            del self.export_ledger[32:]

    def record_mutation(self, action: str, *, status: str, message: str = "", detail: dict[str, object] | None = None) -> None:
        with self.state_lock:
            self.mutation_ledger.insert(
                0,
                {
                    "action": action,
                    "status": status,
                    "message": message,
                    "detail": detail or {},
                    "created_at": core.utc_now(),
                },
            )
            del self.mutation_ledger[64:]

    def unlock(self, passcode: str) -> tuple[bool, str]:
        with self.state_lock:
            configured = self.config.admin_passcode
            if not configured:
                return False, "Admin passcode env is not configured."
            if not hmac.compare_digest(configured, passcode):
                return False, "Invalid passcode."
            self.session_state["unlocked"] = True
            self.session_state["writes_available"] = True
            self.session_state["lock_reason"] = "unlocked"
            self.session_state["unlock_count"] = int(self.session_state["unlock_count"]) + 1
            self.session_state["last_unlock_at"] = core.utc_now()
            return True, "Admin session unlocked."

    def lock_session(self, *, reason: str = "manual-lock") -> None:
        with self.state_lock:
            self.session_state["unlocked"] = False
            self.session_state["writes_available"] = False
            self.session_state["lock_reason"] = reason if self.config.admin_passcode else "passcode-missing"
            self.session_state["last_lock_at"] = core.utc_now()

    def runtime_ledger(self) -> dict[str, object]:
        with self.state_lock:
            return {
                "exports": list(self.export_ledger),
                "mutations": list(self.mutation_ledger),
            }


class CockpitHandler(BaseHTTPRequestHandler):
    server_version = "OmegaCockpit/2.0"

    @property
    def config(self) -> core.CockpitConfig:
        return self.server.config  # type: ignore[attr-defined]

    @property
    def cockpit(self) -> CockpitServer:
        return self.server  # type: ignore[return-value]

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_text(self, text: str, *, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, payload: dict[str, object | None], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_text(json.dumps(payload, ensure_ascii=False, indent=2), content_type="application/json", status=status)

    def send_file(self, path: Path) -> None:
        content = path.read_bytes()
        mime, _ = mimetypes.guess_type(path.name)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def require_nonce(self) -> bool:
        return self.headers.get(core.NONCE_HEADER, "") == self.config.session_nonce

    def ensure_nonce(self) -> bool:
        if self.require_nonce():
            return True
        self.send_json(json_envelope(error={"message": "Missing or invalid session nonce."}), status=HTTPStatus.FORBIDDEN)
        return False

    def ensure_mutation_gate(self, action: str) -> bool:
        if self.cockpit.writes_available():
            return True
        session = self.cockpit.snapshot_session()
        message = "Admin writes are locked. Unlock the session first." if session["passcode_configured"] else "Admin passcode is not configured. Writes are disabled."
        self.cockpit.record_mutation(action, status="blocked", message=message)
        self.send_json(json_envelope(error={"message": message}), status=HTTPStatus.FORBIDDEN)
        return False

    def do_GET(self) -> None:  # noqa: N802
        try:
            if self.path in {"/", "/index.html"}:
                self.send_text(render_index(self.config, self.cockpit.snapshot_session()), content_type="text/html")
                return
            if self.path == "/assets/app.js":
                self.send_text(APP_JS_PATH.read_text(encoding="utf-8"), content_type="application/javascript")
                return
            if self.path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
                return
            if self.path == "/api/health":
                self.send_json(json_envelope(core.serialize_health(self.config)))
                return
            if self.path == "/api/session/state":
                self.send_json(json_envelope(self.cockpit.snapshot_session()))
                return
            if self.path == "/api/skills/live":
                skills = core.scan_live_skills(self.config.skills_root, self.config.catalog_path)
                self.send_json(json_envelope({"summary": {"total": len(skills)}, "skills": skills}))
                return
            if self.path == "/api/skills/audit":
                skills = core.scan_live_skills(self.config.skills_root, self.config.catalog_path)
                self.send_json(json_envelope(core.build_skill_audit(skills, self.config.catalog_path)))
                return
            if self.path.startswith("/api/skills/"):
                skill_ref = unquote(self.path.split("/api/skills/", 1)[1])
                detail = core.get_skill_detail(skill_ref, self.config.skills_root, self.config.catalog_path)
                if detail is None:
                    self.send_json(json_envelope(error={"message": f"Unknown skill: {skill_ref}"}), status=HTTPStatus.NOT_FOUND)
                    return
                self.send_json(json_envelope(detail))
                return
            if self.path == "/api/memory/doctor":
                self.send_json(json_envelope(core.doctor_payload(self.config)))
                return
            if self.path == "/api/memory/inspect":
                self.send_json(json_envelope(core.inspect_payload(self.config)))
                return
            if self.path == "/api/memory/triage":
                self.send_json(json_envelope(core.triage_payload(self.config)))
                return
            if self.path == "/api/memory/suggest":
                self.send_json(json_envelope(core.suggest_payload(self.config)))
                return
            if self.path == "/api/memory/history":
                self.send_json(json_envelope(core.load_memory_history(self.config)))
                return
            if self.path == "/api/memory/analytics":
                self.send_json(json_envelope(core.load_memory_analytics(self.config)))
                return
            if self.path == "/api/memory/token-cost":
                self.send_json(json_envelope(core.load_token_cost(self.config)))
                return
            if self.path == "/api/artifacts/index":
                self.send_json(json_envelope(core.load_artifacts_index(self.config.output_dir)))
                return
            if self.path.startswith("/api/artifacts/"):
                artifact_name = unquote(self.path.split("/api/artifacts/", 1)[1])
                detail = core.get_artifact_detail(self.config, artifact_name)
                if detail is None:
                    self.send_json(json_envelope(error={"message": f"Unknown artifact: {artifact_name}"}), status=HTTPStatus.NOT_FOUND)
                    return
                self.send_json(json_envelope(detail))
                return
            if self.path == "/api/runtime/overview":
                ledger = self.cockpit.runtime_ledger()
                overview = core.build_runtime_overview(
                    self.config,
                    self.cockpit.snapshot_session(),
                    ledger["exports"],  # type: ignore[arg-type]
                    ledger["mutations"],  # type: ignore[arg-type]
                )
                self.send_json(json_envelope(overview))
                return
            if self.path == "/api/runtime/ledger":
                self.send_json(json_envelope(self.cockpit.runtime_ledger()))
                return
            if self.path.startswith("/exports/"):
                artifact_name = unquote(self.path.split("/exports/", 1)[1])
                if Path(artifact_name).name != artifact_name:
                    self.send_json(json_envelope(error={"message": "Invalid artifact name."}), status=HTTPStatus.BAD_REQUEST)
                    return
                path = self.config.output_dir / artifact_name
                if not path.exists() or not path.is_file():
                    self.send_json(json_envelope(error={"message": f"Artifact not found: {artifact_name}"}), status=HTTPStatus.NOT_FOUND)
                    return
                self.send_file(path)
                return
            self.send_json(json_envelope(error={"message": f"Unknown route: {self.path}"}), status=HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            self.send_json(json_envelope(error={"message": str(exc)}), status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        try:
            if not self.ensure_nonce():
                return

            body = self.read_json_body()

            if self.path == "/api/session/unlock":
                passcode = str(body.get("passcode") or "")
                ok, message = self.cockpit.unlock(passcode)
                self.cockpit.record_mutation("session.unlock", status="succeeded" if ok else "failed", message=message)
                if not ok:
                    self.send_json(json_envelope(error={"message": message}), status=HTTPStatus.FORBIDDEN)
                    return
                self.send_json(json_envelope({"message": message, "session": self.cockpit.snapshot_session()}))
                return

            if self.path == "/api/session/lock":
                self.cockpit.lock_session()
                self.cockpit.record_mutation("session.lock", status="succeeded", message="Admin session locked.")
                self.send_json(json_envelope({"message": "Admin session locked.", "session": self.cockpit.snapshot_session()}))
                return

            if self.path == "/api/memory/cleanup/preview":
                self.send_json(json_envelope(core.build_cleanup_preview(self.config)))
                return

            if self.path in MUTATING_PATHS or self.path.startswith("/api/export/"):
                if not self.ensure_mutation_gate(self.path):
                    return

            if self.path == "/api/memory/backfill":
                result = core.backfill_memory(self.config)
                self.cockpit.record_mutation(self.path, status="succeeded", message="Backfill completed.")
                self.send_json(json_envelope(result))
                return
            if self.path == "/api/memory/promote":
                candidate_id = str(body.get("candidate_id") or "").strip()
                result = core.promote_candidate(self.config, candidate_id)
                self.cockpit.record_mutation(self.path, status="succeeded", message=f"Promoted {candidate_id}.", detail={"candidate_id": candidate_id})
                self.send_json(json_envelope(result))
                return
            if self.path == "/api/memory/reject":
                candidate_id = str(body.get("candidate_id") or "").strip()
                reason = str(body.get("reason") or "")
                result = core.reject_candidate(self.config, candidate_id, reason)
                self.cockpit.record_mutation(self.path, status="succeeded", message=f"Rejected {candidate_id}.", detail={"candidate_id": candidate_id})
                self.send_json(json_envelope(result))
                return
            if self.path == "/api/memory/forget":
                scope = str(body.get("scope") or "")
                key = str(body.get("key") or "")
                value = str(body.get("value")) if body.get("value") is not None else None
                project_slug = str(body.get("project_slug")) if body.get("project_slug") is not None else None
                result = core.forget_memory(self.config, scope=scope, key=key, value=value, project_slug=project_slug)
                self.cockpit.record_mutation(self.path, status="succeeded", message=f"Forgot {key}.", detail={"scope": scope, "key": key})
                self.send_json(json_envelope(result))
                return
            if self.path == "/api/memory/rollback":
                event_id = str(body.get("event_id") or "").strip()
                result = core.rollback_event(self.config, event_id)
                self.cockpit.record_mutation(self.path, status="succeeded", message=f"Rolled back {event_id}.", detail={"event_id": event_id})
                self.send_json(json_envelope(result))
                return
            if self.path == "/api/memory/cleanup/execute":
                queue_id = str(body.get("queue_id") or "").strip()
                candidate_ids = body.get("candidate_ids") or []
                if not isinstance(candidate_ids, list):
                    candidate_ids = []
                reason = str(body.get("reason") or "")
                result = core.execute_cleanup(self.config, queue_id, [str(item) for item in candidate_ids], reason)
                self.cockpit.record_mutation(self.path, status="succeeded", message=f"Executed cleanup {queue_id}.", detail={"queue_id": queue_id})
                self.send_json(json_envelope(result))
                return
            if self.path.startswith("/api/export/"):
                surface_id = unquote(self.path.split("/api/export/", 1)[1])
                ledger = self.cockpit.runtime_ledger()
                target = core.export_surface(
                    self.config,
                    surface_id,
                    session_state=self.cockpit.snapshot_session(),
                    export_ledger=ledger["exports"],  # type: ignore[arg-type]
                    mutation_ledger=ledger["mutations"],  # type: ignore[arg-type]
                )
                self.cockpit.record_export(surface_id, target, status="succeeded")
                self.cockpit.record_mutation(self.path, status="succeeded", message=f"Exported {surface_id}.", detail={"surface_id": surface_id})
                self.send_json(json_envelope({"surface_id": surface_id, "output_path": str(target)}))
                return

            self.send_json(json_envelope(error={"message": f"Unknown route: {self.path}"}), status=HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            if self.path.startswith("/api/export/"):
                surface_id = unquote(self.path.split("/api/export/", 1)[1])
                self.cockpit.record_export(surface_id, self.config.output_dir / core.safe_export_filename(surface_id), status="failed", message=str(exc))
            if self.path.startswith("/api/"):
                self.cockpit.record_mutation(self.path, status="failed", message=str(exc))
            self.send_json(json_envelope(error={"message": str(exc)}), status=HTTPStatus.INTERNAL_SERVER_ERROR)


def render_index(config: core.CockpitConfig, session_state: dict[str, object]) -> str:
    health = core.serialize_health(config)
    meta_html = core.metric_strip(
        [
            ("loopback", "محلي", "Local", "accent"),
            (config.workspace_root.name, "workspace", "Workspace", ""),
            ("live truth", "المصدر الحي", "Live truth", ""),
            ("mutations-only", "gated writes", "Gated writes", ""),
        ]
    )
    nav_html = "".join(
        [
            core.route_button("skills", "skills", "مراجعة المهارات", "Skill Review"),
            core.route_button("memory", "skills", "الميموري", "Memory"),
            core.route_button("artifacts", "skills", "الـ Artifacts", "Artifacts"),
            core.route_button("runtime", "skills", "الـ Runtime", "Runtime"),
        ]
    )
    body_html = f"""
      {core.cockpit_topbar("Omega Admin Deck", "Omega Admin Deck", meta_html, session_slot=True)}
      <section class="command-deck-layout">
        <aside class="deck-sidebar">
          <article class="sidebar-card">
            <p class="section-kicker">{core.v2.bilingual_html("Navigation", "Navigation", "span")}</p>
            <h3>{core.v2.bilingual_html("سطوح التحكم", "Control surfaces", "span")}</h3>
            <nav class="deck-nav">{nav_html}</nav>
          </article>
          <article id="sidebar-session" class="sidebar-card"></article>
          <article id="sidebar-overview" class="sidebar-card"></article>
        </aside>
        <main class="deck-main">
          <div id="app-root" class="surface-grid"></div>
        </main>
      </section>
      <div id="drawer-scrim" class="detail-drawer__scrim"></div>
      <aside id="detail-drawer" class="detail-drawer"></aside>
      <div id="modal-backdrop" class="modal-backdrop"></div>
      <div id="modal-layer" class="modal-layer"></div>
      <div id="toast-stack" class="toast-stack"></div>
    """
    bootstrap = json.dumps({"health": health, "session": session_state}, ensure_ascii=False)
    extra_js = f"""
  <script>
    window.OMEGA_BOOTSTRAP = {bootstrap};
  </script>
  <script src="/assets/app.js"></script>
"""
    return core.render_shell(
        title_en="Omega Cockpit Admin V2",
        title_ar="كوكبيت أوميجا الإدارية V2",
        body_class="cockpit-admin-v2",
        body_html=body_html,
        extra_js=extra_js,
    )


def build_server(config: core.CockpitConfig) -> CockpitServer:
    return CockpitServer((config.host, config.port), config)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Omega cockpit local server or export snapshots.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--codex-home", default=str(core.DEFAULT_CODEX_HOME))
    parser.add_argument("--workspace-root", default=str(core.WORKSPACE_ROOT))
    parser.add_argument("--catalog-path", default=str(core.DEFAULT_CATALOG_PATH))
    parser.add_argument("--output-dir", default=str(core.DEFAULT_OUTPUT_DIR))
    parser.add_argument("--export", choices=sorted(core.SURFACE_IDS | {"all"}))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = core.CockpitConfig(
        workspace_root=Path(args.workspace_root),
        codex_home=Path(args.codex_home),
        catalog_path=Path(args.catalog_path),
        output_dir=Path(args.output_dir),
        host=args.host,
        port=args.port,
    ).normalized()

    if args.export:
        surfaces = sorted(core.SURFACE_IDS) if args.export == "all" else [args.export]
        for surface_id in surfaces:
            target = core.export_surface(config, surface_id)
            print(f"Exported {surface_id} -> {target}")
        if args.export == "all":
            report = core.write_implementation_report(config)
            print(f"Exported report -> {report}")
        return 0

    httpd = build_server(config)
    print(f"Omega cockpit listening on http://{config.host}:{httpd.server_address[1]}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
