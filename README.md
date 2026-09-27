# BuildBuddy 🚀

Previously called **Big Jump**. The skill is now invoked as `$buildbuddy`; new installations use the `buildbuddy` folder. Existing installations are not renamed automatically.

> **From “I don't know what to build” to a verified first release.**

[![check-skill](https://github.com/LysanderPhong/buildbuddy/actions/workflows/check-skill.yml/badge.svg)](https://github.com/LysanderPhong/buildbuddy/actions/workflows/check-skill.yml) · 🌐 [Website](https://lysanderphong.github.io/buildbuddy/) · [中文版 README](README.zh.md)

BuildBuddy turns a coding agent into an autonomous builder-coach. Bring a rough idea—or only the skills you have, a recurring problem around you, and a goal such as a credible portfolio or a first software-income experiment. It helps choose a direction, scopes the smallest useful release, builds in testable slices, and verifies through the real entry point.

## For students who learned to code but still feel stuck

You may know some Python, Java, frontend, or data analysis and have completed plenty of coursework—yet still have nothing a real person can use, test, and hear you explain. BuildBuddy began from a gap familiar to many students at China's 985/211 universities: learning plenty without a path from knowledge to a real user. The school label is context, not an entry requirement.

Some students want credible portfolio evidence. Others see people earn from websites, small tools, or indie products and want to test a first software-income hypothesis. Either way, the missing step is usually not another tutorial; it is choosing one reachable problem, finding a first user, and making the first release small enough to finish.

BuildBuddy is for that gap between “I have learned things” and “I shipped something real.” It does not offer a list of supposedly profitable apps or promise that finishing a website creates income. A website is only a delivery surface. The real sequence is to test whether someone has a concrete problem, whether the smallest release solves it, whether they return, and whether they actually choose to pay.

It reduces the first step to:

1. find one problem you can reach this week through classmates, a student group, a lab, family, or a familiar small organization;
2. compare no more than three directions and recommend one zero- or low-cost default that can be tested in a few focused sessions;
3. build only enough for the first real user to complete the core job;
4. keep technical correctness, first use, repeated use, and willingness to pay as separate evidence before expanding, changing direction, or stopping.

Start with this:

> I am a university student who knows some Python and frontend development but has only built coursework. I keep seeing people earn money from small websites and do not know where to start. Give me no more than three directions based on problems I can reach through classmates, student groups, or a lab; recommend one zero-budget default; then help me build the smallest version one real user can try. Do not promise income or deploy without permission.

It is no longer a static-website recipe. It can route and combine:

- browser applications and full-stack products;
- APIs, workers, databases, and backends;
- CLI tools, batch jobs, and safe automation;
- data pipelines, models, RAG, and LLM systems;
- reusable libraries and SDKs;
- mobile and desktop applications;
- substantial changes inside an existing repository.

A successful release might be a public site, a tested API, an installable CLI, a reproducible model, a packaged library, or an app build. BuildBuddy does not force every idea into a public URL.

## Three-step start

1. **Install** — clone this repository and run `bash install.sh`.
2. **Describe the outcome or your situation** — with a direction, say “Build a CLI that safely renames photos from EXIF dates”; without one, say “I know some Python and want a first real project—help me choose from problems around me.”
3. **Review the evidence** — BuildBuddy implements locally, runs stack-appropriate checks, records limitations, and asks before unapproved external actions.

## What makes it different

| Generic coding prompt | BuildBuddy |
|---|---|
| Picks a familiar framework immediately | Inspects the repository and routes by the product's real entry point |
| Uses the same test recipe everywhere | Chooses browser, API, subprocess, data, consumer-install, or simulator evidence as appropriate |
| “Tests pass” with no scope | Maps each claim to a fresh command or interaction and names limitations |
| Treats all existing files as safe to rewrite | Records dirty state and never stashes, commits, or discards user work without permission |
| Deploys because credentials exist | Separates capability from consent and verifies the delivered version |
| Stops after arbitrary retry counts | Continues while a materially different safe diagnostic path exists |

## How the skill is organized

The core `SKILL.md` is deliberately small. It contains routing, the build loop, safety boundaries, evidence rules, and the final acceptance review. It loads only the detail needed for the selected project:

- `references/project-profiles.md` — web, backend, CLI, data/AI, library, mobile/desktop, existing-project, and risk overlays;
- `references/verification-playbook.md` — fast/full evidence sets and real-boundary testing;
- `references/guided-mode.md` — honest operation when commands cannot be run;
- `references/release-and-deployment.md` — websites, APIs, packages, models, and app releases;
- `references/ideation-and-coaching.md` — direction finding, teaching, and retrospectives;
- `assets/PROJECT_NOTES.template.md` — optional durable outcome and evidence log;
- `evals/evals.json` — realistic trigger and project-routing scenarios;
- `scripts/validate_skill.py` — dependency-free structural validation;
- `scripts/test_validator.py` / `scripts/test_installer.py` — negative validation and atomic-update regression tests.

This progressive layout keeps irrelevant stack instructions out of the agent's context while preserving detailed guidance when it matters.

## Safety and honesty

- Uses repository-native tooling before adding new frameworks, hooks, or wrappers.
- Never silently stages unrelated files, overwrites an existing hook, stashes user work, force-pushes, or uses destructive Git recovery.
- Uses fixtures, temporary directories, disposable databases, provider test modes, and clean consumer environments.
- Treats secret scanners as limited evidence, never invents or exposes credentials, and stops for account-owner rotation after suspected leakage.
- Reports outcomes as verified, partially verified, or not verified.
- Treats explicit authorization for a named repository modification, push, or deployment as permission for that scope, without asking twice.

## Install

### Codex

```bash
bash install.sh
```

The installer copies the complete skill—not only `SKILL.md`—to `${CODEX_HOME}/skills/buildbuddy/` when `CODEX_HOME` is set, otherwise to `~/.codex/skills/buildbuddy/`. It stages and validates the whole update before replacing the prior version, rejects unsafe symlink layouts, and records a content fingerprint. Re-run it to update.

The destination directory must be named `buildbuddy`; the installer refuses any other name so it cannot silently land in the wrong folder. To install somewhere else, point `BUILDBUDDY_SKILL_DIR` at a path that ends in `buildbuddy`:

```bash
BUILDBUDDY_SKILL_DIR=/my/own/skills/buildbuddy bash install.sh
```

### skills.sh (any Agent Skills-compatible tool)

```bash
npx skills add lysanderphong/buildbuddy
```

Works with Claude Code, Cursor, Codex, and every other agent supported by [skills.sh](https://skills.sh/LysanderPhong/buildbuddy).

### Other Agent Skills-compatible tools

Copy the whole repository skill set—`SKILL.md`, `references/`, `assets/`, `agents/`, `evals/`, and `scripts/`—into the tool's skill directory. Do not copy only `SKILL.md`, because the core intentionally loads profile guidance on demand.

## Example requests

> Build a local-first meal-splitting web app. Balances must survive reloads, but I do not want deployment yet.

> In this FastAPI repository, add a Postgres-backed import endpoint. Preserve my unrelated edits and do not touch production data.

> Turn these transaction CSVs into a fraud-risk baseline. Split by time, compare against a naive baseline, and do not overclaim accuracy.

> Create a Flutter habit tracker for Android and iOS. I have no Apple signing credentials, so report exactly what you can verify.

If the skill is not selected automatically, say: **“Use the buildbuddy skill.”**

## Design influences

BuildBuddy uses newly written instructions and templates while adapting general workflow ideas from [OpenAI's current skill guidance](https://learn.chatgpt.com/docs/build-skills), the [Agent Skills standard](https://github.com/agentskills/agentskills), [GitHub Spec Kit](https://github.com/github/spec-kit), [Anthropic's skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator), and [Superpowers](https://github.com/obra/superpowers). The synthesis emphasizes progressive disclosure, outcome-first planning, stack-native verification, realistic evals, and fresh evidence before completion claims.

No third-party skill text or templates are bundled here.

## Repository files

- `SKILL.md` — English runtime instructions loaded by the agent;
- `notes/SKILL-zh.md` — Chinese reading translation;
- `README.md` / `README.zh.md` — English and Chinese project pages;
- `docs/` — bilingual GitHub Pages showcase;
- `install.sh` — atomic full-folder installer with rollback, path guards, provenance, and validation;
- `.github/workflows/check-skill.yml` — CI validation and installer test;
- `LICENSE` — MIT.

## License

MIT
