---
status: accepted
date: 2026-11-04
deciders: edouard
---

# ADR-093: Resumable Release Finalization

## Context and Problem Statement

The local release command could publish immutable files successfully, then fail
while pushing the branch/tag or creating the GitHub release. Running the command
again would bump the version and attempt another publication instead of finishing
the existing release. Manual recovery was error-prone and used a hardcoded origin.

## Decision Drivers

- Preserve local house release commands and maintainer-controlled publication.
- Distinguish irreversible upload from safely repeatable finalization.
- Bind tags to the published commit and never overwrite a conflicting tag.
- Test every late failure without credentials or external mutations.

## Considered Options

1. Continue documenting manual push, tag and GitHub commands.
2. Add local publication receipts and idempotent post-upload finalization.
3. Move publication into a hosted deployment pipeline.

## Decision Outcome

Choose option 2. After `uv publish` succeeds, `publish.sh` writes a small JSON
receipt under the Git directory, containing version, commit and completion state.
It contains no credentials or package contents. A pending receipt blocks another
bump/upload; the last completed version cannot be uploaded again from this checkout.

`make release-resume VERSION=X.Y.Z` validates clean branch/upstream state, version
metadata and exact receipt commit before doing remote work. It pushes to the
branch's configured upstream, verifies existing local/remote tags, creates missing
tags and creates the GitHub release only when absent. Query failures stop recovery.
Notes come from that version's changelog section. Successful finalization marks
the receipt complete; repeated finalization is safe. It never builds, bumps,
retrieves a token or publishes artifacts.

### Consequences

- Failures at branch push, local tagging, tag push, GitHub query and release creation
  are recoverable without another upload. Fake-tool integration tests cover them.
- A different HEAD or conflicting tag stops recovery instead of silently changing
  the published source association. New releases cannot hide pending work.
- Receipts are local and are not a replacement for PyPI. Upload and receipt writing
  cannot be atomic. Interrupted uploads, termination just after upload, lost receipts,
  legacy releases and fresh clones require manual reconciliation before recovery.
- Publication remains local. Future CI/CD would use Buildkite.

## More Information

- [ADR-080](080-house-release-commands.md)
- [Release procedure](../RELEASE_PROCESS.md)
- `scripts/release_state.py`, `scripts/finish-release.sh`
- `tests/release/test_release_workflow.py`, `tests/release/test_release_state.py`
