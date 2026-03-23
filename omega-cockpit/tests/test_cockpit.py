#!/usr/bin/env python3

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

import yaml


TESTS_DIR = Path(__file__).resolve().parent
COCKPIT_DIR = TESTS_DIR.parent
if str(COCKPIT_DIR) not in sys.path:
    sys.path.insert(0, str(COCKPIT_DIR))

import core
import server


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_skill(path: Path, *, name: str, description: str, body: str) -> None:
    write_text(
        path,
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n\n{body}\n",
    )


def create_threads_db(path: Path, rows: list[tuple[str, str, str, int, str, str, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            CREATE TABLE threads (
                id TEXT PRIMARY KEY,
                cwd TEXT NOT NULL,
                rollout_path TEXT NOT NULL,
                updated_at INTEGER NOT NULL,
                title TEXT,
                memory_mode TEXT,
                archived INTEGER
            )
            """
        )
        connection.executemany(
            "INSERT INTO threads(id, cwd, rollout_path, updated_at, title, memory_mode, archived) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        connection.commit()
    finally:
        connection.close()


def write_rollout(path: Path, message: str) -> None:
    write_text(
        path,
        json.dumps({"type": "event_msg", "payload": {"type": "user_message", "message": message}}, ensure_ascii=False) + "\n",
    )


class SkillAuditTests(unittest.TestCase):
    def test_live_skills_are_primary_truth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex_home = tmp_path / "codex"
            skills_root = codex_home / "skills"
            catalog_path = tmp_path / "catalog.yaml"
            doc_path = tmp_path / "docs" / "demo.skill.md"

            make_skill(
                skills_root / "demo" / "SKILL.md",
                name="demo",
                description="Demo skill",
                body="Its public/operator name is `Demo Skill`.\n\nInvoke now with `$demo`.",
            )
            make_skill(
                skills_root / ".system" / "openai-docs" / "SKILL.md",
                name="openai-docs",
                description="System docs skill",
                body="Its public/operator name is `OpenAI Docs System`.\n\nInvoke now with `$openai-docs`.",
            )
            write_text(doc_path, "# demo doc\n")
            write_text(
                catalog_path,
                """
catalog_version: "1.0"
entries:
  - skill_id: "demo"
    display_name: "Wrong Demo Name"
    category: "planning"
    status: "active"
    source_skill_path: "__SOURCE__"
    doc_path: "__DOC__"
                """.replace("__SOURCE__", str((skills_root / "demo" / "SKILL.md").resolve())).replace("__DOC__", str(doc_path.relative_to(tmp_path))),
            )

            live_skills = core.scan_live_skills(skills_root, catalog_path)
            audit = core.build_skill_audit(live_skills, catalog_path)

            self.assertEqual(len(live_skills), 2)
            self.assertEqual(audit["summary"]["missing_from_catalog"], 1)
            self.assertGreaterEqual(audit["summary"]["metadata_drift"], 1)
            self.assertEqual(live_skills[0]["skill_id"], "openai-docs")


class MemoryFixtureTests(unittest.TestCase):
    def build_config(self) -> tuple[tempfile.TemporaryDirectory[str], core.CockpitConfig]:
        temp_dir = tempfile.TemporaryDirectory()
        tmp_path = Path(temp_dir.name)
        codex_home = tmp_path / "codex"
        output_dir = tmp_path / "output"
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        write_text(workspace / "index.html", "<html></html>\n")

        now_ms = int(time.time() * 1000)
        old_ms = int((time.time() - (96 * 3600)) * 1000)

        rollout1 = tmp_path / "rollout1.jsonl"
        rollout2 = tmp_path / "rollout2.jsonl"
        rollout3 = tmp_path / "rollout3.jsonl"

        write_rollout(rollout1, "## My request for Codex:\nعاوزك تتكلم مصري\n")
        write_rollout(rollout2, "## My request for Codex:\nمن فضلك استخدم $plan-critic في المراجعة\n")
        write_rollout(
            rollout3,
            "# Context from my IDE setup:\n\n## Active file: index.html\n## Open tabs:\n- index.html\n\n## My request for Codex:\nراجع الملف الحالي\n",
        )

        create_threads_db(
            codex_home / "state_5.sqlite",
            [
                ("thread-1", str(workspace), str(rollout1), now_ms, "thread 1", "enabled", 0),
                ("thread-2", str(workspace), str(rollout2), now_ms, "thread 2", "enabled", 0),
                ("thread-3", str(workspace), str(rollout3), old_ms, "thread 3", "enabled", 0),
            ],
        )

        config = core.CockpitConfig(
            workspace_root=workspace,
            codex_home=codex_home,
            output_dir=output_dir,
        ).normalized()
        return temp_dir, config

    def test_memory_workflow_on_fixture_store(self) -> None:
        temp_dir, config = self.build_config()
        self.addCleanup(temp_dir.cleanup)

        backfill = core.backfill_memory(config)
        self.assertGreater(backfill["candidate_files"], 0)

        pending = core.suggest_payload(config)
        language_candidate = next(item for item in pending if item["normalized_key"] == "communication.language")
        review_candidate = next(item for item in pending if item["normalized_key"] == "workflow.review_preference")

        promoted = core.promote_candidate(config, language_candidate["candidate_id"])
        rejected = core.reject_candidate(config, review_candidate["candidate_id"], "fixture reject")
        forgotten = core.forget_memory(config, scope="global", key="communication.language")
        self.assertIsNotNone(promoted["event_id"])
        self.assertIsNotNone(rejected["event_id"])
        self.assertIsNotNone(forgotten["event_id"])

        core.rollback_event(config, forgotten["event_id"])
        inspect = core.inspect_payload(config, no_pending=True)
        language = inspect["user_profile"]["communication_preferences"]["language"]
        self.assertEqual(language, "arabic-egyptian-mixed")

    def test_cleanup_preview_and_execute_support_partial_ledger(self) -> None:
        temp_dir, config = self.build_config()
        self.addCleanup(temp_dir.cleanup)

        core.backfill_memory(config)
        stale_stamp = "2026-01-01T00:00:00+00:00"
        connection = sqlite3.connect(config.state_db_path)
        try:
            connection.execute(
                """
                UPDATE candidate_items
                SET created_at = ?, updated_at = ?
                WHERE normalized_key = 'project.active_artifact'
                """,
                (stale_stamp, stale_stamp),
            )
            connection.commit()
        finally:
            connection.close()
        for candidate_file in (config.codex_home / "memory" / "candidates" / "pending").glob("*.yaml"):
            payload = yaml.safe_load(candidate_file.read_text(encoding="utf-8")) or {}
            if payload.get("normalized_key") == "project.active_artifact":
                payload["created_at"] = stale_stamp
                payload["updated_at"] = stale_stamp
                candidate_file.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")

        preview = core.build_cleanup_preview(config)
        ephemeral_queue = next(item for item in preview["queues"] if item["id"] == "ephemeral-artifacts")
        stale_queue = next(item for item in preview["queues"] if item["id"] == "stale-pending")

        self.assertGreaterEqual(ephemeral_queue["total"], 1)
        self.assertGreaterEqual(stale_queue["total"], 1)

        valid_candidate_id = ephemeral_queue["items"][0]["candidate_id"]
        result = core.execute_cleanup(config, "ephemeral-artifacts", [valid_candidate_id, "missing-candidate"], "fixture cleanup")
        self.assertEqual(result["summary"]["succeeded"], 1)
        self.assertEqual(result["summary"]["skipped"], 1)

    def test_exports_follow_new_naming_contract(self) -> None:
        temp_dir, config = self.build_config()
        self.addCleanup(temp_dir.cleanup)

        core.backfill_memory(config)
        skills_export = core.export_surface(config, "skills-review")
        memory_export = core.export_surface(config, "memory")

        self.assertEqual(skills_export.name, "omega-hud-skills-review.html")
        self.assertEqual(memory_export.name, "omega-hud-memory.html")
        self.assertTrue(skills_export.exists())
        self.assertTrue(memory_export.exists())


class ServerSmokeTests(unittest.TestCase):
    def test_health_endpoint_uses_loopback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = core.CockpitConfig(
                workspace_root=tmp_path / "workspace",
                codex_home=tmp_path / "codex",
                output_dir=tmp_path / "output",
                host="127.0.0.1",
                port=0,
            ).normalized()
            config.workspace_root.mkdir(parents=True, exist_ok=True)

            httpd = server.build_server(config)
            self.assertEqual(httpd.server_address[0], "127.0.0.1")

            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{httpd.server_address[1]}/api/health"
                payload = json.loads(urllib.request.urlopen(url, timeout=5).read().decode("utf-8"))
                self.assertTrue(payload["ok"])
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
