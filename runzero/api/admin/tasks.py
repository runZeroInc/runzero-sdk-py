"""
Account level management of runZero tasks, including scan templates which apply to all orgs.
"""

import uuid
from typing import List, Optional

from runzero.client import Client
from runzero.types import ScanTemplate, ScanTemplateOptions, Task

# pylint: disable=duplicate-code ##  Acknowledged that this very similar to the org-level tasks interface


class TasksAdmin:
    """Account level management of runZero tasks in all organizations.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/account/tasks"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, status: Optional[str] = None, query: Optional[str] = None) -> List[Task]:
        """
        Retrieves up to 1000 runZero Tasks available within all organizations in the account.

        :param query: An optional query to filter returned tasks.
            Query string format is the same as in-UI search. See https://www.runzero.com/docs/search-query-tasks/
        :param status: An optional status value to filter tasks by. This is a
            case-insensitive string match, stripped of surrounding whitespace.

        :returns: A list of all tasks, or tasks which match the provided query string
        """
        params = {}
        if query is not None:
            params["search"] = query.strip()
        if status is not None:
            params["status"] = status.strip()
        res = self._client.execute("GET", self._ENDPOINT, params=params)
        result: List[Task] = []
        for obj in res.json_obj:
            task = Task.parse_obj(obj)
            result.append(task)
        return result


class TemplatesAdmin:
    """Account level management of runZero scan templates in all organizations.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/account/tasks/templates"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, query: Optional[str] = None) -> List[ScanTemplate]:
        """
        Retrieves up to 1000 runZero task scan templates available to all organizations in the account.

        :param query: An optional query to filter returned templates.
            Query string format is the same as in-UI search. See https://www.runzero.com/docs/search-query-tasks/

        :returns: A list of all task scan templates
        :raises: AuthError, ClientError, ServerError
        """
        params = {}
        if query is not None:
            params["search"] = query.strip()
        res = self._client.execute("GET", f"{self._ENDPOINT}", params=params)
        result: List[ScanTemplate] = []
        for obj in res.json_obj:
            template = ScanTemplate.parse_obj(obj)
            result.append(template)
        return result

    def get(self, name: Optional[str] = None, scan_template_id: Optional[uuid.UUID] = None) -> Optional[ScanTemplate]:
        """
        Retrieves the scan template with the provided name or id, if it exists in your account.

        :param name: Optional, name of the scan template to retrieve
        :param scan_template_id: Optional, the id of the scan template to retrieve

        :returns: ScanTemplate created or None
        :raises: AuthError, ClientError, ServerError
            ValueError if neither scan_template_id nor name are provided.
        """
        if name is None and scan_template_id is None:
            raise ValueError("must provide scan_template_id or scan template name")
        if scan_template_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{scan_template_id}")
            return ScanTemplate.parse_obj(res.json_obj)

        for scan_template in self.get_all():
            if scan_template.name == name:
                return scan_template
        return None

    def create(self, scan_template_options: ScanTemplateOptions) -> Optional[ScanTemplate]:
        """
        Creates a new scan template in your account.

        :param scan_template_options: Description of scan template to create

        :returns: ScanTemplate created or None
        :raises: AuthError, ClientError, ServerError
        """
        res = self._client.execute("POST", f"{self._ENDPOINT}", data=scan_template_options)
        return ScanTemplate.parse_obj(res.json_obj)

    def update(
        self,
        new_scan_template_values: ScanTemplate,
    ) -> Optional[ScanTemplate]:
        """
        Updates an existing scan template in your account by replacing all values.

        The 'id' field of the ScanTemplate must match an existing scan template, which
        will be changed to the new ScanTemplate.

        :param scan_template_id: The id of the scan template to update
        :param new_scan_template_values: Values to update the target scan template with

        :returns: ScanTemplate updated with new values or None
        :raises: AuthError, ClientError, ServerError
        """
        res = self._client.execute("PUT", f"{self._ENDPOINT}", data=new_scan_template_values)
        return ScanTemplate.parse_obj(res.json_obj)

    def delete(self, scan_template_id: uuid.UUID) -> None:
        """
        Deletes a scan template with provided ID from your account.

        :param scan_template_id: The ID of the scan template to delete

        :returns: None
        :raises: AuthError, ClientError, ServerError
        """
        self._client.execute("DELETE", f"{self._ENDPOINT}/{scan_template_id}")
