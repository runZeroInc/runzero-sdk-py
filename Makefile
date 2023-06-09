#/bin/bash

# Can override these from env
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: ci
ci: fmt lint deptry mypy install-check tox-ci

# Runs linter with CI config
.PHONY: lint
lint:
	poetry run pylint ./runzero

# Runs Linter against everything including tests
.PHONY: lint-all
lint-all:
	poetry run pylint ./runzero ./tests

# Runs deptry to analyze deps
.PHONY: deptry
deptry:
	poetry run deptry .

.PHONY: docs
docs:
	poetry install --sync --with docs && \
	poetry run sphinx-build -M clean docs/source docs/build -j auto $(SPHINXOPTS) $(O) && \
	2>&1 echo "Checking for dead links" && \
	poetry run sphinx-build -M linkcheck docs/source docs/build -j auto $(SPHINXOPTS) $(O) && \
	2>&1 echo "Building - will repeat any warnings from above" && \
	poetry run sphinx-build -M html docs/source docs/build -j auto $(SPHINXOPTS) $(O)

# Formats code with black and isort
.PHONY: fmt
fmt:
	poetry run black ./runzero ./tests ./examples && \
	poetry run isort ./runzero ./tests ./examples

# Runs mypy on package
.PHONY: mypy
mypy:
	poetry run mypy ./runzero

# Runs mypy on all code including tests
.PHONY: mypy-all
mypy-all:
	poetry run mypy ./runzero ./tests

# Runs unit tests with coverage using your development python version.
.PHONY: test
test:
	poetry run pytest --cov --without-integration

# Runs integration tests
.PHONY: test-integration
test-integration:
	poetry run pytest --cov --with-integration --integration-cover

# Runs tox tests under all supported python envs with tox executing tests against what is in your source tree.
.PHONY: tox
tox:
	poetry run tox

# Runs unit tests under all supported python envs with tox by installing the package and executing tests against what is built.
.PHONY: tox-ci
tox-ci:
	poetry run tox -e ci

# Runs unit and integration tests under all supported python envs with tox by installing the package and executing tests against what is built.
.PHONY: tox-ci-integration
tox-ci-integration:
	poetry run tox -e ci-integration

# Creates data models via codegen tool
.PHONY: codegen-models
codegen-models: _codegen-models fmt

.PHONY: _codegen-models
_codegen-models:
	poetry run datamodel-codegen --input ./api/proposed-runzero-api.yml --field-constraints --collapse-root-models \
	--use-schema-description --validation --use-field-description --allow-population-by-field-name --output ./runzero/types/_data_models_gen.py --target-python-version 3.8

# Syncs your local deps with the current lockfile
.PHONY: sync-deps
sync-deps:
	poetry install --sync --with dev,codegen,devlocal,docs

.PHONY: install-check
install-check:
	./script/checks/check_install.sh

.PHONY: hooks
hooks:
	git config --local core.hooksPath "$(shell git rev-parse --show-toplevel)/.githooks"

.PHONY: init-test-configs
init-test-configs:
	touch ./test_configs.toml && \
	echo 'url = "" # url for the runZero console \n' \
	'account_token = "" # account token for the test account \n' \
	'org_token = "" # organization token for the test account \n' \
	'org_id = "" # UUID of organization associated with the above token \n' \
	'client_id = "" # OAuth client ID for the test account \n' \
	'client_secret = '' # OAuth client secret for the test account - enclose in single quotes \n' \
	'validate_cert = false # bool for whether to require a valid tsl cert (should be false for dev instance) \n' >> ./test_configs.toml
