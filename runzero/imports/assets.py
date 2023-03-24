"""
enables management of runZero asset data sources.

These operations are privileged and require an account token directly or an OAuth key that can generate one.
"""
import gzip
import tempfile
import time
import uuid
from typing import IO, Iterable, List, Optional

from runzero.client import Client
from runzero.types import ImportAsset, ImportTask, NewAssetImport, Task


class CustomAssets:
    """Management of Custom Asset Data for your own custom integrations.

    Custom data sources are descriptive registered associations between sources of data
    and assets imported which are associated with those sources.

    The data sent to the server has basic checks performed and is loaded as an import task
    when it can find the next available worker to do so. Therefore, the result
    is a `class:runzero.Task` which you can check the status of.

    See related :class:`runzero.account.CustomSources` to work with the custom asset data
    sources registered to the account.

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
        source_id: uuid.UUID,
        assets: List[ImportAsset],
        task_info: Optional[ImportTask] = None,
    ) -> Task:
        """
        Upload your custom assets to the runZero platform.

        :param org_id: Organization ID to import these assets into
        :param site_id: ID of the Site to import these asstes into
        :param source_id: Custom asset source id for the provided Import Assets
        :param assets: A collection of ImportAssets to upload
        :param task_info: Descriptive information associated with the import
            task to be created. If omitted, a task name is generated for you

        :return Task: The runZero task associated with processing the asset upload
        :raises ServerError, ClientError, AuthError
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

        asset_import_req = _create_custom_asset_request(
            site_id=site_id,
            source_id=source_id,
            import_task=task_info,
            assets=assets,
        )

        tags_as_str = ""
        if asset_import_req.import_task.tags is not None:
            tags_as_str = ",".join([tag.__root__ for tag in asset_import_req.import_task.tags])
        multipart_form_data = (
            ("assetData", ("asset_data.jsonl.gz", asset_import_req.asset_data)),
            ("siteId", (None, str(asset_import_req.site_id))),
            ("sourceId", (None, str(asset_import_req.source_id))),
            ("importTask.name", (None, asset_import_req.import_task.name)),
            ("importTask.description", (None, asset_import_req.import_task.description)),
            ("importTask.tags", (None, tags_as_str)),
        )
        res = self._client.execute("POST", self._ENDPOINT.format(oid=org_id), files=multipart_form_data, multipart=True)
        return Task.parse_obj(res.json_obj)


def _import_assets_into_gzip_jsonl(import_assets: Iterable[ImportAsset]) -> IO[bytes]:
    tmp = tempfile.TemporaryFile(mode="w+b")
    with gzip.GzipFile(fileobj=tmp, mode="wb") as gzw:
        for asset_obj in import_assets:
            gzw.write(asset_obj.json(by_alias=True).encode("utf-8") + "\n".encode("utf-8"))
    tmp.seek(0)
    return tmp


def _create_custom_asset_request(
    site_id: uuid.UUID, source_id: uuid.UUID, assets: Iterable[ImportAsset], import_task: ImportTask
) -> NewAssetImport:
    # TODO: We are disabling validation on all fields with .construct
    # until openapi 'bytes' type and pydantic can agree on a file-like.
    # See FastAPI implementation of UploadFile for ref
    return NewAssetImport.construct(
        siteId=site_id,
        sourceId=source_id,
        importTask=import_task,
        assetData=_import_assets_into_gzip_jsonl(assets),  # type: ignore
    )
