"""Show a package summary and the bundled development skill directory."""

from .skills.__main__ import main as skills_main

if __name__ == "__main__":
    print("Evidential provides Evidence-style interactive tables for Marimo and a bundled development skill.")
    raise SystemExit(skills_main(["path"]))
