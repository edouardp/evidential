---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-080: House Release Commands

## Context and Problem Statement

The maintainer wants the same release procedure as Galaga: `make release`,
conventional bump targets and exact versions, an edited changelog, local
validation, explicit keyring retrieval and automatic GitHub release creation.
The existing targets cover only part of that flow. Generated README content
and screenshots also need a release preflight before any version edits.

## Decision Drivers

- Match the sibling repository's familiar commands and credential path.
- Leave the actual release to the maintainer.
- Stop before a version bump when notebook documentation is stale.
- Validate and publish committed code with clean, checked artifacts.
- Exercise release behavior without accessing credentials or remote services.

## Considered Options

1. Retain the partial script and document manual follow-up commands.
2. Introduce a hosted build and publication service.
3. Complete the local Galaga house flow with shared publication and preflight checks.

## Decision Outcome

Chosen option: **3**. Keep the interactive patch/minor/major chooser and add
`VERSION=` requests using Galaga's canonical stable/alpha/beta/RC resolver.
Require an attached branch with an upstream and clean worktree, including
untracked files. Run `make readme-check` before version or changelog edits;
the gate uses source/image hashes rather than modification times.

The script updates the version and lockfile, opens a new changelog section in
`$EDITOR`, commits only the release files and runs `make validate`. Shared
`make pypi` publication rechecks the committed state and README, builds clean
distributions, checks artifacts/metadata, retrieves the token through keyring
and exports it for `uv publish`. Keyring is a locked development dependency,
invoked with `uv run --frozen python -m keyring` rather than a global wrapper.
A Homebrew Python upgrade left the global wrapper pointing at a removed
interpreter and broke the first patch upload. A credential-free `--help`
preflight now verifies the managed CLI starts before version edits or builds;
it does not read credentials or validate the stored token. The release
then pushes the branch, tags and pushes the version to origin, and creates a
GitHub release, marked as a prerelease when appropriate.

### Consequences

Maintainers can release using familiar commands without manual GitHub release
creation. Dirty state and stale documentation fail before release edits or
credentials. CLI startup is independent of the global executable's shebang;
the managed interpreter may require a fresh Keychain access approval.
Version-only bumps preserve screenshot provenance. Aborting the
changelog editor leaves edits available for review rather than discarding
them. Temporary-repository tests use fake publishing tools, proving the script
order and failure behavior without performing a release. Publishing remains
local; future CI/CD would use Buildkite, as in ADR-078.

## More Information

- [Release procedure](../RELEASE_PROCESS.md).
- [ADR-078](078-local-release-validation.md), [ADR-079](079-notebook-generated-readme.md).
- `scripts/release.sh`, `scripts/publish.sh`, `scripts/publish-guard.sh`.
- `scripts/release_version.py`, `tests/release/test_release_workflow.py`.
