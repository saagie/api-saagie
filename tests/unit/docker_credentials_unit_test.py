# pylint: disable=attribute-defined-outside-init
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.docker_credentials import DockerCredentials
from saagieapi.docker_credentials.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestDockerCredentials:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()

        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client()

    def test_get_all_docker_credentials_gql(self):
        query = gql(GQL_GET_ALL_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_get_all_docker_credentials(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "projectId": project_id,
        }

        expected_query = gql(GQL_GET_ALL_DOCKER_CREDENTIALS)

        docker.list_for_project(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_docker_credentials_gql(self):
        query = gql(GQL_GET_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_get_docker_credentials(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        cred = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "projectId": project_id,
            "id": cred,
        }

        expected_query = gql(GQL_GET_DOCKER_CREDENTIALS)

        docker.get_info(project_id=project_id, credential_id=cred)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_docker_credentials_for_username(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        username = "myuser"

        with patch.object(docker, "list_for_project") as l_project:
            l_project.return_value = {
                "allDockerCredentials": [
                    {
                        "id": "0cb2662f-84eb-4a7d-93cb-2340f7773bce",
                        "registry": None,
                        "username": "myuser",
                        "lastUpdate": "2022-04-26T14:20:17.118Z",
                        "jobs": [],
                    }
                ]
            }
            docker.get_info_for_username(project_id=project_id, username=username)

    def test_get_docker_credentials_for_username_error_no_creds_for_user(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        username = "my.user"

        with patch.object(docker, "list_for_project") as l_project, pytest.raises(RuntimeError):
            l_project.return_value = {
                "allDockerCredentials": [
                    {
                        "id": "0cb2662f-84eb-4a7d-93cb-2340f7773bce",
                        "registry": None,
                        "username": "myuser",
                        "lastUpdate": "2022-04-26T14:20:17.118Z",
                        "jobs": [],
                    }
                ]
            }
            docker.get_info_for_username(project_id=project_id, username=username)

    def test_get_docker_credentials_for_username_error_no_creds(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        username = "my.user"

        with patch.object(docker, "list_for_project") as l_project, pytest.raises(RuntimeError):
            l_project.return_value = {"allDockerCredentials": []}
            docker.get_info_for_username(project_id=project_id, username=username)

    def test_create_docker_credentials_gql(self):
        query = gql(GQL_CREATE_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_create_docker_credentials(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        username = "myuser"
        pwd = "mypwd"
        registry = "my.registry.com"

        params = {"projectId": project_id, "username": username, "password": pwd, "registry": registry}

        expected_query = gql(GQL_CREATE_DOCKER_CREDENTIALS)

        docker.create(project_id=project_id, username=username, password=pwd, registry=registry)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_upgrade_docker_credentials_gql(self):
        query = gql(GQL_UPGRADE_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_upgrade_docker_credentials(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        cred_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        username = "myuser"
        pwd = "mypwd"
        registry = "my.registry.com"

        params = {"id": cred_id, "projectId": project_id, "username": username, "password": pwd, "registry": registry}

        expected_query = gql(GQL_UPGRADE_DOCKER_CREDENTIALS)

        docker.upgrade(credential_id=cred_id, project_id=project_id, username=username, password=pwd, registry=registry)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_upgrade_docker_credentials_for_username(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        cred_id = "0cb2662f-84eb-4a7d-93cb-2340f7773bce"
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        username = "myuser"
        pwd = "mypwd"
        registry = "my.registry.com"

        params = {"id": cred_id, "projectId": project_id, "password": pwd, "registry": registry}

        expected_query = gql(GQL_UPGRADE_DOCKER_CREDENTIALS)

        with patch.object(docker, "get_info_for_username") as l_project:
            l_project.return_value = {
                "id": "0cb2662f-84eb-4a7d-93cb-2340f7773bce",
                "registry": None,
                "username": "myuser",
                "lastUpdate": "2022-04-26T14:20:17.118Z",
                "jobs": [],
            }
            docker.upgrade_for_username(project_id=project_id, username=username, password=pwd, registry=registry)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_delete_docker_credentials_gql(self):
        query = gql(GQL_DELETE_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_delete_docker_credentials(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        cred_id = "0cb2662f-84eb-4a7d-93cb-2340f7773bce"
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": cred_id,
            "projectId": project_id,
        }

        expected_query = gql(GQL_DELETE_DOCKER_CREDENTIALS)

        docker.delete(project_id=project_id, credential_id=cred_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_delete_docker_credentials_for_username(self, saagie_api_mock):
        docker = DockerCredentials(saagie_api_mock)

        cred_id = "0cb2662f-84eb-4a7d-93cb-2340f7773bce"
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        username = "myuser"

        params = {
            "id": cred_id,
            "projectId": project_id,
        }

        expected_query = gql(GQL_DELETE_DOCKER_CREDENTIALS)

        with patch.object(docker, "get_info_for_username") as l_project:
            l_project.return_value = {
                "id": "0cb2662f-84eb-4a7d-93cb-2340f7773bce",
                "registry": None,
                "username": "myuser",
                "lastUpdate": "2022-04-26T14:20:17.118Z",
                "jobs": [],
            }
            docker.delete_for_username(project_id=project_id, username=username)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)
