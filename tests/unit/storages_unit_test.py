# pylint: disable=attribute-defined-outside-init
from gql import gql

from saagieapi.storages.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestStorages:
    def setup_method(self):
        self.client = create_gql_client()

    def test_list_storages_for_project(self):
        query = gql(GQL_LIST_STORAGE_FOR_PROJECT)
        self.client.validate(query)

    def test_create_storage(self):
        query = gql(GQL_CREATE_STORAGE)
        self.client.validate(query)

    def test_edit_storage(self):
        query = gql(GQL_EDIT_STORAGE)
        self.client.validate(query)

    def test_delete_storage(self):
        query = gql(GQL_DELETE_STORAGE)
        self.client.validate(query)

    def test_unlink_storage(self):
        query = gql(GQL_UNLINK_STORAGE)
        self.client.validate(query)
