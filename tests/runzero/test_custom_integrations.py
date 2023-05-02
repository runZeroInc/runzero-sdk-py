import pathlib

import pytest
from pydantic import ValidationError

from runzero import Error
from runzero.api import CustomIntegrations
from runzero.api.admin import CustomIntegrationsAdmin
from runzero.client import AuthError, ClientError
from runzero.types import BaseCustomIntegration, NewCustomIntegration


@pytest.mark.integration_test
def test_custom_integrations_admin_admin_no_org_access(org_client):
    """
    This test demonstrates that the org client cannot access custom integrations
    """
    c = org_client
    # Throws an AuthError because we don't have an Account Token
    with pytest.raises(AuthError):
        CustomIntegrationsAdmin(client=c).get_all()


def test_custom_integrations_name_no_whitespace_allowed():
    """
    This test demonstrates that a custom integration name cannot contain a space
    """
    NewCustomIntegration(name="ok")
    with pytest.raises(ValidationError):
        NewCustomIntegration(name="spaces and other whitespace\t are not ok")


@pytest.mark.integration_test
def test_custom_integrations_admin_get(account_client, temp_custom_integration):
    """
    This test demonstrates getting one or more custom integrations
    """
    c = account_client
    integrations = CustomIntegrationsAdmin(client=c).get_all()
    assert len(integrations) > 0

    integration = CustomIntegrationsAdmin(client=c).get(custom_integration_id=integrations[0].id)
    assert integration.id == integrations[0].id

    integration = CustomIntegrationsAdmin(client=c).get(name=integrations[0].name)
    assert integration.id == integrations[0].id
    assert integration.name == integrations[0].name


@pytest.mark.integration_test
def test_custom_integrations_admin_create_and_delete(account_client, integration_config, request, tsstring):
    """
    This test demonstrates creating a custom asset data integration
    """
    c = account_client
    integrations = CustomIntegrationsAdmin(client=c)
    integration_name = tsstring(f"source-for-{request.node.name}")

    created = integrations.create(name=str(integration_name), icon=None)
    assert created.name == integration_name
    assert created.icon is None
    src = integrations.get(custom_integration_id=created.id)
    assert src == created
    deleted = integrations.delete(custom_integration_id=created.id)
    assert deleted.id == created.id

    with pytest.raises(ClientError):
        integrations.get(custom_integration_id=src.id)


@pytest.mark.integration_test
def test_custom_integrations_admin_icon_creation(account_client, integration_config, tmp_path, request, tsstring):
    """
    This test demonstrates creating a custom asset data integration with icon data
    """

    c = account_client
    integrations = CustomIntegrationsAdmin(client=c)
    integration_name = tsstring(f"source-for-{request.node.name}")

    # automatically chosen Python Icon
    created = integrations.create(name=str(integration_name))
    assert created.name == integration_name
    assert created.icon == integrations.PYTHON_ICON
    src = integrations.get(custom_integration_id=created.id)
    assert src == created
    integrations.delete(custom_integration_id=created.id)

    # bytes data specified directly (just re-use the Python icon, it's valid)
    created = integrations.create(name=str(integration_name), icon=integrations.PYTHON_ICON)
    assert created.name == integration_name
    assert created.icon == integrations.PYTHON_ICON
    src = integrations.get(custom_integration_id=created.id)
    assert src == created
    integrations.delete(custom_integration_id=created.id)

    d = tmp_path
    p = d / "icon_file.png"
    p.write_bytes(integrations.PYTHON_ICON)
    # bytes data as pathlib path
    assert isinstance(p, pathlib.Path)
    created = integrations.create(name=str(integration_name), icon=p)
    assert created.name == integration_name
    assert created.icon == integrations.PYTHON_ICON
    src = integrations.get(custom_integration_id=created.id)
    assert src == created
    integrations.delete(custom_integration_id=created.id)

    # bytes data as filename string
    created = integrations.create(name=str(integration_name), icon=str(p))
    assert created.name == integration_name
    assert created.icon == integrations.PYTHON_ICON
    src = integrations.get(custom_integration_id=created.id)
    assert src == created
    integrations.delete(custom_integration_id=created.id)

    # bytes file missing, we wrap underlying error
    with pytest.raises(Error):
        integrations.create(name=str(integration_name), icon="not there")

    # bytes data as pathlib path
    created = integrations.create(name=str(integration_name), icon=p)
    assert created.name == integration_name
    assert created.icon == integrations.PYTHON_ICON
    src = integrations.get(custom_integration_id=created.id)
    assert src == created
    integrations.delete(custom_integration_id=created.id)

    # Bad icon data
    with pytest.raises(ClientError) as exc:
        integrations.create(name=str(integration_name), icon=b"not a 256x256 png")

    assert str(exc.value).startswith("The request was rejected by the server")
    assert "pixels" in exc.value.error_info.detail


@pytest.mark.integration_test
def test_custom_integrations_admin_update(
    account_client, integration_config, request, temp_custom_integration, tsstring
):
    """
    This test demonstrates deleting a custom integration
    """
    c = account_client
    integrations = CustomIntegrationsAdmin(client=c)
    got_int = integrations.get(custom_integration_id=temp_custom_integration.id)
    assert got_int.id == temp_custom_integration.id
    new_name = tsstring(f"renamed-source-for-{request.node.name}")
    updated_integration = integrations.update(
        custom_integration_id=got_int.id, source_options=BaseCustomIntegration(name=str(new_name))
    )
    assert updated_integration.name == new_name
    assert updated_integration.id == got_int.id


@pytest.mark.integration_test
def test_custom_integrations_admin_create_twice_is_error(account_client, integration_config, request, tsstring):
    """
    This test demonstrates creating a custom integration with the same name twice is an error
    """
    c = account_client
    integrations = CustomIntegrationsAdmin(client=c)
    name = tsstring(f"custom-source-for-{request.node.name}")
    created = integrations.create(name=str(name))
    assert created.name == name

    with pytest.raises(ClientError):
        integrations.create(name=str(name))

    # cleanup
    integrations.delete(created.id)
    with pytest.raises(ClientError):
        integrations.get(custom_integration_id=created.id)


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_custom_integrations_get(client, temp_custom_integration, integration_config):
    """
    This test demonstrates getting one or more custom integrations from lower-privilege org api
    """
    c = client
    integrations = CustomIntegrations(client=c).get_all(integration_config.org_id)
    assert len(integrations) > 0

    integration = CustomIntegrations(client=c).get(
        integration_config.org_id, custom_integration_id=temp_custom_integration.id
    )
    assert integration.id == temp_custom_integration.id

    integration = CustomIntegrations(client=c).get(integration_config.org_id, name=temp_custom_integration.name)
    assert integration.id == temp_custom_integration.id
    assert integration.name == temp_custom_integration.name
