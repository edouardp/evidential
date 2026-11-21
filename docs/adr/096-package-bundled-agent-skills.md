---
status: accepted
date: 2026-11-14
deciders: edouard
---

# ADR-096: Package-Bundled Agent Skills

## Context and Problem Statement

The repository skill can describe APIs newer than a user's installed package.
Installing it separately also separates reference/template updates from the
library release. We want version-matched guidance available offline through
the Python package, while retaining a portable skills.sh-compatible entry point.
This supersedes [ADR-082](082-portable-evidential-agent-skill.md)'s decision to
distribute the full skill separately from the runtime wheel.

## Decision Drivers

- Ship instructions and executable templates with the API they describe.
- Keep one maintained copy of the full development skill.
- Preserve standard SKILL.md files and agent-independent discovery.
- Respect each project's environment and dependency version.
- Keep discovery read-only and avoid automatic configuration changes.

## Considered Options

1. Keep all skill content in the separately installed repository skill.
2. Expose a new `__skills__` dunder protocol on the package.
3. Bundle a standard skill directory with a small Python API and path command.

## Decision Outcome

Chosen option: **3**. The canonical full skill is
`src/evidential/skills/developing-with-evidential/`, including its references,
metadata, license and two standalone notebook templates. The normal uv_build
package-data handling includes it in wheels and source distributions.

`evidential.skills.path()` returns its absolute filesystem `pathlib.Path`.
`python -m evidential.skills path` prints that directory, without modifying
agent configuration. `python -m evidential` prints a summary and delegates
path output to the same command. Installed distribution metadata declares
`evidential = evidential.skills:path` in the custom `agent.skills` entry-point
group. Tools can enumerate that group and load the zero-argument path callable.
These interfaces support normal wheel installations and editable checkouts.

`skills/evidential/` becomes a lightweight discovery skill. It instructs the
agent to run the command in the user's project environment, read the returned
SKILL.md and load supporting references as needed. Its name remains `evidential`
for existing installation commands; the bundled skill's distinct name avoids
ambiguity when a repository installer discovers both. Older installed versions
without the module use matching release documentation; discovery does not
silently upgrade dependencies or substitute another Python environment.

### Consequences

A package upgrade updates the corresponding skill automatically. The portable
entry point remains installable from GitHub/skills.sh, while the full guidance
is usable offline without a repository checkout. Consumers still need to make
the skill visible to their agent; importing the package does not register it.

The metadata convention requires explicit consumer support. The generic
group name can collide with other conventions, and another distribution can
use the same entry name. Consumers should check the provider before loading
it, since loading imports Python code. The existing commands and canonical
`SKILL.md` cover direct discovery without another executable or marker file.

Markdown gates include the package's skill tree in both pre-commit and local
lint commands. Templates are package data, excluded from runtime coverage and
type checks, and exercised as marimo notebooks. Artifact checks require every
resource in both archives; an isolated wheel test verifies discovery without
loading this repository's editable package. Existing template interaction tests
now resolve resources through the public API.

## More Information

- [Bundled skill](../../src/evidential/skills/developing-with-evidential/SKILL.md).
- [Discovery entry point](../../skills/evidential/SKILL.md).
- [Streamlit's version-matched bundled skills](https://github.com/streamlit/agent-skills#how-it-works).
- [Agent Skills specification](https://agentskills.io/specification).
- [Python entry points specification](https://packaging.python.org/en/latest/specifications/entry-points/).
