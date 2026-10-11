# Makefile for marimo-evidence-tables
#
# Usage:
#   make              Show all available targets
#   make <target>     Run a specific target

HOST     ?= 127.0.0.1
PORT     ?= 2728
NOTEBOOK ?= notebooks/01_taxi_explore.py

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
install: frontend-install ## Install Python and frontend dependencies
	uv sync --extra dev

.PHONY: install-python
install-python: ## Install Python dependencies with uv
	uv sync --extra dev

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

# ============================================================================
# Notebooks
# ============================================================================

.PHONY: run-marimo
run-marimo: ## Open the notebooks in the marimo editor (HOST=127.0.0.1 PORT=2718)
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
screenshot: frontend-build ## Capture the preview to /tmp/evidence_preview.png (Chromium-based browser)
	@bash scripts/screenshot.sh

# ============================================================================
# Code Quality
# ============================================================================

.PHONY: lint
lint: ## Run Python linting checks
	uv run ruff check src tests

.PHONY: format
format: ## Auto-fix Python linting issues
	uv run ruff check --fix src tests

.PHONY: lint-fix
lint-fix: format ## Alias for format

.PHONY: security
security: ## Run the bandit security scan (install with: uv add --dev bandit)
	uv run bandit -c .bandit -r -q src/evidence_tables

# ============================================================================
# Testing
# ============================================================================

.PHONY: test-python
test-python: ## Run the Python test suite
	uv run pytest -v

.PHONY: test-browser
test-browser: frontend-build ## Run real-browser functional tests (Playwright + installed Edge/Chrome)
	uv run pytest -m browser -v tests/browser

.PHONY: test
test: test-python frontend-test ## Run Python and JavaScript tests

.PHONY: test-all
test-all: test ## Alias for test

# ============================================================================
# Build
# ============================================================================

.PHONY: build
build: frontend-build ## Build a wheel/sdist (bundling the latest frontend)
	uv build

# ============================================================================
# Cleanup
# ============================================================================

.PHONY: clean
clean: ## Remove caches and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist/ __marimo__/

.PHONY: clean-all
clean-all: clean ## Remove caches, build artifacts, the virtualenv and node_modules
	rm -rf .venv frontend/node_modules

# ============================================================================
# Validation
# ============================================================================

.PHONY: all
all: validate ## Run full validation

.PHONY: validate
validate: lint check-notebooks test build ## Run lint, notebook checks, tests and a build
	@echo ""
	@echo "Validation complete."

# ============================================================================
# Default Target
# ============================================================================

.DEFAULT_GOAL := help
