# pylint: disable=attribute-defined-outside-init,unused-wildcard-import,protected-access

from saagieapi.repositories.repositories import *

from .saagie_api_unit_test import create_gql_client


class TestProjects:
    def setup_method(self):
        self.client = create_gql_client(file_name="technology_schema.graphqls")

    def test_list_repositories(self):
        query = gql(GQL_LIST_REPOSITORIES)
        self.client.validate(query)

    def test_get_repository_info(self):
        query = gql(GQL_GET_REPOSITORY_INFO)
        self.client.validate(query)

    def test_edit_repository_info(self):
        query = gql(GQL_EDIT_REPOSITORY)
        self.client.validate(query)

    def test_synchronize_repository(self):
        query = gql(GQL_SYNCHRONIZE_REPOSITORY)
        self.client.validate(query)

    def test_delete_repository(self):
        query = gql(GQL_DELETE_REPOSITORY)
        self.client.validate(query)

    def test_create_repository(self):
        query = gql(GQL_CREATE_REPOSITORY)
        self.client.validate(query)

    def test_revert_repository(self):
        query = gql(GQL_REVERT_LAST_SYNCHRONISATION)
        self.client.validate(query)
