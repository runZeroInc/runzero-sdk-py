from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Union
from uuid import UUID

import pytest
import toml

from runzero.admin.asset_data_sources import CustomSourcesAdmin, NewAssetCustomSource
from runzero.admin.orgs import OrgOptions, OrgsAdmin
from runzero.client import Client, ClientError
from runzero.sites import SiteOptions, Sites


@pytest.fixture
def integration_config():
    return IntegrationConfigs()


@pytest.fixture
def account_client(integration_config):
    return Client(
        account_key=integration_config.account_token,
        server_url=integration_config.url,
        validate_certificate=integration_config.validate_cert,
    )


@pytest.fixture
def org_client(integration_config):
    return Client(
        org_key=integration_config.org_token,
        server_url=integration_config.url,
        validate_certificate=integration_config.validate_cert,
    )


@pytest.fixture
def oauth_client(integration_config):
    c = Client(server_url=integration_config.url, validate_certificate=integration_config.validate_cert)
    c.oauth_login(integration_config.client_id, integration_config.client_secret)


# Temporary objects for test
@pytest.fixture
def temp_site(org_client, integration_config, request):
    c = org_client
    site_mgr = Sites(client=c)
    site_name = TSString(f"site for {request.node.name}")
    create_opts = SiteOptions(name=str(site_name))
    created = site_mgr.create(integration_config.org_id, site_options=create_opts)
    yield created
    try:
        site_mgr.delete(site_id=created.id, org_id=integration_config.org_id)
    except ClientError:
        pass


@pytest.fixture
def temp_org(account_client, request):
    c = account_client
    org_mgr = OrgsAdmin(client=c)
    org_name = TSString(f"org for {request.node.name}")
    create_opts = OrgOptions(name=str(org_name))
    created = org_mgr.create(org_options=create_opts)
    yield created
    try:
        org_mgr.delete(org_id=created.id)
    except ClientError:
        pass


@pytest.fixture
def temp_custom_source(account_client, request):
    c = account_client
    custom_source_mgr = CustomSourcesAdmin(c)
    custom_source_name = TSString(f"custom source for {request.node.name}")
    custom_source = custom_source_mgr.create(name=str(custom_source_name), icon=None)
    yield custom_source
    try:
        custom_source_mgr.delete(custom_source.id)
    except ClientError:
        pass


@pytest.fixture
def tsstring():
    return TSString


class TSString:
    """A helper class for timestamping strings for uniqueness and
    removal of whitespace

    Allows comparison after the fact
    """

    DELIM = "~|"

    def __init__(self, data: str):
        self.data = re.sub(r"\s+", "_", data)
        self.suffix = f"{time.time():.5f}"

    def __eq__(self, other: Union[TSString, str]):
        if isinstance(other, str):
            return self.data == other[: other.rfind(self.DELIM)]
        return self.data == other.data

    def __str__(self):
        return f"{self.data}{self.DELIM}{self.suffix}"


class IntegrationConfigs:
    def __init__(self):
        configs = get_path_to_config()
        if configs.exists():
            t = toml.load(configs)
            self.url: str = t.get("url")
            self.account_token: str = t.get("account_token")
            self.org_token: str = t.get("org_token")
            oid = t.get("org_id")
            if oid is not None:
                self.org_id: UUID = UUID("urn:uuid:" + oid)
            self.client_id: str = t.get("client_id")
            self.client_secret: str = t.get("client_secret")
            self.validate_cert: bool = t.get("validate_cert")
        else:
            self.url: str = os.environ.get("console_url")
            self.account_token: str = os.environ.get("account_token")
            self.org_token: str = os.environ.get("org_token")
            oid = os.environ.get("org_id")
            if oid is not None:
                self.org_id: UUID = UUID("urn:uuid:" + oid)
            self.client_id: str = os.environ.get("client_id")
            self.client_secret: str = os.environ.get("client_secret")
            self.validate_cert: bool = os.environ.get("validate_cert", "true").lower() == "true"


def get_path_to_config() -> Path:
    cwd = Path.cwd()
    while cwd.stem != "runzero-sdk-py":
        cwd = cwd.parent
    config_path = cwd.joinpath("test_configs.toml").resolve()
    return config_path
