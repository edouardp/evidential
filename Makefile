# Makefile for evidential
#
# Usage:
#   make              Show all available targets
#   make <target>     Run a specific target

HOST     ?= 127.0.0.1
PORT     ?= 2728
NOTEBOOK ?= notebooks/01_taxi_explore.py

# marimo Studio demo (see docs/marimo-studio.md).
STUDIO_NOTEBOOK ?= notebooks/21_studio_dashboard.py

# 7-day publication lag for dependency updates (supply-chain protection).
EXCLUDE_NEWER := $(shell date -u -v-7d +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -d '7 days ago' +%Y-%m-%dT00:00:00Z 2>/dev/null)

# ============================================================================
# General
# ============================================================================

.PHONY: help
help: ## Show this help message, grouped by section
	@if [ -t 1 ]; then color=1; else color=0; fi; \
		awk -v color="$$color" 'BEGIN{FS=":.*?## "; t="General"; max=0; c=(color=="1")?"\033[36m":""; b=(color=="1")?"\033[1m":""; r=(color=="1")?"\033[0m":""} \
		/^# =+$$/{s=1; next} \
		s==1{if($$0 ~ /^# [^=]/){t=substr($$0,3); sub(/[ \t]+$$/,"",t); next} s=0} \
		/^[a-zA-Z0-9_-]+:.*## /{n++; name[n]=$$1; desc[n]=$$2; sect[n]=t; if(length($$1)>max)max=length($$1)} \
		END{last=""; for(i=1;i<=n;i++){if(sect[i]!=last){printf "\n  %s%s%s\n",b,sect[i],r; last=sect[i]} printf "  %s%-*s%s %s\n",c,max+2,name[i],r,desc[i]}}' $(MAKEFILE_LIST)

# ============================================================================
# Setup and Installation
# ============================================================================

.PHONY: install
install: frontend-install ## Install Python (incl. dev tools) and frontend dependencies
	uv sync

.PHONY: install-python
install-python: ## Install Python dependencies (incl. dev tools) with uv
	uv sync

.PHONY: install-hooks
install-hooks: ## Install the pre-commit git hooks
	uv run pre-commit install

.PHONY: frontend-install
frontend-install: ## Install the JavaScript build/test dependencies
	cd frontend && npm install

# ============================================================================
# Frontend
# ============================================================================

.PHONY: frontend-build
frontend-build: ## Bundle the anywidget JavaScript and CSS into the Python package
	cd frontend && npm run build

.PHONY: frontend-dev
frontend-dev: ## Rebuild the bundle on every change
	cd frontend && npm run dev

.PHONY: frontend-test
frontend-test: ## Run the JavaScript formatting/colour/renderer tests
	cd frontend && node --test test_*.js

.PHONY: frontend-check
frontend-check: ## Verify committed renderer assets match a fresh build
	cd frontend && npm run check-bundle

# ============================================================================
# Notebooks
# ============================================================================

.PHONY: run-marimo
run-marimo: ## Open the notebooks in the marimo editor (HOST=127.0.0.1 PORT=2728)
	uv run marimo edit --watch --no-sandbox --host $(HOST) notebooks

.PHONY: run-notebook
run-notebook: ## Run NOTEBOOK (default notebooks/01_taxi_explore.py) non-interactively
	uv run python $(NOTEBOOK)

.PHONY: check-notebooks
check-notebooks: ## Lint every marimo notebook
	@for notebook in notebooks/*.py; do \
		echo "checking $$notebook"; \
		uv run marimo check "$$notebook" || exit 1; \
	done

# ============================================================================
# Preview
# ============================================================================

.PHONY: preview
preview: frontend-build ## Serve the renderer preview at http://HOST:PORT/frontend/preview.html
	@echo "Open http://$(HOST):$(PORT)/frontend/preview.html (Ctrl-C to stop)"
	uv run python -m http.server $(PORT) --bind $(HOST)

.PHONY: screenshot
screenshot: frontend-build ## Capture the preview to /tmp/evidential_preview.png (Chromium-based browser)
	@bash scripts/screenshot.sh

.PHONY: api-screenshots
api-screenshots: readme ## Refresh notebook screenshots and their generated README examples

.PHONY: readme
readme: frontend-build ## Generate README examples and Playwright images from marimo notebooks
	uv run python -m scripts.generate_readme

.PHONY: readme-check
readme-check: ## Check generated README text and screenshot provenance without a browser
	uv run python -m scripts.generate_readme --check

# ============================================================================
# marimo Studio
# ============================================================================

.PHONY: studio-serve
studio-serve: ## Open the Studio demo notebook with Studio installed (Server runtime)
	uv run --with "marimo-studio[deno]" marimo edit $(STUDIO_NOTEBOOK)

.PHONY: studio-validate
studio-validate: ## Validate the committed Studio views against their notebook
	uv run --with "marimo-studio[deno]" marimo-studio validate --target $(STUDIO_NOTEBOOK)

# ============================================================================
# Code Quality
# ============================================================================

.PHONY: lint
lint: ## Run all lint gates (ruff, bandit, pip-audit, pyrefly, shellcheck, checkmake, rumdl)
	./scripts/lint.sh

.PHONY: format
format: ## Auto-fix formatting and lint issues
	./scripts/lint.sh --fix

.PHONY: lint-fix
lint-fix: format ## Alias for format

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks against every file
	uv run pre-commit run --all-files

.PHONY: security
security: ## Run security scans (bandit + pip-audit)
	uv run bandit -c .bandit -r -q src/evidential
	uv run pip-audit

.PHONY: typecheck
typecheck: ## Type-check the package with pyrefly
	uv run pyrefly check

.PHONY: markdown-lint
markdown-lint: ## Lint documentation markdown with rumdl
	uvx rumdl check README.md CHANGELOG.md docs notebooks

# ============================================================================
# Testing
# ============================================================================

.PHONY: test-python
test-python: ## Run the Python test suite with coverage
	uv run pytest --cov=evidential --cov-report=term-missing --cov-fail-under=80

.PHONY: test-browser
test-browser: frontend-build ## Run real-browser functional tests (Playwright + installed Edge/Chrome)
	EVIDENTIAL_REQUIRE_BROWSER=1 uv run pytest -m browser -v tests/browser

.PHONY: test
test: test-python frontend-test ## Run Python and JavaScript tests

.PHONY: test-all
test-all: test ## Alias for test

.PHONY: benchmark
benchmark: ## Profile table navigation and grouped summary overrides
	node frontend/benchmark.js
	uv run --locked python scripts/benchmark_aggregations.py

# ============================================================================
# Dependencies
# ============================================================================

.PHONY: update-deps
update-deps: ## Update dependencies (7-day publication lag) and re-audit
	@test -n "$(EXCLUDE_NEWER)" || { echo "Set EXCLUDE_NEWER manually"; exit 1; }
	uv lock --upgrade --exclude-newer "$(EXCLUDE_NEWER)"
	uv sync
	uv run pip-audit

# ============================================================================
# Build
# ============================================================================

.PHONY: build
build: frontend-build ## Build a wheel/sdist (bundling the latest frontend)
	uv build

.PHONY: check-artifact
check-artifact: build ## Verify the built distributions contain the renderer assets
	uv run python scripts/check_artifact.py

# ============================================================================
# Release
# ============================================================================

.PHONY: check
check: check-artifact ## Check the built distributions pass `twine check`
	uvx twine check dist/*

.PHONY: pypi
pypi: check ## Publish the built distributions to PyPI using the keyring
	uv publish --keyring-provider subprocess --username __token__

.PHONY: release
release: ## Release interactively (choose patch, minor or major)
	@CHOICE=$$(uv run scripts/chooser.py --title "Release type?" patch minor major 3>&1 1>&2) || exit 1; \
	./scripts/release.sh $$CHOICE

.PHONY: release-patch
release-patch: ## Release a patch version (bug fixes)
	./scripts/release.sh patch

.PHONY: release-minor
release-minor: ## Release a minor version (new features)
	./scripts/release.sh minor

.PHONY: release-major
release-major: ## Release a major version (breaking changes)
	./scripts/release.sh major

# ============================================================================
# Cleanup
# ============================================================================

.PHONY: clean
clean: ## Remove caches and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .rumdl_cache .coverage htmlcov dist/ __marimo__/

.PHONY: clean-all
clean-all: clean ## Remove caches, build artifacts, the virtualenv and node_modules
	rm -rf .venv frontend/node_modules

# ============================================================================
# Validation
# ============================================================================

.PHONY: all
all: validate ## Run full validation

.PHONY: validate
validate: lint check-notebooks readme-check test frontend-check test-browser build ## Run all local release checks and a build
	@echo ""
	@echo "Validation complete."

# ============================================================================
# Default Target
# ============================================================================

.DEFAULT_GOAL := help
