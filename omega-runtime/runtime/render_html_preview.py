#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_structured_output_pipeline import load_document, validate_bundle

ALLOWED_BUNDLE_VERSION = "1.3.1"
SUPPORTED_TIERS = ("lite", "default", "premium")
ALLOWED_HEADING_LEVELS = {"h1", "h2", "h3", "h4", "h5", "h6"}
WHATSAPP_TARGET_RE = re.compile(r"^https://wa\.me/\d{6,20}$")

BASE_PAGE_CSS = """
:root {
  --bg: #f6f8fc;
  --surface: #ffffff;
  --surface-strong: #eef3fb;
  --line: #d4dceb;
  --text: #172033;
  --muted: #54627a;
  --accent: #0f4c81;
  --accent-soft: #dfeeff;
  --gap-bg: #fff3d6;
  --gap-line: #f1c96b;
  --gap-text: #6f4c00;
  --json-bg: #f3f5f9;
  --shadow: 0 12px 30px rgba(17, 24, 39, 0.06);
  --radius: 18px;
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  text-align: start;
}

body {
  line-height: 1.6;
}

a {
  color: inherit;
}

.shell {
  width: min(100%, 960px);
  margin: 0 auto;
  padding: 20px 16px 88px;
}

.chrome {
  background: linear-gradient(180deg, #ffffff 0%, #eef4fb 100%);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px;
  margin-bottom: 18px;
}

.chrome-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  align-items: center;
}

.token {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--muted);
  font-size: 13px;
}

.doc-title {
  margin: 14px 0 0;
  font-size: 24px;
  line-height: 1.35;
}

.doc-meta {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 14px;
}

main {
  display: grid;
  gap: 16px;
}

.section-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px;
}

.section-card > :first-child {
  margin-top: 0;
}

.section-card > :last-child {
  margin-bottom: 0;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  margin: 0 0 12px;
  line-height: 1.3;
  color: #111827;
}

.slot-stack {
  display: grid;
  gap: 12px;
}

.slot-scalar,
.slot-list,
.slot-cta,
.slot-json,
.gap-token {
  border-radius: 14px;
  border: 1px solid var(--line);
  background: var(--surface-strong);
  padding: 12px 14px;
}

.slot-scalar {
  white-space: pre-wrap;
  word-break: break-word;
}

.slot-list {
  padding-inline-start: 30px;
}

.slot-list li + li {
  margin-top: 8px;
}

.slot-json {
  margin: 0;
  background: var(--json-bg);
  overflow-x: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 13px;
}

.gap-token {
  border-color: var(--gap-line);
  background: var(--gap-bg);
  color: var(--gap-text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 13px;
}

.cta-block {
  display: grid;
  gap: 10px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: var(--surface);
  padding: 14px;
}

.cta-action {
  font-weight: 700;
  color: var(--accent);
  word-break: break-word;
}

.cta-link {
  display: inline-flex;
  width: fit-content;
  max-width: 100%;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--accent);
  color: #ffffff;
  text-decoration: none;
  font-weight: 700;
  word-break: break-all;
}

.cta-link:hover,
.cta-link:focus-visible {
  background: #0c406c;
}

.placement-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.placement-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 9px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface-strong);
  color: var(--muted);
  font-size: 12px;
}

.notes {
  margin-top: 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.notes summary {
  cursor: pointer;
  list-style: none;
  padding: 14px 16px;
  font-weight: 700;
}

.notes summary::-webkit-details-marker {
  display: none;
}

.notes-body {
  padding: 0 16px 16px;
  display: grid;
  gap: 14px;
}

.notes-list {
  margin: 8px 0 0;
  padding-inline-start: 22px;
}

.index-grid {
  display: grid;
  gap: 14px;
}

.index-card {
  display: grid;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
}

.index-card:hover,
.index-card:focus-visible {
  border-color: #adc5e6;
  transform: translateY(-1px);
}

.index-tier {
  font-size: 13px;
  color: var(--muted);
}

.index-title {
  font-size: 20px;
  line-height: 1.35;
}

.sticky-mobile-cta {
  position: fixed;
  inset-inline: 0;
  bottom: 0;
  z-index: 10;
  padding: 12px 14px calc(12px + env(safe-area-inset-bottom, 0px));
  background: rgba(255, 255, 255, 0.97);
  border-top: 1px solid var(--line);
  box-shadow: 0 -10px 24px rgba(17, 24, 39, 0.08);
}

.sticky-mobile-cta .cta-block {
  max-width: 960px;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .shell {
    padding: 28px 24px 44px;
  }

  .sticky-mobile-cta {
    display: none;
  }
}
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a local HTML preview from a validated render_output bundle.")
    parser.add_argument("--bundle", required=True, help="Path to the local pipeline bundle YAML or JSON file.")
    parser.add_argument(
        "--out-dir",
        help="Optional output directory. Defaults to output/html-preview/<case_id>/",
    )
    parser.add_argument(
        "--tiers",
        choices=("all", "lite", "default", "premium"),
        default="all",
        help="Render all emitted tiers or a single emitted tier.",
    )
    return parser.parse_args()


def html_escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def safe_json_script(obj: Any) -> str:
    serialized = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def load_and_validate_bundle(bundle_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    bundle = load_document(bundle_path)
    if not isinstance(bundle, dict):
        raise ValueError("bundle must be an object")
    if bundle.get("pipeline_bundle_version") != ALLOWED_BUNDLE_VERSION:
        raise ValueError(f"pipeline_bundle_version must be exactly {ALLOWED_BUNDLE_VERSION}")

    report = validate_bundle(bundle)
    if report.get("result") != "pass":
        failures = report.get("failures") or []
        if failures:
            first_failure = failures[0]
            code = first_failure.get("code", "validation.failure")
            message = first_failure.get("message", "bundle validation failed")
            path = first_failure.get("path")
            suffix = f" [{path}]" if path else ""
            raise ValueError(f"validator failed: {code}: {message}{suffix}")
        raise ValueError("validator failed")

    render_output = bundle.get("render_output")
    if not isinstance(render_output, dict):
        raise ValueError("render_output must be an object after validator pass")
    render_artifact = render_output.get("render_artifact")
    if not isinstance(render_artifact, dict) or not render_artifact:
        raise ValueError("render_output.render_artifact must be a non-empty object after validator pass")

    case_id = bundle.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string after validator pass")
    return bundle, report


def select_tiers(render_artifact: dict[str, Any], tier_arg: str) -> list[str]:
    available = [tier for tier in SUPPORTED_TIERS if tier in render_artifact]
    if not available:
        raise ValueError("render_output.render_artifact contains no supported emitted tiers")
    if tier_arg == "all":
        return available
    if tier_arg not in render_artifact:
        raise ValueError(f"requested tier {tier_arg} is not present in render_output.render_artifact")
    return [tier_arg]


def ensure_output_dir(case_id: str, out_dir: Path | None) -> Path:
    output_dir = out_dir if out_dir is not None else Path("output") / "html-preview" / case_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def render_index_html(case_id: str, tiers: list[str], render_artifact: dict[str, Any]) -> str:
    first_tier = render_artifact[tiers[0]]
    document = first_tier.get("document", {}) if isinstance(first_tier, dict) else {}
    lang = document.get("lang") if isinstance(document.get("lang"), str) else "en"
    direction = document.get("dir") if isinstance(document.get("dir"), str) else "ltr"

    cards: list[str] = []
    for tier in tiers:
        tier_payload = render_artifact[tier]
        if not isinstance(tier_payload, dict):
            raise ValueError(f"render_output.render_artifact.{tier} must be an object")
        tier_document = tier_payload.get("document")
        if not isinstance(tier_document, dict):
            raise ValueError(f"render_output.render_artifact.{tier}.document must be an object")
        cards.append(
            "\n".join(
                (
                    '      <a class="index-card" href="{href}">'.format(href=html_escape(f"{tier}.html")),
                    '        <div class="index-tier">{tier}</div>'.format(tier=html_escape(tier)),
                    '        <div class="index-title">{title}</div>'.format(
                        title=html_escape(tier_document.get("title", ""))
                    ),
                    '        <div class="doc-meta">{meta}</div>'.format(
                        meta=html_escape(tier_document.get("meta_description", ""))
                    ),
                    "      </a>",
                )
            )
        )

    return "\n".join(
        (
            "<!doctype html>",
            '<html lang="{lang}" dir="{direction}">'.format(
                lang=html_escape(lang),
                direction=html_escape(direction),
            ),
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>{title}</title>".format(title=html_escape(case_id)),
            "  <style>{css}</style>".format(css=BASE_PAGE_CSS),
            "</head>",
            "<body>",
            '  <div class="shell">',
            '    <header class="chrome">',
            '      <div class="chrome-row"><span class="token">{case_id}</span></div>'.format(case_id=html_escape(case_id)),
            "    </header>",
            '    <main class="index-grid">',
            *cards,
            "    </main>",
            "  </div>",
            "</body>",
            "</html>",
        )
    )


def validate_heading_tag(level: Any, tier: str, section_id: str) -> str:
    if not isinstance(level, str) or level not in ALLOWED_HEADING_LEVELS:
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.heading.level must be one of {sorted(ALLOWED_HEADING_LEVELS)}")
    return level


def render_scalar(value: Any) -> str:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return '<div class="slot-scalar">{text}</div>'.format(text=html_escape(text))


def render_value_html(value: Any) -> str:
    if isinstance(value, list):
        if all(not isinstance(item, (list, dict)) for item in value):
            items = "".join("<li>{item}</li>".format(item=html_escape(item)) for item in value)
            return '<ul class="slot-list">{items}</ul>'.format(items=items)
        rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False)
        return '<pre class="slot-json">{payload}</pre>'.format(payload=html_escape(rendered))
    if isinstance(value, dict):
        rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False)
        return '<pre class="slot-json">{payload}</pre>'.format(payload=html_escape(rendered))
    return render_scalar(value)


def validate_cta_payload(cta_payload: Any, tier: str) -> dict[str, Any]:
    if not isinstance(cta_payload, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.cta.primary must be an object")
    action = cta_payload.get("action")
    target = cta_payload.get("target")
    placements = cta_payload.get("placements")
    if not isinstance(action, str) or not action.strip():
        raise ValueError(f"render_output.render_artifact.{tier}.cta.primary.action must be a non-empty string")
    if not isinstance(target, str) or not target.strip():
        raise ValueError(f"render_output.render_artifact.{tier}.cta.primary.target must be a non-empty string")
    if not isinstance(placements, list) or any(not isinstance(item, str) or not item.strip() for item in placements):
        raise ValueError(f"render_output.render_artifact.{tier}.cta.primary.placements must be a list of non-empty strings")
    if action == "direct_whatsapp" and not WHATSAPP_TARGET_RE.fullmatch(target):
        raise ValueError(f"render_output.render_artifact.{tier}.cta.primary.target must match https://wa.me/<digits> for direct_whatsapp")
    return {"action": action, "target": target, "placements": placements}


def render_cta_block(cta_payload: dict[str, Any], sticky: bool = False) -> str:
    placements = "".join(
        '<li class="placement-chip">{placement}</li>'.format(placement=html_escape(item))
        for item in cta_payload["placements"]
    )
    if cta_payload["action"] == "direct_whatsapp":
        target_html = '<a class="cta-link" href="{href}">{label}</a>'.format(
            href=html_escape(cta_payload["target"]),
            label=html_escape(cta_payload["target"]),
        )
    else:
        target_html = '<div class="slot-scalar">{target}</div>'.format(target=html_escape(cta_payload["target"]))

    wrapper_class = "sticky-mobile-cta" if sticky else ""
    wrapper_open = '<div class="{klass}">'.format(klass=wrapper_class) if wrapper_class else ""
    wrapper_close = "</div>" if wrapper_class else ""
    return "\n".join(
        (
            wrapper_open,
            '  <div class="cta-block">',
            '    <div class="cta-action">{action}</div>'.format(action=html_escape(cta_payload["action"])),
            "    {target}".format(target=target_html),
            '    <ul class="placement-list">{placements}</ul>'.format(placements=placements),
            "  </div>",
            wrapper_close,
        )
    ).strip()


def render_slot_html(slot: Any, cta_payload: dict[str, Any], tier: str, section_id: str, index: int) -> str:
    if not isinstance(slot, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}] must be an object")
    slot_id = slot.get("slot_id")
    status = slot.get("status")
    if not isinstance(slot_id, str) or not slot_id.strip():
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].slot_id must be a non-empty string")
    if status == "resolved":
        value = slot.get("value")
        fallback = slot.get("fallback")
        if slot_id == "primary_cta_ref":
            if value != "primary":
                raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}] primary_cta_ref must resolve to primary")
            return render_cta_block(cta_payload)
        if fallback is not None:
            raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].fallback must be null for resolved slots")
        return render_value_html(value)
    if status == "unresolved":
        fallback = slot.get("fallback")
        value = slot.get("value")
        if value is not None:
            raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].value must be null for unresolved slots")
        if not isinstance(fallback, str):
            raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].fallback must be a string for unresolved slots")
        return '<div class="gap-token">{token}</div>'.format(token=html_escape(fallback))
    raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].status must be resolved or unresolved")


def render_section_html(section_id: str, section_payload: Any, cta_payload: dict[str, Any], tier: str) -> str:
    if not isinstance(section_payload, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id} must be an object")
    heading = section_payload.get("heading")
    slots = section_payload.get("slots")
    render_status = section_payload.get("render_status")
    if render_status != "ready":
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.render_status must be ready")
    if not isinstance(heading, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.heading must be an object")
    if not isinstance(slots, list):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots must be a list")

    heading_level = validate_heading_tag(heading.get("level"), tier, section_id)
    heading_text = heading.get("text")
    if not isinstance(heading_text, str):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.heading.text must be a string")

    slot_html = "\n".join(
        render_slot_html(slot, cta_payload, tier, section_id, index)
        for index, slot in enumerate(slots)
    )

    return "\n".join(
        (
            '<section class="section-card" id="{section_id}">'.format(section_id=html_escape(section_id)),
            '  <{level}>{text}</{level}>'.format(level=heading_level, text=html_escape(heading_text)),
            '  <div class="slot-stack">{slots}</div>'.format(slots=slot_html),
            "</section>",
        )
    )


def render_details_block(render_notes: Any, tier: str) -> str:
    if not isinstance(render_notes, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.render_notes must be an object")
    keys = ("withheld_sections", "unresolved_slots", "required_inputs")
    for key in keys:
        value = render_notes.get(key)
        if not isinstance(value, list):
            raise ValueError(f"render_output.render_artifact.{tier}.render_notes.{key} must be a list")
    if not any(render_notes[key] for key in keys):
        return ""

    groups: list[str] = []
    for key in keys:
        items = "".join("<li>{item}</li>".format(item=html_escape(item)) for item in render_notes[key])
        groups.append(
            "\n".join(
                (
                    "      <div>",
                    "        <div>{label}</div>".format(label=html_escape(key)),
                    '        <ul class="notes-list">{items}</ul>'.format(items=items),
                    "      </div>",
                )
            )
        )

    return "\n".join(
        (
            '  <details class="notes">',
            "    <summary>render_notes</summary>",
            '    <div class="notes-body">',
            *groups,
            "    </div>",
            "  </details>",
        )
    )


def render_tier_html(case_id: str, tier: str, tier_payload: Any) -> str:
    if not isinstance(tier_payload, dict):
        raise ValueError(f"render_output.render_artifact.{tier} must be an object")

    document = tier_payload.get("document")
    head = tier_payload.get("head")
    body = tier_payload.get("body")
    cta = tier_payload.get("cta")
    render_notes = tier_payload.get("render_notes")
    if not isinstance(document, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.document must be an object")
    if not isinstance(head, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.head must be an object")
    if not isinstance(body, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body must be an object")
    if not isinstance(cta, dict) or not isinstance(cta.get("primary"), dict):
        raise ValueError(f"render_output.render_artifact.{tier}.cta.primary must be an object")

    lang = document.get("lang")
    direction = document.get("dir")
    title = document.get("title")
    meta_description = document.get("meta_description")
    if not isinstance(lang, str) or not lang.strip():
        raise ValueError(f"render_output.render_artifact.{tier}.document.lang must be a non-empty string")
    if not isinstance(direction, str) or not direction.strip():
        raise ValueError(f"render_output.render_artifact.{tier}.document.dir must be a non-empty string")
    if not isinstance(title, str):
        raise ValueError(f"render_output.render_artifact.{tier}.document.title must be a string")
    if not isinstance(meta_description, str):
        raise ValueError(f"render_output.render_artifact.{tier}.document.meta_description must be a string")

    head_jsonld = head.get("jsonld")
    if not isinstance(head_jsonld, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.head.jsonld must be an object")
    section_order = body.get("section_order")
    sections = body.get("sections")
    if not isinstance(section_order, list):
        raise ValueError(f"render_output.render_artifact.{tier}.body.section_order must be a list")
    if not isinstance(sections, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections must be an object")

    cta_payload = validate_cta_payload(cta["primary"], tier)
    section_ids = [section_id for section_id in section_order if isinstance(section_id, str)]
    if len(section_ids) != len(section_order):
        raise ValueError(f"render_output.render_artifact.{tier}.body.section_order must contain only strings")
    section_markup = []
    for section_id in section_ids:
        if section_id not in sections:
            raise ValueError(f"render_output.render_artifact.{tier}.body.sections is missing {section_id}")
        section_markup.append(render_section_html(section_id, sections[section_id], cta_payload, tier))
    details_html = render_details_block(render_notes, tier)

    jsonld_scripts = []
    for payload in head_jsonld.values():
        jsonld_scripts.append(
            '<script type="application/ld+json">{payload}</script>'.format(payload=safe_json_script(payload))
        )

    sticky_mobile_html = ""
    if "sticky_mobile" in cta_payload["placements"]:
        sticky_mobile_html = render_cta_block(cta_payload, sticky=True)

    return "\n".join(
        (
            "<!doctype html>",
            '<html lang="{lang}" dir="{direction}">'.format(
                lang=html_escape(lang),
                direction=html_escape(direction),
            ),
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            '  <title>{title}</title>'.format(title=html_escape(title)),
            '  <meta name="description" content="{content}">'.format(content=html_escape(meta_description)),
            *["  " + script for script in jsonld_scripts],
            "  <style>{css}</style>".format(css=BASE_PAGE_CSS),
            "</head>",
            "<body>",
            '  <div class="shell">',
            '    <header class="chrome">',
            '      <div class="chrome-row">',
            '        <span class="token">{case_id}</span>'.format(case_id=html_escape(case_id)),
            '        <span class="token">{tier}</span>'.format(tier=html_escape(tier)),
            "      </div>",
            '      <div class="doc-title">{title}</div>'.format(title=html_escape(title)),
            '      <div class="doc-meta">{meta}</div>'.format(meta=html_escape(meta_description)),
            "    </header>",
            "    <main>",
            *section_markup,
            "    </main>",
            details_html if details_html else "",
            "  </div>",
            sticky_mobile_html,
            "</body>",
            "</html>",
        )
    )


def write_output_files(output_dir: Path, documents: dict[str, str]) -> list[Path]:
    for stale_file in output_dir.glob("*.html"):
        stale_file.unlink()

    written: list[Path] = []
    for name, content in documents.items():
        path = output_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    args = parse_args()
    bundle_path = Path(args.bundle)
    out_dir = Path(args.out_dir) if args.out_dir else None

    try:
        bundle, _report = load_and_validate_bundle(bundle_path)
        case_id = bundle["case_id"]
        render_artifact = bundle["render_output"]["render_artifact"]
        tiers = select_tiers(render_artifact, args.tiers)

        rendered_documents: dict[str, str] = {
            "index.html": render_index_html(case_id, tiers, render_artifact),
        }
        for tier in tiers:
            rendered_documents[f"{tier}.html"] = render_tier_html(case_id, tier, render_artifact[tier])

        output_dir = ensure_output_dir(case_id, out_dir)
        written_paths = write_output_files(output_dir, rendered_documents)
    except Exception as exc:  # pragma: no cover - CLI failure surface
        print(str(exc), file=sys.stderr)
        return 1

    for path in written_paths:
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
