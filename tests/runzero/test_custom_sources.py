import base64
import io
import pathlib

import pytest
from pydantic import ValidationError

from runzero import Error
from runzero.admin import CustomSourcesAdmin
from runzero.asset_data_sources import CustomSources
from runzero.client import AuthError, ClientError
from runzero.types import BaseAssetCustomSource, NewAssetCustomSource


@pytest.mark.integration_test
def test_custom_sources_admin_admin_no_org_access(org_client):
    """
    This test demonstrates that the org client cannot access custom asset sources
    """
    c = org_client
    # Throws an AuthError because we don't have an Account Token
    with pytest.raises(AuthError):
        CustomSourcesAdmin(client=c).get_all()


def test_custom_sources_name_no_whitespace_allowed(org_client):
    """
    This test demonstrates that a custom asset source name cannot contain a space
    """
    NewAssetCustomSource(name="ok")
    with pytest.raises(ValidationError):
        NewAssetCustomSource(name="spaces and other whitespace\t are not ok")


@pytest.mark.integration_test
def test_custom_sources_admin_get(account_client, temp_custom_source):
    """
    This test demonstrates getting one or more custom asset data sources
    """
    c = account_client
    sources = CustomSourcesAdmin(client=c).get_all()
    assert len(sources) > 0

    source = CustomSourcesAdmin(client=c).get(source_id=sources[0].id)
    assert source.id == sources[0].id

    source = CustomSourcesAdmin(client=c).get(name=sources[0].name)
    assert source.id == sources[0].id
    assert source.name == sources[0].name


@pytest.mark.integration_test
def test_custom_sources_admin_create_and_delete(account_client, integration_config, request, tsstring):
    """
    This test demonstrates creating a custom asset data source
    """
    c = account_client
    sources = CustomSourcesAdmin(client=c)
    source_name = tsstring(f"source-for-{request.node.name}")

    created = sources.create(name=str(source_name), icon=None)
    assert created.name == source_name
    assert created.icon is None
    src = sources.get(source_id=created.id)
    assert src == created
    sources.delete(source_id=created.id)

    with pytest.raises(ClientError):
        sources.get(source_id=src.id)


@pytest.mark.integration_test
def test_custom_sources_admin_icon_creation(account_client, integration_config, tmp_path, request, tsstring):
    """
    This test demonstrates creating a custom asset data source with icon data
    """

    c = account_client
    sources = CustomSourcesAdmin(client=c)
    source_name = tsstring(f"source-for-{request.node.name}")

    # automatically chosen Python Icon
    created = sources.create(name=str(source_name))
    assert created.name == source_name
    assert created.icon == sources.PYTHON_ICON
    src = sources.get(source_id=created.id)
    assert src == created
    sources.delete(source_id=created.id)

    # bytes data specified directly (just re-use the Python icon, it's valid)
    created = sources.create(name=str(source_name), icon=sources.PYTHON_ICON)
    assert created.name == source_name
    assert created.icon == sources.PYTHON_ICON
    src = sources.get(source_id=created.id)
    assert src == created
    sources.delete(source_id=created.id)

    d = tmp_path
    p = d / "icon_file.png"
    p.write_bytes(sources.PYTHON_ICON)
    # bytes data as pathlib path
    assert isinstance(p, pathlib.Path)
    created = sources.create(name=str(source_name), icon=p)
    assert created.name == source_name
    assert created.icon == sources.PYTHON_ICON
    src = sources.get(source_id=created.id)
    assert src == created
    sources.delete(source_id=created.id)

    # bytes data as filename string
    created = sources.create(name=str(source_name), icon=str(p))
    assert created.name == source_name
    assert created.icon == sources.PYTHON_ICON
    src = sources.get(source_id=created.id)
    assert src == created
    sources.delete(source_id=created.id)

    # bytes file missing, we wrap underlying error
    with pytest.raises(Error):
        sources.create(name=str(source_name), icon="not there")

    # bytes data as pathlib path
    created = sources.create(name=str(source_name), icon=p)
    assert created.name == source_name
    assert created.icon == sources.PYTHON_ICON
    src = sources.get(source_id=created.id)
    assert src == created
    sources.delete(source_id=created.id)

    # Bad icon data
    with pytest.raises(ClientError) as exc:
        sources.create(name=str(source_name), icon=b"not a 32x32 png")

    assert str(exc.value).startswith("The request was rejected by the server")
    assert "32 pixels" in exc.value.error_info.detail


@pytest.mark.integration_test
def test_custom_sources_admin_update(account_client, integration_config, request, temp_custom_source, tsstring):
    """
    This test demonstrates deleting a custom asset source
    """
    c = account_client
    sources = CustomSourcesAdmin(client=c)
    got_source = sources.get(source_id=temp_custom_source.id)
    assert got_source.id == temp_custom_source.id
    new_name = tsstring(f"renamed-source-for-{request.node.name}")
    updated_source = sources.update(source_id=got_source.id, source_options=BaseAssetCustomSource(name=str(new_name)))
    assert updated_source.name == new_name
    assert updated_source.id == got_source.id


@pytest.mark.integration_test
def test_custom_sources_admin_create_twice_is_error(account_client, integration_config, request, tsstring):
    """
    This test demonstrates creating a custom source with the same name twice is an error
    """
    c = account_client
    sources = CustomSourcesAdmin(client=c)
    name = tsstring(f"custom-source-for-{request.node.name}")
    created = sources.create(name=str(name))
    assert created.name == name

    with pytest.raises(ClientError):
        sources.create(name=str(name))

    # cleanup
    sources.delete(created.id)
    with pytest.raises(ClientError):
        sources.get(source_id=created.id)


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_custom_sources_get(client, temp_custom_source, integration_config):
    """
    This test demonstrates getting one or more custom asset data sources from lower-privilege org api
    """
    c = client
    sources = CustomSources(client=c).get_all(integration_config.org_id)
    assert len(sources) > 0

    source = CustomSources(client=c).get(integration_config.org_id, source_id=sources[0].id)
    assert source.id == sources[0].id

    source = CustomSources(client=c).get(integration_config.org_id, name=sources[0].name)
    assert source.id == sources[0].id
    assert source.name == sources[0].name
