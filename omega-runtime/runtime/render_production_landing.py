#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from validate_structured_output_pipeline import load_document, validate_bundle

ALLOWED_BUNDLE_VERSION = "1.3.1"
SUPPORTED_TIERS = ("lite", "default", "premium")
ALLOWED_HEADING_LEVELS = {"h1", "h2", "h3", "h4", "h5", "h6"}
KNOWN_SECTION_CLASSES = {
    "hero",
    "service-summary",
    "service-list",
    "trust-strip",
    "hours",
    "whatsapp-cta",
    "footer-contact",
}
WHATSAPP_TARGET_RE = re.compile(r"^https://wa\.me/\d{6,20}$")
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}")
REQUIRED_PLACEHOLDERS = (
    "BODY_CLASS",
    "LANG",
    "DIR",
    "TITLE",
    "META_DESCRIPTION",
    "JSONLD_SCRIPTS",
    "SECTIONS_HTML",
    "STICKY_MOBILE_CTA",
    "RENDER_NOTES_JSON",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one validated render_output tier into a production-like HTML landing page."
    )
    parser.add_argument("--bundle", required=True, help="Path to the pipeline bundle YAML/JSON file.")
    parser.add_argument(
        "--tier",
        required=True,
        choices=SUPPORTED_TIERS,
        help="Rendered tier to consume from render_output.render_artifact.",
    )
    parser.add_argument("--out", help="Optional output HTML path.")
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


def load_and_validate_bundle(bundle_path: Path) -> dict[str, Any]:
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

    case_id = bundle.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string after validator pass")

    render_output = bundle.get("render_output")
    if not isinstance(render_output, dict):
        raise ValueError("render_output must be an object after validator pass")
    render_artifact = render_output.get("render_artifact")
    if not isinstance(render_artifact, dict) or not render_artifact:
        raise ValueError("render_output.render_artifact must be a non-empty object after validator pass")

    return bundle


def resolve_output_path(case_id: str, tier: str, out_arg: str | None) -> Path:
    if out_arg:
        return Path(out_arg)
    return Path("output") / "html-production" / case_id / f"{tier}.html"


def load_template(template_path: Path) -> str:
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"template file not found: {template_path}") from exc


def validate_selected_tier_payload(tier_payload: Any, tier: str) -> dict[str, Any]:
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
    if not isinstance(cta, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.cta must be an object")
    if not isinstance(render_notes, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.render_notes must be an object")

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
    if any(not isinstance(section_id, str) or not section_id.strip() for section_id in section_order):
        raise ValueError(f"render_output.render_artifact.{tier}.body.section_order must contain only non-empty strings")
    if section_order != list(sections.keys()):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections must match body.section_order exactly")

    withheld_sections = render_notes.get("withheld_sections")
    unresolved_slots = render_notes.get("unresolved_slots")
    required_inputs = render_notes.get("required_inputs")
    if not isinstance(withheld_sections, list):
        raise ValueError(f"render_output.render_artifact.{tier}.render_notes.withheld_sections must be a list")
    if not isinstance(unresolved_slots, list):
        raise ValueError(f"render_output.render_artifact.{tier}.render_notes.unresolved_slots must be a list")
    if not isinstance(required_inputs, list):
        raise ValueError(f"render_output.render_artifact.{tier}.render_notes.required_inputs must be a list")
    if any(section_id in set(withheld_sections) for section_id in section_order):
        raise ValueError(f"render_output.render_artifact.{tier}.render_notes.withheld_sections must not appear in body.section_order")

    return tier_payload


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
        raise ValueError(
            f"render_output.render_artifact.{tier}.cta.primary.target must match https://wa.me/<digits> for direct_whatsapp"
        )

    return {
        "action": action,
        "target": target,
        "placements": list(placements),
    }


def render_scalar_primitive(value: Any) -> str:
    if isinstance(value, str):
        rendered = value
    else:
        rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return f'<p class="slot-text">{html_escape(rendered)}</p>'


def render_list_item(item: Any) -> str:
    if isinstance(item, str):
        rendered = item
    else:
        rendered = json.dumps(item, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return f"<li>{html_escape(rendered)}</li>"


def render_value_html(value: Any) -> str:
    if isinstance(value, str) or value is None or isinstance(value, (bool, int, float)):
        return render_scalar_primitive(value)
    if isinstance(value, list):
        if all(isinstance(item, str) or item is None or isinstance(item, (bool, int, float)) for item in value):
            items = "".join(render_list_item(item) for item in value)
            return f'<ul class="slot-list">{items}</ul>'
        rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False)
        return f'<pre class="slot-json">{html_escape(rendered)}</pre>'
    if isinstance(value, dict):
        rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False)
        return f'<pre class="slot-json">{html_escape(rendered)}</pre>'

    rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    return f'<p class="slot-text">{html_escape(rendered)}</p>'


def render_cta_block(cta_payload: dict[str, Any], sticky: bool = False) -> str:
    block_class = "cta-block cta-block--sticky-mobile" if sticky else "cta-block"
    action_html = html_escape(cta_payload["action"])
    target_html = html_escape(cta_payload["target"])

    if cta_payload["action"] == "direct_whatsapp":
        target_markup = f'<a class="cta-block__target" href="{target_html}">{target_html}</a>'
    else:
        target_markup = f'<div class="cta-block__target cta-block__target--static">{target_html}</div>'

    return "\n".join(
        (
            f'<div class="{block_class}">',
            f'  <div class="cta-block__action">{action_html}</div>',
            f"  {target_markup}",
            "</div>",
        )
    )


def render_slot_html(slot: Any, cta_payload: dict[str, Any], tier: str, section_id: str, index: int) -> str:
    if not isinstance(slot, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}] must be an object")

    slot_id = slot.get("slot_id")
    status = slot.get("status")
    if not isinstance(slot_id, str) or not slot_id.strip():
        raise ValueError(
            f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].slot_id must be a non-empty string"
        )

    if status == "resolved":
        value = slot.get("value")
        fallback = slot.get("fallback")
        if slot_id == "primary_cta_ref":
            if value != "primary":
                raise ValueError(
                    f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}] primary_cta_ref must resolve to primary"
                )
            if fallback is not None:
                raise ValueError(
                    f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].fallback must be null for resolved slots"
                )
            return render_cta_block(cta_payload)
        if fallback is not None:
            raise ValueError(
                f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].fallback must be null for resolved slots"
            )
        return render_value_html(value)

    if status == "unresolved":
        value = slot.get("value")
        fallback = slot.get("fallback")
        if value is not None:
            raise ValueError(
                f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].value must be null for unresolved slots"
            )
        if not isinstance(fallback, str):
            raise ValueError(
                f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].fallback must be a string for unresolved slots"
            )
        return (
            f'<p class="slot-unresolved" data-slot-status="unresolved" '
            f'data-slot-id="{html_escape(slot_id)}">{html_escape(fallback)}</p>'
        )

    raise ValueError(
        f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots[{index}].status must be resolved or unresolved"
    )


def render_section_html(section_id: str, section_payload: Any, cta_payload: dict[str, Any], tier: str) -> str:
    if not isinstance(section_payload, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id} must be an object")

    render_status = section_payload.get("render_status")
    heading = section_payload.get("heading")
    slots = section_payload.get("slots")
    if render_status != "ready":
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.render_status must be ready")
    if not isinstance(heading, dict):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.heading must be an object")
    if not isinstance(slots, list):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots must be a list")

    heading_level = heading.get("level")
    heading_text = heading.get("text")
    if not isinstance(heading_level, str) or heading_level not in ALLOWED_HEADING_LEVELS:
        raise ValueError(
            f"render_output.render_artifact.{tier}.body.sections.{section_id}.heading.level must be one of {sorted(ALLOWED_HEADING_LEVELS)}"
        )
    if not isinstance(heading_text, str):
        raise ValueError(f"render_output.render_artifact.{tier}.body.sections.{section_id}.heading.text must be a string")

    modifier_class = f" landing-section--{section_id}" if section_id in KNOWN_SECTION_CLASSES else " landing-section--generic"
    slots_html = "\n".join(
        render_slot_html(slot, cta_payload, tier, section_id, index)
        for index, slot in enumerate(slots)
    )

    return "\n".join(
        (
            f'<section class="landing-section{modifier_class}" id="{html_escape(section_id)}">',
            '  <div class="landing-section__inner">',
            f'    <{heading_level} class="landing-section__heading">{html_escape(heading_text)}</{heading_level}>',
            f'    <div class="landing-section__content">{slots_html}</div>',
            "  </div>",
            "</section>",
        )
    )


def render_jsonld_scripts(head_jsonld: dict[str, Any]) -> str:
    scripts = []
    for payload in head_jsonld.values():
        scripts.append(f'<script type="application/ld+json">{safe_json_script(payload)}</script>')
    return "\n".join(scripts)


def build_render_context(case_id: str, tier: str, tier_payload: dict[str, Any]) -> dict[str, str]:
    _ = case_id
    validated_payload = validate_selected_tier_payload(tier_payload, tier)
    document = validated_payload["document"]
    head = validated_payload["head"]
    body = validated_payload["body"]
    cta = validated_payload["cta"]
    render_notes = validated_payload["render_notes"]

    cta_payload = validate_cta_payload(cta.get("primary"), tier)
    section_html = "\n".join(
        render_section_html(section_id, body["sections"][section_id], cta_payload, tier)
        for section_id in body["section_order"]
    )
    sticky_mobile_cta_html = ""
    if "sticky_mobile" in cta_payload["placements"]:
        sticky_mobile_cta_html = render_cta_block(cta_payload, sticky=True)

    return {
        "BODY_CLASS": html_escape(f"tier-{tier}"),
        "LANG": html_escape(document["lang"]),
        "DIR": html_escape(document["dir"]),
        "TITLE": html_escape(document["title"]),
        "META_DESCRIPTION": html_escape(document["meta_description"]),
        "JSONLD_SCRIPTS": render_jsonld_scripts(head["jsonld"]),
        "SECTIONS_HTML": section_html,
        "STICKY_MOBILE_CTA": sticky_mobile_cta_html,
        "RENDER_NOTES_JSON": safe_json_script(render_notes),
    }


def apply_template(template_html: str, context: dict[str, str]) -> str:
    missing_placeholders = [key for key in REQUIRED_PLACEHOLDERS if f"{{{{{key}}}}}" not in template_html]
    if missing_placeholders:
        raise ValueError(f"template is missing required placeholders: {', '.join(missing_placeholders)}")

    missing_context = [key for key in REQUIRED_PLACEHOLDERS if key not in context]
    if missing_context:
        raise ValueError(f"render context is missing required keys: {', '.join(missing_context)}")

    rendered = template_html
    for key in REQUIRED_PLACEHOLDERS:
        rendered = rendered.replace(f"{{{{{key}}}}}", context[key])

    remaining_tokens = PLACEHOLDER_RE.findall(rendered)
    if remaining_tokens:
        raise ValueError(f"template has unreplaced placeholder tokens: {', '.join(sorted(set(remaining_tokens)))}")

    return rendered


def write_atomically(final_path: Path, html_text: str) -> Path:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=final_path.parent,
            prefix=f".{final_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(html_text)
            temp_path = Path(handle.name)
        os.replace(temp_path, final_path)
        return final_path
    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
        raise


def cleanup_failure(created_dir: Path | None) -> None:
    if created_dir is not None and created_dir.exists():
        try:
            next(created_dir.iterdir())
        except StopIteration:
            created_dir.rmdir()


def main() -> int:
    args = parse_args()
    template_path = Path(__file__).resolve().parent / "templates" / "production_landing_v1.html"
    created_dir: Path | None = None

    try:
        bundle = load_and_validate_bundle(Path(args.bundle))
        case_id = bundle["case_id"]
        render_artifact = bundle["render_output"]["render_artifact"]
        if args.tier not in render_artifact:
            raise ValueError(f"requested tier {args.tier} is not present in render_output.render_artifact")

        template_html = load_template(template_path)
        context = build_render_context(case_id, args.tier, render_artifact[args.tier])
        page_html = apply_template(template_html, context)

        final_path = resolve_output_path(case_id, args.tier, args.out)
        parent_exists = final_path.parent.exists()
        if not parent_exists:
            final_path.parent.mkdir(parents=True, exist_ok=True)
            created_dir = final_path.parent

        written_path = write_atomically(final_path, page_html)
    except Exception as exc:  # pragma: no cover - CLI failure surface
        cleanup_failure(created_dir)
        print(str(exc), file=sys.stderr)
        return 1

    print(written_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
