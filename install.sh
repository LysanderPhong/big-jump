#!/usr/bin/env bash
# Install or update the complete BuildBuddy skill folder.
# Usage: bash install.sh
set -euo pipefail

REPO_URL="https://github.com/LysanderPhong/buildbuddy"
ARCHIVE_URL="${BUILDBUDDY_ARCHIVE_URL:-https://codeload.github.com/LysanderPhong/buildbuddy/tar.gz/refs/heads/main}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd -P)"
REQUESTED_SKILL_DIR="${BUILDBUDDY_SKILL_DIR:-${CODEX_HOME:-${HOME}/.codex}/skills/buildbuddy}"
PYTHON_BIN="${BUILDBUDDY_PYTHON:-python3}"
DOWNLOAD_DIR=""
STAGING_PARENT=""
BACKUP_PARENT=""
INSTALL_COMPLETE=0
SWAP_STARTED=0

required_files=(
  "SKILL.md"
  "agents/openai.yaml"
  "assets/PROJECT_NOTES.template.md"
  "evals/evals.json"
  "evals/README.md"
  "references/project-profiles.md"
  "references/verification-playbook.md"
  "references/guided-mode.md"
  "references/release-and-deployment.md"
  "references/ideation-and-coaching.md"
  "scripts/validate_skill.py"
  "scripts/test_validator.py"
  "scripts/test_installer.py"
)
managed_entries=(SKILL.md agents assets evals references scripts)

fail() {
  echo "Install failed: $*" >&2
  exit 1
}

cleanup() {
  local exit_status=$?
  trap - EXIT

  if [[ ${exit_status} -ne 0 && -n "${BACKUP_PARENT}" \
    && -e "${BACKUP_PARENT}/buildbuddy" && ! -e "${SKILL_DIR:-}" ]]; then
    if ! "${PYTHON_BIN}" -c 'import os, sys; os.rename(sys.argv[1], sys.argv[2])' \
      "${BACKUP_PARENT}/buildbuddy" "${SKILL_DIR}"; then
      echo "Recovery failed: the previous installation remains at ${BACKUP_PARENT}/buildbuddy" >&2
    fi
  elif [[ ${exit_status} -ne 0 && ${SWAP_STARTED} -eq 1 \
    && -n "${BACKUP_PARENT}" && -e "${BACKUP_PARENT}/buildbuddy" ]]; then
    echo "Install aborted because the destination changed during replacement." >&2
    echo "The previous installation is preserved at ${BACKUP_PARENT}/buildbuddy" >&2
  fi

  if [[ -n "${STAGING_PARENT}" && -d "${STAGING_PARENT}" ]]; then
    rm -rf -- "${STAGING_PARENT}"
  fi
  if [[ -n "${DOWNLOAD_DIR}" && -d "${DOWNLOAD_DIR}" ]]; then
    rm -rf -- "${DOWNLOAD_DIR}"
  fi
  if [[ ${INSTALL_COMPLETE} -eq 1 && -n "${BACKUP_PARENT}" \
    && -d "${BACKUP_PARENT}" ]]; then
    rm -rf -- "${BACKUP_PARENT}"
  elif [[ -n "${BACKUP_PARENT}" && -d "${BACKUP_PARENT}" \
    && ! -e "${BACKUP_PARENT}/buildbuddy" ]]; then
    rmdir -- "${BACKUP_PARENT}" 2>/dev/null || true
  fi

  exit "${exit_status}"
}
trap cleanup EXIT

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  fail "python3 is required to validate a complete installation"
fi

if [[ "${REQUESTED_SKILL_DIR}" != /* ]]; then
  REQUESTED_SKILL_DIR="${PWD}/${REQUESTED_SKILL_DIR}"
fi
if [[ -L "${REQUESTED_SKILL_DIR}" ]]; then
  fail "the destination itself must not be a symbolic link: ${REQUESTED_SKILL_DIR}"
fi

SKILL_DIR="$("${PYTHON_BIN}" -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "${REQUESTED_SKILL_DIR}")"
if [[ "$(basename -- "${SKILL_DIR}")" != "buildbuddy" ]]; then
  fail "the destination directory must be named buildbuddy: ${SKILL_DIR}. To install elsewhere, set BUILDBUDDY_SKILL_DIR to a path ending in /buildbuddy, for example BUILDBUDDY_SKILL_DIR=/my/own/skills/buildbuddy"
fi
SKILL_PARENT="$(dirname -- "${SKILL_DIR}")"

looks_like_complete_source() {
  local candidate=$1
  local relative_path
  for relative_path in "${required_files[@]}"; do
    [[ -s "${candidate}/${relative_path}" ]] || return 1
  done
}

if [[ -n "${BUILDBUDDY_SOURCE_DIR:-}" ]]; then
  if [[ -L "${BUILDBUDDY_SOURCE_DIR}" ]]; then
    fail "the source directory must not be a symbolic link: ${BUILDBUDDY_SOURCE_DIR}"
  fi
  [[ -d "${BUILDBUDDY_SOURCE_DIR}" ]] || fail "source directory not found: ${BUILDBUDDY_SOURCE_DIR}"
  SOURCE_DIR="$(cd -- "${BUILDBUDDY_SOURCE_DIR}" && pwd -P)"
  SOURCE_LABEL="explicit local source ${SOURCE_DIR}"
elif looks_like_complete_source "${SCRIPT_DIR}"; then
  SOURCE_DIR="${SCRIPT_DIR}"
  SOURCE_LABEL="local checkout ${SOURCE_DIR}"
else
  command -v curl >/dev/null 2>&1 || fail "curl is required when install.sh is run outside a checkout"
  command -v tar >/dev/null 2>&1 || fail "tar is required when install.sh is run outside a checkout"
  DOWNLOAD_DIR="$(mktemp -d)"
  curl -fsSL "${ARCHIVE_URL}" -o "${DOWNLOAD_DIR}/buildbuddy.tar.gz"
  tar -xzf "${DOWNLOAD_DIR}/buildbuddy.tar.gz" -C "${DOWNLOAD_DIR}"
  mv -- "${DOWNLOAD_DIR}/buildbuddy-main" "${DOWNLOAD_DIR}/buildbuddy"
  SOURCE_DIR="${DOWNLOAD_DIR}/buildbuddy"
  SOURCE_LABEL="main-branch archive from ${REPO_URL}"
fi

if [[ "${SOURCE_DIR}" == "${SKILL_DIR}" ]]; then
  fail "source and destination resolve to the same directory"
fi
case "${SKILL_DIR}/" in
  "${SOURCE_DIR}/"*) fail "destination must not be inside the source directory" ;;
esac
case "${SOURCE_DIR}/" in
  "${SKILL_DIR}/"*) fail "source must not be inside the destination directory" ;;
esac

reject_runtime_symlinks() {
  local root=$1
  local label=$2
  local entry
  local first_link
  for entry in "${managed_entries[@]}"; do
    if [[ -L "${root}/${entry}" ]]; then
      fail "${label} contains a symbolic link at ${entry}"
    fi
    if [[ -d "${root}/${entry}" ]]; then
      first_link="$(find "${root}/${entry}" -type l -print -quit)"
      if [[ -n "${first_link}" ]]; then
        fail "${label} contains a symbolic link: ${first_link}"
      fi
    fi
  done
}

reject_runtime_symlinks "${SOURCE_DIR}" "source"
for relative_path in "${required_files[@]}"; do
  if [[ ! -s "${SOURCE_DIR}/${relative_path}" || -L "${SOURCE_DIR}/${relative_path}" ]]; then
    fail "required source file is missing, empty, or unsafe: ${relative_path}"
  fi
done
"${PYTHON_BIN}" "${SOURCE_DIR}/scripts/validate_skill.py" "${SOURCE_DIR}"

if [[ -e "${SKILL_DIR}" ]]; then
  [[ -d "${SKILL_DIR}" ]] || fail "destination exists but is not a directory: ${SKILL_DIR}"
  reject_runtime_symlinks "${SKILL_DIR}" "destination"
fi

mkdir -p -- "${SKILL_PARENT}"
STAGING_PARENT="$(mktemp -d "${SKILL_PARENT}/.buildbuddy-stage.XXXXXX")"
STAGING_DIR="${STAGING_PARENT}/buildbuddy"
mkdir -- "${STAGING_DIR}"
cp -- "${SOURCE_DIR}/SKILL.md" "${STAGING_DIR}/SKILL.md"
for managed_dir in agents assets evals references scripts; do
  cp -R -- "${SOURCE_DIR}/${managed_dir}" "${STAGING_DIR}/${managed_dir}"
done
reject_runtime_symlinks "${STAGING_DIR}" "staging copy"
for relative_path in "${required_files[@]}"; do
  if [[ ! -s "${STAGING_DIR}/${relative_path}" || -L "${STAGING_DIR}/${relative_path}" ]]; then
    fail "required staged file is missing, empty, or unsafe: ${relative_path}"
  fi
done

CONTENT_SHA256="$("${PYTHON_BIN}" "${STAGING_DIR}/scripts/validate_skill.py" --fingerprint "${STAGING_DIR}")"
COMMIT_SHA="not-recorded"
if command -v git >/dev/null 2>&1 \
  && git -C "${SOURCE_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  COMMIT_SHA="$(git -C "${SOURCE_DIR}" rev-parse HEAD 2>/dev/null || echo not-recorded)"
  if [[ -n "$(git -C "${SOURCE_DIR}" status --porcelain 2>/dev/null)" ]]; then
    COMMIT_SHA="${COMMIT_SHA}-with-local-changes"
  fi
fi
SOURCE_LABEL="${SOURCE_LABEL//$'\n'/ }"

{
  echo "repo: ${REPO_URL}"
  echo "commit: ${COMMIT_SHA}"
  echo "content-sha256: ${CONTENT_SHA256}"
  echo "source: ${SOURCE_LABEL}"
  echo "installed: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${STAGING_DIR}/install-info.txt"

"${PYTHON_BIN}" "${STAGING_DIR}/scripts/validate_skill.py" "${STAGING_DIR}"

if [[ -e "${SKILL_DIR}" ]]; then
  BACKUP_PARENT="$(mktemp -d "${SKILL_PARENT}/.buildbuddy-backup.XXXXXX")"
  SWAP_STARTED=1
  "${PYTHON_BIN}" -c 'import os, sys; os.rename(sys.argv[1], sys.argv[2])' \
    "${SKILL_DIR}" "${BACKUP_PARENT}/buildbuddy"
else
  SWAP_STARTED=1
fi
"${PYTHON_BIN}" -c 'import os, sys; os.rename(sys.argv[1], sys.argv[2])' \
  "${STAGING_DIR}" "${SKILL_DIR}"
"${PYTHON_BIN}" "${SKILL_DIR}/scripts/validate_skill.py" "${SKILL_DIR}"
FINAL_SHA256="$("${PYTHON_BIN}" "${SKILL_DIR}/scripts/validate_skill.py" --fingerprint "${SKILL_DIR}")"
if [[ "${FINAL_SHA256}" != "${CONTENT_SHA256}" ]]; then
  fail "final content fingerprint changed during replacement"
fi
INSTALL_COMPLETE=1

echo "Installed BuildBuddy to ${SKILL_DIR}"
echo "The complete skill includes its profiles, verification playbook, metadata, template, and evals."
echo "Content fingerprint: ${CONTENT_SHA256}"
echo "Re-run this script to update. Restart Codex only if the updated skill does not appear automatically."
