import logging
from typing import Dict, Optional

from gql import gql

from .gql_queries import *


class DockerCredentials:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list_for_project(self, project_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """
        Get all saved docker credentials for a specific project

        Parameters
        ----------
        project_id : str
            ID of the project
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of all docker credentials for a specific project
        """
        params = {"projectId": project_id}
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_ALL_DOCKER_CREDENTIALS), variable_values=params, pprint_result=pprint_result
        )

    def get_info(self, project_id: str, credential_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """
        Get the info of a specific docker credentials in a specific project

        Parameters
        ----------
        project_id :
            ID of the project
        credential_id : str
            ID of the credentials of the container registry
            pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of the info of the docker credentials
        """
        params = {"projectId": project_id, "id": credential_id}
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_DOCKER_CREDENTIALS), variable_values=params, pprint_result=pprint_result
        )

    def get_info_for_username(self, project_id: str, username: str, registry: str = None) -> Dict:
        """
        Get the info of a specific docker credentials in a specific project using the username
        and the registry

        Parameters
        ----------
        project_id :
            ID of the project
        username : str
            Login of the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.

        Returns
        -------
        dict
            Dict of the info of the docker credentials
        """
        all_docker_credentials = self.list_for_project(project_id, pprint_result=False)["allDockerCredentials"]
        if len(all_docker_credentials):
            res = [
                credentials
                for credentials in all_docker_credentials
                if credentials["username"] == username and credentials["registry"] == registry
            ]
            if len(res):
                return res[0]
            raise RuntimeError(
                f"❌ There are no docker credentials in the project: '{project_id}' with the username: '{username}' "
                f"and registry '{registry}'"
            )
        raise RuntimeError(f"❌ There are no docker credentials in the project: '{project_id}'")

    def create(self, project_id: str, username: str, password: str, registry: str = None) -> Dict:
        """
        Create docker credentials for a specific project

        Parameters
        ----------
        project_id : str
            ID of the project
        username : str
            Login to the container registry
        password: str
            Password to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Else, you have to put the url of the container registry

        Returns
        -------
        dict
            Dict of the created docker credentials
        """
        params = {"username": username, "password": password, "projectId": project_id}
        if registry:
            params["registry"] = registry

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_DOCKER_CREDENTIALS), variable_values=params)
        logging.info("✅ Docker Credentials for user [%s] successfully created", username)
        return result

    def upgrade(
        self, project_id: str, credential_id: str, password: str, registry: str = None, username: str = ""
    ) -> Dict:
        """
        Update docker credentials for a specific project

        Parameters
        ----------
        project_id : str
            ID of the project
        credential_id: str
            ID of the created docker credentials
        password: str
            Password to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Otherwise, you have to put the url of the container registry
        username : str, optional
            If you want to change the login of the container registry, you have to set it.
            Otherwise, you can let it to default value

        Returns
        -------
        dict
            Dict of the updated docker credentials
        """
        params = {"id": credential_id, "password": password, "projectId": project_id}
        if registry:
            params["registry"] = registry
        if username:
            params["username"] = username
        result = self.saagie_api.client.execute(query=gql(GQL_UPGRADE_DOCKER_CREDENTIALS), variable_values=params)
        logging.info("✅ Docker Credentials for user [%s] successfully upgraded", username)
        return result

    def upgrade_for_username(self, project_id: str, username: str, password: str, registry: str = None) -> Dict:
        """
        Update docker credentials for a specific project

        Parameters
        ----------
        project_id : str
            ID of the project
        username : str
            Login of the container registry
        password: str
            Password to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Otherwise, you have to put the url of the container registry

        Returns
        -------
        dict
            Dict of the updated docker credentials
        """
        credential_id = self.get_info_for_username(project_id, username, registry)["id"]
        params = {"id": credential_id, "password": password, "projectId": project_id}

        if registry:
            params["registry"] = registry

        result = self.saagie_api.client.execute(query=gql(GQL_UPGRADE_DOCKER_CREDENTIALS), variable_values=params)
        logging.info("✅ Docker Credentials for user [%s] successfully upgraded", username)
        return result

    def delete(self, project_id: str, credential_id: str) -> Dict:
        """
        Delete a specific container registry credentials in a specific project

        Parameters
        ----------
        project_id :
            ID of the project
        credential_id : str
            ID of the credential

        Returns
        -------
        dict
            Dict of the deleted docker credentials
        """
        params = {"id": credential_id, "projectId": project_id}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_DOCKER_CREDENTIALS), variable_values=params)
        logging.info("✅ Docker Credentials [%s] successfully deleted", credential_id)
        return result

    def delete_for_username(self, project_id: str, username: str, registry: str = None) -> Dict:
        """
        Delete a specific container registry credentials in a specific project

        Parameters
        ----------
        project_id :
            ID of the project
        username : str
            Login to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Otherwise, you have to put the url of the container registry

        Returns
        -------
        dict
            Dict of the deleted docker credentials
        """
        credential_id = self.get_info_for_username(project_id, username, registry)["id"]
        params = {"id": credential_id, "projectId": project_id}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_DOCKER_CREDENTIALS), variable_values=params)
        logging.info("✅ Docker Credentials for user [%s] successfully deleted", username)
        return result
