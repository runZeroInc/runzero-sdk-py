from pathlib import Path


def build_test_data_path(file: str) -> Path:
    cwd = Path.cwd()
    while cwd.stem != "runzero-sdk-py":
        cwd = cwd.parent
    cwd = cwd.joinpath("./tests/runzero/test_data").resolve()
    cwd = cwd.joinpath(file).resolve()
    return cwd
