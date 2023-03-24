"""
Management of runZero tasks.
"""
import uuid
from typing import List, Optional

from runzero.client import Client
from runzero.types import Task


class Tasks:
    """Management of runZero tasks.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/tasks"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, org_id: uuid.UUID, status: Optional[str] = None) -> List[Task]:
        """
        Retrieves all runZero Tasks available within the given Organization

        :param org_id: The unique ID of the organization to retrieve the tasks from.
        :param status: An optional status value to filter tasks by. This is a
            case-insensitive string match, stripped of surrounding whitespace.
        :return: A list of all tasks
        """
        params = {"_oid": str(org_id)}
        res = self._client.execute("GET", self._ENDPOINT, params=params)
        result: List[Task] = []
        for obj in res.json_obj:
            task = Task.parse_obj(obj)
            if status is not None and task.status is not None and task.status.strip().lower() != status.strip().lower():
                continue
            result.append(task)
        return result

    def get(self, org_id: uuid.UUID, name: Optional[str] = None, task_id: Optional[uuid.UUID] = None) -> Optional[Task]:
        """
        Retrieves the runZero Task with the provided name or id, if it exists in your organization.

        One of either name or id must be provided.

        :param org_id: ID of the organization the requested Task is in
        :param name: Optional name of the task you want returned
        :param task_id: Optional id of the task you want returned
        :return: Task or None
        """
        params = {"_oid": str(org_id)}
        if name is None and task_id is None:
            raise ValueError("must provide either task_id or task name")
        if task_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{str(task_id)}", params=params)
            return Task.parse_obj(res.json_obj)
        # name
        for task in self.get_all(org_id):
            if task.name == name:
                return task
        return None

    def get_status(self, org_id: uuid.UUID, task_id: uuid.UUID) -> Optional[str]:
        """
        Retrieves the status of a runZero Task with the provided id, if it exists in your organization.

        The org_id should be provided if using an Account level api key.

        :param task_id: ID of the Task you want the status for
        :param org_id: Optional id of the organization the requested Task is in. This is
            necessary if you use an Auth token.
        :return: a string result indicating task status, or None
        """
        params = {"_oid": str(org_id)}
        res = self._client.execute("GET", f"{self._ENDPOINT}/{str(task_id)}", params=params)
        task = Task.parse_obj(res.json_obj)
        if task is None:
            return None
        return task.status
