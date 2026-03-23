#!/usr/bin/env python3
"""Generate a deterministic summary artifact for the preflight fixture."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "preflight-preview.txt"

CASES = {
    "parallel-safe": {
        "mode": "multi-agent",
        "files": [
            "parallel-safe/catalog/public_names.yaml",
            "parallel-safe/docs/operator_runbook.md",
        ],
    },
    "high-coupling": {
        "mode": "single-agent",
        "files": [
            "high-coupling/render/render_shell.py",
            "high-coupling/render/render_cards.py",
            "high-coupling/consumers/skill_cards.md",
        ],
    },
}


def main() -> int:
    lines = ["# Omega Planning Stack Preflight Preview", ""]
    for name, payload in CASES.items():
        lines.append(f"## {name}")
        lines.append(f"- expected-mode: {payload['mode']}")
        for rel_path in payload["files"]:
            exists = (ROOT / rel_path).exists()
            lines.append(f"- {rel_path}: {'present' if exists else 'missing'}")
        lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines).rstrip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
