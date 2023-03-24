# Testing the runZero Python SDK

We believe tests describe the system to you. Even if you are not modifying the code,
test code in the [tests](/tests) directory can help us all learn how the system
is supposed to work.

## Running tests

The SDK is tested in two different ways. Unit tests execute without requiring credentials or network
access to the server. These tests ensure that parts of the code are tested independently - as units.

This is a poetry-based project. 

### Unit tests

To run all unit tests, run:

```console
make test
```

from the repository root.


Integration tests run more slowly and require a reachable runZero server, some configuration information,
and some credentials. These can be inserted into the environment or stored in a file in the root of the
repository which is read at test time. The [Makefile](Makefile) has a target which can create an 
outline of the TOML-formatted test config file for you.

To run all unit tests, run:

```console
make test-integration
```

from the repository root.


To validate changes via unit test against a fully built package that is installed into each supported Python version,
run:

```console
make tox-ci
```

To do the same with integration tests running against a live server, run:

```console
make tox-ci-integration
```

To quickly run a single test:

```console
poetry run pytest tests/test_auth.py::test_client_oauth_login
```

To run tests which match a pattern:

```console
poetry run pytest -k <your_test_function_name>
```

The value after `-k` can be any substring expression. These are case-insensitive substring matches,
and may be prefixed with 'not'.

