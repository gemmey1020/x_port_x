#!/usr/bin/env python3

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_skill_reports as base
import build_skill_reports_v2 as v2


ROOT = base.ROOT
OUTPUT_HTML_DIR = ROOT / "output/html"
SKILLS_OUTPUT = OUTPUT_HTML_DIR / "omega-skills-hud-v3.html"
MEMORY_OUTPUT = OUTPUT_HTML_DIR / "omega-memory-learning-report-v3.html"

V3_CSS = (
    v2.SHARED_CSS
    .replace("--bg: #05070b;", "--bg: #021218;")
    .replace("--bg-soft: #0f141c;", "--bg-soft: #07232d;")
    .replace("--surface: rgba(12, 16, 21, 0.74);", "--surface: rgba(4, 24, 31, 0.76);")
    .replace("--surface-strong: rgba(18, 24, 31, 0.9);", "--surface-strong: rgba(5, 30, 39, 0.92);")
    .replace("--surface-soft: rgba(255, 255, 255, 0.03);", "--surface-soft: rgba(124, 255, 248, 0.05);")
    .replace("--line: rgba(255, 194, 117, 0.18);", "--line: rgba(84, 244, 255, 0.18);")
    .replace("--line-strong: rgba(255, 194, 117, 0.38);", "--line-strong: rgba(84, 244, 255, 0.4);")
    .replace("--ink: #f6efe5;", "--ink: #e8feff;")
    .replace("--muted: rgba(246, 239, 229, 0.74);", "--muted: rgba(232, 254, 255, 0.76);")
    .replace("--dim: rgba(246, 239, 229, 0.48);", "--dim: rgba(232, 254, 255, 0.5);")
    .replace("--accent: #ffc275;", "--accent: #54f4ff;")
    .replace("--accent-strong: #ffe0ad;", "--accent-strong: #c9ffff;")
    .replace("--accent-soft: rgba(255, 194, 117, 0.12);", "--accent-soft: rgba(84, 244, 255, 0.14);")
    .replace("--success: #9ed4b0;", "--success: #83f6da;")
    .replace("--shadow: 0 30px 80px rgba(0, 0, 0, 0.34);", "--shadow: 0 34px 90px rgba(0, 12, 18, 0.42);")
    .replace("--bg: #f4eee5;", "--bg: #e8feff;")
    .replace("--bg-soft: #fbf7f1;", "--bg-soft: #f6ffff;")
    .replace("--surface: rgba(255, 252, 247, 0.82);", "--surface: rgba(248, 255, 255, 0.84);")
    .replace("--surface-strong: rgba(255, 252, 247, 0.94);", "--surface-strong: rgba(251, 255, 255, 0.95);")
    .replace("--surface-soft: rgba(76, 53, 18, 0.04);", "--surface-soft: rgba(0, 133, 148, 0.05);")
    .replace("--line: rgba(146, 103, 33, 0.16);", "--line: rgba(0, 133, 148, 0.16);")
    .replace("--line-strong: rgba(146, 103, 33, 0.34);", "--line-strong: rgba(0, 133, 148, 0.34);")
    .replace("--ink: #1f1a16;", "--ink: #0a3038;")
    .replace("--muted: rgba(31, 26, 22, 0.74);", "--muted: rgba(10, 48, 56, 0.72);")
    .replace("--dim: rgba(31, 26, 22, 0.48);", "--dim: rgba(10, 48, 56, 0.5);")
    .replace("--accent: #b56d1d;", "--accent: #007c8a;")
    .replace("--accent-strong: #8d5512;", "--accent-strong: #005967;")
    .replace("--accent-soft: rgba(181, 109, 29, 0.12);", "--accent-soft: rgba(0, 124, 138, 0.12);")
    .replace("--shadow: 0 26px 70px rgba(62, 41, 15, 0.12);", "--shadow: 0 26px 70px rgba(0, 74, 86, 0.14);")
    .replace("rgba(255, 194, 117, 0.14)", "rgba(84, 244, 255, 0.16)")
    .replace("rgba(255, 194, 117, 0.08)", "rgba(59, 214, 255, 0.12)")
    .replace("rgba(255, 194, 117, 0.06)", "rgba(84, 244, 255, 0.08)")
    .replace("rgba(255, 194, 117, 0.09)", "rgba(59, 214, 255, 0.12)")
    .replace("rgba(255, 194, 117, 0.16)", "rgba(84, 244, 255, 0.18)")
    .replace("rgba(255, 194, 117, 0.18)", "rgba(84, 244, 255, 0.18)")
    .replace("rgba(255, 194, 117, 0.38)", "rgba(84, 244, 255, 0.38)")
    .replace("rgba(255, 194, 117, 0.1)", "rgba(84, 244, 255, 0.1)")
    .replace("rgba(255, 194, 117, 0.03)", "rgba(84, 244, 255, 0.04)")
    .replace("rgba(255, 194, 117, 0.12)", "rgba(84, 244, 255, 0.14)")
    .replace("rgba(255, 194, 117, 0.18)", "rgba(84, 244, 255, 0.18)")
    .replace("rgba(255, 194, 117, 0.34)", "rgba(84, 244, 255, 0.36)")
    .replace("rgba(255, 194, 117, 0.4)", "rgba(84, 244, 255, 0.42)")
    .replace("rgba(255, 194, 117, 0.05)", "rgba(84, 244, 255, 0.06)")
    .replace("rgba(255, 194, 117, 0.02)", "rgba(84, 244, 255, 0.03)")
    .replace("rgba(255, 194, 117, 0.015)", "rgba(84, 244, 255, 0.02)")
    .replace("rgba(255, 194, 117, 0.14)", "rgba(84, 244, 255, 0.18)")
    .replace("rgba(255, 194, 117, 0.18)", "rgba(84, 244, 255, 0.2)")
    .replace("rgba(255, 194, 117, 0.09)", "rgba(59, 214, 255, 0.14)")
    .replace("rgba(255, 194, 117, 0.1)", "rgba(84, 244, 255, 0.12)")
    .replace("rgba(255, 194, 117, 0.06)", "rgba(59, 214, 255, 0.08)")
    .replace("rgba(255, 194, 117, 0.03)", "rgba(84, 244, 255, 0.04)")
    .replace("rgba(255, 194, 117, 0.04)", "rgba(84, 244, 255, 0.05)")
    .replace("rgba(255, 194, 117, 0.18)", "rgba(84, 244, 255, 0.2)")
    .replace("background-size: 40px 40px;", "background-size: 34px 34px;")
    .replace("letter-spacing: 0.24em;", "letter-spacing: 0.28em;")
    .replace("border-radius: 32px 32px 0 32px;", "border-radius: 34px 34px 0 34px;")
    .replace(".hero-copy h1 {\n", ".hero-copy h1 {\n  text-shadow: 0 0 34px rgba(84, 244, 255, 0.14);\n")
    .replace(".poster-surface__score strong {\n", ".poster-surface__score strong {\n  text-shadow: 0 0 36px rgba(84, 244, 255, 0.18);\n")
    .replace(".poster-surface__name {\n", ".poster-surface__name {\n  text-shadow: 0 0 28px rgba(84, 244, 255, 0.1);\n")
)

COMMON_REPLACEMENTS = [
    (
        "OMEGA HUD V2 / cinematic alternate artifact / local only / no external assets",
        "OMEGA HUD V3 / teal-cyan alternate artifact / local only / no external assets",
    ),
    ("OMEGA HUD V2", "OMEGA HUD V3"),
    ("omega-cinematic-v2", "omega-teal-cyan-v3"),
    ("cinematic alternate artifact", "teal-cyan alternate artifact"),
]

SKILLS_REPLACEMENTS = [
    ("Omega Skills HUD V2", "Omega Skills HUD V3"),
    ("لوحة مهارات أوميجا V2", "لوحة مهارات أوميجا V3"),
    ("نسخة سينمائية بديلة", "نسخة Teal + Cyan V3"),
    ("Cinematic alternate edition", "Teal + Cyan V3 edition"),
    ("Taste Upgrade Mode / بلا source drift", "Teal + Cyan Signal / بلا source drift"),
    ("Taste Upgrade Mode / no source drift", "Teal + Cyan Signal / no source drift"),
]

MEMORY_REPLACEMENTS = [
    ("Omega Memory Learning Report V2", "Omega Memory Learning Report V3"),
    ("تقرير ذاكرة وتعلّم أوميجا V2", "تقرير ذاكرة وتعلّم أوميجا V3"),
    ("نسخة تحليلية V2", "نسخة Teal + Cyan تحليلية"),
    ("Forensic companion edition", "Teal + Cyan forensic edition"),
    ("Forensic companion / same pipeline", "Teal + Cyan Forensics / same pipeline"),
    ("Forensic companion / نفس pipeline", "Teal + Cyan Forensics / نفس pipeline"),
]


def restyle_document(document: str, page_kind: str) -> str:
    for old, new in COMMON_REPLACEMENTS:
        document = document.replace(old, new)

    page_specific = SKILLS_REPLACEMENTS if page_kind == "skills" else MEMORY_REPLACEMENTS
    for old, new in page_specific:
        document = document.replace(old, new)
    return document


def main():
    OUTPUT_HTML_DIR.mkdir(parents=True, exist_ok=True)
    original_css = v2.SHARED_CSS
    try:
        v2.SHARED_CSS = V3_CSS
        skills = base.build_skill_index()
        snapshot = base.build_memory_snapshot()
        skills_html = restyle_document(v2.build_skills_page(skills), "skills")
        memory_html = restyle_document(v2.build_memory_page(skills, snapshot), "memory")
        SKILLS_OUTPUT.write_text(skills_html, encoding="utf-8")
        MEMORY_OUTPUT.write_text(memory_html, encoding="utf-8")
    finally:
        v2.SHARED_CSS = original_css

    print("Wrote:")
    print(SKILLS_OUTPUT)
    print(MEMORY_OUTPUT)


if __name__ == "__main__":
    main()
