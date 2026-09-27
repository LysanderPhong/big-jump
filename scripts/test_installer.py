#!/usr/bin/env python3
"""Regression tests for the atomic BuildBuddy installer."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Mapping, Optional


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ENTRIES = ("SKILL.md", "agents", "assets", "evals", "references", "scripts")


def run_install(
    destination: Path,
    *,
    source: Optional[Path] = None,
    python_bin: Optional[str] = None,
    script_path: Optional[Path] = None,
    archive_url: Optional[str] = None,
    extra_env: Optional[Mapping[str, str]] = None,
    should_succeed: bool,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BUILDBUDDY_SKILL_DIR"] = str(destination)
    if source is None:
        env.pop("BUILDBUDDY_SOURCE_DIR", None)
    else:
        env["BUILDBUDDY_SOURCE_DIR"] = str(source)
    if python_bin is None:
        env.pop("BUILDBUDDY_PYTHON", None)
    else:
        env["BUILDBUDDY_PYTHON"] = python_bin
    if archive_url is None:
        env.pop("BUILDBUDDY_ARCHIVE_URL", None)
    else:
        env["BUILDBUDDY_ARCHIVE_URL"] = archive_url
    if extra_env:
        env.update(extra_env)
    selected_script = script_path or (ROOT / "install.sh")
    result = subprocess.run(
        ["bash", str(selected_script)],
        cwd=selected_script.parent,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if (result.returncode == 0) != should_succeed:
        expected = "success" if should_succeed else "failure"
        raise AssertionError(
            f"expected installer {expected}, got exit {result.returncode}:\n{result.stdout}"
        )
    return result


def copy_source(parent: Path) -> Path:
    destination = parent / "buildbuddy"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"),
    )
    return destination


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(relative)
        if path.is_symlink():
            digest.update(b"symlink\0")
            digest.update(os.readlink(path).encode())
        elif path.is_file():
            digest.update(b"file\0")
            digest.update(path.read_bytes())
        elif path.is_dir():
            digest.update(b"dir\0")
    return digest.hexdigest()


def assert_runtime_matches(source: Path, destination: Path) -> None:
    expected: dict[str, bytes] = {}
    actual: dict[str, bytes] = {}
    for entry in RUNTIME_ENTRIES:
        source_path = source / entry
        paths = [source_path] if source_path.is_file() else source_path.rglob("*")
        for path in paths:
            if path.is_file():
                expected[path.relative_to(source).as_posix()] = path.read_bytes()
    for path in destination.rglob("*"):
        if path.is_file() and path.name != "install-info.txt":
            actual[path.relative_to(destination).as_posix()] = path.read_bytes()
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        changed = sorted(key for key in set(actual) & set(expected) if actual[key] != expected[key])
        raise AssertionError(f"installed runtime mismatch: missing={missing}, extra={extra}, changed={changed}")


def assert_fingerprint_matches(destination: Path) -> None:
    info = (destination / "install-info.txt").read_text(encoding="utf-8").splitlines()
    recorded = next(line.split(": ", 1)[1] for line in info if line.startswith("content-sha256: "))
    result = subprocess.run(
        [
            sys.executable,
            str(destination / "scripts" / "validate_skill.py"),
            "--fingerprint",
            str(destination),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    assert result.stdout.strip() == recorded, "install-info fingerprint does not match installed bytes"


def test_clean_and_repeat_update(temp_root: Path) -> None:
    destination = temp_root / "clean" / "buildbuddy"
    result = run_install(destination, should_succeed=True)
    assert "Content fingerprint:" in result.stdout
    assert_runtime_matches(ROOT, destination)
    assert_fingerprint_matches(destination)

    stale = destination / "references" / "removed-in-new-version.md"
    stale.write_text("stale", encoding="utf-8")
    run_install(destination, source=ROOT, should_succeed=True)
    assert not stale.exists(), "a complete update must remove stale managed files"
    assert_runtime_matches(ROOT, destination)


def test_standalone_archive_install(temp_root: Path) -> None:
    standalone = temp_root / "standalone"
    standalone.mkdir()
    script_path = standalone / "install.sh"
    shutil.copy2(ROOT / "install.sh", script_path)
    archive = temp_root / "buildbuddy-main.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for entry in RUNTIME_ENTRIES:
            bundle.add(ROOT / entry, arcname=f"buildbuddy-main/{entry}")

    destination = temp_root / "archive-target" / "buildbuddy"
    run_install(
        destination,
        script_path=script_path,
        archive_url=archive.as_uri(),
        should_succeed=True,
    )
    assert_runtime_matches(ROOT, destination)


def test_invalid_update_preserves_previous_version(temp_root: Path) -> None:
    destination = temp_root / "rollback" / "buildbuddy"
    run_install(destination, source=ROOT, should_succeed=True)
    before = tree_digest(destination)

    invalid_source = copy_source(temp_root / "invalid-source")
    skill_path = invalid_source / "SKILL.md"
    skill_path.write_text(
        skill_path.read_text(encoding="utf-8")
        + "\n[broken link](references/does-not-exist.md)\n",
        encoding="utf-8",
    )
    run_install(destination, source=invalid_source, should_succeed=False)
    assert tree_digest(destination) == before, "a failed update changed the working installation"


def test_empty_runtime_source_fails_closed(temp_root: Path) -> None:
    for index, relative_path in enumerate(
        (
            "references/project-profiles.md",
            "scripts/validate_skill.py",
            "scripts/test_installer.py",
        )
    ):
        source = copy_source(temp_root / f"empty-source-{index}")
        (source / relative_path).write_text("", encoding="utf-8")
        destination = temp_root / f"empty-target-{index}" / "buildbuddy"
        run_install(destination, source=source, should_succeed=False)
        assert not destination.exists(), f"installer accepted empty runtime file: {relative_path}"


def test_concurrent_target_preserves_backup_without_nesting(temp_root: Path) -> None:
    destination = temp_root / "concurrent-target" / "buildbuddy"
    run_install(destination, source=ROOT, should_succeed=True)
    before = tree_digest(destination)

    shim = temp_root / "python-rename-fault-shim"
    shim.write_text(
        f"#!{sys.executable}\n"
        "import os\n"
        "import sys\n"
        "if (len(sys.argv) >= 5 and sys.argv[1] == '-c' "
        "and 'os.rename' in sys.argv[2] and '.buildbuddy-stage.' in sys.argv[3]):\n"
        "    os.mkdir(sys.argv[4])\n"
        "    with open(os.path.join(sys.argv[4], 'concurrent-sentinel'), 'w') as handle:\n"
        "        handle.write('do not overwrite')\n"
        "real_python = os.environ['BUILDBUDDY_REAL_PYTHON']\n"
        "os.execv(real_python, [real_python, *sys.argv[1:]])\n",
        encoding="utf-8",
    )
    shim.chmod(0o755)

    result = run_install(
        destination,
        source=ROOT,
        python_bin=str(shim),
        extra_env={"BUILDBUDDY_REAL_PYTHON": sys.executable},
        should_succeed=False,
    )
    assert (destination / "concurrent-sentinel").is_file()
    assert not (destination / "buildbuddy").exists(), "staging was nested into a concurrent target"
    backups = list(destination.parent.glob(".buildbuddy-backup.*/buildbuddy"))
    assert len(backups) == 1, "the prior installation backup was not preserved"
    assert tree_digest(backups[0]) == before, "the preserved backup changed"
    assert "previous installation is preserved" in result.stdout.lower()


def test_destination_symlink_is_rejected(temp_root: Path) -> None:
    destination = temp_root / "destination-link" / "buildbuddy"
    run_install(destination, source=ROOT, should_succeed=True)
    outside = temp_root / "outside-destination"
    outside.mkdir()
    shutil.rmtree(destination / "agents")
    (destination / "agents").symlink_to(outside, target_is_directory=True)

    run_install(destination, source=ROOT, should_succeed=False)
    assert not (outside / "openai.yaml").exists(), "installer followed a destination symlink"


def test_source_symlink_is_rejected(temp_root: Path) -> None:
    source = copy_source(temp_root / "source-link")
    outside = temp_root / "outside-source"
    shutil.copytree(source / "agents", outside)
    shutil.rmtree(source / "agents")
    (source / "agents").symlink_to(outside, target_is_directory=True)
    destination = temp_root / "source-link-target" / "buildbuddy"

    run_install(destination, source=source, should_succeed=False)
    assert not destination.exists(), "installer accepted a source symlink"


def test_source_target_relationships_are_rejected(temp_root: Path) -> None:
    source = copy_source(temp_root / "relationships")
    before = tree_digest(source)
    run_install(source, source=source, should_succeed=False)
    assert tree_digest(source) == before, "source==destination changed the source"

    nested = source / "nested" / "buildbuddy"
    run_install(nested, source=source, should_succeed=False)
    assert not nested.exists(), "installer created a destination inside its source"


def test_missing_python_fails_closed(temp_root: Path) -> None:
    destination = temp_root / "no-python" / "buildbuddy"
    missing_python = str(temp_root / "missing-python")
    run_install(
        destination,
        source=ROOT,
        python_bin=missing_python,
        should_succeed=False,
    )
    assert not destination.exists(), "installer claimed completeness without validation"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="buildbuddy-installer-tests-") as temp:
        temp_root = Path(temp)
        test_clean_and_repeat_update(temp_root)
        test_standalone_archive_install(temp_root)
        test_invalid_update_preserves_previous_version(temp_root)
        test_empty_runtime_source_fails_closed(temp_root)
        test_concurrent_target_preserves_backup_without_nesting(temp_root)
        test_destination_symlink_is_rejected(temp_root)
        test_source_symlink_is_rejected(temp_root)
        test_source_target_relationships_are_rejected(temp_root)
        test_missing_python_fails_closed(temp_root)
    print(
        "PASS: installer clean, archive, update, rollback, concurrent-target, symlink, "
        "relationship, and fail-closed tests"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
