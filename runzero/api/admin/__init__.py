"""
admin holds API interactions which require 'account' level authorization. These operations can have
broad effects across a customer estate and, as such, are kept separately from other API.
"""

from .custom_integrations import CustomIntegrationsAdmin
from .orgs import OrgsAdmin

__all__ = [
    "CustomIntegrationsAdmin",
    "OrgsAdmin",
]
