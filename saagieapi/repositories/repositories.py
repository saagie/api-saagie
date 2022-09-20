import logging
from pathlib import Path
from typing import Dict, Optional

from gql import gql

from .gql_queries import *


class Repositories:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(
        self, minimal: Optional[bool] = False, last_synchronization: bool = True, pprint_result: Optional[bool] = None
    ) -> Dict:
        """
        Get information for all repositories
        NB: You can only get repositories information if you have the right to
        access the technology catalog

        Parameters
        ----------
        minimal : bool, optional
            Whether to only return the repository's name and id, default to False
        last_synchronization : bool, optional
            Whether to only fetch the last synchronization of each repository
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of repositories
        """
        params = {
            "minimal": minimal,
            "lastSynchronization": last_synchronization,
        }
        query = gql(GQL_LIST_REPOSITORIES)
        return self.saagie_api.client_gateway.execute(query, variable_values=params, pprint_result=pprint_result)

    def get_info(
        self,
        repository_id: str,
        with_reverted: bool = False,
        synchronization_reports_limit: Optional[int] = None,
        last_synchronization: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get information for a given repository
        NB: You can only get repository information if you have at least the
        viewer role on the catalog

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)
        with_reverted : bool, optional
            Whether to only fetch not reverted synchronization reports
        synchronization_reports_limit : int, optional
            Maximum limit of synchronization reports per repository. Fetch from most recent
            to oldest
        last_synchronization : bool, optional
            Whether to only fetch the last synchronization of each repository
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of repository information
        """

        params = {
            "id": repository_id,
            "withReverted": with_reverted,
            "lastSynchronization": last_synchronization,
            "limit": synchronization_reports_limit,
        }
        return self.saagie_api.client_gateway.execute(
            query=gql(GQL_GET_REPOSITORY_INFO), variable_values=params, pprint_result=pprint_result
        )

    def create(self, name: str, file: str = None, url: str = None) -> Dict:
        """Create a new repository on the platform.

        Parameters
        ----------
        name : str
            Name of the repository (must not already exist)
        file : str, optional
            Local path of the repository zip to upload
        url : str, optional
            Repository URL, should have public access

        Returns
        -------
        dict
            Dict of created repository

        Raises
        ------
        ValueError
            If the parameters 'file' and 'url' are not filled
        """
        params = {"repositoryInput": {"name": name}}
        result = self.__launch_request(file, url, GQL_CREATE_REPOSITORY, params)
        logging.info("✅ Repository [%s] successfully created", name)
        return result

    def __launch_request(self, file: str, url: str, payload_str: str, params: Dict) -> Dict:
        """Launch a GQL request with specified file, payload and params
        GQL3 needed to use this function
        Parameters
        ----------
        file : str
            Path to your file
        url : str
            Repository URL
        payload_str : str
            Payload to send
        params: dict
            variable values to pass to the GQL request

        Returns
        -------
        dict
            Dict of the request response
        """
        if file:
            file = Path(file)
            with file.open(mode="rb") as file_content:
                params["upload"] = file_content
                try:
                    res = self.saagie_api.client_gateway.execute(
                        query=gql(payload_str), variable_values=params, upload_files=True
                    )
                except Exception as exception:
                    logging.error("Something went wrong %s", exception)
                    raise exception
                return res

        elif url:
            params["repositoryInput"]["url"] = url
            try:
                res = self.saagie_api.client_gateway.execute(query=gql(payload_str), variable_values=params)
            except Exception as exception:
                logging.error("Something went wrong %s", exception)
                raise exception
            return res

        else:
            raise ValueError("❌ Value error: Must specify a fill 'file' or 'url'")

    def delete(self, repository_id: str) -> Dict:
        """Delete a given repository

        Parameters
        ----------
        repository_id : str
            UUID of your repository

        Returns
        -------
        dict
            Dict of deleted repository

        """

        result = self.saagie_api.client_gateway.execute(
            query=gql(GQL_DELETE_REPOSITORY), variable_values={"removeRepositoryId": repository_id}
        )
        logging.info("✅ Repository [%s] successfully deleted", repository_id)
        return result

    def edit(
        self, repository_id: str, name: str = None, url: str = None, trigger_synchronization: bool = False
    ) -> Dict:
        """
        Edit a repository information only for repository fetch from URL.
        If you want to change the zip file for a repository, please use the function synchronize

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)
        name : str, optional
            Repository name
            If not filled, defaults to current value, else it will change the repository's name
        url : str, optional
            Repository URL
            if not filled, defaults to current value, else it will change the URL of the repository
        trigger_synchronization : bool, optional
            If URL is modified and this flag is set to true, the update triggers the synchronization
            if not filled, it will no trigger the synchronization

        Returns
        -------
        dict
            Dict of repository information

        """
        params = {"repositoryInput": {"id": repository_id, "triggerSynchronization": trigger_synchronization}}
        if name:
            params["repositoryInput"]["name"] = name

        if url:
            params["repositoryInput"]["url"] = url

        result = self.saagie_api.client_gateway.execute(query=gql(GQL_EDIT_REPOSITORY), variable_values=params)
        logging.info("✅ Repository [%s] successfully edited", repository_id)
        return result

    def synchronize(self, repository_id: str, file: str = None) -> Dict:
        """
        Synchronize manually a repository.
        If you repository has created by zip file, you should provide a new path of the local repository zip file

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)
        file : str, optional
            Path to your file

        Returns
        -------
        dict
            Dict of repository information

        """
        params = {"id": repository_id}
        if file:
            result = self.__launch_request(file, "", GQL_SYNCHRONIZE_REPOSITORY, params)
        else:
            result = self.saagie_api.client_gateway.execute(
                query=gql(GQL_SYNCHRONIZE_REPOSITORY), variable_values=params
            )
        logging.info("✅ Repository [%s] successfully synchronized", repository_id)
        return result

    def revert_last_synchronization(self, repository_id: str) -> Dict:
        """
        Revert the last synchronization

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)

        Returns
        -------
        dict
            Dict of repository information
        Raises
        ------
        NameError
            If the repository does not exist or the user don't have the permission to see it or can not be revert
        """
        repositories = self.list(minimal=True, last_synchronization=True)["repositories"]
        repository = list(filter(lambda p: p["id"] == repository_id, repositories))
        if repository:
            synchronization_report_id = repository[0]["synchronizationReports"]["lastReversibleId"]
            if synchronization_report_id:
                params = {"repositoryId": repository_id, "synchronizationReportId": synchronization_report_id}
                return self.saagie_api.client_gateway.execute(
                    query=gql(GQL_REVERT_LAST_SYNCHRONISATION), variable_values=params
                )
        raise NameError(
            f"❌ Repository [{repository_id}] does not exist or "
            f"you don't have permission to see it or can not be revert."
        )

    def get_id(self, repository_name: str) -> str:
        """Get the repository id with the repository name
        Parameters
        ----------
        repository_name : str
            Name of your project
        Returns
        -------
        str
            Repository UUID

        Raises
        ------
        NameError
            If repository does not exist or the user don't have permission to see it
        """
        repositories = self.list(minimal=True, last_synchronization=True)["repositories"]
        repository = list(filter(lambda p: p["name"] == repository_name, repositories))
        if repository:
            repository_id = repository[0]["id"]
            return repository_id
        raise NameError(f"❌ Repository {repository_name} does not exist or you don't have permission to see it.")
