#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

SUPPORTED_TIERS = ("lite", "default", "premium")
SUPPORTED_TARGETS = ("LocalBusiness", "ProfessionalService")
REQUIRED_BRIEF_FIELDS = ("trade_type", "primary_locality", "service_scope", "whatsapp_target")
STAGE_ORDER = (
    ("portfolio-spectrum-builder", "portfolio", "portfolio_output"),
    ("schema-mapper", "mapping", "schema_mapping_output"),
    ("jsonld-generator", "jsonld", "jsonld_output"),
)
ALLOWED_BLOCK_SIGNALS = {"Ω_INSUFFICIENT_DATA"}


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
    return len(failures) == start


def cross_stage_no_invented_conditionals(
    brief: dict[str, Any],
    mapping_meta: dict[str, Any] | None,
    jsonld_meta: dict[str, Any] | None,
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
    return len(failures) == start


def validate_bundle(bundle: Any, snapshot_bundle: Any | None = None) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    report = {
        "result": "fail",
        "case_id": "",
        "bundle_version": None,
        "stage_results": {"portfolio": "skipped", "mapping": "skipped", "jsonld": "skipped"},
        "cross_stage_results": {
            "target_alignment": "pass",
            "resolved_value_integrity": "pass",
            "gap_propagation": "pass",
            "no_invented_conditionals": "pass",
        },
        "snapshot_comparison": {"status": "skipped", "diff_keys": []},
        "failures": failures,
    }

    if not isinstance(bundle, dict):
        add_failure(failures, "bundle.type", "Bundle must be an object", "bundle")
        return report

    report["case_id"] = bundle.get("case_id", "")
    report["bundle_version"] = bundle.get("pipeline_bundle_version")

    if bundle.get("pipeline_bundle_version") != "1.1":
        add_failure(
            failures,
            "bundle.version",
            "pipeline_bundle_version must be 1.1",
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
    valid_block_stages = {stage_name for stage_name, _, _ in STAGE_ORDER}
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
        for index, (stage_name, _, _) in enumerate(STAGE_ORDER):
            if stage_name == block_stage:
                block_index = index
                break

    for index, (stage_name, report_key, bundle_key) in enumerate(STAGE_ORDER):
        present = bundle_key in bundle and bundle[bundle_key] is not None
        if block_index is None:
            if not present:
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

    if block_index is not None:
        for index, (_, report_key, _) in enumerate(STAGE_ORDER):
            if index >= block_index:
                report["stage_results"][report_key] = "skipped"

    if not cross_stage_target_alignment(portfolio_meta, mapping_meta, jsonld_meta, failures):
        report["cross_stage_results"]["target_alignment"] = "fail"
    if not cross_stage_resolved_value_integrity(brief, mapping_meta, failures):
        report["cross_stage_results"]["resolved_value_integrity"] = "fail"
    if not cross_stage_gap_propagation(brief, mapping_meta, jsonld_meta, failures):
        report["cross_stage_results"]["gap_propagation"] = "fail"
    if not cross_stage_no_invented_conditionals(brief, mapping_meta, jsonld_meta, failures):
        report["cross_stage_results"]["no_invented_conditionals"] = "fail"

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
    parser = argparse.ArgumentParser(description="Validate the structured output pipeline V1.1 bundle.")
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
