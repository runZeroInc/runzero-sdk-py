import os

IS_GITHUB_ACTION = os.getenv("GITHUB_ACTIONS") == "true"


def testing_in_cloud_ci() -> bool:
    """True when we are running on public build infrastructure"""
    return IS_GITHUB_ACTION
