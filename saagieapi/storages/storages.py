import logging
from typing import Dict, Optional

from gql import gql

from .gql_queries import *


class Storages:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list_for_project(
        self, project_id: str, minimal: Optional[bool] = False, pprint_result: Optional[bool] = None
    ) -> Dict:
        """List storages of project.
        NB: You can only list storage if you have at least the viewer role on
        the project.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        minimal : bool, optional
            Whether to only return the storage's name and id, default to False
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of storage information
        """
        params = {
            "id": project_id,
            "minimal": minimal,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_STORAGE_FOR_PROJECT), variable_values=params, pprint_result=pprint_result
        )

    def get_info(self, project_id: str, storage_id: str) -> Dict:
        """Get storage information.
        NB: You can only get storage information if you have at least the viewer role on
        the project.

        Parameters
        ----------
        project_id : str
            UUID of your project
        storage_id : str
            UUID of your storage

        Returns
        -------
        dict
            Dict of storage information
        """
        storages = self.list_for_project(project_id)["project"]["volumes"]
        for storage in storages:
            if storage["id"] == storage_id:
                return storage

        raise ValueError(f"❌ Storage '{storage_id}' not found in project '{project_id}'")

    def create(
        self,
        project_id,
        storage_name: str,
        storage_size: int,
        storage_description: Optional[str] = None,
    ) -> Dict:
        """Create a storage
        Each optional parameter can be set to change the value of the corresponding field.
        Parameters
        ----------
        storage_name : str
            Storage name
        storage_size : int, optional
            Size of the storage
        storage_description : str, optional
            Description of storage
            if not filled, the storage will have no description
        Returns
        -------
        dict
            Dict of storage information
        """
        params = {
            "projectId": project_id,
            "name": storage_name,
            "size": storage_size,
        }

        if storage_description:
            params["description"] = storage_description

        params = {"volume": params}
        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_STORAGE), variable_values=params)
        logging.info("✅ Storage [%s] successfully created", storage_name)
        return result

    def edit(
        self,
        storage_id: str,
        storage_name: str = None,
        description: str = None,
    ) -> Dict:
        """Edit a storage
        Each optional parameter can be set to change the value of the corresponding field.
        Parameters
        ----------
        storage_id : str
            UUID of your storage
        storage_name : str, optional
            Storage name
            If not filled, defaults to current value, else it will change the storage's name
        description : str, optional
            Description of storage
            if not filled, defaults to current value, else it will change the description of the storage
        Returns
        -------
        dict
            Dict of storage information
        """
        params = {
            "id": storage_id,
        }

        if storage_name:
            params["name"] = storage_name

        if description:
            params["description"] = description

        params = {"volume": params}
        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_STORAGE), variable_values=params)
        logging.info("✅ Storage [%s] successfully edited", storage_id)
        return result

    def delete(self, storage_id: str, project_id: str) -> Dict:
        """Delete a given storage (not currently used)

        Parameters
        ----------
        storage_id : str
            UUID of your storage
        project_id : str
            UUID of your storage project

        Returns
        -------
        dict
            Dict of deleted storage

        Raises
        ------
        ValueError
            When the storage is currently used
        """
        storage_info = self.get_info(project_id, storage_id)
        if storage_info["linkedApp"] is not None and "currentVersion" in storage_info["linkedApp"]:
            for volume in storage_info["linkedApp"]["currentVersion"]["volumesWithPath"]:
                if volume["volume"]["id"] == storage_id:
                    raise ValueError(f"❌ Storage '{storage_id}' is currently used by an App. Deletion impossible.")

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_STORAGE), variable_values={"id": storage_id})
        logging.info("✅ Storage [%s] successfully deleted", storage_id)
        return result

    def unlink(self, storage_id: str, project_id: str) -> Dict:
        """Unlink a given storage (not currently used) to the associated app

        Parameters
        ----------
        storage_id : str
            UUID of your storage
        project_id : str
            UUID of your storage project

        Returns
        -------
        dict
            Dict of unlink storage

        Raises
        ------
        ValueError
            When the storage is currently used
        """
        storage_info = self.get_info(project_id, storage_id)
        if storage_info["linkedApp"] is not None and "currentVersion" in storage_info["linkedApp"].keys():
            for volume in storage_info["linkedApp"]["currentVersion"]["volumesWithPath"]:
                if volume["volume"]["id"] == storage_id:
                    raise ValueError(f"❌ Storage '{storage_id}' is currently used by an App. Unlink impossible.")

        result = self.saagie_api.client.execute(query=gql(GQL_UNLINK_STORAGE), variable_values={"id": storage_id})
        logging.info("✅ Storage [%s] successfully unlinked", storage_id)
        return result
