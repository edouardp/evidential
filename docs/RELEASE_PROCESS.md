# Release Process

Releases follow the local house flow used by `../galaga`: choose a version,
write the changelog, validate, build, publish through the keyring, push a tag
and create a GitHub release. The first release, `0.1.0`, has already shipped.
Do not republish it; use the bump flow for the next release.

## Commands

```bash
make release                       # choose patch, minor or major
make release-patch                 # bug fixes and documentation
make release-minor                 # new features
make release-major                 # breaking changes
make release VERSION=0.2.0rc1       # exact stable, alpha, beta or RC version
```

Exact versions accept `X.Y.Z`, `X.Y.ZaN`, `X.Y.ZbN` and `X.Y.ZrcN`, matching
Galaga's version resolver. Use an exact version for transitions from a
prerelease. GitHub releases for alpha, beta and RC versions are marked as
prereleases.

The current version lives in `pyproject.toml`. Every version must have a matching
`CHANGELOG.md` section; `tests/release/test_release.py` checks this.

To inspect that pair without making changes:

```python
import tomllib
from pathlib import Path

version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
assert f"## {version} (" in Path("CHANGELOG.md").read_text()
print(version)
```

## Before starting

- Use an attached branch with a configured upstream, normally `main` tracking
  `origin/main`. The working tree must be clean, including untracked files.
  The script reports the branch and upstream before changing anything.
- Install project tools with `make install` and have a Chromium browser for
  the required Playwright tests. Chrome, Edge or Playwright Chromium works.
- Have the GitHub CLI (`gh`) installed and authenticated.
- Set `$EDITOR` to your preferred editor; it defaults to `vim`.
- Keyring is installed as a locked development dependency by `uv sync`.
  If setting up a production token for the first time, use the project CLI:

  ```bash
  uv run --frozen python -m keyring set https://upload.pypi.org/legacy/ __token__
  ```

The release invokes `uv run --frozen python -m keyring get
https://upload.pypi.org/legacy/ __token__` once, exports its result as
`UV_PUBLISH_TOKEN`, and runs `uv publish dist/*`. This uses Galaga's explicit
token retrieval flow with a managed interpreter instead of a global wrapper.
macOS may ask you to approve
access according to the keychain item's access policy. The script does not
print the token. A `--help` preflight checks the CLI starts before release
edits or builds, without retrieving credentials. No credentials are needed
for validation or dry-run tests.

## Notebook and README gate

Before bumping a version or opening the changelog editor, the script runs:

```bash
make readme-check
```

This compares notebook-derived README content, the generated PyPI copy, source
hashes and screenshot hashes. It uses content rather than modification times,
so a checkout with fresh timestamps does not make stale output appear current.
If it fails, regenerate and inspect the outputs, then commit them:

```bash
make readme
make readme-check
```

See [notebook documentation](notebook-documentation.md) for the source cells
and extraction rules. `make readme-check` also runs in pre-commit, `make lint`
and `make validate`. A version-only bump does not invalidate screenshot hashes.

## What the release does

1. Checks the branch, upstream and clean worktree; validates the version request
   and rejects an existing local version tag.
2. Checks the README, images and keyring CLI startup, stopping before any
   release edits if stale or broken.
3. Bumps `pyproject.toml`, refreshes `uv.lock`, and prepends a dated changelog
   section. Opens `$EDITOR` for your notes and rejects the untouched placeholder.
4. Formats the changelog and commits the three release files as `Release vX.Y.Z`.
5. Runs `make validate`: lint, audit, types, notebook checks, README provenance,
   Python/frontend tests, renderer freshness, required Playwright tests and build.
6. Runs `make pypi`, which rechecks the committed state and README, cleans old
   distributions, builds the wheel/sdist and checks their contents and metadata.
7. Retrieves the production token via the managed keyring CLI, then uploads
   the wheel and sdist.
8. Pushes the branch to its configured upstream, creates `vX.Y.Z`, pushes the tag
   to `origin` and creates the GitHub release using `CHANGELOG.md` as its notes.

`make check` performs the clean build, artifact inspection and `twine check`
without publishing. `make pypi` is the direct publication path for an already
prepared version; it does not bump, edit the changelog, tag or create a GitHub
release. Normally use `make release` instead.

## Failures and recovery

A failed gate stops the script before credentials or upload. If you leave the
changelog placeholder untouched, no release is committed or published; the
version and changelog edits remain available for review. Review or revert those
generated edits before starting again.

If validation fails after the release commit, fix it in a new commit. Never
amend or force-push. Publishing, pushing and creating the GitHub release are
separate steps: inspect which steps completed before retrying. PyPI files are
immutable. For a partial upload, inspect the existing version and use an
explicit recovery upload with `uv publish --check-url https://pypi.org/simple/`
to skip files already present; do not replace a published file.

A dirty worktree or missing upstream must be resolved before release. Commit
or stash intended work, including untracked files, and check `git status`.
The release script stages only `pyproject.toml`, `uv.lock` and `CHANGELOG.md`.

If the version commit exists but upload never started, do not rerun the bump
command: that would increment the version again. After fixing and committing
the issue, use `make pypi` to publish the current version, then finish the
branch push, version tag and GitHub release manually. For the failed stable
`0.1.1` attempt, those final steps are:

```bash
make pypi
git push
git tag v0.1.1
git push origin v0.1.1
gh release create v0.1.1 --title v0.1.1 --notes-file CHANGELOG.md
```

An error such as `keyring: ...python3.14: bad interpreter` means a global
wrapper points at a removed Python, not that the stored token was rejected.
The project-managed CLI avoids that wrapper. The preflight only checks startup;
the maintainer's actual upload is what exercises Keychain access and authentication.

## Local validation

There is no hosted build or publication pipeline. GitHub hosts the source,
tags and release notes. If CI/CD is added later, use **Buildkite**, as recorded
in [ADR-078](adr/078-local-release-validation.md).

Release-workflow tests use temporary local Git repositories and fake editor,
build, keyring, publishing and GitHub commands. They exercise success and
failure paths without reading credentials, uploading packages or contacting
GitHub. The ordinary tests still validate real renderer assets and package
contents.

## See also

- [Contributor guide](../AGENTS.md).
- [ADR-080: House release commands](adr/080-house-release-commands.md).
- [ADR-034: Build backend](adr/034-uv-build-backend.md).
- [ADR-079: Notebook-generated README](adr/079-notebook-generated-readme.md).
