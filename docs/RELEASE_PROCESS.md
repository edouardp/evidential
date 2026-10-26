# Release Process

How `evidential` reaches PyPI: the one-time setup, the first release, and the
ongoing flow. The first public release is **0.1.0**. Its version and changelog entry
already exist, so the first release *publishes* rather than *bumps*.

The house flow lives in the sibling repositories (`../galaga`,
`docs/RELEASE_PROCESS.md` there is the most mature; `../gamr` uses the same
script shape as this repo). This document adapts that flow to `evidential`'s
targets.

## Status at a glance

| | |
| --- | --- |
| Distribution | [`evidential`](https://pypi.org/project/evidential/) |
| Import package | `evidential` |
| Version | `0.1.0` (`pyproject.toml`) |
| Changelog | `CHANGELOG.md` has the `## 0.1.0` section |
| Branch | `main` |
| Remote | <https://github.com/edouardp/evidential> |
| Build backend | `uv_build` ([ADR-034](adr/034-uv-build-backend.md)) |
| Python | ≥ 3.11 |
| Licence | MIT |

The version and the changelog must stay in step: `tests/release/test_release.py`
asserts the `pyproject.toml` `version` has a matching `CHANGELOG.md` section.

## One-time setup

### PyPI account and tokens

1. Create a production account at <https://pypi.org/account/register/> and a
   **separate** Test PyPI account at <https://test.pypi.org/account/register/>
   (they do not share credentials).
2. Generate API tokens:
   - production: <https://pypi.org/manage/account/token/>
   - test: <https://test.pypi.org/manage/account/token/>
3. For the **first** upload there is no project to scope the token to, so use an
   account-scoped token. Afterwards, add a project-scoped token for `evidential`
   with the `upload` ability and delete the broad one.

### Store the tokens in the keyring

```bash
keyring set https://upload.pypi.org/legacy/  __token__   # production (paste pypi-…)
keyring set https://test.pypi.org/legacy/    __token__   # Test PyPI
keyring get https://upload.pypi.org/legacy/  __token__   # verify
```

`uv publish` does not read the keyring by default, so both `make pypi` and the
release script pass
`--keyring-provider subprocess --username __token__`, or you supply the token via
`UV_PUBLISH_TOKEN=$(keyring get https://upload.pypi.org/legacy/ __token__)`.

### GitHub CLI

The house flow creates a GitHub release from the changelog:

```bash
brew install gh
gh auth login
```

### Git remote

```bash
git remote add origin git@github.com:edouardp/evidential.git
git push -u origin main
```

## The first release (`0.1.0`)

The version is already `0.1.0` with its changelog entry, so use the direct
publish path — **not** `make release`, which always bumps.

### 1. Land the code on `main`

```bash
git switch main
git status --short --branch      # must be clean, and main must be current
git push -u origin main
```

### 2. Run the full gate

```bash
make validate
```

This runs `make lint` (ruff, bandit, pip-audit, pyrefly, shellcheck, checkmake,
rumdl), `marimo check` on every notebook, the Python and frontend test suites,
`frontend-check` (the committed bundle matches a fresh build), and a build.

### 3. Dry run on Test PyPI

Do this for the first release (and any release that changes packaging or the
release scripts). It exercises the whole upload with throwaway credentials.

```bash
rm -rf dist
make check                                   # builds + artifact check + twine check
uv publish --publish-url https://test.pypi.org/legacy/ \
  --keyring-provider subprocess --username __token__ dist/*
```

Then install from Test PyPI in a throwaway environment and import it:

```bash
uv run --isolated --no-project \
  --index https://test.pypi.org/simple/ --index-strategy unsafe-best-match \
  --with evidential python -c "import evidential; print(evidential.__file__)"
```

Test PyPI keeps its own version history, separate from production.

### 4. Build and verify the production artifacts

```bash
rm -rf dist
make check
```

`make check` → `check-artifact` → `build` runs `make frontend-build` (so the
bundled `static/table.{js,css}` are fresh), `uv build`, `scripts/check_artifact.py`
(the wheel and sdist contain every runtime module plus the renderer assets, and
no `tests/`, `notebooks/` or `frontend/` files leak), and `twine check`.

### 5. Publish

```bash
make pypi        # = make check + uv publish with the subprocess keyring provider
```

`uv publish` uploads **both** the wheel and the sdist. If it fails partway,
check each artifact's status on PyPI before retrying — the same version cannot be
re-uploaded, so use `uv publish --check-url https://pypi.org/simple/` to skip
files that are already there.

### 6. Tag and create the GitHub release

```bash
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 --title v0.1.0 --notes-file CHANGELOG.md
```

### 7. Verify

```bash
python -m pip install "evidential==0.1.0"    # or: uv add evidential
python -c "import evidential; print(evidential.__file__)"
```

Check <https://pypi.org/project/evidential/0.1.0/> renders (long description,
links, licence).

## Later releases

For every release after the first, use the bump flow, which also writes the
changelog and re-validates before publishing:

```bash
make release          # interactive chooser: patch / minor / major
make release-patch    # bug fixes, docs
make release-minor    # new features (pre-1.0 breaking changes too)
make release-major    # breaking changes (post-1.0)
```

`make release` runs `scripts/chooser.py` (a Textual picker) then
`scripts/release.sh <bump>`, which:

1. **guards** that you are on `main` with a clean tree;
2. **bumps** `version` in `pyproject.toml` and refreshes `uv.lock`;
3. **prepends** a `CHANGELOG.md` section and opens `$EDITOR` for the notes
   (aborting if the placeholder is untouched);
4. **commits** `Release vX.Y.Z`;
5. runs **`make validate`**;
6. **builds** and `twine check`s `dist/*`;
7. **publishes** with `uv publish` (keyring token);
8. pushes the branch, tags `vX.Y.Z`, and pushes the tag.

If a step fails after the commit, fix it in a **new** commit — never amend or
force-push. Publishing is sequential, not transactional: if a partial upload
happens, do not try to replace the published file; publish a new patch version.

## Quality gates

`make validate` is the gate, and it is the same set that CI runs on every push
and pull request ([`.github/workflows/tests.yml`](../.github/workflows/tests.yml)):

- **ruff** (lint + format), **bandit**, **pip-audit**, **pyrefly** (types),
  **shellcheck**, **checkmake** and **rumdl** (markdown) — `make lint`;
- **`marimo check`** on every notebook — `make check-notebooks`;
- **pytest** (unit) and the **jsdom** frontend tests — `make test`;
- **`frontend-check`** — the committed renderer bundle matches a fresh build;
- **build** — `uv build`.

`tests/release/` holds the repository-workflow tests that keep the release
machinery honest: the Makefile help, that the lint gate fails fast, that ADRs and
their index stay consistent, that notebook examples remain valid, that the wheel
contains the renderer assets, and that the `version` / changelog / release script
/ CI stay in place.

Before publishing, confirm the release state mechanically:

```python
import tomllib

version = tomllib.load(open("pyproject.toml", "rb"))["project"]["version"]
changelog = open("CHANGELOG.md").read()
assert version == "0.1.0"          # or the version being released
assert f"## {version}" in changelog, "CHANGELOG.md has no section for this version"
```

## Troubleshooting

- **"Missing credentials" on publish** — the keyring has no token:
  `keyring get https://upload.pypi.org/legacy/ __token__`, then re-set it.
- **"Version already exists"** — a published project/version pair is immutable.
  Bump and release again; do not delete tags or rewrite pushed history.
- **`make release` refuses the bump** — it requires branch `main` and a clean
  working tree. Commit or stash first.
- **`frontend-check` fails** — the committed bundle is stale. Run
  `make frontend-build` and commit `src/evidential/static/table.{js,css}` with
  the source change ([ADR-014](adr/014-committed-frontend-bundle.md)).
- **`dist/` is stale** — always `rm -rf dist` before a build; `uv build` does not
  prune older artifacts.

## Not automated yet

The sibling `galaga` flow has a few pieces this repo does not, and that the first
release above performs by hand:

- a `scripts/publish-guard.sh` (attached branch + configured upstream + clean
  tree) and a release that also runs from a branch, not only `main`;
- an explicit `make release VERSION=X.Y.Z` for pre-release trains
  (`aN` / `bN` / `rcN`);
- a `release-testpypi` target for the dry run in step 3;
- `gh release create` inside the release script;
- an `rm -rf dist` in `make pypi` / `make check`.

Folding these in is tracked separately; until then, follow the manual commands in
step 3 and step 6.

## See also

- [AGENTS.md](../AGENTS.md) — contributor workflow and the quality gates.
- [ADR-034](adr/034-uv-build-backend.md) — the build backend.
- [ADR-014](adr/014-committed-frontend-bundle.md) — why the bundle is committed.
- [ADR-017](adr/017-release-workflow-tests.md) — the release-workflow tests.
