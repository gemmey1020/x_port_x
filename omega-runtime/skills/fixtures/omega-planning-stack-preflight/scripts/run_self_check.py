#!/usr/bin/env python3
"""Verify the preflight fixture has the expected files and mode hints."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "parallel-safe": {
        "mode": "multi-agent",
        "paths": [
            "parallel-safe/approved-plan.md",
            "parallel-safe/catalog/public_names.yaml",
            "parallel-safe/docs/operator_runbook.md",
        ],
    },
    "high-coupling": {
        "mode": "single-agent",
        "paths": [
            "high-coupling/approved-plan.md",
            "high-coupling/render/render_shell.py",
            "high-coupling/render/render_cards.py",
            "high-coupling/consumers/skill_cards.md",
        ],
    },
}


def main() -> int:
    results: list[dict[str, object]] = []
    ok = True
    for case, payload in REQUIRED.items():
        missing = [path for path in payload["paths"] if not (ROOT / path).exists()]
        results.append(
            {
                "case": case,
                "expected_mode": payload["mode"],
                "missing": missing,
                "ok": not missing,
            }
        )
        ok = ok and not missing

    print(json.dumps({"ok": ok, "results": results}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
