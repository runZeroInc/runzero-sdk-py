# Development Guide for the runZero SDK

## Initial Setup

1. Install the latest version of the minimum supported version
   1. Presently our minimum supported version is 3.12
   2. We recommend you install this with [pyenv](https://github.com/pyenv/pyenv) for convenience of following these setup instructions, but you may install however you wish
   3. Here are the dev env setup steps using `pyenv`
      1. `brew install pyenv`
      2. `pyenv install 3.12`
         * this installs the latest version of `3.12`
      3. `pyenv global 3.12`
         * this sets the system alias of `python` to version `3.12` for your system
         * this is not required, but it is convenient for installing poetry on your system
      4. `pyenv local 3.12`
         * this creates a `.python-version` which poetry will depend upon for version and path resolution when creating your virtual environment
2. Install [poetry](https://python-poetry.org/docs/) which will be our toolchain for managing all things python
   1. `poetry` will install to a global directory on your system. I recommend you set it using the `POETRY_HOME` env var - but that is not a requirement
   2. `curl -sSL https://install.python-poetry.org | POETRY_HOME=~/.poetry python -` (use python3 vs python if needed)
   3. `echo 'export POETRY_HOME=~/.poetry' >> ~/.zshrc`
   4. `echo 'export PATH="$POETRY_HOME/bin:$PATH"'  >> ~/.zshrc`
   5. `source ~/.zshrc`
   6. If `poetry` has installed correctly then you should be able to run `poetry --version`
3. Create the virtual environment and install dependencies with `poetry`
   1. `poetry install`
      * This creates a virtual env and installs all dependencies
   2. `poetry` does not require juggling virtual environments; you can simply use the `poetry` commands it will handle your virtualenv. However, if you need to debug something within the virtualenv, then you can run `poetry shell` to activate the virtualenv.

* [PyCharm has an integration](https://www.jetbrains.com/help/pycharm/poetry.html) with `poetry` (and other IDE/editors presumably do too)

## Using the Makefile

The makefile included in this repo provides a convenient shorthand for calling common poetry commands.

* `make ci`: runs linters, type checking, build docs, unit tests, etc - basically everything needed for CI except integration tests as a quick feedback loop
* `make ci-int`: runs everything that's needed for CI to pass including integration tests
* `make fmt`: runs black and isort formatters on all python code
* `make lint`: runs the linter against the `runzero` package to check for CI criteria
* `make lint-all`: runs the linter against all python code in the repo; beyond what is required for CI
* `make mypy`: runs the mypy type checker against the `runzero` package to check for CI criteria
* `make mypy-all`: runs the mypy type checker against all python code in the repo; beyond what is required for CI
* `make test`: runs unit tests
* `make test-int`: runs all (unit and integration) tests
* `make docs`: builds the sphinx docs locally from the SDK
* `make deptry`: runs deptry to analyze deps for issues
* `make tox`: runs all tests under all supported python envs with tox
* `make tox-ci`: runs unit tests under all supported python envs with tox by installing the package and executing tests against what is built
* `make tox-ci-int`: runs unit and integration tests under all supported python envs with tox by installing the package and executing tests against what is built
* `make codegen-models`: runs the pydantic data-model code generator against the API spec
* `make sync-deps`: updates poetry and syncs your current local deps with the current poetry lockfile
* `make init-test-config`: creates a test configuration template locally for overriding integration test configs
* `make hooks`: installs optional local git hooks to keep remote build surprises at bay

## Running tests

This SDK uses pytest to manage running its unit and integration tests.

### Integration tests

The integration tests require configurations to provide a URL and various client secrets. For local development, be sure to run `make init-test-config` and fill in the missing values for your local test instance.

Integration tests can be run using `make test-int` for convenience or by calling pytest directly via `poetry run pytest -m integration ./tests` if you desire to utilize specific pytest cli flags.

## Using `poetry`

Poetry is an incredibly powerful toolchain and I recommend you [read its docs](https://python-poetry.org/docs/), but the following will serve as a quick guide for onboarding.

### Adding a dependency

1. Unlike `pip`, `poetry` has the ability to manage multiple dependency groups so that a published library only includes the dependencies that it needs to run
2. To add a dependency, it's as simple as `poetry add {lib}`
   1. Poetry also offers a number of versioning restrictions like such:

   ```# Allow >=2.0.5, <3.0.0 versions
   poetry add {lib}@^2.0.5

   # Allow >=2.0.5, <2.1.0 versions
   poetry add {lib}@~2.0.5

   # Allow >=2.0.5 versions, without upper bound
   poetry add "{lib}>=2.0.5"

   # Allow only 2.0.5 version
   poetry add {lib}==2.0.5
   ```

3. To install a dev-only dependency, you need to use the `-G` flag and declare a dependency group (like `dev`) ala `poetry add -G dev {lib}`
   * Dependency groups can be used for all sorts of things like `test`, `docs`, `lint`, `codegen`, etc

### Remove a dependency

1. Removing dependencies (and any sub-deps) is very straight forward with `poetry`, you just need to run `poetry remove {lib}`
   * You can also remove dependencies from groups with the `-G` flag ala `poetry remove -G dev {lib}`

### Synchronizing your dependencies with the current lock file

1. If you want to synchronize your dependencies with the current lock file (ie after switching branches), then it's as simple as running `poetry install --sync`
   * This will remove any deps not found in the lockfile as well as downgrade/upgrade where appropriate

### Running linters and code formatting

1. `poetry` can manage running your formatters and linters for you as well by leveraging the settings in the `pyproject.toml` file
2. It's as simple as running the `poetry run {cmd}`
   * To format with `black`:`poetry run black ./runzero ./tests`
   * To format with `isort`: `poetry run isort ./runzero ./tests`
   * To type check with `mypy`: `poetry run mypy ./runzero`
   * To lint with `pylint`: `poetry run pylint ./runzero`
3. Consider auto-linting with the local git hook. Install with `make hooks`

### Codegen the pydantic data models for our api

1. First we need to install the codegen dependency
   * `poetry install --with codegen`
2. Next, we can run the command to generate the pydantic models from the openapi spec
   * `poetry run datamodel-codegen --input ./api/runzero-api.yml --field-constraints --output ./models/asset.py --target-python-version 3.14`

### Preparing a release

To prepare a release by:

1. Ensuring semver conventions by taking a 'major', 'minor' or 'patch' argument, or accepting a forced but standard,
   version string
2. Bumping the project version
3. Creating a standard release commit
4. Creating the annotated release tag with a required committer signature
5. Pushing to remote

Use `./script/prepare_release.sh`. Use -h flag for help / details. It will not execute in a dirty repo, and will back out
all changes on failure.
