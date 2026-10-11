---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-001: Use Architectural Decision Records

## Context and Problem Statement

How do we document and track the architectural decisions made in this project so
that future contributors understand *why* the table works the way it does, and
so we do not relitigate settled questions without the original constraints?

The [design & DX document](../design-and-dx.md) explains the current reasoning,
but it is a narrative that is rewritten as the design evolves. Decisions need
their own immutable, dated record.

## Decision Drivers

- Preserve the rationale and alternatives behind API and rendering choices.
- Keep decisions version-controlled and readable without special tooling.
- Make it cheap to add a decision, so the practice survives.

## Considered Options

1. MADR (Markdown Any Decision Records)
2. A single evolving design document only
3. Code comments only
4. No formal documentation

## Decision Outcome

Chosen option: "MADR", because it is a lightweight, version-controlled format
that lives with the code, has a consistent structure, and is already the
convention in the sibling `galaga` and `hello_world_api_lambda_container`
projects.

### Consequences

- Good, because decisions are version-controlled alongside the code.
- Good, because markdown needs no special tools and renders on GitHub.
- Good, because a consistent template keeps records comparable.
- Bad, because it requires discipline: a decision is not done until its ADR is
  written.
- Bad, because the index must be maintained by hand.

## ADR Template

All ADRs follow the [MADR](https://adr.github.io/madr/) format:

```markdown
---
status: {proposed | accepted | deprecated | superseded by ADR-XXX}
date: YYYY-MM-DD
deciders: {list of people involved}
---

# ADR-XXX: {Title}

## Context and Problem Statement

{Describe the context and problem in 2-3 sentences}

## Decision Drivers

- {driver 1}
- {driver 2}

## Considered Options

1. {option 1}
2. {option 2}

## Decision Outcome

Chosen option: "{option}" because {justification}.

### Consequences

- Good, because {positive consequence}
- Bad, because {negative consequence}

## More Information

{Optional: links, references, related ADRs}
```

## More Information

- [MADR template](https://adr.github.io/madr/)
- [Index](README.md)
