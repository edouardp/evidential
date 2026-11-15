---
name: evidential
description: Discover version-matched instructions for building Evidential tables, dimension slicers and marimo reports from the project's installed Python package. Use when the user requests Evidential or is working in an existing Evidential notebook or application.
license: MIT
---

# Evidential

Load the development skill bundled with the project's installed Evidential.
It includes API guidance, focused references and runnable report/explorer
templates that match that library release.

From the user's project directory, use its Python environment to locate the
skill. For a uv project:

```bash
uv run python -m evidential.skills path
```

With an already activated virtual environment:

```bash
python -m evidential.skills path
```

Read `SKILL.md` in the returned directory, then follow its reference links as
needed. Read supporting resources relative to that directory; the templates
are in its `assets/` folder. The command prints a path and makes no agent
configuration changes. Do not substitute a global Python environment when
the project command fails: that could load instructions for a different release.

If Evidential is not installed, follow the project's dependency setup. If the
installed version predates bundled skills, use its matching release documentation
and inspect its exports/signatures. Do not upgrade solely to obtain the skill.
The [release documentation](https://github.com/edouardp/evidential/tags) and
[public API reference](https://github.com/edouardp/evidential/blob/main/docs/api/API.md)
can help; the main-branch reference may describe a newer version.
