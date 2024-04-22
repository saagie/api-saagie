# pylint: disable=attribute-defined-outside-init
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.storages import Storages
from saagieapi.storages.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestStorages:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()

        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_storages_for_project_gql(self):
        query = gql(GQL_LIST_STORAGE_FOR_PROJECT)
        self.client.validate(query)

    def test_list_storages_for_project(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": project_id,
            "minimal": False,
        }

        expected_query = gql(GQL_LIST_STORAGE_FOR_PROJECT)

        storage.list_for_project(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_storage_gql(self):
        query = gql(GQL_GET_STORAGE_INFO)
        self.client.validate(query)

    def test_get_storage(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "volumeId": storage_id,
        }

        expected_query = gql(GQL_GET_STORAGE_INFO)

        storage.get(storage_id=storage_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_storage_gql(self):
        query = gql(GQL_CREATE_STORAGE)
        self.client.validate(query)

    def test_create_storage(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "name_test"
        size = "1024"
        desc = "description"

        params = {
            "volume": {
                "projectId": project_id,
                "name": name,
                "size": size,
                "description": desc,
            }
        }

        expected_query = gql(GQL_CREATE_STORAGE)

        storage.create(project_id=project_id, storage_name=name, storage_size=size, storage_description=desc)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_edit_storage_gql(self):
        query = gql(GQL_EDIT_STORAGE)
        self.client.validate(query)

    def test_edit_storage(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "name_test"
        desc = "description"

        params = {
            "volume": {
                "id": storage_id,
                "name": name,
                "description": desc,
            }
        }

        expected_query = gql(GQL_EDIT_STORAGE)

        storage.edit(storage_id=storage_id, storage_name=name, description=desc)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_delete_storage_gql(self):
        query = gql(GQL_DELETE_STORAGE)
        self.client.validate(query)

    def test_delete_storage(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": storage_id,
        }

        expected_query = gql(GQL_DELETE_STORAGE)

        with patch.object(storage, "get") as get:
            get.return_value = {
                "volume": {
                    "id": "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f",
                    "linkedApp": {
                        "id": "6871e9a2-2c06-45fe-bf8d-6356090f1d1d",
                        "name": "Jupyter Notebook",
                        "currentVersion": {"number": 1, "volumesWithPath": []},
                    },
                }
            }
            storage.delete(storage_id=storage_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_delete_storage_error(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f"

        with patch.object(storage, "get") as get, pytest.raises(ValueError):
            get.return_value = {
                "volume": {
                    "id": "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f",
                    "linkedApp": {
                        "id": "6871e9a2-2c06-45fe-bf8d-6356090f1d1d",
                        "name": "Jupyter Notebook",
                        "currentVersion": {
                            "number": 1,
                            "volumesWithPath": [
                                {"path": "/notebooks-dir", "volume": {"id": "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f"}}
                            ],
                        },
                    },
                }
            }
            storage.delete(storage_id=storage_id)

    def test_unlink_storage_gql(self):
        query = gql(GQL_UNLINK_STORAGE)
        self.client.validate(query)

    def test_unlink_storage(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": storage_id,
        }

        expected_query = gql(GQL_UNLINK_STORAGE)

        with patch.object(storage, "get") as get:
            get.return_value = {
                "volume": {
                    "id": "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f",
                    "linkedApp": {
                        "id": "6871e9a2-2c06-45fe-bf8d-6356090f1d1d",
                        "name": "Jupyter Notebook",
                        "currentVersion": {"number": 1, "volumesWithPath": []},
                    },
                }
            }
            storage.unlink(storage_id=storage_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_unlink_storage_error(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f"

        with patch.object(storage, "get") as get, pytest.raises(ValueError):
            get.return_value = {
                "volume": {
                    "id": "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f",
                    "linkedApp": {
                        "id": "6871e9a2-2c06-45fe-bf8d-6356090f1d1d",
                        "name": "Jupyter Notebook",
                        "currentVersion": {
                            "number": 1,
                            "volumesWithPath": [
                                {"path": "/notebooks-dir", "volume": {"id": "89bf5f86-3fc3-4bf6-879b-7ca8eafe6c4f"}}
                            ],
                        },
                    },
                }
            }
            storage.unlink(storage_id=storage_id)

    def test_move_storage_gql(self):
        query = gql(GQL_MOVE_STORAGE)
        self.client.validate(query)

    def test_move_storage(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        target_pf_id = 1
        target_project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "volumeId": storage_id,
            "targetPlatformId": target_pf_id,
            "targetProjectId": target_project_id,
        }

        expected_query = gql(GQL_MOVE_STORAGE)

        storage.move(storage_id=storage_id, target_platform_id=target_pf_id, target_project_id=target_project_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_duplicate_storage_gql(self):
        query = gql(GQL_DUPLICATE_STORAGE)
        self.client.validate(query)

    def test_duplicate_storage(self, saagie_api_mock):
        storage = Storages(saagie_api_mock)

        storage_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "volumeId": storage_id,
        }

        expected_query = gql(GQL_DUPLICATE_STORAGE)

        storage.duplicate(storage_id=storage_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)
