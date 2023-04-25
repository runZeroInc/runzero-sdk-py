import pytest

from runzero import ClientError
from runzero.api import Tasks, TasksAdmin, TemplatesAdmin
from runzero.api.tasks import TaskOptions
from runzero.types import ScanTemplate, ScanTemplateOptions


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_tasks_get(client, integration_config, temp_task):
    if temp_task is None:
        pytest.skip("cannot run test with no explorers connected, task creation fails")

    c = client
    tasks = Tasks(client=c).get_all(integration_config.org_id)
    assert len(tasks) > 0

    # Can query
    tasks = Tasks(client=c).get_all(integration_config.org_id, query=f"id:{temp_task.id}")
    assert len(tasks) == 1
    task = tasks[0]
    assert task.name == temp_task.name
    assert task.id == temp_task.id

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


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_tasks_patch(client, integration_config, temp_task):
    if temp_task is None:
        pytest.skip("cannot run test with no explorers connected, task creation fails")

    c = client
    task = Tasks(client=c).get(integration_config.org_id, task_id=temp_task.id)
    assert task.name == temp_task.name
    assert task.id == temp_task.id

    updated = Tasks(client=c).update(
        integration_config.org_id,
        task_id=temp_task.id,
        task_options=TaskOptions(
            name="new name",
        ),
    )
    assert updated.name == "new name"
    assert updated.id == temp_task.id


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "client",
    [
        (pytest.lazy_fixture("account_client")),
        (pytest.lazy_fixture("org_client")),
    ],
)
def test_tasks_patch_with_hosted_zone(client, integration_config, temp_monthly_task, hosted_zones):
    # a repeating scan task, or task in the future, is required for a PATCH to accept a modification
    # of the hosted_zone_id
    # for this reason, we use temp_monthly_task instead of temp_task

    if temp_monthly_task is None:
        pytest.skip("cannot run test with no explorers connected, task creation fails")

    if len(hosted_zones) == 0:
        pytest.skip("cannot run test with no hosted zones accessible")

    c = client
    task = Tasks(client=c).get(integration_config.org_id, task_id=temp_monthly_task.id)
    assert task.id == temp_monthly_task.id

    hosted_zone = hosted_zones[0]

    task = Tasks(client=c).update(
        integration_config.org_id,
        task_id=temp_monthly_task.id,
        task_options=TaskOptions(name="new name", hosted_zone_id=hosted_zone.id),
    )
    assert task.name == "new name"
    assert task.id == temp_monthly_task.id
    assert task.hosted_zone_id == hosted_zone.id

    task = Tasks(client=c).update(
        integration_config.org_id,
        task_id=temp_monthly_task.id,
        task_options=TaskOptions(
            name="newer name",
            hosted_zone_name="auto",
        ),
    )
    assert task.name == "newer name"
    assert task.id == temp_monthly_task.id
    assert task.hosted_zone_id == hosted_zone.id

    # PATCH should not remove the hosted_zone_id if it is not provided
    task = Tasks(client=c).update(
        integration_config.org_id,
        task_id=temp_monthly_task.id,
        task_options=TaskOptions(
            name="newest name",
        ),
    )
    assert task.name == "newest name"
    assert task.id == temp_monthly_task.id
    assert task.hosted_zone_id == hosted_zone.id


## Admin


@pytest.mark.integration_test
def test_tasks_admin_get_all(account_client, integration_config, temp_task):
    if temp_task is None:
        pytest.skip("cannot run test with no explorers connected, task creation fails")

    c = account_client
    tasks = TasksAdmin(client=c).get_all()
    found_task = None
    for t in tasks:
        if t.id == temp_task.id:
            found_task = t
    assert found_task is not None
    assert found_task.id == temp_task.id
    assert found_task.name == temp_task.name


@pytest.mark.integration_test
def test_tasks_admin_get_all_status_search(account_client, integration_config, temp_task):
    if temp_task is None:
        pytest.skip("cannot run test with no explorers connected, task creation fails")

    c = account_client
    tasks = TasksAdmin(client=c).get_all(status=temp_task.status)
    found_task = None
    assert len(tasks) > 0
    for t in tasks:
        if t.id == temp_task.id:
            found_task = t
    assert found_task is not None
    assert found_task.id == temp_task.id
    assert found_task.name == temp_task.name


@pytest.mark.integration_test
def test_tasks_admin_get_all_query_search(account_client, integration_config, temp_task):
    if temp_task is None:
        pytest.skip("cannot run test with no explorers connected, task creation fails")

    c = account_client
    tasks = TasksAdmin(client=c).get_all(query=f"id:{temp_task.id}")
    assert len(tasks) == 1
    found_task = tasks[0]
    assert found_task.id == temp_task.id
    assert found_task.name == temp_task.name


@pytest.mark.integration_test
def test_templates_admin_get_all(account_client, integration_config, temp_account_scan_template):
    c = account_client
    templates = TemplatesAdmin(client=c).get_all()
    found_template = None
    assert len(templates) > 0
    for t in templates:
        if t.id == temp_account_scan_template.id:
            found_template = t
    assert found_template is not None
    assert found_template.id == temp_account_scan_template.id
    assert found_template.name == temp_account_scan_template.name


@pytest.mark.integration_test
def test_templates_admin_get_all_query_search(account_client, integration_config, temp_account_scan_template):
    c = account_client
    templates = TemplatesAdmin(client=c).get_all(query=f"id:{temp_account_scan_template.id}")
    assert len(templates) == 1
    found_template = templates[0]
    assert found_template.id == temp_account_scan_template.id
    assert found_template.name == temp_account_scan_template.name


@pytest.mark.integration_test
def test_templates_admin_get(account_client, integration_config, temp_account_scan_template):
    c = account_client
    template = TemplatesAdmin(client=c).get(scan_template_id=temp_account_scan_template.id)
    assert template.name == temp_account_scan_template.name
    assert template.id == temp_account_scan_template.id


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "template_is_global,create_acl_spec",
    [
        pytest.param(True, False, id="Global true, no ACL"),
        pytest.param(True, True, id="Global true, with ACL"),
        pytest.param(False, True, id="Global false, with ACL"),
    ],
)
def test_templates_admin_create(
    account_client, temp_org, request, tsstring, uuid_nil, template_is_global, create_acl_spec
):
    c = account_client
    acl = {}
    if create_acl_spec:
        acl = {str(temp_org.id): "user"}
    template_name = tsstring(f"scan task template for {request.node.name}")
    create_opts = ScanTemplateOptions(
        name=str(template_name),
        params={
            "max-host-rate": "1000",
            "rate": "3000",
        },
        organization_id=temp_org.id,
        acl=acl,
        global_=template_is_global,
        description="Python SDK Test Template",
    )
    template = TemplatesAdmin(client=c).create(scan_template_options=create_opts)
    assert template.name == create_opts.name
    assert template.description == create_opts.description
    assert template.id != uuid_nil
    assert len(template.params) > len(create_opts.params)
    assert template.global_ is template_is_global
    assert template.acl == acl
    for k in create_opts.params.keys():
        assert create_opts.params[k] == template.params[k]


@pytest.mark.integration_test
def test_templates_admin_create_requires_either_acl_or_global_flag(account_client, temp_org, request, tsstring):
    c = account_client
    template_name = tsstring(f"scan task template for {request.node.name}")
    create_opts = ScanTemplateOptions(
        name=str(template_name),
        params={
            "max-host-rate": "1000",
            "rate": "3000",
        },
        organization_id=temp_org.id,
        acl={},
        global_=False,
        description="Python SDK Test Template",
    )
    with pytest.raises(ClientError) as exc_info:
        template = TemplatesAdmin(client=c).create(scan_template_options=create_opts)
    assert exc_info.value.error_info.title == "global or ACL permissions field required"


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "template_is_global,create_acl_spec",
    [
        pytest.param(True, False, id="Global true, no ACL"),
        pytest.param(False, True, id="Global false, with ACL"),
    ],
)
def test_templates_admin_update(
    account_client,
    integration_config,
    temp_account_scan_template,
    temp_org,
    uuid_nil,
    template_is_global,
    create_acl_spec,
):
    c = account_client
    acl = {}
    if create_acl_spec:
        acl = {str(temp_org.id): "user"}
    update_to = ScanTemplate(
        name=str(temp_account_scan_template.name + " - updated"),
        id=temp_account_scan_template.id,
        params={
            "excludes": "excludesparam",
            "host-ping": "true",
            "max-attempts": "4",
            "max-group-size": "1",
            "max-host-rate": "3030",
            "max-sockets": "522",
            "max-ttl": "102",
            "nameservers": "a.nameserver",
            "passes": "5",
            "probes": "arp",
            "rate": "3020",
            "scan-tags": "tag1,tag2",
            "screenshots": "true",
            "subnet-ping": "true",
            "subnet-ping-net-size": "251",
            "subnet-ping-sample-rate": "5",
            "tcp-excludes": "excludes",
        },
        organization_id=temp_org.id,
        global_=template_is_global,
        description="Python SDK Test Template Updated",
        acl=acl,
    )
    template = TemplatesAdmin(client=c).update(new_scan_template_values=update_to)
    assert template.name == update_to.name
    assert template.description == update_to.description
    assert template.id == temp_account_scan_template.id
    assert template.global_ is template_is_global
    assert len(template.params) > len(update_to.params)
    for k in update_to.params.keys():
        assert update_to.params[k] == template.params[k]


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "template_is_global,create_acl_spec",
    [
        pytest.param(True, False, id="Global true, no ACL"),
        pytest.param(False, True, id="Global false, with ACL"),
    ],
)
def test_templates_admin_delete(
    account_client, temp_org, request, tsstring, uuid_nil, template_is_global, create_acl_spec
):
    c = account_client
    template_name = tsstring(f"scan task template for {request.node.name}")
    acl = {}
    if create_acl_spec:
        acl = {str(temp_org.id): "user"}
    create_opts = ScanTemplateOptions(
        name=str(template_name),
        params={
            "max-host-rate": "1000",
            "rate": "3000",
        },
        organization_id=temp_org.id,
        global_=template_is_global,
        acl=acl,
        description="Python SDK Test Template",
    )

    template = TemplatesAdmin(client=c).create(scan_template_options=create_opts)
    assert template.name == create_opts.name
    assert template.id != uuid_nil

    TemplatesAdmin(client=c).delete(scan_template_id=template.id)
    with pytest.raises(ClientError) as exc_info:
        TemplatesAdmin(client=c).get(scan_template_id=template.id)
    assert str(exc_info.value.error_info.title) == "scan template not found"
