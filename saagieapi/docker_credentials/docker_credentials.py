from typing import Dict

from gql import gql

from .gql_queries import *


class DockerCredentials:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_for_project(self, project_id: str) -> Dict:
        """
        Get all saved docker credentials for a specific project
        Parameters
        ----------
        project_id : str
            ID of the project
        Returns
        -------
        dict

        """
        params = {"projectId": project_id}
        return self.client.execute(gql(GQL_GET_ALL_DOCKER_CREDENTIALS), variable_values=params)

    def get_info(self, project_id: str, credential_id: str) -> Dict:
        """
        Get the info of a specific docker credentials in a specific project
        Parameters
        ----------
        project_id :
            ID of the project
        credential_id : str
            ID of the credentials of the container registry
        Returns
        -------
        dict

        """
        params = {"projectId": project_id, "id": credential_id}
        return self.client.execute(gql(GQL_GET_DOCKER_CREDENTIALS), variable_values=params)

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

        """
        all_docker_credentials = self.list_for_project(project_id)["allDockerCredentials"]
        if len(all_docker_credentials):
            res = [
                credentials
                for credentials in all_docker_credentials
                if credentials["username"] == username and credentials["registry"] == registry
            ]
            if len(res):
                return res[0]
            raise RuntimeError(
                f"There are no docker credentials in the project: '{project_id}' with the username: '{username}' "
                f"and registry '{registry}'"
            )
        raise RuntimeError(f"There are no docker credentials in the project: '{project_id}'")

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

        """
        params = {"username": username, "password": password, "projectId": project_id}
        if registry:
            params["registry"] = registry
        return self.client.execute(gql(GQL_CREATE_DOCKER_CREDENTIALS), variable_values=params)

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

        """
        params = {"id": credential_id, "password": password, "projectId": project_id}
        if registry:
            params["registry"] = registry
        if username:
            params["username"] = username
        return self.client.execute(gql(GQL_UPGRADE_DOCKER_CREDENTIALS), variable_values=params)

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
        """
        credential_id = self.get_info_for_username(project_id, username, registry)["id"]
        params = {"id": credential_id, "password": password, "projectId": project_id}

        if registry:
            params["registry"] = registry

        return self.client.execute(gql(GQL_UPGRADE_DOCKER_CREDENTIALS), variable_values=params)

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
        """
        params = {"id": credential_id, "projectId": project_id}
        return self.client.execute(gql(GQL_DELETE_DOCKER_CREDENTIALS), variable_values=params)

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
        """
        credential_id = self.get_info_for_username(project_id, username, registry)["id"]
        params = {"id": credential_id, "projectId": project_id}
        return self.client.execute(gql(GQL_DELETE_DOCKER_CREDENTIALS), variable_values=params)
