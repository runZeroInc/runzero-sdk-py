import pytest

from runzero.imports import CustomAssets
from runzero.types import ImportAsset, ImportTask, Tag


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_client_custom_asset_import(client, integration_config, temp_custom_source, temp_site):
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
    custom_source_id = temp_custom_source.id

    task = import_mgr.upload_assets(
        org_id=target_org_id,
        site_id=target_site_id,
        source_id=custom_source_id,
        assets=import_assets,
        task_info=ImportTask(
            name="task name",
            description="task description",
            # Todo: this is uncomfortable
            tags=[Tag(__root__="one"), Tag(__root__="two")],
        ),
    )

    assert task.id is not None
    assert task.name == "task name"
    assert task.description == "task description"
