"""
enables management of runZero custom integrations.

These operations are privileged and require an account token directly or an OAuth key that can generate one.
"""

import gzip
import tempfile
import time
import uuid
from typing import Iterable, List, Optional

from runzero.client import Client
from runzero.types import ImportAsset, ImportTask, NewAssetImport, Task


class CustomAssets:
    """Management of Custom Asset Data for your own custom integrations.

    Custom data integrations are descriptive registered associations between integrations of data
    and assets imported which are associated with those integrations.

    The data sent to the server has basic checks performed and is loaded as an import task
    when it can find the next available worker to do so. Therefore, the result
    is a `class:runzero.Task` which you can check the status of.

    See related :class:`runzero.account.CustomIntegrations` to work with the custom asset data
    integrations registered to the account.

    :param client: A handle to the :class:`runzero.Client` which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/import/org/{oid}/assets"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def upload_assets(
        self,
        org_id: uuid.UUID,
        site_id: uuid.UUID,
        custom_integration_id: uuid.UUID,
        assets: List[ImportAsset],
        task_info: Optional[ImportTask] = None,
    ) -> Task:
        """
        Upload your custom assets to the runZero platform.

        See the ImportAsset object for a description of the data that can be imported.

        Assets are merged according to the merge logic in the release of the platform. This
        involves fields other than the custom_properties dictionary.

        If the runZero asset ID is known externally, it may be specified on any single
        ImportAsset object to override all merge rules and force that object's data onto
        the runZero asset with that ID.

        :param org_id: Organization ID to import these assets into
        :param site_id: ID of the Site to import these asstes into
        :param custom_integration_id: custom integration id for the provided Import Assets
        :param assets: A collection of ImportAssets to upload
        :param task_info: Descriptive information associated with the import
            task to be created. If omitted, a task name is generated for you

        :returns: Task: The runZero task associated with processing the asset upload
        :raises: ServerError, ClientError, AuthError
        """
        # create default task_info not supplied
        if task_info is None:
            task_info = ImportTask(name=f"Custom Asset Import {time.time_ns():.0f}", description="py-sdk import")
        else:
            # set defaults if user sets these to empty
            if task_info.name == "":
                task_info.name = f"Custom Asset Import {time.time_ns():.0f}"
            if task_info.description is None or task_info.description == "":
                task_info.description = "py-sdk import"
            if task_info.exclude_unknown is None:
                task_info.exclude_unknown = False

        asset_import_req = _create_custom_asset_request(
            site_id=site_id,
            custom_integration_id=custom_integration_id,
            import_task=task_info,
            assets=assets,
        )

        tags_as_str = ""
        if asset_import_req.import_task.tags is not None:
            tags_as_str = ",".join([tag.__root__ for tag in asset_import_req.import_task.tags])
        multipart_form_data = (
            ("assetData", ("asset_data.jsonl.gz", asset_import_req.asset_data)),
            ("siteId", (None, str(asset_import_req.site_id))),
            ("customIntegrationId", (None, str(asset_import_req.custom_integration_id))),
            ("importTask.name", (None, asset_import_req.import_task.name)),
            ("importTask.description", (None, asset_import_req.import_task.description)),
            # this requires casting to a lower-cased string to function properly
            ("importTask.excludeUnknown", (None, str(asset_import_req.import_task.exclude_unknown).lower())),
            ("importTask.tags", (None, tags_as_str)),
        )
        res = self._client.execute("POST", self._ENDPOINT.format(oid=org_id), files=multipart_form_data, multipart=True)
        return Task.parse_obj(res.json_obj)


def _import_assets_into_gzip_jsonl(import_assets: Iterable[ImportAsset]) -> bytes:
    tmp = tempfile.TemporaryFile(mode="w+b")
    with gzip.GzipFile(fileobj=tmp, mode="wb") as gzw:
        for asset_obj in import_assets:
            gzw.write(asset_obj.json(by_alias=True).encode("utf-8") + "\n".encode("utf-8"))
    tmp.seek(0)
    return tmp.read()


def _create_custom_asset_request(
    site_id: uuid.UUID, custom_integration_id: uuid.UUID, assets: Iterable[ImportAsset], import_task: ImportTask
) -> NewAssetImport:
    return NewAssetImport(
        site_id=site_id,
        custom_integration_id=custom_integration_id,
        import_task=import_task,
        asset_data=_import_assets_into_gzip_jsonl(assets),
    )
