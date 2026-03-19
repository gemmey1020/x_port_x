#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

SUPPORTED_TIERS = ("lite", "default", "premium")
SUPPORTED_TARGETS = ("LocalBusiness", "ProfessionalService")
REQUIRED_BRIEF_FIELDS = ("trade_type", "primary_locality", "service_scope", "whatsapp_target")
ALLOWED_BUNDLE_VERSIONS = ("1.1", "1.2", "1.3.1")
STAGE_ORDER = (
    ("portfolio-spectrum-builder", "portfolio", "portfolio_output", True),
    ("schema-mapper", "mapping", "schema_mapping_output", True),
    ("jsonld-generator", "jsonld", "jsonld_output", True),
    ("landing-generator", "landing", "landing_output", False),
    ("seo-artifact-generator", "seo", "seo_output", False),
    ("render-artifact-generator", "render", "render_output", False),
)
VERSION_STAGE_COUNTS = {
    "1.1": 4,
    "1.2": 5,
    "1.3.1": 6,
}
ALLOWED_BLOCK_SIGNALS = {"Ω_INSUFFICIENT_DATA"}
ASSET_GAP_TOKENS = ("gallery_assets", "video_asset_or_video_slot", "review_items")
LANDING_FIELD_ORDER = (
    "trade_type",
    "business_label",
    "primary_locality",
    "service_scope",
    "whatsapp_target",
    "differentiators",
    "trust_signals",
    "work_hours",
    "gallery_assets",
    "video_asset",
    "video_url",
    "review_items",
)
LANDING_NON_ASSET_INPUT_ORDER = ("business_label", "work_hours", "differentiators", "trust_signals")
SEO_FIELD_ORDER = (
    "trade_type",
    "business_label",
    "primary_locality",
    "service_scope",
    "whatsapp_target",
    "differentiators",
    "trust_signals",
    "work_hours",
)
SEO_UNRESOLVED_INPUT_ORDER = (
    "business_label",
    "trust_signals",
    "work_hours",
    "gallery_assets",
    "video_asset_or_video_slot",
    "review_items",
)
SEO_HEADING_TEXT = {
    "service-summary": "Services",
    "service-list": "Services",
    "trust-strip": "Trust signals",
    "hours": "Working hours",
    "whatsapp-cta": "Contact on WhatsApp",
    "footer-contact": "Area and contact",
    "gallery": "Previous work",
    "video-anchor": "Video",
    "reviews": "Reviews",
}
SEO_HEADING_ALIGNMENT_RULES = (
    "h1_maps_to_hero",
    "section_heading_order_matches_landing_section_order",
    "withheld_sections_keep_withheld_status",
    "headings_must_not_introduce_unproven_fields",
)
SEO_RENDER_REQUIREMENTS = (
    "apply_metadata_verbatim",
    "preserve_heading_section_alignment",
    "keep_locality_mentions_exact",
    "preserve_landing_cta_positions",
    "attach_existing_jsonld_verbatim",
)
SEO_VALIDATION_PRIORITIES = (
    "validate_metadata_presence",
    "validate_heading_section_alignment",
    "validate_locality_consistency",
    "validate_jsonld_linkage",
    "validate_gap_preservation",
)


def active_stage_specs(bundle_version: Any) -> tuple[tuple[str, str, str, bool], ...]:
    count = VERSION_STAGE_COUNTS.get(bundle_version)
    if count is None:
        return STAGE_ORDER
    return STAGE_ORDER[:count]


def load_document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Empty file: {path}")
    return yaml.safe_load(text)


def add_failure(failures: list[dict[str, Any]], code: str, message: str, path: str | None = None) -> None:
    item: dict[str, Any] = {"code": code, "message": message}
    if path:
        item["path"] = path
    failures.append(item)


def is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def is_usable_whatsapp_target(value: Any) -> bool:
    if not is_non_empty_str(value):
        return False
    value = value.strip()
    if re.fullmatch(r"\d{6,20}", value):
        return True
    return bool(re.fullmatch(r"https://wa\.me/\d{6,20}", value))


def requested_tiers(brief: dict[str, Any]) -> set[str]:
    requested_scope = brief.get("requested_scope")
    if requested_scope in (None, "", "all"):
        return set(SUPPORTED_TIERS)
    if requested_scope in SUPPORTED_TIERS:
        return {requested_scope}
    return set()


def first_service_item(brief: dict[str, Any]) -> str:
    service_scope = brief.get("service_scope")
    if not is_non_empty_list(service_scope):
        raise ValueError("trade_brief.service_scope must be a non-empty list")
    first_item = service_scope[0]
    if not is_non_empty_str(first_item):
        raise ValueError("trade_brief.service_scope[0] must be a non-empty string")
    return first_item


def service_list_sentence(brief: dict[str, Any]) -> str:
    service_scope = brief.get("service_scope")
    if not is_non_empty_list(service_scope):
        raise ValueError("trade_brief.service_scope must be a non-empty list")
    items = [item for item in service_scope[:3] if is_non_empty_str(item)]
    if not items:
        raise ValueError("trade_brief.service_scope must contain at least one non-empty string")
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{items[0]}, {items[1]}, and {items[2]}"


def build_seo_title(brief: dict[str, Any]) -> str:
    trade_type = brief.get("trade_type")
    primary_locality = brief.get("primary_locality")
    business_label = brief.get("business_label")
    if not is_non_empty_str(trade_type) or not is_non_empty_str(primary_locality):
        raise ValueError("trade_brief must contain trade_type and primary_locality")
    if is_non_empty_str(business_label):
        return f"{business_label} | {trade_type} in {primary_locality}"
    return f"{trade_type} in {primary_locality} | {first_service_item(brief)}"


def build_seo_h1(brief: dict[str, Any]) -> str:
    trade_type = brief.get("trade_type")
    primary_locality = brief.get("primary_locality")
    business_label = brief.get("business_label")
    if not is_non_empty_str(trade_type) or not is_non_empty_str(primary_locality):
        raise ValueError("trade_brief must contain trade_type and primary_locality")
    if is_non_empty_str(business_label):
        return f"{business_label} | {trade_type} in {primary_locality}"
    return f"{trade_type} in {primary_locality}"


def build_meta_description(brief: dict[str, Any]) -> str:
    trade_type = brief.get("trade_type")
    primary_locality = brief.get("primary_locality")
    business_label = brief.get("business_label")
    if not is_non_empty_str(trade_type) or not is_non_empty_str(primary_locality):
        raise ValueError("trade_brief must contain trade_type and primary_locality")
    services = service_list_sentence(brief)
    if is_non_empty_str(business_label):
        return f"{business_label}: {trade_type} in {primary_locality} for {services}. WhatsApp contact available."
    return f"{trade_type} in {primary_locality} for {services}. WhatsApp contact available."


def build_canonical_slug_hint(brief: dict[str, Any]) -> str:
    trade_type = brief.get("trade_type")
    primary_locality = brief.get("primary_locality")
    if not is_non_empty_str(trade_type) or not is_non_empty_str(primary_locality):
        raise ValueError("trade_brief must contain trade_type and primary_locality")
    raw = f"{trade_type}-{primary_locality}".strip().lower()
    ascii_text = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    normalized = ascii_text if ascii_text else raw
    normalized = normalized.replace("_", "-")
    normalized = re.sub(r"[^\w-]+", "-", normalized, flags=re.UNICODE)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    if not normalized:
        raise ValueError("canonical_slug_hint could not be derived from trade_type and primary_locality")
    return normalized


def tier_section_status(tier_payload: dict[str, Any], section_id: str) -> str:
    sections = tier_payload.get("sections")
    if not isinstance(sections, dict):
        raise ValueError("landing tier sections must be an object")
    section_payload = sections.get(section_id)
    if not isinstance(section_payload, dict):
        raise ValueError(f"landing section {section_id} must be an object")
    status = section_payload.get("render_status")
    if status not in {"ready", "withheld"}:
        raise ValueError(f"landing section {section_id} render_status must be ready or withheld")
    return status


def supported_targets_for_tier(mapping_tier: dict[str, Any], jsonld_tier: dict[str, Any]) -> list[str]:
    return [target for target in SUPPORTED_TARGETS if target in mapping_tier and target in jsonld_tier]


def critical_portfolio_violations(brief: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if not is_non_empty_str(brief.get("trade_type")):
        violations.append("trade_type")
    if not is_non_empty_str(brief.get("primary_locality")):
        violations.append("primary_locality")
    service_scope = brief.get("service_scope")
    if not is_non_empty_list(service_scope) or not all(is_non_empty_str(item) for item in service_scope):
        violations.append("service_scope")
    if not is_usable_whatsapp_target(brief.get("whatsapp_target")):
        violations.append("whatsapp_target")
    return violations


def required_mapping_fields_for_target(target: str, work_hours_present: bool, business_label_present: bool) -> set[str]:
    if target == "LocalBusiness":
        fields = {"areaServed", "makesOffer.itemOffered", "potentialAction.target"}
        if work_hours_present:
            fields.add("openingHours")
    else:
        fields = {"areaServed", "serviceType", "potentialAction.target"}
        if work_hours_present:
            fields.add("hoursAvailable")
    if business_label_present:
        fields.add("name")
    return fields


def mapping_row_map(entity_map: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["target_field"]: row for row in entity_map if isinstance(row, dict) and "target_field" in row}


def diff_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    if type(left) is not type(right):
        return [prefix or "$"]
    if isinstance(left, dict):
        paths: list[str] = []
        keys = set(left) | set(right)
        for key in sorted(keys):
            child = f"{prefix}.{key}" if prefix else key
            if key not in left or key not in right:
                paths.append(child)
                continue
            paths.extend(diff_paths(left[key], right[key], child))
        return paths
    if isinstance(left, list):
        paths: list[str] = []
        if len(left) != len(right):
            paths.append(prefix or "$")
            return paths
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            child = f"{prefix}[{index}]" if prefix else f"[{index}]"
            paths.extend(diff_paths(left_item, right_item, child))
        return paths
    if left != right:
        return [prefix or "$"]
    return []


def ordered_tiers(tiers: set[str] | list[str]) -> list[str]:
    tier_set = set(tiers)
    return [tier for tier in SUPPORTED_TIERS if tier in tier_set]


def resolved_slot(slot_id: str, value: Any, stage: str, field: str) -> dict[str, Any]:
    return {
        "slot_id": slot_id,
        "status": "resolved",
        "value": value,
        "source": {
            "stage": stage,
            "field": field,
        },
    }


def unresolved_slot(slot_id: str, required_input: str) -> dict[str, Any]:
    return {
        "slot_id": slot_id,
        "status": "unresolved",
        "required_input": required_input,
    }


def section_slot_map(section_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slots = section_payload.get("slots")
    if not isinstance(slots, list):
        return {}
    return {
        slot["slot_id"]: slot
        for slot in slots
        if isinstance(slot, dict) and is_non_empty_str(slot.get("slot_id"))
    }


def ordered_section_slots(section_payload: dict[str, Any], section_path: str) -> list[dict[str, Any]]:
    slot_order = section_payload.get("slot_order")
    slots = section_payload.get("slots")
    if not isinstance(slot_order, list):
        raise ValueError(f"{section_path}.slot_order must be a list")
    if not isinstance(slots, list):
        raise ValueError(f"{section_path}.slots must be a list")

    slot_map: dict[str, dict[str, Any]] = {}
    for index, slot in enumerate(slots):
        if not isinstance(slot, dict):
            raise ValueError(f"{section_path}.slots[{index}] must be an object")
        slot_id = slot.get("slot_id")
        if not is_non_empty_str(slot_id):
            raise ValueError(f"{section_path}.slots[{index}].slot_id must be a non-empty string")
        if slot_id in slot_map:
            raise ValueError(f"{section_path}.slots contains duplicate slot_id {slot_id}")
        slot_map[slot_id] = slot

    ordered_slots: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, slot_id in enumerate(slot_order):
        if not is_non_empty_str(slot_id):
            raise ValueError(f"{section_path}.slot_order[{index}] must be a non-empty string")
        if slot_id in seen:
            raise ValueError(f"{section_path}.slot_order contains duplicate slot_id {slot_id}")
        if slot_id not in slot_map:
            raise ValueError(f"{section_path}.slot_order references missing slot_id {slot_id}")
        seen.add(slot_id)
        ordered_slots.append(slot_map[slot_id])

    extra_slot_ids = [slot_id for slot_id in slot_map if slot_id not in seen]
    if extra_slot_ids:
        raise ValueError(f"{section_path}.slots contains slot_ids not listed in slot_order: {sorted(extra_slot_ids)}")
    return ordered_slots


def expected_render_cta(landing_cta_primary: dict[str, Any], tier_path: str) -> dict[str, Any]:
    action = landing_cta_primary.get("action")
    target = landing_cta_primary.get("target")
    placements = landing_cta_primary.get("placements")
    if not is_non_empty_str(action):
        raise ValueError(f"{tier_path}.cta.primary.action must be a non-empty string")
    if not is_non_empty_str(target):
        raise ValueError(f"{tier_path}.cta.primary.target must be a non-empty string")
    if not isinstance(placements, list):
        raise ValueError(f"{tier_path}.cta.primary.placements must be a list")
    return {
        "action": action,
        "target": target,
        "placements": list(placements),
    }


def build_expected_section(section_id: str, brief: dict[str, Any]) -> dict[str, Any]:
    service_scope = brief.get("service_scope")
    service_items = service_scope if isinstance(service_scope, list) else []
    trust_signals = brief.get("trust_signals")
    trust_items = trust_signals if isinstance(trust_signals, list) else []
    differentiators = brief.get("differentiators")
    differentiator_items = differentiators if isinstance(differentiators, list) else []
    review_items = brief.get("review_items")
    reviews = review_items if isinstance(review_items, list) else []
    gallery_assets = brief.get("gallery_assets")
    gallery_items = gallery_assets if isinstance(gallery_assets, list) else []
    work_hours = brief.get("work_hours")
    business_label = brief.get("business_label")
    video_asset = brief.get("video_asset")
    video_url = brief.get("video_url")

    if section_id == "hero":
        slots = [
            resolved_slot("trade_type", brief.get("trade_type"), "trade_brief", "trade_type"),
            resolved_slot("business_label", business_label, "trade_brief", "business_label")
            if is_non_empty_str(business_label)
            else unresolved_slot("business_label", "business_label"),
            resolved_slot("primary_locality", brief.get("primary_locality"), "trade_brief", "primary_locality"),
            resolved_slot("primary_cta_ref", "primary", "landing_artifact", "cta.primary"),
        ]
        render_status = "ready" if is_non_empty_str(brief.get("trade_type")) and is_non_empty_str(brief.get("primary_locality")) and is_usable_whatsapp_target(brief.get("whatsapp_target")) else "withheld"
        return {
            "render_status": render_status,
            "slot_order": ["trade_type", "business_label", "primary_locality", "primary_cta_ref"],
            "slots": slots,
        }

    if section_id == "service-summary":
        service_preview = service_items[:3]
        slot = (
            resolved_slot("service_scope_preview", service_preview, "trade_brief", "service_scope")
            if service_preview
            else unresolved_slot("service_scope_preview", "service_scope")
        )
        return {
            "render_status": "ready" if service_preview else "withheld",
            "slot_order": ["service_scope_preview"],
            "slots": [slot],
        }

    if section_id == "service-list":
        slot = (
            resolved_slot("service_items", service_items, "trade_brief", "service_scope")
            if service_items
            else unresolved_slot("service_items", "service_scope")
        )
        return {
            "render_status": "ready" if service_items else "withheld",
            "slot_order": ["service_items"],
            "slots": [slot],
        }

    if section_id == "trust-strip":
        trust_slot = (
            resolved_slot("trust_signals", trust_items, "trade_brief", "trust_signals")
            if trust_items
            else unresolved_slot("trust_signals", "trust_signals")
        )
        differentiator_slot = (
            resolved_slot("differentiators", differentiator_items, "trade_brief", "differentiators")
            if differentiator_items
            else unresolved_slot("differentiators", "differentiators")
        )
        render_status = "ready" if trust_items or differentiator_items else "withheld"
        return {
            "render_status": render_status,
            "slot_order": ["trust_signals", "differentiators"],
            "slots": [trust_slot, differentiator_slot],
        }

    if section_id == "hours":
        slot = (
            resolved_slot("work_hours", work_hours, "trade_brief", "work_hours")
            if is_non_empty_str(work_hours)
            else unresolved_slot("work_hours", "work_hours")
        )
        return {
            "render_status": "ready" if is_non_empty_str(work_hours) else "withheld",
            "slot_order": ["work_hours"],
            "slots": [slot],
        }

    if section_id == "whatsapp-cta":
        return {
            "render_status": "ready" if is_usable_whatsapp_target(brief.get("whatsapp_target")) else "withheld",
            "slot_order": ["primary_cta_ref"],
            "slots": [resolved_slot("primary_cta_ref", "primary", "landing_artifact", "cta.primary")],
        }

    if section_id == "footer-contact":
        return {
            "render_status": "ready" if is_usable_whatsapp_target(brief.get("whatsapp_target")) else "withheld",
            "slot_order": ["primary_cta_ref", "primary_locality"],
            "slots": [
                resolved_slot("primary_cta_ref", "primary", "landing_artifact", "cta.primary"),
                resolved_slot("primary_locality", brief.get("primary_locality"), "trade_brief", "primary_locality"),
            ],
        }

    if section_id == "gallery":
        slot = (
            resolved_slot("gallery_assets", gallery_items, "trade_brief", "gallery_assets")
            if gallery_items
            else unresolved_slot("gallery_assets", "gallery_assets")
        )
        return {
            "render_status": "ready" if gallery_items else "withheld",
            "slot_order": ["gallery_assets"],
            "slots": [slot],
        }

    if section_id == "video-anchor":
        if is_non_empty_str(video_asset):
            slot = resolved_slot("video_asset", video_asset, "trade_brief", "video_asset")
            render_status = "ready"
        elif is_non_empty_str(video_url):
            slot = resolved_slot("video_asset", video_url, "trade_brief", "video_url")
            render_status = "ready"
        else:
            slot = unresolved_slot("video_asset", "video_asset_or_video_slot")
            render_status = "withheld"
        return {
            "render_status": render_status,
            "slot_order": ["video_asset"],
            "slots": [slot],
        }

    if section_id == "reviews":
        slot = (
            resolved_slot("review_items", reviews, "trade_brief", "review_items")
            if reviews
            else unresolved_slot("review_items", "review_items")
        )
        return {
            "render_status": "ready" if reviews else "withheld",
            "slot_order": ["review_items"],
            "slots": [slot],
        }

    raise ValueError(f"Unsupported landing section {section_id}")


def build_expected_landing_output(
    brief: dict[str, Any],
    portfolio_output: dict[str, Any],
    schema_mapping_output: dict[str, Any],
    jsonld_output: dict[str, Any],
) -> dict[str, Any]:
    portfolio_spectrum = portfolio_output.get("portfolio_spectrum")
    if not isinstance(portfolio_spectrum, dict) or not portfolio_spectrum:
        raise ValueError("portfolio_output.portfolio_spectrum must be a non-empty object")

    schema_mapping = schema_mapping_output.get("schema_mapping")
    if not isinstance(schema_mapping, dict) or not schema_mapping:
        raise ValueError("schema_mapping_output.schema_mapping must be a non-empty object")

    jsonld_payloads = jsonld_output.get("jsonld_payloads")
    if not isinstance(jsonld_payloads, dict) or not jsonld_payloads:
        raise ValueError("jsonld_output.jsonld_payloads must be a non-empty object")

    missing_inputs = portfolio_output.get("missing_inputs")
    if not isinstance(missing_inputs, list):
        raise ValueError("portfolio_output.missing_inputs must be a list")

    portfolio_handoff = portfolio_output.get("implementation_handoff")
    if not isinstance(portfolio_handoff, dict):
        raise ValueError("portfolio_output.implementation_handoff must be an object")
    content_gaps = portfolio_handoff.get("content_gaps")
    if not isinstance(content_gaps, list):
        raise ValueError("portfolio_output.implementation_handoff.content_gaps must be a list")

    schema_missing = schema_mapping_output.get("missing_required_fields")
    jsonld_missing = jsonld_output.get("missing_required_fields")
    if not isinstance(schema_missing, list):
        raise ValueError("schema_mapping_output.missing_required_fields must be a list")
    if not isinstance(jsonld_missing, list):
        raise ValueError("jsonld_output.missing_required_fields must be a list")

    jsonld_handoff = jsonld_output.get("implementation_handoff")
    if not isinstance(jsonld_handoff, dict):
        raise ValueError("jsonld_output.implementation_handoff must be an object")
    jsonld_unresolved = jsonld_handoff.get("unresolved_inputs")
    if not isinstance(jsonld_unresolved, list):
        raise ValueError("jsonld_output.implementation_handoff.unresolved_inputs must be a list")

    landing_artifact: dict[str, Any] = {}
    used_fields: set[str] = set()
    unresolved_inputs_seen: list[str] = []
    content_gaps_seen: list[str] = []
    render_ready_tiers: list[str] = []

    for tier in ordered_tiers(list(portfolio_spectrum.keys())):
        tier_portfolio = portfolio_spectrum.get(tier)
        if not isinstance(tier_portfolio, dict):
            raise ValueError(f"portfolio_output.portfolio_spectrum.{tier} must be an object")
        if tier not in schema_mapping:
            raise ValueError(f"schema_mapping_output.schema_mapping.{tier} must exist")
        tier_jsonld = jsonld_payloads.get(tier)
        if not isinstance(tier_jsonld, dict) or not tier_jsonld:
            raise ValueError(f"jsonld_output.jsonld_payloads.{tier} must be a non-empty object")

        sections = tier_portfolio.get("sections")
        if not is_non_empty_list(sections):
            raise ValueError(f"portfolio_output.portfolio_spectrum.{tier}.sections must be a non-empty list")

        cta_model = tier_portfolio.get("cta_model")
        if not isinstance(cta_model, dict):
            raise ValueError(f"portfolio_output.portfolio_spectrum.{tier}.cta_model must be an object")
        if cta_model.get("primary") != "direct_whatsapp":
            raise ValueError(f"portfolio_output.portfolio_spectrum.{tier}.cta_model.primary must be direct_whatsapp")
        placements = cta_model.get("placements")
        if not isinstance(placements, list):
            raise ValueError(f"portfolio_output.portfolio_spectrum.{tier}.cta_model.placements must be a list")

        planned_section_order = list(sections)
        renderable_section_order: list[str] = []
        tier_sections: dict[str, Any] = {}

        for section_id in planned_section_order:
            section_payload = build_expected_section(section_id, brief)
            tier_sections[section_id] = section_payload
            if section_payload["render_status"] == "ready":
                renderable_section_order.append(section_id)

            for slot in section_payload["slots"]:
                if slot.get("status") == "resolved":
                    source = slot.get("source")
                    if isinstance(source, dict) and source.get("stage") == "trade_brief" and is_non_empty_str(source.get("field")):
                        used_fields.add(source["field"])
                elif slot.get("status") == "unresolved":
                    required_input = slot.get("required_input")
                    if required_input in ASSET_GAP_TOKENS:
                        content_gaps_seen.append(required_input)
                    elif is_non_empty_str(required_input):
                        unresolved_inputs_seen.append(required_input)

        used_fields.add("whatsapp_target")
        if renderable_section_order:
            render_ready_tiers.append(tier)

        landing_artifact[tier] = {
            "rendering_handoff": {
                "locale": "ar-EG",
                "direction": "rtl",
                "mobile_first": True,
                "renderer_mode": "structured_slots_only",
                "planned_section_order": planned_section_order,
                "renderable_section_order": renderable_section_order,
            },
            "cta": {
                "primary": {
                    "cta_id": "primary",
                    "action": "direct_whatsapp",
                    "target": brief.get("whatsapp_target"),
                    "placements": placements,
                }
            },
            "structured_data": {
                "page_level_jsonld": tier_jsonld,
            },
            "sections": tier_sections,
        }

    landing_fields = [field for field in LANDING_FIELD_ORDER if field in used_fields]
    missing_required_fields = dedupe_preserve(list(schema_missing) + list(jsonld_missing))
    normalized_content_gaps = dedupe_preserve(list(content_gaps) + [gap for gap in ASSET_GAP_TOKENS if gap in content_gaps_seen])
    normalized_unresolved_inputs = dedupe_preserve(
        list(jsonld_unresolved) + [field for field in LANDING_NON_ASSET_INPUT_ORDER if field in unresolved_inputs_seen]
    )

    return {
        "landing_artifact": landing_artifact,
        "missing_inputs": list(missing_inputs),
        "missing_required_fields": missing_required_fields,
        "source_evidence": {
            "landing_fields": landing_fields,
        },
        "implementation_handoff": {
            "render_ready_tiers": render_ready_tiers,
            "content_gaps": normalized_content_gaps,
            "unresolved_inputs": normalized_unresolved_inputs,
        },
    }


def build_expected_seo_output(
    brief: dict[str, Any],
    portfolio_output: dict[str, Any],
    schema_mapping_output: dict[str, Any],
    jsonld_output: dict[str, Any],
    landing_output: dict[str, Any],
) -> dict[str, Any]:
    portfolio_spectrum = portfolio_output.get("portfolio_spectrum")
    schema_mapping = schema_mapping_output.get("schema_mapping")
    jsonld_payloads = jsonld_output.get("jsonld_payloads")
    landing_artifact = landing_output.get("landing_artifact")
    if not isinstance(portfolio_spectrum, dict) or not portfolio_spectrum:
        raise ValueError("portfolio_output.portfolio_spectrum must be a non-empty object")
    if not isinstance(schema_mapping, dict) or not schema_mapping:
        raise ValueError("schema_mapping_output.schema_mapping must be a non-empty object")
    if not isinstance(jsonld_payloads, dict) or not jsonld_payloads:
        raise ValueError("jsonld_output.jsonld_payloads must be a non-empty object")
    if not isinstance(landing_artifact, dict) or not landing_artifact:
        raise ValueError("landing_output.landing_artifact must be a non-empty object")

    portfolio_tiers = set(portfolio_spectrum.keys())
    schema_tiers = set(schema_mapping.keys())
    jsonld_tiers = set(jsonld_payloads.keys())
    landing_tiers = set(landing_artifact.keys())
    if not portfolio_tiers or portfolio_tiers != schema_tiers or schema_tiers != jsonld_tiers or jsonld_tiers != landing_tiers:
        raise ValueError("portfolio, schema_mapping, jsonld, and landing tiers must align exactly")

    business_label_present = is_non_empty_str(brief.get("business_label"))
    trust_signals_present = is_non_empty_list(brief.get("trust_signals"))
    differentiators_present = is_non_empty_list(brief.get("differentiators"))
    work_hours_present = is_non_empty_str(brief.get("work_hours"))
    primary_locality = brief.get("primary_locality")
    if not is_non_empty_str(primary_locality):
        raise ValueError("trade_brief.primary_locality must be a non-empty string")

    used_trade_fields = {"trade_type", "primary_locality", "service_scope", "whatsapp_target"}
    if business_label_present:
        used_trade_fields.add("business_label")
    landing_sections_seen: list[str] = []
    entity_targets_seen: list[str] = []
    unresolved_inputs_seen: list[str] = []
    seo_artifact: dict[str, Any] = {}

    for tier in ordered_tiers(list(landing_artifact.keys())):
        tier_landing = landing_artifact.get(tier)
        tier_portfolio = portfolio_spectrum.get(tier)
        tier_mapping = schema_mapping.get(tier)
        tier_jsonld = jsonld_payloads.get(tier)
        if not isinstance(tier_landing, dict):
            raise ValueError(f"landing_output.landing_artifact.{tier} must be an object")
        if not isinstance(tier_portfolio, dict):
            raise ValueError(f"portfolio_output.portfolio_spectrum.{tier} must be an object")
        if not isinstance(tier_mapping, dict) or not tier_mapping:
            raise ValueError(f"schema_mapping_output.schema_mapping.{tier} must be a non-empty object")
        if not isinstance(tier_jsonld, dict) or not tier_jsonld:
            raise ValueError(f"jsonld_output.jsonld_payloads.{tier} must be a non-empty object")

        rendering_handoff = tier_landing.get("rendering_handoff")
        if not isinstance(rendering_handoff, dict):
            raise ValueError(f"landing_output.landing_artifact.{tier}.rendering_handoff must be an object")
        planned_section_order = rendering_handoff.get("planned_section_order")
        if not is_non_empty_list(planned_section_order):
            raise ValueError(f"landing_output.landing_artifact.{tier}.rendering_handoff.planned_section_order must be a non-empty list")

        landing_sections_seen.extend([section for section in planned_section_order if section not in landing_sections_seen])

        service_section = "service-summary" if "service-summary" in planned_section_order else "service-list" if "service-list" in planned_section_order else None
        if service_section is None:
            raise ValueError(f"landing_output.landing_artifact.{tier} must include service-summary or service-list")

        hero_ready = tier_section_status(tier_landing, "hero") == "ready"
        service_ready = tier_section_status(tier_landing, service_section) == "ready"
        whatsapp_ready = tier_section_status(tier_landing, "whatsapp-cta") == "ready"
        if not (hero_ready and service_ready and whatsapp_ready):
            raise ValueError(f"{tier} SEO artifact requires hero, {service_section}, and whatsapp-cta to be ready")

        if "trust-strip" in planned_section_order:
            if trust_signals_present:
                used_trade_fields.add("trust_signals")
            if differentiators_present:
                used_trade_fields.add("differentiators")
        if "hours" in planned_section_order and work_hours_present:
            used_trade_fields.add("work_hours")

        for target in supported_targets_for_tier(tier_mapping, tier_jsonld):
            if target not in entity_targets_seen:
                entity_targets_seen.append(target)

        landing_jsonld = tier_landing.get("structured_data", {}).get("page_level_jsonld")
        if landing_jsonld != tier_jsonld:
            raise ValueError(f"landing_output.landing_artifact.{tier}.structured_data.page_level_jsonld must match jsonld_output.jsonld_payloads.{tier}")
        entity_targets = supported_targets_for_tier(tier_mapping, tier_jsonld)
        if not entity_targets:
            raise ValueError(f"{tier} must include at least one supported entity target")

        locality_values: list[str] = [primary_locality]
        for target in entity_targets:
            mapping_target = tier_mapping.get(target)
            if not isinstance(mapping_target, dict):
                raise ValueError(f"schema_mapping_output.schema_mapping.{tier}.{target} must be an object")
            entity_map = mapping_target.get("entity_map")
            if not isinstance(entity_map, list):
                raise ValueError(f"schema_mapping_output.schema_mapping.{tier}.{target}.entity_map must be a list")
            row_map = mapping_row_map(entity_map)
            area_served = row_map.get("areaServed", {}).get("resolved_value")
            if not is_non_empty_str(area_served):
                raise ValueError(f"schema_mapping_output.schema_mapping.{tier}.{target}.areaServed resolved_value is required")
            locality_values.append(area_served)

            jsonld_target = tier_jsonld.get(target)
            if not isinstance(jsonld_target, dict):
                raise ValueError(f"jsonld_output.jsonld_payloads.{tier}.{target} must be an object")
            jsonld_area_served = jsonld_target.get("areaServed")
            if not is_non_empty_str(jsonld_area_served):
                raise ValueError(f"jsonld_output.jsonld_payloads.{tier}.{target}.areaServed is required")
            locality_values.append(jsonld_area_served)

        landing_sections = tier_landing.get("sections")
        if not isinstance(landing_sections, dict):
            raise ValueError(f"landing_output.landing_artifact.{tier}.sections must be an object")
        for section_id in ("hero", "footer-contact"):
            section_payload = landing_sections.get(section_id)
            if not isinstance(section_payload, dict):
                continue
            locality_slot = section_slot_map(section_payload).get("primary_locality")
            if isinstance(locality_slot, dict) and locality_slot.get("status") == "resolved":
                locality_value = locality_slot.get("value")
                if is_non_empty_str(locality_value):
                    locality_values.append(locality_value)

        if any(value != primary_locality for value in locality_values):
            raise ValueError(f"{tier} locality values must remain exactly aligned to trade_brief.primary_locality")

        secondary_intents: list[str] = ["service_scope_review"]
        if "trust-strip" in planned_section_order and tier_section_status(tier_landing, "trust-strip") == "ready":
            secondary_intents.append("trust_review")
        if "hours" in planned_section_order and tier_section_status(tier_landing, "hours") == "ready":
            secondary_intents.append("hours_check")
        if (
            ("footer-contact" in planned_section_order and tier_section_status(tier_landing, "footer-contact") == "ready")
            or hero_ready
        ):
            secondary_intents.append("location_confirmation")

        section_headings: list[dict[str, Any]] = []
        for section_id in planned_section_order:
            status = tier_section_status(tier_landing, section_id)
            if section_id == "hero":
                text = build_seo_h1(brief)
                level = "h1"
            else:
                if section_id not in SEO_HEADING_TEXT:
                    raise ValueError(f"Unsupported SEO heading section {section_id}")
                text = SEO_HEADING_TEXT[section_id]
                level = "h2"
            section_headings.append(
                {
                    "section": section_id,
                    "status": status,
                    "level": level,
                    "text": text,
                }
            )

        missing_identity_fields = ["business_label"] if not business_label_present else []
        missing_trust_signals = ["trust_signals"] if "trust-strip" in planned_section_order and not trust_signals_present else []
        missing_supporting_assets: list[str] = []
        if "gallery" in planned_section_order and tier_section_status(tier_landing, "gallery") == "withheld":
            missing_supporting_assets.append("gallery_assets")
        if "video-anchor" in planned_section_order and tier_section_status(tier_landing, "video-anchor") == "withheld":
            missing_supporting_assets.append("video_asset_or_video_slot")
        if "reviews" in planned_section_order and tier_section_status(tier_landing, "reviews") == "withheld":
            missing_supporting_assets.append("review_items")

        identity_gap = bool(missing_identity_fields)
        trust_gap = bool(missing_trust_signals)
        hours_gap = "hours" in planned_section_order and tier_section_status(tier_landing, "hours") == "withheld"
        supporting_assets_gap = bool(missing_supporting_assets)

        thin_content_reasons: list[str] = []
        if identity_gap:
            thin_content_reasons.append("missing_business_label")
            unresolved_inputs_seen.append("business_label")
        if trust_gap:
            thin_content_reasons.append("missing_trust_signals")
            unresolved_inputs_seen.append("trust_signals")
        if hours_gap:
            thin_content_reasons.append("missing_work_hours")
            unresolved_inputs_seen.append("work_hours")
        if supporting_assets_gap:
            thin_content_reasons.append("missing_supporting_assets")
            unresolved_inputs_seen.extend(missing_supporting_assets)

        if not thin_content_reasons:
            thin_content_level = "low"
        elif identity_gap and trust_gap and supporting_assets_gap:
            thin_content_level = "high"
        else:
            thin_content_level = "medium"

        seo_artifact[tier] = {
            "metadata": {
                "title": build_seo_title(brief),
                "meta_description": build_meta_description(brief),
                "canonical_slug_hint": build_canonical_slug_hint(brief),
            },
            "intent_model": {
                "primary_intent": "local_service_contact",
                "secondary_intents": secondary_intents,
                "intent_confidence": "high"
                if (hero_ready and service_ready and whatsapp_ready and (
                    ("trust-strip" in planned_section_order and tier_section_status(tier_landing, "trust-strip") == "ready")
                    or ("hours" in planned_section_order and tier_section_status(tier_landing, "hours") == "ready")
                ))
                else "medium",
            },
            "heading_plan": {
                "h1": build_seo_h1(brief),
                "section_headings": section_headings,
                "heading_alignment_rules": list(SEO_HEADING_ALIGNMENT_RULES),
            },
            "local_seo": {
                "primary_locality": primary_locality,
                "service_area_focus": {
                    "mode": "single_locality",
                    "localities": [primary_locality],
                },
                "locality_placement_rules": {
                    "required_fields": ["metadata.title", "metadata.meta_description", "heading_plan.h1"],
                    "supporting_sections": [section for section in ("hero", "footer-contact") if section in planned_section_order],
                    "expansion_mode": "exact_primary_locality_only",
                },
                "locality_confidence": "exact",
            },
            "structured_search_support": {
                "jsonld_status": "attached",
                "entity_targets": entity_targets,
            },
            "seo_gaps": {
                "missing_identity_fields": missing_identity_fields,
                "missing_trust_signals": missing_trust_signals,
                "missing_supporting_assets": missing_supporting_assets,
                "ambiguous_targeting": {
                    "status": "clear",
                    "reasons": [],
                },
                "thin_content_risk": {
                    "level": thin_content_level,
                    "reasons": thin_content_reasons,
                },
            },
        }

    unresolved_inputs = [field for field in SEO_UNRESOLVED_INPUT_ORDER if field in dedupe_preserve(unresolved_inputs_seen)]
    trade_brief_fields = [field for field in SEO_FIELD_ORDER if field in used_trade_fields]

    return {
        "seo_artifact": seo_artifact,
        "source_evidence": {
            "trade_brief_fields": trade_brief_fields,
            "landing_sections": landing_sections_seen,
            "entity_targets": entity_targets_seen,
        },
        "implementation_handoff": {
            "render_requirements": list(SEO_RENDER_REQUIREMENTS),
            "unresolved_inputs": unresolved_inputs,
            "validation_priorities": list(SEO_VALIDATION_PRIORITIES),
        },
    }


def build_expected_render_output(
    landing_output: dict[str, Any],
    seo_output: dict[str, Any],
    jsonld_output: dict[str, Any],
) -> dict[str, Any]:
    landing_artifact = landing_output.get("landing_artifact")
    seo_artifact = seo_output.get("seo_artifact")
    jsonld_payloads = jsonld_output.get("jsonld_payloads")
    if not isinstance(landing_artifact, dict) or not landing_artifact:
        raise ValueError("landing_output.landing_artifact must be a non-empty object")
    if not isinstance(seo_artifact, dict) or not seo_artifact:
        raise ValueError("seo_output.seo_artifact must be a non-empty object")
    if not isinstance(jsonld_payloads, dict) or not jsonld_payloads:
        raise ValueError("jsonld_output.jsonld_payloads must be a non-empty object")

    landing_tiers = set(landing_artifact.keys())
    seo_tiers = set(seo_artifact.keys())
    jsonld_tiers = set(jsonld_payloads.keys())
    if not landing_tiers or landing_tiers != seo_tiers or seo_tiers != jsonld_tiers:
        raise ValueError("landing, seo, and jsonld tiers must align exactly")

    render_artifact: dict[str, Any] = {}
    for tier in ordered_tiers(list(landing_artifact.keys())):
        tier_landing = landing_artifact.get(tier)
        tier_seo = seo_artifact.get(tier)
        tier_jsonld = jsonld_payloads.get(tier)
        tier_path = f"render_output.render_artifact.{tier}"
        if not isinstance(tier_landing, dict):
            raise ValueError(f"landing_output.landing_artifact.{tier} must be an object")
        if not isinstance(tier_seo, dict):
            raise ValueError(f"seo_output.seo_artifact.{tier} must be an object")
        if not isinstance(tier_jsonld, dict) or not tier_jsonld:
            raise ValueError(f"jsonld_output.jsonld_payloads.{tier} must be a non-empty object")

        rendering_handoff = tier_landing.get("rendering_handoff")
        if not isinstance(rendering_handoff, dict):
            raise ValueError(f"landing_output.landing_artifact.{tier}.rendering_handoff must be an object")
        planned_section_order = rendering_handoff.get("planned_section_order")
        renderable_section_order = rendering_handoff.get("renderable_section_order")
        if not isinstance(planned_section_order, list):
            raise ValueError(f"landing_output.landing_artifact.{tier}.rendering_handoff.planned_section_order must be a list")
        if not isinstance(renderable_section_order, list):
            raise ValueError(f"landing_output.landing_artifact.{tier}.rendering_handoff.renderable_section_order must be a list")

        tier_sections = tier_landing.get("sections")
        if not isinstance(tier_sections, dict):
            raise ValueError(f"landing_output.landing_artifact.{tier}.sections must be an object")

        section_headings = tier_seo.get("heading_plan", {}).get("section_headings")
        if not isinstance(section_headings, list):
            raise ValueError(f"seo_output.seo_artifact.{tier}.heading_plan.section_headings must be a list")

        cta_primary = tier_landing.get("cta", {}).get("primary")
        if not isinstance(cta_primary, dict):
            raise ValueError(f"landing_output.landing_artifact.{tier}.cta.primary must be an object")

        body_sections: dict[str, Any] = {}
        unresolved_slot_tokens: list[str] = []
        required_inputs: list[str] = []
        withheld_sections: list[str] = []

        for section_id in planned_section_order:
            section_payload = tier_sections.get(section_id)
            if not isinstance(section_payload, dict):
                raise ValueError(f"landing_output.landing_artifact.{tier}.sections.{section_id} must be an object")
            render_status = section_payload.get("render_status")
            if render_status not in {"ready", "withheld"}:
                raise ValueError(f"landing_output.landing_artifact.{tier}.sections.{section_id}.render_status must be ready or withheld")
            if render_status == "withheld":
                withheld_sections.append(section_id)

        for section_id in renderable_section_order:
            if section_id not in tier_sections:
                raise ValueError(f"landing_output.landing_artifact.{tier}.sections must contain renderable section {section_id}")
            section_payload = tier_sections[section_id]
            if section_payload.get("render_status") != "ready":
                raise ValueError(f"landing_output.landing_artifact.{tier}.sections.{section_id}.render_status must be ready")

            heading_rows = [
                row for row in section_headings
                if isinstance(row, dict) and row.get("section") == section_id
            ]
            if len(heading_rows) != 1:
                raise ValueError(f"seo_output.seo_artifact.{tier}.heading_plan.section_headings must contain exactly one row for {section_id}")
            heading_row = heading_rows[0]
            if heading_row.get("status") != "ready":
                raise ValueError(f"seo_output.seo_artifact.{tier}.heading_plan.section_headings row for {section_id} must be ready")
            if not is_non_empty_str(heading_row.get("level")):
                raise ValueError(f"seo_output.seo_artifact.{tier}.heading_plan.section_headings row for {section_id} must contain level")
            if not is_non_empty_str(heading_row.get("text")):
                raise ValueError(f"seo_output.seo_artifact.{tier}.heading_plan.section_headings row for {section_id} must contain text")

            rendered_slots: list[dict[str, Any]] = []
            for slot in ordered_section_slots(section_payload, f"landing_output.landing_artifact.{tier}.sections.{section_id}"):
                slot_id = slot["slot_id"]
                status = slot.get("status")
                if status == "resolved":
                    rendered_slots.append(
                        {
                            "slot_id": slot_id,
                            "status": "resolved",
                            "value": slot.get("value"),
                            "fallback": None,
                        }
                    )
                elif status == "unresolved":
                    fallback = slot.get("required_input")
                    if not is_non_empty_str(fallback):
                        raise ValueError(f"landing_output.landing_artifact.{tier}.sections.{section_id}.slots.{slot_id} unresolved slot must contain required_input")
                    rendered_slots.append(
                        {
                            "slot_id": slot_id,
                            "status": "unresolved",
                            "value": None,
                            "fallback": fallback,
                        }
                    )
                    unresolved_slot_tokens.append(f"{section_id}.{slot_id}")
                    if fallback not in required_inputs:
                        required_inputs.append(fallback)
                else:
                    raise ValueError(f"landing_output.landing_artifact.{tier}.sections.{section_id}.slots.{slot_id} must use resolved or unresolved status")

            body_sections[section_id] = {
                "render_status": "ready",
                "heading": {
                    "level": heading_row["level"],
                    "text": heading_row["text"],
                },
                "slots": rendered_slots,
            }

        for section_id in planned_section_order:
            if section_id in renderable_section_order:
                continue
            section_payload = tier_sections.get(section_id)
            if not isinstance(section_payload, dict):
                raise ValueError(f"landing_output.landing_artifact.{tier}.sections.{section_id} must be an object")
            if section_payload.get("render_status") != "withheld":
                continue
            for slot in ordered_section_slots(section_payload, f"landing_output.landing_artifact.{tier}.sections.{section_id}"):
                if slot.get("status") != "unresolved":
                    continue
                fallback = slot.get("required_input")
                if not is_non_empty_str(fallback):
                    raise ValueError(f"landing_output.landing_artifact.{tier}.sections.{section_id}.slots.{slot.get('slot_id')} unresolved slot must contain required_input")
                if fallback not in required_inputs:
                    required_inputs.append(fallback)

        render_artifact[tier] = {
            "document": {
                "lang": rendering_handoff.get("locale"),
                "dir": rendering_handoff.get("direction"),
                "title": tier_seo.get("metadata", {}).get("title"),
                "meta_description": tier_seo.get("metadata", {}).get("meta_description"),
            },
            "head": {
                "jsonld": tier_jsonld,
            },
            "body": {
                "section_order": list(renderable_section_order),
                "sections": body_sections,
            },
            "cta": {
                "primary": expected_render_cta(cta_primary, f"landing_output.landing_artifact.{tier}"),
            },
            "render_notes": {
                "withheld_sections": withheld_sections,
                "unresolved_slots": unresolved_slot_tokens,
                "required_inputs": required_inputs,
            },
        }

    return {
        "render_artifact": render_artifact,
    }


def validate_portfolio_output(
    brief: dict[str, Any],
    payload: Any,
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    meta = {"tiers": set(), "tier_targets": {}, "tier_sections": {}}
    if not isinstance(payload, dict):
        add_failure(failures, "portfolio.type", "portfolio_output must be an object", "portfolio_output")
        return meta

    portfolio_spectrum = payload.get("portfolio_spectrum")
    if not isinstance(portfolio_spectrum, dict) or not portfolio_spectrum:
        add_failure(
            failures,
            "portfolio.missing_spectrum",
            "portfolio_output.portfolio_spectrum must be a non-empty object",
            "portfolio_output.portfolio_spectrum",
        )
        return meta

    actual_tiers = set(portfolio_spectrum.keys())
    unknown_tiers = actual_tiers - set(SUPPORTED_TIERS)
    if unknown_tiers:
        add_failure(
            failures,
            "portfolio.unknown_tiers",
            f"Unsupported portfolio tiers: {sorted(unknown_tiers)}",
            "portfolio_output.portfolio_spectrum",
        )

    expected_tiers = requested_tiers(brief)
    if not expected_tiers:
        add_failure(
            failures,
            "portfolio.invalid_requested_scope",
            "trade_brief.requested_scope must be omitted, all, lite, default, or premium",
            "trade_brief.requested_scope",
        )
    elif actual_tiers != expected_tiers:
        add_failure(
            failures,
            "portfolio.scope_mismatch",
            f"Portfolio tiers {sorted(actual_tiers)} do not match requested scope {sorted(expected_tiers)}",
            "portfolio_output.portfolio_spectrum",
        )

    for tier in sorted(actual_tiers):
        tier_payload = portfolio_spectrum.get(tier)
        tier_path = f"portfolio_output.portfolio_spectrum.{tier}"
        if not isinstance(tier_payload, dict):
            add_failure(failures, "portfolio.tier_type", f"{tier} tier must be an object", tier_path)
            continue

        sections = tier_payload.get("sections")
        if not is_non_empty_list(sections):
            add_failure(failures, "portfolio.sections", f"{tier} sections must be a non-empty list", f"{tier_path}.sections")
        cta_model = tier_payload.get("cta_model")
        if not isinstance(cta_model, dict) or not is_non_empty_str(cta_model.get("primary")):
            add_failure(failures, "portfolio.cta_model", f"{tier} cta_model.primary is required", f"{tier_path}.cta_model.primary")
        elif cta_model["primary"] != "direct_whatsapp":
            add_failure(
                failures,
                "portfolio.cta_primary",
                f"{tier} cta_model.primary must stay direct_whatsapp",
                f"{tier_path}.cta_model.primary",
            )

        copy_direction = tier_payload.get("copy_direction")
        if not isinstance(copy_direction, dict) or copy_direction.get("language") != "egyptian_arabic":
            add_failure(
                failures,
                "portfolio.copy_direction",
                f"{tier} copy_direction.language must be egyptian_arabic",
                f"{tier_path}.copy_direction.language",
            )
        if not isinstance(tier_payload.get("proof_requirements"), list):
            add_failure(
                failures,
                "portfolio.proof_requirements",
                f"{tier} proof_requirements must be a list",
                f"{tier_path}.proof_requirements",
            )

        schema_targets = tier_payload.get("schema_targets")
        if not is_non_empty_list(schema_targets):
            add_failure(
                failures,
                "portfolio.schema_targets",
                f"{tier} schema_targets must be a non-empty list",
                f"{tier_path}.schema_targets",
            )
            schema_target_set: set[str] = set()
        else:
            schema_target_set = set(schema_targets)
            if schema_target_set != set(SUPPORTED_TARGETS):
                add_failure(
                    failures,
                    "portfolio.schema_target_set",
                    f"{tier} schema_targets must be exactly {list(SUPPORTED_TARGETS)}",
                    f"{tier_path}.schema_targets",
                )

        meta["tiers"].add(tier)
        meta["tier_targets"][tier] = schema_target_set
        meta["tier_sections"][tier] = set(sections or [])

    source_evidence = payload.get("source_evidence")
    if not isinstance(source_evidence, dict) or not is_non_empty_list(source_evidence.get("brief_fields")):
        add_failure(
            failures,
            "portfolio.source_evidence",
            "portfolio_output.source_evidence.brief_fields must be a non-empty list",
            "portfolio_output.source_evidence.brief_fields",
        )
    else:
        brief_fields = set(source_evidence["brief_fields"])
        missing = set(REQUIRED_BRIEF_FIELDS) - brief_fields
        if missing:
            add_failure(
                failures,
                "portfolio.source_evidence_missing",
                f"portfolio_output.source_evidence.brief_fields is missing {sorted(missing)}",
                "portfolio_output.source_evidence.brief_fields",
            )

    implementation_handoff = payload.get("implementation_handoff")
    if not isinstance(implementation_handoff, dict):
        add_failure(
            failures,
            "portfolio.handoff",
            "portfolio_output.implementation_handoff must be an object",
            "portfolio_output.implementation_handoff",
        )
    else:
        required_entities = implementation_handoff.get("required_entities")
        if not is_non_empty_list(required_entities):
            add_failure(
                failures,
                "portfolio.required_entities",
                "portfolio_output.implementation_handoff.required_entities must be a non-empty list",
                "portfolio_output.implementation_handoff.required_entities",
            )
        else:
            missing = set(REQUIRED_BRIEF_FIELDS) - set(required_entities)
            if missing:
                add_failure(
                    failures,
                    "portfolio.required_entities_missing",
                    f"portfolio_output.implementation_handoff.required_entities is missing {sorted(missing)}",
                    "portfolio_output.implementation_handoff.required_entities",
                )

        frontend_priorities = implementation_handoff.get("frontend_priorities")
        required_priorities = {"arabic_first", "mobile_first", "direct_whatsapp_primary"}
        if not is_non_empty_list(frontend_priorities):
            add_failure(
                failures,
                "portfolio.frontend_priorities",
                "portfolio_output.implementation_handoff.frontend_priorities must be a non-empty list",
                "portfolio_output.implementation_handoff.frontend_priorities",
            )
        else:
            missing = required_priorities - set(frontend_priorities)
            if missing:
                add_failure(
                    failures,
                    "portfolio.frontend_priorities_missing",
                    f"portfolio_output.implementation_handoff.frontend_priorities is missing {sorted(missing)}",
                    "portfolio_output.implementation_handoff.frontend_priorities",
                )

        content_gaps = implementation_handoff.get("content_gaps")
        if not isinstance(content_gaps, list):
            add_failure(
                failures,
                "portfolio.content_gaps",
                "portfolio_output.implementation_handoff.content_gaps must be a list",
                "portfolio_output.implementation_handoff.content_gaps",
            )
            content_gaps = []
        content_gap_set = set(content_gaps)
        if brief.get("gallery_available") is False and actual_tiers & {"default", "premium"} and "gallery_assets" not in content_gap_set:
            add_failure(
                failures,
                "portfolio.gallery_gap",
                "gallery_assets must remain an explicit content gap when gallery_available is false",
                "portfolio_output.implementation_handoff.content_gaps",
            )
        if brief.get("video_available") is False and "premium" in actual_tiers and "video_asset_or_video_slot" not in content_gap_set:
            add_failure(
                failures,
                "portfolio.video_gap",
                "video_asset_or_video_slot must remain an explicit content gap when video_available is false",
                "portfolio_output.implementation_handoff.content_gaps",
            )
        if brief.get("reviews_available") is False and "premium" in actual_tiers and "reviews_or_case_proof" not in content_gap_set:
            add_failure(
                failures,
                "portfolio.reviews_gap",
                "reviews_or_case_proof must remain an explicit content gap when reviews_available is false",
                "portfolio_output.implementation_handoff.content_gaps",
            )

    if not isinstance(payload.get("missing_inputs"), list):
        add_failure(
            failures,
            "portfolio.missing_inputs",
            "portfolio_output.missing_inputs must be a list",
            "portfolio_output.missing_inputs",
        )

    return meta


def validate_schema_mapping_output(
    brief: dict[str, Any],
    portfolio_meta: dict[str, Any],
    payload: Any,
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    meta = {
        "tiers": set(),
        "tier_targets": {},
        "row_maps": {},
        "missing_required_fields": set(),
        "unresolved_inputs": set(),
        "next_priority": set(),
        "source_fields": set(),
    }
    if not isinstance(payload, dict):
        add_failure(failures, "mapping.type", "schema_mapping_output must be an object", "schema_mapping_output")
        return meta

    schema_mapping = payload.get("schema_mapping")
    if not isinstance(schema_mapping, dict) or not schema_mapping:
        add_failure(
            failures,
            "mapping.missing_schema_mapping",
            "schema_mapping_output.schema_mapping must be a non-empty object",
            "schema_mapping_output.schema_mapping",
        )
        return meta

    actual_tiers = set(schema_mapping.keys())
    if actual_tiers != portfolio_meta["tiers"]:
        add_failure(
            failures,
            "mapping.tier_alignment",
            f"schema_mapping tiers {sorted(actual_tiers)} do not match portfolio tiers {sorted(portfolio_meta['tiers'])}",
            "schema_mapping_output.schema_mapping",
        )

    business_label_present = is_non_empty_str(brief.get("business_label"))
    work_hours_present = is_non_empty_str(brief.get("work_hours"))
    emitted_targets: set[str] = set()
    used_source_fields: set[str] = set()

    for tier in sorted(actual_tiers):
        tier_payload = schema_mapping.get(tier)
        tier_path = f"schema_mapping_output.schema_mapping.{tier}"
        if not isinstance(tier_payload, dict) or not tier_payload:
            add_failure(failures, "mapping.tier_type", f"{tier} mapping tier must be a non-empty object", tier_path)
            continue

        tier_targets = set(tier_payload.keys())
        expected_targets = portfolio_meta["tier_targets"].get(tier, set())
        if tier_targets != expected_targets:
            add_failure(
                failures,
                "mapping.target_alignment",
                f"{tier} mapping targets {sorted(tier_targets)} do not match portfolio schema_targets {sorted(expected_targets)}",
                tier_path,
            )

        meta["tiers"].add(tier)
        meta["tier_targets"][tier] = tier_targets
        meta["row_maps"][tier] = {}
        emitted_targets |= tier_targets

        for target in sorted(tier_targets):
            target_payload = tier_payload.get(target)
            target_path = f"{tier_path}.{target}"
            if not isinstance(target_payload, dict):
                add_failure(failures, "mapping.target_type", f"{target} payload must be an object", target_path)
                continue

            entity_map = target_payload.get("entity_map")
            if not is_non_empty_list(entity_map):
                add_failure(failures, "mapping.entity_map", f"{target} entity_map must be a non-empty list", f"{target_path}.entity_map")
                continue

            row_map: dict[str, dict[str, Any]] = {}
            for index, row in enumerate(entity_map):
                row_path = f"{target_path}.entity_map[{index}]"
                if not isinstance(row, dict):
                    add_failure(failures, "mapping.entity_row_type", "entity_map rows must be objects", row_path)
                    continue
                for required_key in ("target_field", "source_field", "status", "resolved_value"):
                    if required_key not in row:
                        add_failure(
                            failures,
                            "mapping.entity_row_key",
                            f"entity_map row is missing {required_key}",
                            row_path,
                        )
                if row.get("status") != "mapped":
                    add_failure(
                        failures,
                        "mapping.entity_row_status",
                        "entity_map rows must use status: mapped",
                        f"{row_path}.status",
                    )
                target_field = row.get("target_field")
                source_field = row.get("source_field")
                if target_field in row_map and target_field is not None:
                    add_failure(
                        failures,
                        "mapping.duplicate_target_field",
                        f"Duplicate target_field {target_field} in {target}",
                        row_path,
                    )
                if is_non_empty_str(target_field):
                    row_map[target_field] = row

                if is_non_empty_str(source_field) and source_field in brief:
                    expected_value = brief[source_field]
                    if row.get("resolved_value") != expected_value:
                        add_failure(
                            failures,
                            "mapping.resolved_value_match",
                            f"resolved_value for {target_field} must match trade_brief.{source_field}",
                            f"{row_path}.resolved_value",
                        )
                    used_source_fields.add(source_field)

                if source_field == "service_scope" and not isinstance(row.get("resolved_value"), list):
                    add_failure(
                        failures,
                        "mapping.service_scope_shape",
                        "resolved_value for service_scope mappings must stay a list",
                        f"{row_path}.resolved_value",
                    )
                if source_field in {"primary_locality", "whatsapp_target", "work_hours", "business_label"} and isinstance(row.get("resolved_value"), list):
                    add_failure(
                        failures,
                        "mapping.scalar_shape",
                        f"resolved_value for {source_field} must stay scalar",
                        f"{row_path}.resolved_value",
                    )

            expected_fields = required_mapping_fields_for_target(target, work_hours_present, business_label_present)
            actual_fields = set(row_map.keys())
            if actual_fields != expected_fields:
                add_failure(
                    failures,
                    "mapping.required_fields",
                    f"{target} mapped fields {sorted(actual_fields)} do not match expected {sorted(expected_fields)}",
                    f"{target_path}.entity_map",
                )

            section_map = target_payload.get("section_map")
            if not isinstance(section_map, list):
                add_failure(failures, "mapping.section_map", f"{target} section_map must be a list", f"{target_path}.section_map")
                section_map = []
            for index, section in enumerate(section_map):
                section_path = f"{target_path}.section_map[{index}]"
                if not isinstance(section, dict):
                    add_failure(failures, "mapping.section_type", "section_map rows must be objects", section_path)
                    continue
                section_id = section.get("section")
                target_fields = section.get("target_fields")
                if section_id not in portfolio_meta["tier_sections"].get(tier, set()):
                    add_failure(
                        failures,
                        "mapping.section_presence",
                        f"section_map entry {section_id} must exist in the portfolio tier sections",
                        section_path,
                    )
                if not isinstance(target_fields, list):
                    add_failure(
                        failures,
                        "mapping.section_target_fields",
                        "section_map.target_fields must be a list",
                        f"{section_path}.target_fields",
                    )
                elif not business_label_present and "name" in target_fields:
                    add_failure(
                        failures,
                        "mapping.name_invented",
                        "name must not appear in section_map when business_label is absent",
                        f"{section_path}.target_fields",
                    )

            if not business_label_present and "name" in row_map:
                add_failure(
                    failures,
                    "mapping.name_invented",
                    "name must not appear in entity_map when business_label is absent",
                    f"{target_path}.entity_map",
                )

            meta["row_maps"][tier][target] = row_map

    source_evidence = payload.get("source_evidence")
    if not isinstance(source_evidence, dict) or not is_non_empty_list(source_evidence.get("upstream_fields")):
        add_failure(
            failures,
            "mapping.source_evidence",
            "schema_mapping_output.source_evidence.upstream_fields must be a non-empty list",
            "schema_mapping_output.source_evidence.upstream_fields",
        )
    else:
        actual_source_fields = set(source_evidence["upstream_fields"])
        if actual_source_fields != used_source_fields:
            add_failure(
                failures,
                "mapping.source_evidence_match",
                f"source_evidence.upstream_fields {sorted(actual_source_fields)} do not match mapped source fields {sorted(used_source_fields)}",
                "schema_mapping_output.source_evidence.upstream_fields",
            )
        meta["source_fields"] = actual_source_fields

    missing_required_fields = payload.get("missing_required_fields")
    if not isinstance(missing_required_fields, list):
        add_failure(
            failures,
            "mapping.missing_required_fields",
            "schema_mapping_output.missing_required_fields must be a list",
            "schema_mapping_output.missing_required_fields",
        )
        missing_required_fields = []
    meta["missing_required_fields"] = set(missing_required_fields)

    handoff = payload.get("implementation_handoff")
    if not isinstance(handoff, dict):
        add_failure(
            failures,
            "mapping.handoff",
            "schema_mapping_output.implementation_handoff must be an object",
            "schema_mapping_output.implementation_handoff",
        )
    else:
        ready_targets = handoff.get("ready_targets")
        if not is_non_empty_list(ready_targets):
            add_failure(
                failures,
                "mapping.ready_targets",
                "schema_mapping_output.implementation_handoff.ready_targets must be a non-empty list",
                "schema_mapping_output.implementation_handoff.ready_targets",
            )
        elif set(ready_targets) != emitted_targets:
            add_failure(
                failures,
                "mapping.ready_targets_match",
                f"ready_targets {sorted(set(ready_targets))} do not match emitted targets {sorted(emitted_targets)}",
                "schema_mapping_output.implementation_handoff.ready_targets",
            )

        unresolved_inputs = handoff.get("unresolved_inputs")
        if not isinstance(unresolved_inputs, list):
            add_failure(
                failures,
                "mapping.unresolved_inputs",
                "schema_mapping_output.implementation_handoff.unresolved_inputs must be a list",
                "schema_mapping_output.implementation_handoff.unresolved_inputs",
            )
            unresolved_inputs = []
        next_priority = handoff.get("next_mapping_priority")
        if not isinstance(next_priority, list):
            add_failure(
                failures,
                "mapping.next_priority",
                "schema_mapping_output.implementation_handoff.next_mapping_priority must be a list",
                "schema_mapping_output.implementation_handoff.next_mapping_priority",
            )
            next_priority = []

        meta["unresolved_inputs"] = set(unresolved_inputs)
        meta["next_priority"] = set(next_priority)

    if not business_label_present:
        if "business_label" not in meta["missing_required_fields"]:
            add_failure(
                failures,
                "mapping.business_label_gap",
                "business_label must remain in missing_required_fields when absent upstream",
                "schema_mapping_output.missing_required_fields",
            )
        if "business_label" not in meta["unresolved_inputs"]:
            add_failure(
                failures,
                "mapping.business_label_unresolved",
                "business_label must remain in implementation_handoff.unresolved_inputs when absent upstream",
                "schema_mapping_output.implementation_handoff.unresolved_inputs",
            )
        if "resolve_business_label" not in meta["next_priority"]:
            add_failure(
                failures,
                "mapping.business_label_priority",
                "resolve_business_label must remain in next_mapping_priority when business_label is absent",
                "schema_mapping_output.implementation_handoff.next_mapping_priority",
            )

    if work_hours_present:
        for tier in meta["tiers"]:
            for target in meta["tier_targets"].get(tier, set()):
                row_map = meta["row_maps"][tier].get(target, {})
                required_hours_field = "openingHours" if target == "LocalBusiness" else "hoursAvailable"
                if required_hours_field not in row_map:
                    add_failure(
                        failures,
                        "mapping.hours_missing",
                        f"{required_hours_field} must be emitted when work_hours is present",
                        f"schema_mapping_output.schema_mapping.{tier}.{target}.entity_map",
                    )

    return meta


def validate_jsonld_output(
    brief: dict[str, Any],
    mapping_meta: dict[str, Any],
    payload: Any,
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    meta = {
        "tiers": set(),
        "tier_targets": {},
        "mapping_fields": set(),
        "missing_required_fields": set(),
        "unresolved_inputs": set(),
        "next_priority": set(),
    }
    if not isinstance(payload, dict):
        add_failure(failures, "jsonld.type", "jsonld_output must be an object", "jsonld_output")
        return meta

    jsonld_payloads = payload.get("jsonld_payloads")
    if not isinstance(jsonld_payloads, dict) or not jsonld_payloads:
        add_failure(
            failures,
            "jsonld.missing_payloads",
            "jsonld_output.jsonld_payloads must be a non-empty object",
            "jsonld_output.jsonld_payloads",
        )
        return meta

    actual_tiers = set(jsonld_payloads.keys())
    if actual_tiers != mapping_meta["tiers"]:
        add_failure(
            failures,
            "jsonld.tier_alignment",
            f"jsonld tiers {sorted(actual_tiers)} do not match schema_mapping tiers {sorted(mapping_meta['tiers'])}",
            "jsonld_output.jsonld_payloads",
        )

    business_label_present = is_non_empty_str(brief.get("business_label"))
    work_hours_present = is_non_empty_str(brief.get("work_hours"))
    used_mapping_fields: set[str] = set()
    emitted_targets: set[str] = set()

    for tier in sorted(actual_tiers):
        tier_payload = jsonld_payloads.get(tier)
        tier_path = f"jsonld_output.jsonld_payloads.{tier}"
        if not isinstance(tier_payload, dict) or not tier_payload:
            add_failure(failures, "jsonld.tier_type", f"{tier} JSON-LD tier must be a non-empty object", tier_path)
            continue

        tier_targets = set(tier_payload.keys())
        expected_targets = mapping_meta["tier_targets"].get(tier, set())
        if tier_targets != expected_targets:
            add_failure(
                failures,
                "jsonld.target_alignment",
                f"{tier} JSON-LD targets {sorted(tier_targets)} do not match schema_mapping targets {sorted(expected_targets)}",
                tier_path,
            )

        meta["tiers"].add(tier)
        meta["tier_targets"][tier] = tier_targets
        emitted_targets |= tier_targets

        for target in sorted(tier_targets):
            target_payload = tier_payload.get(target)
            target_path = f"{tier_path}.{target}"
            if not isinstance(target_payload, dict):
                add_failure(failures, "jsonld.target_type", f"{target} JSON-LD payload must be an object", target_path)
                continue

            if target_payload.get("@context") != "https://schema.org":
                add_failure(
                    failures,
                    "jsonld.context",
                    f"{target} must use @context https://schema.org",
                    f"{target_path}.@context",
                )
            if target_payload.get("@type") != target:
                add_failure(
                    failures,
                    "jsonld.type_match",
                    f"{target} must use @type {target}",
                    f"{target_path}.@type",
                )

            row_map = mapping_meta["row_maps"].get(tier, {}).get(target, {})

            area_served_row = row_map.get("areaServed")
            if not area_served_row or target_payload.get("areaServed") != area_served_row.get("resolved_value"):
                add_failure(
                    failures,
                    "jsonld.area_served",
                    f"{target} areaServed must match schema_mapping resolved_value",
                    f"{target_path}.areaServed",
                )
            else:
                used_mapping_fields.add("areaServed")

            action = target_payload.get("potentialAction")
            potential_action_row = row_map.get("potentialAction.target")
            if (
                not isinstance(action, dict)
                or action.get("@type") != "CommunicateAction"
                or not potential_action_row
                or action.get("target") != potential_action_row.get("resolved_value")
            ):
                add_failure(
                    failures,
                    "jsonld.potential_action",
                    f"{target} potentialAction.target must match schema_mapping resolved_value",
                    f"{target_path}.potentialAction",
                )
            else:
                used_mapping_fields.add("potentialAction.target")

            if target == "LocalBusiness":
                offer_row = row_map.get("makesOffer.itemOffered")
                offers = target_payload.get("makesOffer")
                if not offer_row:
                    add_failure(
                        failures,
                        "jsonld.missing_offer_row",
                        "LocalBusiness requires makesOffer.itemOffered in schema_mapping",
                        target_path,
                    )
                else:
                    expected_services = offer_row["resolved_value"]
                    if isinstance(expected_services, list):
                        expected_offers = [
                            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": service}}
                            for service in expected_services
                        ]
                    else:
                        expected_offers = [
                            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": expected_services}}
                        ]
                    if offers != expected_offers:
                        add_failure(
                            failures,
                            "jsonld.makes_offer",
                            "LocalBusiness makesOffer must be derived exactly from schema_mapping makesOffer.itemOffered",
                            f"{target_path}.makesOffer",
                        )
                    else:
                        used_mapping_fields.add("makesOffer.itemOffered")

                hours_row = row_map.get("openingHours")
                if work_hours_present:
                    if not hours_row or target_payload.get("openingHours") != hours_row.get("resolved_value"):
                        add_failure(
                            failures,
                            "jsonld.opening_hours",
                            "LocalBusiness openingHours must match schema_mapping resolved_value when work_hours is present",
                            f"{target_path}.openingHours",
                        )
                    else:
                        used_mapping_fields.add("openingHours")
                elif "openingHours" in target_payload:
                    add_failure(
                        failures,
                        "jsonld.invented_opening_hours",
                        "LocalBusiness openingHours must not be emitted when work_hours is absent",
                        f"{target_path}.openingHours",
                    )
            else:
                service_type_row = row_map.get("serviceType")
                if not service_type_row or target_payload.get("serviceType") != service_type_row.get("resolved_value"):
                    add_failure(
                        failures,
                        "jsonld.service_type",
                        "ProfessionalService serviceType must match schema_mapping resolved_value",
                        f"{target_path}.serviceType",
                    )
                else:
                    used_mapping_fields.add("serviceType")

                hours_row = row_map.get("hoursAvailable")
                if work_hours_present:
                    if not hours_row or target_payload.get("hoursAvailable") != hours_row.get("resolved_value"):
                        add_failure(
                            failures,
                            "jsonld.hours_available",
                            "ProfessionalService hoursAvailable must match schema_mapping resolved_value when work_hours is present",
                            f"{target_path}.hoursAvailable",
                        )
                    else:
                        used_mapping_fields.add("hoursAvailable")
                elif "hoursAvailable" in target_payload:
                    add_failure(
                        failures,
                        "jsonld.invented_hours_available",
                        "ProfessionalService hoursAvailable must not be emitted when work_hours is absent",
                        f"{target_path}.hoursAvailable",
                    )

            name_row = row_map.get("name")
            if business_label_present:
                if not name_row or target_payload.get("name") != name_row.get("resolved_value"):
                    add_failure(
                        failures,
                        "jsonld.name_required",
                        f"{target} name must match schema_mapping resolved_value when business_label is present",
                        f"{target_path}.name",
                    )
                else:
                    used_mapping_fields.add("name")
            elif "name" in target_payload:
                add_failure(
                    failures,
                    "jsonld.invented_name",
                    f"{target} name must not be emitted when business_label is absent",
                    f"{target_path}.name",
                )

    source_evidence = payload.get("source_evidence")
    if not isinstance(source_evidence, dict) or not is_non_empty_list(source_evidence.get("mapping_fields")):
        add_failure(
            failures,
            "jsonld.source_evidence",
            "jsonld_output.source_evidence.mapping_fields must be a non-empty list",
            "jsonld_output.source_evidence.mapping_fields",
        )
    else:
        mapping_fields = set(source_evidence["mapping_fields"])
        if mapping_fields != used_mapping_fields:
            add_failure(
                failures,
                "jsonld.mapping_fields_match",
                f"mapping_fields {sorted(mapping_fields)} do not match JSON-LD fields used {sorted(used_mapping_fields)}",
                "jsonld_output.source_evidence.mapping_fields",
            )
        meta["mapping_fields"] = mapping_fields

    missing_required_fields = payload.get("missing_required_fields")
    if not isinstance(missing_required_fields, list):
        add_failure(
            failures,
            "jsonld.missing_required_fields",
            "jsonld_output.missing_required_fields must be a list",
            "jsonld_output.missing_required_fields",
        )
        missing_required_fields = []
    meta["missing_required_fields"] = set(missing_required_fields)

    handoff = payload.get("implementation_handoff")
    if not isinstance(handoff, dict):
        add_failure(
            failures,
            "jsonld.handoff",
            "jsonld_output.implementation_handoff must be an object",
            "jsonld_output.implementation_handoff",
        )
    else:
        ready_payloads = handoff.get("ready_payloads")
        if not is_non_empty_list(ready_payloads):
            add_failure(
                failures,
                "jsonld.ready_payloads",
                "jsonld_output.implementation_handoff.ready_payloads must be a non-empty list",
                "jsonld_output.implementation_handoff.ready_payloads",
            )
        elif set(ready_payloads) != emitted_targets:
            add_failure(
                failures,
                "jsonld.ready_payloads_match",
                f"ready_payloads {sorted(set(ready_payloads))} do not match emitted targets {sorted(emitted_targets)}",
                "jsonld_output.implementation_handoff.ready_payloads",
            )

        unresolved_inputs = handoff.get("unresolved_inputs")
        if not isinstance(unresolved_inputs, list):
            add_failure(
                failures,
                "jsonld.unresolved_inputs",
                "jsonld_output.implementation_handoff.unresolved_inputs must be a list",
                "jsonld_output.implementation_handoff.unresolved_inputs",
            )
            unresolved_inputs = []
        next_priority = handoff.get("next_jsonld_priority")
        if not isinstance(next_priority, list):
            add_failure(
                failures,
                "jsonld.next_priority",
                "jsonld_output.implementation_handoff.next_jsonld_priority must be a list",
                "jsonld_output.implementation_handoff.next_jsonld_priority",
            )
            next_priority = []

        meta["unresolved_inputs"] = set(unresolved_inputs)
        meta["next_priority"] = set(next_priority)

    if not business_label_present:
        if "business_label" not in meta["missing_required_fields"]:
            add_failure(
                failures,
                "jsonld.business_label_gap",
                "business_label must remain in missing_required_fields when absent upstream",
                "jsonld_output.missing_required_fields",
            )
        if "business_label" not in meta["unresolved_inputs"]:
            add_failure(
                failures,
                "jsonld.business_label_unresolved",
                "business_label must remain in implementation_handoff.unresolved_inputs when absent upstream",
                "jsonld_output.implementation_handoff.unresolved_inputs",
            )
        if "resolve_business_label" not in meta["next_priority"]:
            add_failure(
                failures,
                "jsonld.business_label_priority",
                "resolve_business_label must remain in next_jsonld_priority when business_label is absent",
                "jsonld_output.implementation_handoff.next_jsonld_priority",
            )

    return meta


def validate_landing_output(
    brief: dict[str, Any],
    portfolio_output: Any,
    schema_mapping_output: Any,
    jsonld_output: Any,
    payload: Any,
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    meta = {
        "tiers": set(),
        "missing_required_fields": set(),
        "content_gaps": set(),
        "unresolved_inputs": set(),
        "payloads": {},
    }
    if not isinstance(payload, dict):
        add_failure(failures, "landing.type", "landing_output must be an object", "landing_output")
        return meta

    landing_artifact = payload.get("landing_artifact")
    if not isinstance(landing_artifact, dict) or not landing_artifact:
        add_failure(
            failures,
            "landing.missing_artifact",
            "landing_output.landing_artifact must be a non-empty object",
            "landing_output.landing_artifact",
        )
        return meta

    meta["tiers"] = set(landing_artifact.keys())
    meta["payloads"] = landing_artifact

    missing_required_fields = payload.get("missing_required_fields")
    if isinstance(missing_required_fields, list):
        meta["missing_required_fields"] = set(missing_required_fields)

    handoff = payload.get("implementation_handoff")
    if isinstance(handoff, dict):
        if isinstance(handoff.get("content_gaps"), list):
            meta["content_gaps"] = set(handoff["content_gaps"])
        if isinstance(handoff.get("unresolved_inputs"), list):
            meta["unresolved_inputs"] = set(handoff["unresolved_inputs"])

    try:
        expected_payload = build_expected_landing_output(
            brief,
            portfolio_output if isinstance(portfolio_output, dict) else {},
            schema_mapping_output if isinstance(schema_mapping_output, dict) else {},
            jsonld_output if isinstance(jsonld_output, dict) else {},
        )
    except ValueError as exc:
        add_failure(
            failures,
            "landing.expected_build",
            str(exc),
            "landing_output",
        )
        return meta

    diff_keys = diff_paths(payload, expected_payload, "landing_output")
    if diff_keys:
        for diff_key in diff_keys[:10]:
            add_failure(
                failures,
                "landing.diff",
                "landing_output does not match the expected deterministic landing artifact",
                diff_key,
            )

    return meta


def validate_seo_output(
    brief: dict[str, Any],
    portfolio_output: Any,
    schema_mapping_output: Any,
    jsonld_output: Any,
    landing_output: Any,
    payload: Any,
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    meta = {
        "tiers": set(),
        "payloads": {},
        "missing_identity_fields": set(),
        "unresolved_inputs": set(),
    }
    if not isinstance(payload, dict):
        add_failure(failures, "seo.type", "seo_output must be an object", "seo_output")
        return meta

    seo_artifact = payload.get("seo_artifact")
    if not isinstance(seo_artifact, dict) or not seo_artifact:
        add_failure(
            failures,
            "seo.missing_artifact",
            "seo_output.seo_artifact must be a non-empty object",
            "seo_output.seo_artifact",
        )
        return meta

    meta["tiers"] = set(seo_artifact.keys())
    meta["payloads"] = seo_artifact

    handoff = payload.get("implementation_handoff")
    if isinstance(handoff, dict) and isinstance(handoff.get("unresolved_inputs"), list):
        meta["unresolved_inputs"] = set(handoff["unresolved_inputs"])

    for tier_payload in seo_artifact.values():
        if not isinstance(tier_payload, dict):
            continue
        seo_gaps = tier_payload.get("seo_gaps")
        if isinstance(seo_gaps, dict) and isinstance(seo_gaps.get("missing_identity_fields"), list):
            meta["missing_identity_fields"].update(seo_gaps["missing_identity_fields"])

    try:
        expected_payload = build_expected_seo_output(
            brief,
            portfolio_output if isinstance(portfolio_output, dict) else {},
            schema_mapping_output if isinstance(schema_mapping_output, dict) else {},
            jsonld_output if isinstance(jsonld_output, dict) else {},
            landing_output if isinstance(landing_output, dict) else {},
        )
    except ValueError as exc:
        add_failure(
            failures,
            "seo.expected_build",
            str(exc),
            "seo_output",
        )
        return meta

    diff_keys = diff_paths(payload, expected_payload, "seo_output")
    if diff_keys:
        for diff_key in diff_keys[:12]:
            add_failure(
                failures,
                "seo.diff",
                "seo_output does not match the expected deterministic SEO artifact",
                diff_key,
            )

    return meta


def validate_render_output(
    landing_output: Any,
    seo_output: Any,
    jsonld_output: Any,
    payload: Any,
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    meta = {
        "tiers": set(),
        "payloads": {},
        "section_orders": {},
        "withheld_sections": {},
        "unresolved_slots": {},
        "required_inputs": {},
    }
    if not isinstance(payload, dict):
        add_failure(failures, "render.type", "render_output must be an object", "render_output")
        return meta

    render_artifact = payload.get("render_artifact")
    if not isinstance(render_artifact, dict) or not render_artifact:
        add_failure(
            failures,
            "render.missing_artifact",
            "render_output.render_artifact must be a non-empty object",
            "render_output.render_artifact",
        )
        return meta

    meta["tiers"] = set(render_artifact.keys())
    meta["payloads"] = render_artifact

    for tier, tier_payload in render_artifact.items():
        if not isinstance(tier_payload, dict):
            continue
        body = tier_payload.get("body")
        if isinstance(body, dict) and isinstance(body.get("section_order"), list):
            meta["section_orders"][tier] = list(body["section_order"])
        render_notes = tier_payload.get("render_notes")
        if isinstance(render_notes, dict):
            if isinstance(render_notes.get("withheld_sections"), list):
                meta["withheld_sections"][tier] = list(render_notes["withheld_sections"])
            if isinstance(render_notes.get("unresolved_slots"), list):
                meta["unresolved_slots"][tier] = list(render_notes["unresolved_slots"])
            if isinstance(render_notes.get("required_inputs"), list):
                meta["required_inputs"][tier] = list(render_notes["required_inputs"])

    try:
        expected_payload = build_expected_render_output(
            landing_output if isinstance(landing_output, dict) else {},
            seo_output if isinstance(seo_output, dict) else {},
            jsonld_output if isinstance(jsonld_output, dict) else {},
        )
    except ValueError as exc:
        add_failure(
            failures,
            "render.expected_build",
            str(exc),
            "render_output",
        )
        return meta

    diff_keys = diff_paths(payload, expected_payload, "render_output")
    if diff_keys:
        for diff_key in diff_keys[:15]:
            add_failure(
                failures,
                "render.diff",
                "render_output does not match the expected deterministic render artifact",
                diff_key,
            )

    return meta


def cross_stage_target_alignment(
    portfolio_meta: dict[str, Any] | None,
    mapping_meta: dict[str, Any] | None,
    jsonld_meta: dict[str, Any] | None,
    failures: list[dict[str, Any]],
) -> bool:
    start = len(failures)
    if portfolio_meta and mapping_meta:
        for tier in portfolio_meta["tiers"]:
            if mapping_meta["tier_targets"].get(tier, set()) != portfolio_meta["tier_targets"].get(tier, set()):
                add_failure(
                    failures,
                    "cross.target_alignment.mapping",
                    f"{tier} mapping targets do not match portfolio schema_targets",
                    f"schema_mapping_output.schema_mapping.{tier}",
                )
    if mapping_meta and jsonld_meta:
        for tier in mapping_meta["tiers"]:
            if jsonld_meta["tier_targets"].get(tier, set()) != mapping_meta["tier_targets"].get(tier, set()):
                add_failure(
                    failures,
                    "cross.target_alignment.jsonld",
                    f"{tier} JSON-LD targets do not match schema_mapping targets",
                    f"jsonld_output.jsonld_payloads.{tier}",
                )
    return len(failures) == start


def cross_stage_resolved_value_integrity(
    brief: dict[str, Any],
    mapping_meta: dict[str, Any] | None,
    failures: list[dict[str, Any]],
) -> bool:
    start = len(failures)
    if not mapping_meta:
        return True

    service_scope = brief.get("service_scope")
    for tier in mapping_meta["tiers"]:
        for target in mapping_meta["tier_targets"].get(tier, set()):
            row_map = mapping_meta["row_maps"][tier].get(target, {})
            for target_field, row in row_map.items():
                source_field = row.get("source_field")
                if "resolved_value" not in row:
                    add_failure(
                        failures,
                        "cross.resolved_value.missing",
                        f"{tier}.{target}.{target_field} is missing resolved_value",
                        f"schema_mapping_output.schema_mapping.{tier}.{target}.entity_map",
                    )
                    continue
                resolved_value = row.get("resolved_value")
                if source_field == "service_scope" and resolved_value != service_scope:
                    add_failure(
                        failures,
                        "cross.resolved_value.service_scope",
                        f"{tier}.{target}.{target_field} must preserve service_scope exactly",
                        f"schema_mapping_output.schema_mapping.{tier}.{target}.entity_map",
                    )
                if source_field != "service_scope" and source_field in brief and resolved_value != brief[source_field]:
                    add_failure(
                        failures,
                        "cross.resolved_value.scalar",
                        f"{tier}.{target}.{target_field} must preserve {source_field} exactly",
                        f"schema_mapping_output.schema_mapping.{tier}.{target}.entity_map",
                    )
    return len(failures) == start


def cross_stage_gap_propagation(
    brief: dict[str, Any],
    mapping_meta: dict[str, Any] | None,
    jsonld_meta: dict[str, Any] | None,
    landing_meta: dict[str, Any] | None,
    seo_meta: dict[str, Any] | None,
    failures: list[dict[str, Any]],
) -> bool:
    start = len(failures)
    if not mapping_meta or not jsonld_meta:
        return True

    if not is_non_empty_str(brief.get("business_label")):
        if "business_label" not in mapping_meta["missing_required_fields"] or "business_label" not in jsonld_meta["missing_required_fields"]:
            add_failure(
                failures,
                "cross.gap.business_label",
                "business_label gap must propagate from schema_mapping to jsonld_output",
                "jsonld_output.missing_required_fields",
            )
        if "business_label" not in mapping_meta["unresolved_inputs"] or "business_label" not in jsonld_meta["unresolved_inputs"]:
            add_failure(
                failures,
                "cross.gap.business_label_unresolved",
                "business_label must remain unresolved across both downstream stages",
                "jsonld_output.implementation_handoff.unresolved_inputs",
            )
        if landing_meta:
            if "business_label" not in landing_meta["missing_required_fields"]:
                add_failure(
                    failures,
                    "cross.gap.business_label_landing",
                    "business_label gap must propagate into landing_output.missing_required_fields",
                    "landing_output.missing_required_fields",
                )
            if "business_label" not in landing_meta["unresolved_inputs"]:
                add_failure(
                    failures,
                    "cross.gap.business_label_landing_unresolved",
                    "business_label must remain unresolved in landing_output.implementation_handoff.unresolved_inputs",
                    "landing_output.implementation_handoff.unresolved_inputs",
                )
        if seo_meta:
            if "business_label" not in seo_meta["missing_identity_fields"]:
                add_failure(
                    failures,
                    "cross.gap.business_label_seo",
                    "business_label gap must propagate into seo_output.seo_artifact.*.seo_gaps.missing_identity_fields",
                    "seo_output.seo_artifact",
                )
            if "business_label" not in seo_meta["unresolved_inputs"]:
                add_failure(
                    failures,
                    "cross.gap.business_label_seo_unresolved",
                    "business_label must remain unresolved in seo_output.implementation_handoff.unresolved_inputs",
                    "seo_output.implementation_handoff.unresolved_inputs",
                )
    return len(failures) == start


def cross_stage_no_invented_conditionals(
    brief: dict[str, Any],
    mapping_meta: dict[str, Any] | None,
    jsonld_meta: dict[str, Any] | None,
    landing_meta: dict[str, Any] | None,
    failures: list[dict[str, Any]],
) -> bool:
    start = len(failures)
    business_label_present = is_non_empty_str(brief.get("business_label"))
    work_hours_present = is_non_empty_str(brief.get("work_hours"))

    if mapping_meta:
        for tier in mapping_meta["tiers"]:
            for target in mapping_meta["tier_targets"].get(tier, set()):
                row_map = mapping_meta["row_maps"][tier].get(target, {})
                if not business_label_present and "name" in row_map:
                    add_failure(
                        failures,
                        "cross.invented_name.mapping",
                        "schema_mapping must not invent name when business_label is absent",
                        f"schema_mapping_output.schema_mapping.{tier}.{target}.entity_map",
                    )
                if not work_hours_present:
                    hours_field = "openingHours" if target == "LocalBusiness" else "hoursAvailable"
                    if hours_field in row_map:
                        add_failure(
                            failures,
                            "cross.invented_hours.mapping",
                            f"schema_mapping must not emit {hours_field} when work_hours is absent",
                            f"schema_mapping_output.schema_mapping.{tier}.{target}.entity_map",
                        )

    if jsonld_meta:
        payloads = jsonld_meta.get("payloads", {})
        for tier, tier_payload in payloads.items():
            for target, target_payload in tier_payload.items():
                if not isinstance(target_payload, dict):
                    continue
                if not business_label_present and "name" in target_payload:
                    add_failure(
                        failures,
                        "cross.invented_name.jsonld",
                        "jsonld_output must not emit name when business_label is absent",
                        f"jsonld_output.jsonld_payloads.{tier}.{target}.name",
                    )
                if not work_hours_present:
                    hours_field = "openingHours" if target == "LocalBusiness" else "hoursAvailable"
                    if hours_field in target_payload:
                        add_failure(
                            failures,
                            "cross.invented_hours.jsonld",
                            f"jsonld_output must not emit {hours_field} when work_hours is absent",
                            f"jsonld_output.jsonld_payloads.{tier}.{target}.{hours_field}",
                        )

    if landing_meta:
        payloads = landing_meta.get("payloads", {})
        for tier, tier_payload in payloads.items():
            if not isinstance(tier_payload, dict):
                continue
            sections = tier_payload.get("sections")
            if not isinstance(sections, dict):
                continue

            if not business_label_present and isinstance(sections.get("hero"), dict):
                business_slot = section_slot_map(sections["hero"]).get("business_label")
                if isinstance(business_slot, dict) and business_slot.get("status") == "resolved":
                    add_failure(
                        failures,
                        "cross.invented_name.landing",
                        "landing_output must not resolve business_label when business_label is absent",
                        f"landing_output.landing_artifact.{tier}.sections.hero.slots",
                    )

            if not work_hours_present and isinstance(sections.get("hours"), dict) and sections["hours"].get("render_status") == "ready":
                add_failure(
                    failures,
                    "cross.invented_hours.landing",
                    "landing_output must not mark hours ready when work_hours is absent",
                    f"landing_output.landing_artifact.{tier}.sections.hours.render_status",
                )

            if not is_non_empty_list(brief.get("gallery_assets")) and isinstance(sections.get("gallery"), dict) and sections["gallery"].get("render_status") == "ready":
                add_failure(
                    failures,
                    "cross.invented_gallery.landing",
                    "landing_output must not mark gallery ready when concrete gallery_assets are absent",
                    f"landing_output.landing_artifact.{tier}.sections.gallery.render_status",
                )

            if not (is_non_empty_str(brief.get("video_asset")) or is_non_empty_str(brief.get("video_url"))) and isinstance(sections.get("video-anchor"), dict) and sections["video-anchor"].get("render_status") == "ready":
                add_failure(
                    failures,
                    "cross.invented_video.landing",
                    "landing_output must not mark video-anchor ready when concrete video evidence is absent",
                    f"landing_output.landing_artifact.{tier}.sections.video-anchor.render_status",
                )

            if not is_non_empty_list(brief.get("review_items")) and isinstance(sections.get("reviews"), dict) and sections["reviews"].get("render_status") == "ready":
                add_failure(
                    failures,
                    "cross.invented_reviews.landing",
                    "landing_output must not mark reviews ready when concrete review_items are absent",
                    f"landing_output.landing_artifact.{tier}.sections.reviews.render_status",
                )
    return len(failures) == start


def cross_stage_render_copy_integrity(
    landing_meta: dict[str, Any] | None,
    seo_meta: dict[str, Any] | None,
    jsonld_meta: dict[str, Any] | None,
    render_meta: dict[str, Any] | None,
    failures: list[dict[str, Any]],
) -> bool:
    start = len(failures)
    if not landing_meta or not seo_meta or not jsonld_meta or not render_meta:
        return True

    landing_payloads = landing_meta.get("payloads", {})
    seo_payloads = seo_meta.get("payloads", {})
    jsonld_payloads = jsonld_meta.get("payloads", {})
    render_payloads = render_meta.get("payloads", {})

    for tier in render_meta.get("tiers", set()):
        landing_tier = landing_payloads.get(tier)
        seo_tier = seo_payloads.get(tier)
        jsonld_tier = jsonld_payloads.get(tier)
        render_tier = render_payloads.get(tier)
        if not isinstance(landing_tier, dict) or not isinstance(seo_tier, dict) or not isinstance(jsonld_tier, dict) or not isinstance(render_tier, dict):
            continue

        render_document = render_tier.get("document")
        if not isinstance(render_document, dict):
            continue

        if render_document.get("title") != seo_tier.get("metadata", {}).get("title"):
            add_failure(
                failures,
                "cross.render.title_copy",
                f"{tier} render title must copy seo metadata.title exactly",
                f"render_output.render_artifact.{tier}.document.title",
            )
        if render_document.get("meta_description") != seo_tier.get("metadata", {}).get("meta_description"):
            add_failure(
                failures,
                "cross.render.meta_copy",
                f"{tier} render meta_description must copy seo metadata.meta_description exactly",
                f"render_output.render_artifact.{tier}.document.meta_description",
            )

        if render_tier.get("head", {}).get("jsonld") != jsonld_tier:
            add_failure(
                failures,
                "cross.render.jsonld_copy",
                f"{tier} render head.jsonld must copy jsonld_output exactly",
                f"render_output.render_artifact.{tier}.head.jsonld",
            )

        landing_cta_primary = landing_tier.get("cta", {}).get("primary")
        render_cta_primary = render_tier.get("cta", {}).get("primary")
        if isinstance(landing_cta_primary, dict) and isinstance(render_cta_primary, dict):
            expected_cta = {
                "action": landing_cta_primary.get("action"),
                "target": landing_cta_primary.get("target"),
                "placements": list(landing_cta_primary.get("placements", []))
                if isinstance(landing_cta_primary.get("placements"), list)
                else landing_cta_primary.get("placements"),
            }
            if render_cta_primary != expected_cta:
                add_failure(
                    failures,
                    "cross.render.cta_copy",
                    f"{tier} render CTA must copy landing CTA semantics exactly",
                    f"render_output.render_artifact.{tier}.cta.primary",
                )

        renderable_section_order = landing_tier.get("rendering_handoff", {}).get("renderable_section_order")
        render_section_order = render_tier.get("body", {}).get("section_order")
        if isinstance(renderable_section_order, list) and render_section_order != renderable_section_order:
            add_failure(
                failures,
                "cross.render.section_order_copy",
                f"{tier} render body.section_order must copy landing renderable_section_order exactly",
                f"render_output.render_artifact.{tier}.body.section_order",
            )

    return len(failures) == start


def cross_stage_render_gap_visibility(
    landing_meta: dict[str, Any] | None,
    render_meta: dict[str, Any] | None,
    failures: list[dict[str, Any]],
) -> bool:
    start = len(failures)
    if not landing_meta or not render_meta:
        return True

    landing_payloads = landing_meta.get("payloads", {})
    render_payloads = render_meta.get("payloads", {})
    for tier in render_meta.get("tiers", set()):
        landing_tier = landing_payloads.get(tier)
        render_tier = render_payloads.get(tier)
        if not isinstance(landing_tier, dict) or not isinstance(render_tier, dict):
            continue

        rendering_handoff = landing_tier.get("rendering_handoff")
        landing_sections = landing_tier.get("sections")
        render_body = render_tier.get("body")
        render_notes = render_tier.get("render_notes")
        if not isinstance(rendering_handoff, dict) or not isinstance(landing_sections, dict) or not isinstance(render_body, dict) or not isinstance(render_notes, dict):
            continue

        planned_section_order = rendering_handoff.get("planned_section_order")
        renderable_section_order = rendering_handoff.get("renderable_section_order")
        render_sections = render_body.get("sections")
        actual_section_order = render_body.get("section_order")
        actual_withheld = render_notes.get("withheld_sections")
        actual_unresolved = render_notes.get("unresolved_slots")
        actual_required_inputs = render_notes.get("required_inputs")
        if not isinstance(planned_section_order, list) or not isinstance(renderable_section_order, list):
            continue
        if not isinstance(render_sections, dict) or not isinstance(actual_section_order, list):
            continue
        if not isinstance(actual_withheld, list) or not isinstance(actual_unresolved, list) or not isinstance(actual_required_inputs, list):
            continue

        expected_withheld: list[str] = []
        expected_unresolved: list[str] = []
        expected_required_inputs: list[str] = []

        for section_id in planned_section_order:
            section_payload = landing_sections.get(section_id)
            if not isinstance(section_payload, dict):
                continue
            if section_payload.get("render_status") == "withheld":
                expected_withheld.append(section_id)

        for section_id in renderable_section_order:
            section_payload = landing_sections.get(section_id)
            if not isinstance(section_payload, dict):
                continue
            for slot in ordered_section_slots(section_payload, f"landing_output.landing_artifact.{tier}.sections.{section_id}"):
                if slot.get("status") != "unresolved":
                    continue
                fallback = slot.get("required_input")
                if not is_non_empty_str(fallback):
                    continue
                token = f"{section_id}.{slot['slot_id']}"
                expected_unresolved.append(token)
                if fallback not in expected_required_inputs:
                    expected_required_inputs.append(fallback)

                render_section = render_sections.get(section_id)
                if not isinstance(render_section, dict):
                    add_failure(
                        failures,
                        "cross.render.unresolved_hidden",
                        f"{tier} render body.sections must retain rendered section {section_id}",
                        f"render_output.render_artifact.{tier}.body.sections.{section_id}",
                    )
                    continue
                render_slots = render_section.get("slots")
                if not isinstance(render_slots, list):
                    add_failure(
                        failures,
                        "cross.render.unresolved_hidden",
                        f"{tier} render section {section_id} must retain slot list visibility",
                        f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots",
                    )
                    continue
                matching_render_slot = None
                for render_slot in render_slots:
                    if isinstance(render_slot, dict) and render_slot.get("slot_id") == slot["slot_id"]:
                        matching_render_slot = render_slot
                        break
                if not isinstance(matching_render_slot, dict):
                    add_failure(
                        failures,
                        "cross.render.unresolved_hidden",
                        f"{tier} unresolved slot {section_id}.{slot['slot_id']} must remain visible in render output",
                        f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots",
                    )
                    continue
                if matching_render_slot.get("status") != "unresolved" or matching_render_slot.get("value") is not None or matching_render_slot.get("fallback") != fallback:
                    add_failure(
                        failures,
                        "cross.render.unresolved_hidden",
                        f"{tier} unresolved slot {section_id}.{slot['slot_id']} must preserve unresolved mapping exactly",
                        f"render_output.render_artifact.{tier}.body.sections.{section_id}.slots",
                    )

        for section_id in expected_withheld:
            section_payload = landing_sections.get(section_id)
            if not isinstance(section_payload, dict):
                continue
            for slot in ordered_section_slots(section_payload, f"landing_output.landing_artifact.{tier}.sections.{section_id}"):
                if slot.get("status") != "unresolved":
                    continue
                fallback = slot.get("required_input")
                if is_non_empty_str(fallback) and fallback not in expected_required_inputs:
                    expected_required_inputs.append(fallback)

        unexpected_rendered = [section_id for section_id in actual_section_order if section_id in expected_withheld]
        if unexpected_rendered:
            add_failure(
                failures,
                "cross.render.withheld_reintroduced",
                f"{tier} render output must not reintroduce withheld sections {unexpected_rendered}",
                f"render_output.render_artifact.{tier}.body.section_order",
            )
        if any(section_id in expected_withheld for section_id in render_sections):
            add_failure(
                failures,
                "cross.render.withheld_reintroduced",
                f"{tier} render body.sections must exclude withheld landing sections",
                f"render_output.render_artifact.{tier}.body.sections",
            )

        if actual_withheld != expected_withheld:
            add_failure(
                failures,
                "cross.render.withheld_reintroduced",
                f"{tier} render_notes.withheld_sections must match landing withheld sections exactly",
                f"render_output.render_artifact.{tier}.render_notes.withheld_sections",
            )
        if actual_unresolved != expected_unresolved:
            add_failure(
                failures,
                "cross.render.unresolved_hidden",
                f"{tier} render_notes.unresolved_slots must expose unresolved rendered slots in exact order",
                f"render_output.render_artifact.{tier}.render_notes.unresolved_slots",
            )
        if actual_required_inputs != expected_required_inputs:
            add_failure(
                failures,
                "cross.render.required_inputs_visibility",
                f"{tier} render_notes.required_inputs must preserve all visible gaps in exact order",
                f"render_output.render_artifact.{tier}.render_notes.required_inputs",
            )

    return len(failures) == start


def validate_bundle(bundle: Any, snapshot_bundle: Any | None = None) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    report = {
        "result": "fail",
        "case_id": "",
        "bundle_version": None,
        "stage_results": {"portfolio": "skipped", "mapping": "skipped", "jsonld": "skipped", "landing": "skipped", "seo": "skipped", "render": "skipped"},
        "cross_stage_results": {
            "target_alignment": "pass",
            "resolved_value_integrity": "pass",
            "gap_propagation": "pass",
            "no_invented_conditionals": "pass",
            "render_copy_integrity": "skipped",
            "render_gap_visibility": "skipped",
        },
        "snapshot_comparison": {"status": "skipped", "diff_keys": []},
        "failures": failures,
    }

    if not isinstance(bundle, dict):
        add_failure(failures, "bundle.type", "Bundle must be an object", "bundle")
        return report

    report["case_id"] = bundle.get("case_id", "")
    report["bundle_version"] = bundle.get("pipeline_bundle_version")
    stage_specs = active_stage_specs(report["bundle_version"])

    if bundle.get("pipeline_bundle_version") not in ALLOWED_BUNDLE_VERSIONS:
        add_failure(
            failures,
            "bundle.version",
            f"pipeline_bundle_version must be one of {list(ALLOWED_BUNDLE_VERSIONS)}",
            "pipeline_bundle_version",
        )
    if not is_non_empty_str(bundle.get("case_id")):
        add_failure(failures, "bundle.case_id", "case_id must be a non-empty string", "case_id")

    brief = bundle.get("trade_brief")
    if not isinstance(brief, dict):
        add_failure(failures, "bundle.trade_brief", "trade_brief must be an object", "trade_brief")
        brief = {}

    expected = bundle.get("expected")
    if not isinstance(expected, dict):
        add_failure(failures, "bundle.expected", "expected must be an object", "expected")
        expected = {}

    block_stage = expected.get("block_stage")
    expected_signal = expected.get("signal")
    valid_block_stages = {stage_name for stage_name, _, _, _ in stage_specs}
    if block_stage is not None and block_stage not in valid_block_stages:
        add_failure(
            failures,
            "bundle.block_stage",
            f"expected.block_stage must be one of {sorted(valid_block_stages)} or null",
            "expected.block_stage",
        )
        block_stage = None
    if block_stage is None and expected_signal is not None:
        add_failure(
            failures,
            "bundle.signal_without_block",
            "expected.signal must be null when expected.block_stage is null",
            "expected.signal",
        )
    if block_stage is not None and expected_signal not in ALLOWED_BLOCK_SIGNALS:
        add_failure(
            failures,
            "bundle.signal",
            f"expected.signal must be one of {sorted(ALLOWED_BLOCK_SIGNALS)} when blocking is expected",
            "expected.signal",
        )

    block_index = None
    if block_stage is not None:
        for index, (stage_name, _, _, _) in enumerate(stage_specs):
            if stage_name == block_stage:
                block_index = index
                break

    for index, (stage_name, report_key, bundle_key, required_on_nonblocked) in enumerate(stage_specs):
        present = bundle_key in bundle and bundle[bundle_key] is not None
        if block_index is None:
            if required_on_nonblocked and not present:
                add_failure(
                    failures,
                    f"bundle.{report_key}_missing",
                    f"{bundle_key} must be present for a non-blocked bundle",
                    bundle_key,
                )
        else:
            if index < block_index and not present:
                add_failure(
                    failures,
                    f"bundle.{report_key}_missing",
                    f"{bundle_key} must be present before the blocked stage",
                    bundle_key,
                )
            if index >= block_index and present:
                add_failure(
                    failures,
                    f"bundle.{report_key}_unexpected",
                    f"{bundle_key} must be omitted once the pipeline blocks at {block_stage}",
                    bundle_key,
                )

    if bundle.get("pipeline_bundle_version") == "1.1" and bundle.get("seo_output") is not None:
        add_failure(
            failures,
            "bundle.seo_not_allowed",
            "seo_output must be absent for pipeline_bundle_version 1.1",
            "seo_output",
        )
    if bundle.get("pipeline_bundle_version") == "1.2" and block_index is None and bundle.get("seo_output") is None:
        add_failure(
            failures,
            "bundle.seo_required",
            "seo_output must be present for a non-blocked pipeline_bundle_version 1.2 bundle",
            "seo_output",
        )
    if bundle.get("pipeline_bundle_version") in {"1.1", "1.2"} and bundle.get("render_output") is not None:
        add_failure(
            failures,
            "bundle.render_not_allowed",
            f"render_output must be absent for pipeline_bundle_version {bundle.get('pipeline_bundle_version')}",
            "render_output",
        )
    if bundle.get("pipeline_bundle_version") == "1.3.1" and block_index is None and bundle.get("render_output") is None:
        add_failure(
            failures,
            "bundle.render_required",
            "render_output must be present for a non-blocked pipeline_bundle_version 1.3.1 bundle",
            "render_output",
        )

    if block_stage == "portfolio-spectrum-builder":
        violations = critical_portfolio_violations(brief)
        if not violations:
            add_failure(
                failures,
                "bundle.block_without_cause",
                "portfolio-spectrum-builder blocked case must contain at least one real critical brief violation",
                "trade_brief",
            )

    portfolio_meta = None
    if bundle.get("portfolio_output") is not None:
        start = len(failures)
        portfolio_meta = validate_portfolio_output(brief, bundle["portfolio_output"], failures)
        report["stage_results"]["portfolio"] = "pass" if len(failures) == start else "fail"

    mapping_meta = None
    if bundle.get("schema_mapping_output") is not None:
        start = len(failures)
        mapping_meta = validate_schema_mapping_output(brief, portfolio_meta or {"tiers": set(), "tier_targets": {}, "tier_sections": {}}, bundle["schema_mapping_output"], failures)
        report["stage_results"]["mapping"] = "pass" if len(failures) == start else "fail"

    jsonld_meta = None
    if bundle.get("jsonld_output") is not None:
        start = len(failures)
        jsonld_meta = validate_jsonld_output(brief, mapping_meta or {"tiers": set(), "tier_targets": {}, "row_maps": {}}, bundle["jsonld_output"], failures)
        if isinstance(bundle["jsonld_output"], dict):
            jsonld_meta["payloads"] = bundle["jsonld_output"].get("jsonld_payloads", {})
        report["stage_results"]["jsonld"] = "pass" if len(failures) == start else "fail"

    landing_meta = None
    if bundle.get("landing_output") is not None:
        start = len(failures)
        landing_meta = validate_landing_output(
            brief,
            bundle.get("portfolio_output"),
            bundle.get("schema_mapping_output"),
            bundle.get("jsonld_output"),
            bundle["landing_output"],
            failures,
        )
        if isinstance(bundle["landing_output"], dict):
            landing_meta["payloads"] = bundle["landing_output"].get("landing_artifact", {})
        report["stage_results"]["landing"] = "pass" if len(failures) == start else "fail"

    seo_meta = None
    if bundle.get("seo_output") is not None:
        start = len(failures)
        seo_meta = validate_seo_output(
            brief,
            bundle.get("portfolio_output"),
            bundle.get("schema_mapping_output"),
            bundle.get("jsonld_output"),
            bundle.get("landing_output"),
            bundle["seo_output"],
            failures,
        )
        if isinstance(bundle["seo_output"], dict):
            seo_meta["payloads"] = bundle["seo_output"].get("seo_artifact", {})
        report["stage_results"]["seo"] = "pass" if len(failures) == start else "fail"

    render_meta = None
    if bundle.get("render_output") is not None:
        start = len(failures)
        render_meta = validate_render_output(
            bundle.get("landing_output"),
            bundle.get("seo_output"),
            bundle.get("jsonld_output"),
            bundle["render_output"],
            failures,
        )
        if isinstance(bundle["render_output"], dict):
            render_meta["payloads"] = bundle["render_output"].get("render_artifact", {})
        report["stage_results"]["render"] = "pass" if len(failures) == start else "fail"

    if block_index is not None:
        for index, (_, report_key, _, _) in enumerate(stage_specs):
            if index >= block_index:
                report["stage_results"][report_key] = "skipped"

    if not cross_stage_target_alignment(portfolio_meta, mapping_meta, jsonld_meta, failures):
        report["cross_stage_results"]["target_alignment"] = "fail"
    if not cross_stage_resolved_value_integrity(brief, mapping_meta, failures):
        report["cross_stage_results"]["resolved_value_integrity"] = "fail"
    if not cross_stage_gap_propagation(brief, mapping_meta, jsonld_meta, landing_meta, seo_meta, failures):
        report["cross_stage_results"]["gap_propagation"] = "fail"
    if not cross_stage_no_invented_conditionals(brief, mapping_meta, jsonld_meta, landing_meta, failures):
        report["cross_stage_results"]["no_invented_conditionals"] = "fail"
    if render_meta is not None:
        report["cross_stage_results"]["render_copy_integrity"] = "pass"
        report["cross_stage_results"]["render_gap_visibility"] = "pass"
        if not cross_stage_render_copy_integrity(landing_meta, seo_meta, jsonld_meta, render_meta, failures):
            report["cross_stage_results"]["render_copy_integrity"] = "fail"
        if not cross_stage_render_gap_visibility(landing_meta, render_meta, failures):
            report["cross_stage_results"]["render_gap_visibility"] = "fail"

    if snapshot_bundle is not None:
        diff_keys = diff_paths(bundle, snapshot_bundle)
        report["snapshot_comparison"] = {
            "status": "pass" if not diff_keys else "fail",
            "diff_keys": diff_keys,
        }
        if diff_keys:
            add_failure(
                failures,
                "snapshot.diff",
                "Bundle does not match the expected snapshot bundle",
                diff_keys[0],
            )

    report["result"] = "pass" if not failures else "fail"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the structured output pipeline bundle.")
    parser.add_argument("--bundle", required=True, help="Path to the pipeline bundle YAML or JSON file.")
    parser.add_argument(
        "--snapshot",
        help="Optional path to a canonical snapshot bundle for exact deterministic comparison.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "yaml"),
        default="json",
        help="Output report format.",
    )
    args = parser.parse_args()

    try:
        bundle = load_document(Path(args.bundle))
        snapshot_bundle = load_document(Path(args.snapshot)) if args.snapshot else None
    except Exception as exc:  # pragma: no cover - CLI failure surface
        print(json.dumps({"result": "fail", "failures": [{"code": "bundle.load", "message": str(exc)}]}, ensure_ascii=False, indent=2))
        return 1

    report = validate_bundle(bundle, snapshot_bundle)
    if args.format == "yaml":
        print(yaml.safe_dump(report, sort_keys=False, allow_unicode=True))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
