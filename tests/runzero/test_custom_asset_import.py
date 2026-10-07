import time
from datetime import datetime, timedelta, timezone

import pytest

from runzero.api import Tasks
from runzero.api.imports import CustomAssets
from runzero.types import Communication, ImportAsset, ImportTask, Tag


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


@pytest.mark.integration_test
def test_client_custom_asset_import_with_communications(
    account_client, integration_config, temp_custom_integration, temp_site
):
    """
    This test demonstrates loading custom asset data that carries aggregated communications.
    It is skipped until the integration test console accepts them (communications=true in the test config).
    """
    integration_config.skip_unless_communications()

    window_end = datetime.now(timezone.utc) - timedelta(minutes=1)
    import_assets = [
        ImportAsset(
            id="asset with communications",
            communications=[
                Communication(
                    role="client",
                    protocol="https",
                    ports=[443],
                    start_ts=window_end - timedelta(days=1),
                    end_ts=window_end,
                    bytes_tx=1500,
                    bytes_rx=300,
                ),
                Communication(
                    role="server",
                    protocol="modbus",
                    ports=[502],
                    start_ts=window_end - timedelta(days=1),
                    end_ts=window_end,
                    bytes_rx=64,
                ),
            ],
        ),
    ]

    c = account_client
    task = CustomAssets(c).upload_assets(
        org_id=integration_config.org_id,
        site_id=temp_site.id,
        custom_integration_id=temp_custom_integration.id,
        assets=import_assets,
        task_info=ImportTask(name="communications import"),
    )
    assert task.id is not None

    # The console processes the upload asynchronously; a rejected communications record fails the task.
    status = task.status
    deadline = time.monotonic() + 300
    while status not in ("processed", "failed", "error") and time.monotonic() < deadline:
        time.sleep(6)
        status = Tasks(client=c).get_status(integration_config.org_id, task.id)
    assert status == "processed"
