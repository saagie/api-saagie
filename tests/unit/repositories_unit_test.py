# pylint: disable=attribute-defined-outside-init,protected-access,redefined-builtin
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.repositories import Repositories
from saagieapi.repositories.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestProjects:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()

        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client(file_name="technology_schema.graphqls")

    def test_list_repositories_gql(self):
        query = gql(GQL_LIST_REPOSITORIES)
        self.client.validate(query)

    def test_list_repositories(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        params = {
            "minimal": False,
            "lastSynchronization": True,
        }

        expected_query = gql(GQL_LIST_REPOSITORIES)

        repository.list()

        saagie_api_mock.client_gateway.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_repository_info_gql(self):
        query = gql(GQL_GET_REPOSITORY_INFO)
        self.client.validate(query)

    def test_get_repository_info(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": repository_id,
            "withReverted": False,
            "lastSynchronization": False,
            "limit": None,
        }

        expected_query = gql(GQL_GET_REPOSITORY_INFO)

        repository.get_info(repository_id=repository_id)

        saagie_api_mock.client_gateway.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_create_repository_gql(self):
        query = gql(GQL_CREATE_REPOSITORY)
        self.client.validate(query)

    def test_create_repository(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_name = "new_catalog"
        req_info = {
            "addRepository": {
                "count": 1,
                "objects": [
                    {
                        "id": "d04e578f-546a-41bf-bb8c-790e99a4f6c8",
                        "name": repository_name,
                    }
                ],
            }
        }

        with patch.object(repository, "_Repositories__launch_request") as req:
            req.return_value = req_info
            res = repository.create(name=repository_name)

        assert res == req_info

    def test_delete_repository_gql(self):
        query = gql(GQL_DELETE_REPOSITORY)
        self.client.validate(query)

    def test_delete_repository(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {"removeRepositoryId": repository_id}

        expected_query = gql(GQL_DELETE_REPOSITORY)

        repository.delete(repository_id=repository_id)

        saagie_api_mock.client_gateway.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_edit_repository_info_gql(self):
        query = gql(GQL_EDIT_REPOSITORY)
        self.client.validate(query)

    def test_edit_repository_info(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "new_name"
        url = "new_url"

        params = {
            "repositoryInput": {
                "id": repository_id,
                "triggerSynchronization": False,
                "name": name,
                "url": url,
            }
        }

        expected_query = gql(GQL_EDIT_REPOSITORY)

        repository.edit(repository_id=repository_id, name=name, url=url)

        saagie_api_mock.client_gateway.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_synchronize_repository_gql(self):
        query = gql(GQL_SYNCHRONIZE_REPOSITORY)
        self.client.validate(query)

    def test_synchronize_repository_without_file(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {"id": repository_id}

        expected_query = gql(GQL_SYNCHRONIZE_REPOSITORY)

        repository.synchronize(repository_id=repository_id)

        saagie_api_mock.client_gateway.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_synchronize_repository_with_file(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        req_info = {
            "synchronizeRepository": {
                "count": 5,
                "report": {
                    "id": "47589bad-729d-4afe-99e8-05824dd66858",
                    "endedAt": "2022-09-21T12:15:50.513Z",
                    "startedAt": "2022-09-21T12:15:50.513Z",
                    "trigger": {"author": "hello.world", "type": "MANUAL"},
                    "technologyReports": [
                        {"status": "DELETED", "technologyId": "aws-batch"},
                        {"status": "DELETED", "technologyId": "aws-emr"},
                        {"status": "DELETED", "technologyId": "aws-glue"},
                        {"status": "DELETED", "technologyId": "aws-lambda"},
                        {"status": "UNCHANGED", "technologyId": "cloudbeaver"},
                        {"status": "UNCHANGED", "technologyId": "dash"},
                    ],
                    "issues": [],
                },
                "repositoryId": "0e09c160-7f68-402e-9156-0d414e53318b",
                "repositoryName": "hello world repo",
            }
        }

        with patch.object(repository, "_Repositories__launch_request") as req:
            req.return_value = req_info

            res = repository.synchronize(repository_id=repository_id, file="file")

        assert res == req_info

    def test_revert_repository_gql(self):
        query = gql(GQL_REVERT_LAST_SYNCHRONISATION)
        self.client.validate(query)

    def test_revert_repository_success(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        last_id = "a17c73ed-fca1-4f25-a343-914c7ac23bae"

        params = {
            "repositoryId": repository_id,
            "synchronizationReportId": last_id,
        }

        expected_query = gql(GQL_REVERT_LAST_SYNCHRONISATION)

        with patch.object(repository, "list") as list:
            list.return_value = {
                "repositories": [
                    {
                        "id": repository_id,
                        "name": "Saagie",
                        "synchronizationReports": {
                            "lastReversibleId": last_id,
                            "count": 1,
                            "list": [{"endedAt": "2022-09-12T10:27:44.549Z", "issues": [], "revert": None}],
                        },
                    }
                ]
            }
            repository.revert_last_synchronization(repository_id=repository_id)

        saagie_api_mock.client_gateway.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_revert_repository_error(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        with patch.object(repository, "list") as list, pytest.raises(NameError):
            list.return_value = {"repositories": []}
            repository.revert_last_synchronization(repository_id=repository_id)

    def test_get_repository_id_success(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_name = "Saagie"

        with patch.object(repository, "list") as list:
            list.return_value = {
                "repositories": [
                    {
                        "id": "860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                        "name": repository_name,
                    }
                ]
            }
            repository.get_id(repository_name=repository_name)

    def test_get_repository_id_error(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        repository_name = "Saagie"

        with patch.object(repository, "list") as list, pytest.raises(NameError):
            list.return_value = {
                "repositories": [
                    {
                        "id": "860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                        "name": "Sagie",
                    }
                ]
            }
            repository.get_id(repository_name=repository_name)

    def test_launch_request_with_file_success(self, saagie_api_mock, tmp_path):
        saagie_api_mock.client_gateway.execute.return_value = True
        repository = Repositories(saagie_api_mock)

        tmp_file = Path(tmp_path / "file.txt")
        tmp_file.write_text("This is a test file.", encoding="utf-8")

        request = GQL_DELETE_REPOSITORY

        res = repository._Repositories__launch_request(file=tmp_file, url="", payload_str=request, params={})

        assert res is True

    def test_launch_request_with_file_exception(self, saagie_api_mock, tmp_path):
        repository = Repositories(saagie_api_mock)

        tmp_file = Path(tmp_path / "file.txt")
        tmp_file.write_text("This is a test file.", encoding="utf-8")

        with pytest.raises(Exception):
            repository._Repositories__launch_request(file=tmp_file, url="", payload_str="request", params={})

    def test_launch_request_with_url_success(self, saagie_api_mock):
        saagie_api_mock.client_gateway.execute.return_value = True
        repository = Repositories(saagie_api_mock)

        request = GQL_DELETE_REPOSITORY

        res = repository._Repositories__launch_request(
            file=None, url="url", payload_str=request, params={"repositoryInput": {}}
        )

        assert res is True

    def test_launch_request_with_url_exception(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        with pytest.raises(Exception):
            repository._Repositories__launch_request(
                file=None, url="url", payload_str="request", params={"repositoryInput": {}}
            )

    def test_launch_request_without_file_and_url(self, saagie_api_mock):
        repository = Repositories(saagie_api_mock)

        with pytest.raises(ValueError):
            repository._Repositories__launch_request(file=None, url=None, payload_str="request", params={})
