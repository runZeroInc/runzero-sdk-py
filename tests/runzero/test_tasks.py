import pytest

from runzero.api import Tasks


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_tasks_get(client, integration_config):
    c = client
    conf = integration_config
    tasks = Tasks(client=c).get_all(conf.org_id)
    assert len(tasks) > 0

    # requires either name or id
    with pytest.raises(ValueError):
        Tasks(client=c).get(integration_config.org_id)

    task = Tasks(client=c).get(integration_config.org_id, name=tasks[0].name)
    assert task.name == tasks[0].name
    assert task.id == tasks[0].id

    task = Tasks(client=c).get(integration_config.org_id, task_id=tasks[0].id)
    assert task.name == tasks[0].name
    assert task.id == tasks[0].id

    status = Tasks(client=c).get_status(integration_config.org_id, task_id=tasks[0].id)
    assert status == tasks[0].status
