from __future__ import annotations

import os
import re
import signal
import time
import uuid
from pathlib import Path
from typing import Union
from uuid import UUID

import pytest
import toml

from runzero.api import (
    CustomIntegrationsAdmin,
    Explorers,
    HostedZones,
    OrgsAdmin,
    Scans,
    Sites,
    Tasks,
    TemplatesAdmin,
)
from runzero.client import Client, ClientError
from runzero.types import (
    OrgOptions,
    ScanOptions,
    ScanTemplateOptions,
    SiteOptions,
    Task,
)


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
    site_mgr.delete(site_id=created.id, org_id=integration_config.org_id)


@pytest.fixture
def temp_org(account_client, request):
    c = account_client
    org_mgr = OrgsAdmin(client=c)
    org_name = TSString(f"org for {request.node.name}")
    create_opts = OrgOptions(name=str(org_name))
    created = org_mgr.create(org_options=create_opts)
    yield created
    org_mgr.delete(org_id=created.id)


@pytest.fixture
def temp_custom_integration(account_client, request):
    c = account_client
    custom_integration_mgr = CustomIntegrationsAdmin(c)
    custom_integration_name = TSString(f"custom integration for {request.node.name}")
    custom_integration = custom_integration_mgr.create(name=str(custom_integration_name), icon=None)
    yield custom_integration
    custom_integration_mgr.delete(custom_integration.id)


@pytest.fixture
def temp_custom_integration_with_icon(account_client, request):
    c = account_client
    custom_integration_mgr = CustomIntegrationsAdmin(c)
    custom_integration_name = TSString(f"custom integration for {request.node.name}")
    custom_integration = custom_integration_mgr.create(name=str(custom_integration_name))
    yield custom_integration
    custom_integration_mgr.delete(custom_integration.id)


@pytest.fixture
def temp_task(org_client, integration_config, request, temp_site):
    """This fixture may return an empty list if the integration test server has no explorers (agents) registered.

    Tests which require this task should pytest.skipif temp_task None
    """
    c = org_client
    task_name = TSString(f"scan task for {request.node.name}")
    create_opts = ScanOptions(
        name=str(task_name), targets="some targets", probes="arp, echo, syn", scan_start="2219296293"
    )
    try:
        task = Scans(client=c).create(org_id=integration_config.org_id, site_id=temp_site.id, scan_options=create_opts)
        yield task
        Tasks(c).stop(org_id=integration_config.org_id, task_id=task.id)
    except ClientError as exc:
        if exc.error_info.detail == "no available agents":
            yield None


@pytest.fixture
def temp_monthly_task(org_client, integration_config, request, temp_site):
    """This fixture may return an empty list if the integration test server has no explorers (agents) registered.

    Tests which require this task should pytest.skipif temp_monthly_task is None
    """
    c = org_client
    task_name = TSString(f"monthly scan task for {request.node.name}")
    create_opts = ScanOptions(
        name=str(task_name),
        targets="some targets",
        probes="arp, echo, syn",
        scan_frequency="monthly",
        scan_start="2219296293",
    )
    try:
        task = Scans(client=c).create(org_id=integration_config.org_id, site_id=temp_site.id, scan_options=create_opts)
        yield task
        Tasks(c).stop(org_id=integration_config.org_id, task_id=task.id)
    except ClientError as exc:
        if exc.error_info.detail == "no available agents":
            yield None


@pytest.fixture
def temp_account_scan_template(account_client, integration_config, request, temp_site, temp_org):
    c = account_client
    template_name = TSString(f"scan task template for {request.node.name}")
    create_opts = ScanTemplateOptions(
        name=str(template_name),
        params={
            "credentials": "",
            "excludes": "",
            "host-ping": "false",
            "max-attempts": "3",
            "max-group-size": "4096",
            "max-host-rate": "1000",
            "max-sockets": "2048",
            "max-ttl": "255",
            "nameservers": "",
            "passes": "0",
            "probes": "arp",
            "rate": "3000",
            "scan-tags": "",
            "screenshots": "false",
            "subnet-ping": "false",
            "subnet-ping-net-size": "256",
            "subnet-ping-sample-rate": "3",
            "tcp-excludes": "",
        },
        organization_id=temp_org.id,
        acl={str(temp_org.id): "user"},
        global_=False,
        description="Python SDK Test Template",
    )
    created = TemplatesAdmin(client=c).create(scan_template_options=create_opts)
    yield created
    TemplatesAdmin(client=c).delete(created.id)


@pytest.fixture
def hosted_zones(org_client, integration_config):
    c = org_client
    conf = integration_config
    hosted_zones = HostedZones(client=c).get_all(conf.org_id)
    return [hz for hz in hosted_zones if hz.enabled]


@pytest.fixture
def explorers(org_client, integration_config):
    """This fixture may return an empty list if the integration test server has no explorers (agents) registered.

    Tests which requires explorers should skipif == []
    """
    c = org_client
    explorers = []
    explorers = Explorers(client=c).get_all(integration_config.org_id)
    return [e for e in explorers if e.connected and not e.inactive]


@pytest.fixture
def tsstring():
    return TSString


@pytest.fixture(scope="session", autouse=True)
def term_handler():
    # This handler is suggested by pytest maintainers as a way to help ensure
    # cleanup when the process is externally terminated. Because we create
    # resources during integration tests, it's important that those resources
    # are removed in reasonable circumstance.
    # Obviously we cannot handle SIGKILL situations ;)
    orig = signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))
    yield
    signal.signal(signal.SIGTERM, orig)


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
            self.url: str = os.environ.get("url")
            self.account_token: str = os.environ.get("account_token")
            self.org_token: str = os.environ.get("org_token")
            oid = os.environ.get("org_id")
            if oid is not None:
                self.org_id: UUID = UUID("urn:uuid:" + oid)
            self.client_id: str = os.environ.get("client_id")
            self.client_secret: str = os.environ.get("client_secret")
            self.validate_cert: bool = os.environ.get("validate_cert", "true").lower() == "true"
        self._validate_config()

    def _validate_config(self):
        try:
            if all(
                prop
                for prop in [
                    self.url,
                    self.account_token,
                    self.org_token,
                    self.org_id,
                    self.client_id,
                    self.client_secret,
                ]
            ):
                return
        except AttributeError:
            pass
        raise RuntimeError(
            "Incomplete integration config while trying to run an integration tests. Check that all tests using"
            " IntegrationConfigs have @pytest.mark.integration_test above them"
        )


def get_path_to_config() -> Path:
    return (
        Path(__file__)
        .parent.parent.joinpath(
            "test_configs.toml",
        )
        .resolve()
    )


@pytest.fixture
def uuid_nil() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000000")
