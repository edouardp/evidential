---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-082: Portable Evidential Agent Skill

## Context and Problem Statement

Agents building Evidential tables repeatedly need to discover the same API
semantics, data/presentation boundary and marimo widget lifecycle. We want a
maintained skill that can eventually be distributed through skills.sh without
requiring a repository clone or the maintainer's local environment.

## Decision Drivers

- Keep usage guidance with the API it describes.
- Support the standard Agent Skills format and multiple coding agents.
- Make installation independent of the Python runtime package.
- Preserve user tooling, data sources and authorization boundaries.
- Test examples as executable code rather than matching instructional wording.

## Considered Options

1. Keep an unpublished personal skill outside the repository.
2. Copy the full API manual into one large skill entrypoint.
3. Ship a focused skill directory with bundled references and runnable templates.

## Decision Outcome

Chosen option: **3**. `skills/evidential/` is the versioned distribution unit.
`SKILL.md` holds discovery metadata, essential invariants and reference routing.
Focused references cover table composition, graphics and marimo integration.
Two standalone illustrative notebooks provide a static report and a persistent
live explorer. Optional Codex UI metadata lives in `agents/openai.yaml`; it
does not restrict the portable instructions to Codex.

All required relative links resolve within the skill directory. Public API and
notebook links provide optional deeper reading. The skill checks installed
capabilities before using API additions: the repository can lead the published
package. It does not install itself globally, upgrade dependencies or publish
anything as part of ordinary use.

Repository tests validate portable metadata and links, execute reference code
and copied notebook templates, and exercise live-query updates and selection.
Browser tests verify rendered annotations and persistent linked-table behavior,
including clearing details when a selected record is filtered out.
Markdown lint includes `skills/` in the same local, pre-commit and Makefile
commands. The runtime wheel remains separate from skill distribution.

### Consequences

The skill can be installed from the repository using the skills CLI once the
files are pushed; no publication is performed by this change. Maintaining
focused references adds a small documentation surface, while executable
examples catch incompatible API changes. Passing structural and execution
checks does not prove agent behavior across every model or host; improve the
instructions from observed use rather than adding speculative requirements.

## More Information

- [Skill entrypoint](../../skills/evidential/SKILL.md).
- [Agent Skills specification](https://agentskills.io/specification).
- [Skills CLI creation and discovery](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md).
- [ADR-011: Persistent Live Tables](011-live-tables-reactive-cell.md).
- [ADR-079: Notebook-Generated README Examples](079-notebook-generated-readme.md).
