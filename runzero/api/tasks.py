"""
Management of runZero tasks.
"""

import uuid
from typing import Dict, List, Optional, Union

from runzero.client import Client
from runzero.types import Task, TaskOptions


class Tasks:
    """Management of runZero tasks.

    :param client: A handle to the :class:`runzero.Client` client which manages interactions
        with the runZero server.
    """

    _ENDPOINT = "api/v1.0/org/tasks"

    def __init__(self, client: Client):
        """Constructor method"""
        self._client = client

    def get_all(self, org_id: uuid.UUID, status: Optional[str] = None, query: Optional[str] = None) -> List[Task]:
        """
        Retrieves all runZero Tasks available within the given Organization

        :param org_id: The unique ID of the organization to retrieve the tasks from.
        :param status: An optional status value to filter tasks by. This is a
            case-insensitive string match, stripped of surrounding whitespace.
        :param query: An optional query to filter returned tasks.
            Query string format is the same as in-UI search. See https://www.runzero.com/docs/search-query-tasks/
        :returns: A list of all tasks
        """
        params: Dict[str, Union[str, uuid.UUID]] = {"_oid": org_id}
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

    def get(self, org_id: uuid.UUID, name: Optional[str] = None, task_id: Optional[uuid.UUID] = None) -> Optional[Task]:
        """
        Retrieves the runZero Task with the provided name or id, if it exists in your organization.

        :param org_id: ID of the organization the requested task is in
        :param name: Optional name of the task to retrieve. If not provided, must provide task_id.
        :param task_id: Optional id of the task to retrieve. If not provided, must provide name.

        :raises: AuthError, ClientError, ServerError
            ValueError if neither task_id nor name are provided.
        """
        params = {"_oid": org_id}
        if name is None and task_id is None:
            raise ValueError("must provide either task_id or task name")
        if task_id is not None:
            res = self._client.execute("GET", f"{self._ENDPOINT}/{task_id}", params=params)
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

        :param org_id: ID of the organization the requested task is in
        :param task_id: ID of the task you want the status for
        :returns: a string result indicating task status, or None
        """
        params = {"_oid": org_id}
        res = self._client.execute("GET", f"{self._ENDPOINT}/{task_id}", params=params)
        task = Task.parse_obj(res.json_obj)
        if task is None:
            return None
        return task.status

    def update(self, org_id: uuid.UUID, task_id: uuid.UUID, task_options: TaskOptions) -> Task:
        """
        Updates task parameters with provided task options values.

        :param org_id: ID of the organization the requested task is in
        :param task_id: ID of task to modify
        :param task_options: task values to update

        :returns: Task which has been updated
        :raises: AuthError, ClientError, ServerError
        """
        params = {"_oid": org_id}
        res = self._client.execute("PATCH", f"{self._ENDPOINT}/{task_id}", data=task_options, params=params)
        return Task.parse_obj(res.json_obj)

    def stop(self, org_id: uuid.UUID, task_id: uuid.UUID) -> Task:
        """
        Signals an explorer to stop a currently running task, or signals server to remove
        a future or recurring task.

        :param org_id: ID of the organization the requested task is in
        :param task_id: ID of task to stop, or scheduled task to remove from schedule.

        :returns: Task which has been signalled to stop
        :raises: AuthError, ClientError, ServerError
        """
        params = {"_oid": org_id}
        res = self._client.execute("POST", f"{self._ENDPOINT}/{task_id}/stop", params=params)
        return Task.parse_obj(res.json_obj)

    def hide(self, org_id: uuid.UUID, task_id: uuid.UUID) -> Task:
        """
        Signal that a completed task should be hidden.

        :param org_id: ID of the organization the requested task is in
        :param task_id: task to modify

        :returns: Completed task which has been hidden
        :raises: AuthError, ClientError, ServerError
        """
        params = {"_oid": org_id}
        res = self._client.execute("POST", f"{self._ENDPOINT}/{task_id}/hide", params=params)
        return Task.parse_obj(res.json_obj)
