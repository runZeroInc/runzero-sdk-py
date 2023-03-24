"""
errors provides named exception types for working with or derived from runZero's data model types.
"""

from runzero import errors
from runzero.types._data_models_gen import Problem


class RFC7807Error(Problem):
    """
    RFC7807Error is a named Exception class representing json error details messages.
    """

    pass


class ValidationError(errors.Error):
    """
    ValidationError is a named Exception class for validation issues when working with runZero data models

    Common types of validation issues are:
    * Incorrect type or data format for conversion into data model
    * Missing required values for data model
    * Out of bounds values for data model
    """

    def __init__(self, message: str):
        super().__init__(message)
