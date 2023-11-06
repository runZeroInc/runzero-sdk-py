"""
errors provides named exception types for working with or derived from runZero's data model types.
"""

from runzero.types._data_models_gen import Problem


class RFC7807Error(Problem):
    """
    RFC7807Error is a named Exception class representing json error details messages.
    """

    pass
