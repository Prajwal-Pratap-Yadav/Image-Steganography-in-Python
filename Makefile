PYTHON ?= python3
PY = .venv/bin/python
OUTPUT ?= .

.PHONY: setup setup-dev lint typecheck test run reproduce docs clean security build
setup:
	test -x $(PY) || $(PYTHON) -m venv .venv
	$(PY) -m pip install --disable-pip-version-check --require-hashes -r requirements-bootstrap.lock
	.venv/bin/uv pip install --python $(PY) --link-mode copy --require-hashes -r requirements.lock
	.venv/bin/uv pip install --python $(PY) --no-deps --no-build-isolation -e .
setup-dev: setup
	.venv/bin/uv pip install --python $(PY) --link-mode copy --require-hashes -r requirements-dev.lock
	$(PY) scripts/install_gitleaks.py
	.venv/bin/pre-commit install
lint:
	.venv/bin/ruff format --check src tests scripts
	.venv/bin/ruff check src tests scripts
typecheck:
	.venv/bin/mypy
test:
	.venv/bin/pytest --cov --cov-report=term-missing --cov-report=xml
run:
	$(PY) scripts/demo.py
reproduce:
	$(PY) scripts/reproduce.py --output $(OUTPUT)
docs:
	$(PY) scripts/check_docs.py
security:
	mkdir -p reports/local
	.tools/gitleaks git --log-opts=--all --redact --report-path reports/local/gitleaks.json
	.venv/bin/bandit -q -r src -f json -o reports/local/bandit.json
	.venv/bin/pip-audit --disable-pip --no-deps --require-hashes -r requirements.lock -f json -o reports/local/pip-audit.json
build:
	$(PY) -m build --no-isolation
clean:
	$(PYTHON) -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov']]; [p.unlink(missing_ok=True) for p in [Path('coverage.xml'), Path('.coverage')]]"
