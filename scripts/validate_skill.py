#!/usr/bin/env python3
"""Validate BuildBuddy without third-party Python packages."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import NoReturn


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class ValidationError(Exception):
    pass


def fail(message: str) -> NoReturn:
    raise ValidationError(message)


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, str], str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with a YAML frontmatter fence")
    try:
        closing = text.index("\n---\n", 4)
    except ValueError:
        fail("SKILL.md frontmatter is missing its closing fence")

    lines = text[4:closing].splitlines()
    values: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([a-z_]+):\s*(.*)", line)
        if not match:
            fail(f"invalid frontmatter line: {line!r}")
        key, raw = match.groups()
        if key in values:
            fail(f"duplicate frontmatter key: {key}")
        if key == "name":
            values[key] = raw
        elif key == "description":
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                fail(f"description must be a valid double-quoted YAML/JSON string: {exc}")
            if not isinstance(value, str):
                fail("description must be a string")
            values[key] = value
        else:
            fail(f"unexpected frontmatter key: {key}")

    if set(values) != {"name", "description"}:
        fail("frontmatter must contain exactly name and description")
    return values, text[closing + 5 :]


def validate_frontmatter(root: Path) -> None:
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        fail("SKILL.md is missing")
    values, body = parse_frontmatter(skill_md)
    if not NAME_RE.fullmatch(values["name"]):
        fail("name must use lowercase letters, digits, and hyphens")
    if values["name"] != root.name:
        fail("frontmatter name must match the skill directory")
    description = values["description"]
    if not 80 <= len(description) <= 900:
        fail("description must be specific but concise (80-900 characters)")
    if not body.strip():
        fail("SKILL.md body is empty")
    line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        fail(f"SKILL.md has {line_count} lines; split detail into references")


def validate_local_links(root: Path) -> None:
    markdown_files = [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]
    for markdown in markdown_files:
        if not markdown.is_file():
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LOCAL_LINK_RE.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith(("#", "mailto:")):
                continue
            resolved = (markdown.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                fail(f"{markdown.relative_to(root)} links outside the skill: {raw_target}")
            if not resolved.exists():
                fail(f"broken local link in {markdown.relative_to(root)}: {raw_target}")


def validate_openai_yaml(root: Path) -> None:
    metadata = root / "agents" / "openai.yaml"
    if not metadata.is_file():
        fail("agents/openai.yaml is missing")
    lines = [line for line in metadata.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines or lines[0] != "interface:":
        fail("agents/openai.yaml must contain one top-level interface mapping")
    values: dict[str, str] = {}
    for line in lines[1:]:
        match = re.fullmatch(r"  ([a-z_]+):\s*(\".*\")", line)
        if not match:
            fail(f"invalid agents/openai.yaml line: {line!r}")
        key, raw = match.groups()
        if key in values:
            fail(f"duplicate agents/openai.yaml field: {key}")
        if key not in {"display_name", "short_description", "default_prompt"}:
            fail(f"unexpected agents/openai.yaml field: {key}")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"invalid quoted value for agents/openai.yaml {key}: {exc}")
        if not isinstance(parsed, str) or not parsed:
            fail(f"agents/openai.yaml {key} must be a non-empty string")
        values[key] = parsed
    required = {"display_name", "short_description", "default_prompt"}
    if set(values) != required:
        fail(f"agents/openai.yaml must contain exactly: {', '.join(sorted(required))}")
    short = values["short_description"]
    if not 25 <= len(short) <= 64:
        fail("openai.yaml short_description must be 25-64 characters")
    prompt = values["default_prompt"]
    if "$buildbuddy" not in prompt:
        fail("openai.yaml default_prompt must mention $buildbuddy")


def validate_runtime_files(root: Path) -> None:
    required = [
        "references/project-profiles.md",
        "references/verification-playbook.md",
        "references/guided-mode.md",
        "references/release-and-deployment.md",
        "references/ideation-and-coaching.md",
        "assets/PROJECT_NOTES.template.md",
        "evals/README.md",
        "scripts/validate_skill.py",
        "scripts/test_installer.py",
        "scripts/test_validator.py",
    ]
    missing = [
        path
        for path in required
        if not (root / path).is_file() or (root / path).stat().st_size == 0
    ]
    if missing:
        fail(
            f"missing or empty runtime files: {', '.join(missing)}. "
            "Install by copying the whole skill folder (SKILL.md plus references/, "
            "assets/, agents/, evals/, and scripts/), not only SKILL.md."
        )

    core = (root / "SKILL.md").read_text(encoding="utf-8")
    legacy_patterns = [
        "logic.js",
        "tests/check.sh",
        "one commit per phase",
        "install a real git pre-commit hook",
    ]
    found = [pattern for pattern in legacy_patterns if pattern.lower() in core.lower()]
    if found:
        fail(f"stack-specific legacy rules leaked into the core: {', '.join(found)}")


def validate_evals(root: Path) -> None:
    path = root / "evals" / "evals.json"
    if not path.is_file():
        fail("evals/evals.json is missing")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"evals/evals.json is invalid JSON: {exc}")
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or len(cases) < 8:
        fail("evals must contain at least 8 realistic cases")

    ids: set[str] = set()
    trigger_values: set[bool] = set()
    covered_engagements: set[str] = set()
    covered_profiles: set[str] = set()
    valid_engagements = {"direction finding", "new build", "existing project", "spike"}
    valid_profiles = {
        "web UI",
        "backend/API",
        "CLI/automation",
        "data/AI",
        "library/SDK",
        "mobile/desktop",
    }
    valid_overlays = {
        "production data",
        "sensitive data",
        "third-party writes",
        "paid resources",
        "publication or deployment",
        "signing or stores",
        "destructive operations",
    }
    for case in cases:
        if not isinstance(case, dict):
            fail("every eval case must be an object")
        case_id = case.get("id")
        prompt = case.get("prompt")
        should_trigger = case.get("should_trigger")
        if not isinstance(case_id, str) or not case_id:
            fail("every eval case needs a non-empty id")
        if case_id in ids:
            fail(f"duplicate eval id: {case_id}")
        ids.add(case_id)
        if not isinstance(prompt, str) or len(prompt) < 20:
            fail(f"eval {case_id} needs a realistic prompt")
        if not isinstance(should_trigger, bool):
            fail(f"eval {case_id} needs a boolean should_trigger")
        trigger_values.add(should_trigger)
        if should_trigger:
            route = case.get("expected_route")
            if not isinstance(route, dict):
                fail(f"trigger eval {case_id} needs an expected_route")
            engagement = route.get("engagement")
            if engagement not in valid_engagements:
                fail(f"eval {case_id} has an invalid engagement")
            covered_engagements.add(engagement)
            profiles = route.get("profiles")
            if not isinstance(profiles, list) or not all(
                isinstance(profile, str) and profile for profile in profiles
            ):
                fail(f"eval {case_id} profiles must be a string list")
            if engagement == "direction finding" and profiles:
                fail(f"eval {case_id} must defer profiles during direction finding")
            if engagement != "direction finding" and not profiles:
                fail(f"eval {case_id} needs one or more expected profiles")
            unknown_profiles = sorted(set(profiles) - valid_profiles)
            if unknown_profiles:
                fail(f"eval {case_id} uses unknown profiles: {', '.join(unknown_profiles)}")
            overlays = route.get("risk_overlays")
            if not isinstance(overlays, list) or not all(
                isinstance(overlay, str) and overlay for overlay in overlays
            ):
                fail(f"eval {case_id} risk_overlays must be a string list")
            unknown_overlays = sorted(set(overlays) - valid_overlays)
            if unknown_overlays:
                fail(f"eval {case_id} uses unknown overlays: {', '.join(unknown_overlays)}")
            must_include = case.get("must_include")
            must_avoid = case.get("must_avoid")
            if not isinstance(must_include, list) or len(must_include) < 2 or not all(
                isinstance(item, str) and item for item in must_include
            ):
                fail(f"trigger eval {case_id} needs at least two must_include checks")
            if not isinstance(must_avoid, list) or not must_avoid or not all(
                isinstance(item, str) and item for item in must_avoid
            ):
                fail(f"trigger eval {case_id} needs at least one must_avoid check")
            covered_profiles.update(profiles)
        elif not isinstance(case.get("exclusion_reason"), str) or not case[
            "exclusion_reason"
        ].strip():
            fail(f"non-trigger eval {case_id} needs an exclusion_reason")
    if trigger_values != {False, True}:
        fail("evals must include trigger and near-miss non-trigger cases")
    missing_engagements = sorted(valid_engagements - covered_engagements)
    if missing_engagements:
        fail(f"evals do not cover engagements: {', '.join(missing_engagements)}")
    missing_profiles = sorted(valid_profiles - covered_profiles)
    if missing_profiles:
        fail(f"evals do not cover profiles: {', '.join(missing_profiles)}")


def content_fingerprint(root: Path) -> str:
    hasher = hashlib.sha256()
    paths = [root / "SKILL.md"]
    for directory in ("agents", "assets", "evals", "references", "scripts"):
        paths.extend(path for path in (root / directory).rglob("*") if path.is_file())
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        hasher.update(len(relative).to_bytes(8, "big"))
        hasher.update(relative)
        data = path.read_bytes()
        hasher.update(len(data).to_bytes(8, "big"))
        hasher.update(data)
    return hasher.hexdigest()


def main() -> int:
    fingerprint_mode = len(sys.argv) > 1 and sys.argv[1] == "--fingerprint"
    root_arg = sys.argv[2] if fingerprint_mode and len(sys.argv) > 2 else (
        sys.argv[1] if len(sys.argv) > 1 else "."
    )
    root = Path(root_arg).resolve()
    try:
        validate_frontmatter(root)
        validate_runtime_files(root)
        validate_local_links(root)
        validate_openai_yaml(root)
        validate_evals(root)
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if fingerprint_mode:
        print(content_fingerprint(root))
    else:
        print("PASS: BuildBuddy skill structure, metadata, links, and evals are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
