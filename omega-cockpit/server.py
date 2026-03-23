#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

import core


APP_JS_PATH = Path(__file__).resolve().parent / "app.js"


def json_envelope(data: object | None = None, error: object | None = None) -> dict[str, object | None]:
    return {"ok": error is None, "data": data, "error": error}


class CockpitServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], config: core.CockpitConfig):
        self.config = config.normalized()
        super().__init__(server_address, CockpitHandler)


class CockpitHandler(BaseHTTPRequestHandler):
    server_version = "OmegaCockpit/1.0"

    @property
    def config(self) -> core.CockpitConfig:
        return self.server.config  # type: ignore[attr-defined]

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

    def read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def require_nonce(self) -> bool:
        return self.headers.get(core.NONCE_HEADER, "") == self.config.session_nonce

    def do_GET(self) -> None:  # noqa: N802
        try:
            if self.path in {"/", "/index.html"}:
                self.send_text(render_index(self.config), content_type="text/html")
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

            self.send_json(json_envelope(error={"message": f"Unknown route: {self.path}"}), status=HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            self.send_json(json_envelope(error={"message": str(exc)}), status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        try:
            if not self.require_nonce():
                self.send_json(json_envelope(error={"message": "Missing or invalid session nonce."}), status=HTTPStatus.FORBIDDEN)
                return

            body = self.read_json_body()

            if self.path == "/api/memory/backfill":
                self.send_json(json_envelope(core.backfill_memory(self.config)))
                return
            if self.path == "/api/memory/promote":
                candidate_id = str(body.get("candidate_id") or "").strip()
                self.send_json(json_envelope(core.promote_candidate(self.config, candidate_id)))
                return
            if self.path == "/api/memory/reject":
                candidate_id = str(body.get("candidate_id") or "").strip()
                reason = str(body.get("reason") or "")
                self.send_json(json_envelope(core.reject_candidate(self.config, candidate_id, reason)))
                return
            if self.path == "/api/memory/forget":
                scope = str(body.get("scope") or "")
                key = str(body.get("key") or "")
                value = str(body.get("value")) if body.get("value") is not None else None
                project_slug = str(body.get("project_slug")) if body.get("project_slug") is not None else None
                self.send_json(json_envelope(core.forget_memory(self.config, scope=scope, key=key, value=value, project_slug=project_slug)))
                return
            if self.path == "/api/memory/rollback":
                event_id = str(body.get("event_id") or "").strip()
                self.send_json(json_envelope(core.rollback_event(self.config, event_id)))
                return
            if self.path == "/api/memory/cleanup/preview":
                self.send_json(json_envelope(core.build_cleanup_preview(self.config)))
                return
            if self.path == "/api/memory/cleanup/execute":
                queue_id = str(body.get("queue_id") or "").strip()
                candidate_ids = body.get("candidate_ids") or []
                if not isinstance(candidate_ids, list):
                    candidate_ids = []
                reason = str(body.get("reason") or "")
                self.send_json(json_envelope(core.execute_cleanup(self.config, queue_id, [str(item) for item in candidate_ids], reason)))
                return
            if self.path.startswith("/api/export/"):
                surface_id = unquote(self.path.split("/api/export/", 1)[1])
                target = core.export_surface(self.config, surface_id)
                self.send_json(json_envelope({"surface_id": surface_id, "output_path": str(target)}))
                return

            self.send_json(json_envelope(error={"message": f"Unknown route: {self.path}"}), status=HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001
            self.send_json(json_envelope(error={"message": str(exc)}), status=HTTPStatus.INTERNAL_SERVER_ERROR)


def render_index(config: core.CockpitConfig) -> str:
    health = core.serialize_health(config)
    meta_html = core.metric_strip(
        [
            ("127.0.0.1", "loopback", "Loopback", "accent"),
            (config.workspace_root.name, "workspace", "Workspace", ""),
            ("live skills", "مصدر الحقيقة", "Source of truth", ""),
            ("memory tools", "السطح التنفيذي", "Tool-enabled surface", ""),
        ]
    )
    nav_html = "".join(
        [
            core.route_button("skills", "skills", "مراجعة المهارات", "Skill Review"),
            core.route_button("memory", "skills", "الميموري", "Memory"),
        ]
    )
    body_html = f"""
      {core.cockpit_topbar("Omega Cockpit", "Omega Cockpit", meta_html)}
      <section class="hero-stage" data-parallax>
        <div class="hero-inner">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">{core.v2.bilingual_html("Live local cockpit", "Live local cockpit", "span")}</p>
              <h1>{core.v2.bilingual_html('الكوكبيت الحية لـ <span class="accent">Omega</span> داخل الـ workspace', 'The live <span class="accent">Omega</span> cockpit inside the workspace', "span")}</h1>
              {core.v2.bilingual_text("الصفحة دي هي runtime حقيقية، وليست report فقط. الحقيقة تأتي من `~/.codex/skills` ومن `memory_cli.py` وSQLite المحلي.", "This page is a real runtime, not just a report. Truth comes from `~/.codex/skills`, `memory_cli.py`, and local SQLite.", "p", "muted-copy")}
              <div class="tag-row">
                {core.v2.inline_tag("live skill truth", "live skill truth", "accent")}
                {core.v2.inline_tag("memory tools gated", "memory tools gated")}
                {core.v2.inline_tag("exports use omega-hud-{filename}.html", "exports use omega-hud-{filename}.html")}
              </div>
              <div class="workspace-chip">
                <strong>{core.escape(config.workspace_root.name)}</strong>
                <span>{core.escape(str(config.workspace_root))}</span>
              </div>
            </div>
            <article class="poster-surface hero-panel">
              <div class="poster-surface__headline">
                <div class="tag-row">
                  {core.v2.inline_tag("runtime", "runtime", "accent")}
                  {core.v2.code_tag("skills")}
                  {core.v2.code_tag("memory")}
                </div>
                <div class="poster-surface__score">
                  <strong>V1</strong>
                  <span>{core.v2.bilingual_html("الميلستون الحالية", "Current milestone", "span")}</span>
                </div>
                <div class="poster-surface__name">{core.v2.bilingual_html("Skill Review + Memory Control", "Skill Review + Memory Control", "span")}</div>
              </div>
              {core.kv_fact_list([
                  ("workspace_root", str(config.workspace_root)),
                  ("skills_root", str(config.skills_root)),
                  ("catalog_overlay", str(config.catalog_path)),
                  ("output_dir", str(config.output_dir)),
              ])}
            </article>
          </div>
        </div>
      </section>
      <section class="section-block">
        <div class="surface-header">
          <p class="section-kicker">{core.v2.bilingual_html("Navigation", "Navigation", "span")}</p>
          <h2>{core.v2.bilingual_html("السطوح الحية", "Live surfaces", "span")}</h2>
          <div class="cockpit-nav">{nav_html}</div>
        </div>
        <div class="section-divider"></div>
        <div id="app-root" class="surface-grid"></div>
      </section>
      <div id="drawer-scrim" class="detail-drawer__scrim"></div>
      <aside id="detail-drawer" class="detail-drawer"></aside>
      <div id="modal-backdrop" class="modal-backdrop"></div>
      <div id="modal-layer" class="modal-layer"></div>
      <div id="toast-stack" class="toast-stack"></div>
    """
    bootstrap = json.dumps(health, ensure_ascii=False)
    extra_js = f"""
  <script>
    window.OMEGA_BOOTSTRAP = {bootstrap};
  </script>
  <script src="/assets/app.js"></script>
"""
    return core.render_shell(
        title_en="Omega Cockpit",
        title_ar="كوكبيت أوميجا",
        body_class="cockpit-page",
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
