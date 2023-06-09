import pytest

from runzero.api.imports import CustomAssets
from runzero.types import ImportAsset, ImportTask, Tag


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_custom_asset_import(client, integration_config, temp_custom_integration, temp_site):
    """
    This test demonstrates loading of custom asset data
    """

    import_assets = [
        ImportAsset(id="asset one"),
    ]

    c = client

    import_mgr = CustomAssets(c)
    target_org_id = integration_config.org_id
    target_site_id = temp_site.id
    custom_integration_id = temp_custom_integration.id

    task = import_mgr.upload_assets(
        org_id=target_org_id,
        site_id=target_site_id,
        custom_integration_id=custom_integration_id,
        assets=import_assets,
        task_info=ImportTask(
            name="task name",
            description="task description",
            tags=[Tag("one"), Tag("two")],
        ),
    )

    assert task.id is not None
    assert task.name == "task name"
    assert task.description == "task description"
