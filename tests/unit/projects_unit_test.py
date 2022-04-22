from gql import gql
from .saagie_api_unit_test import create_gql_client
from saagieapi.projects.gql_queries import *


class TestProjects:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_projects(self):
        query = gql(GQL_LIST_PROJECTS)
        self.client.validate(query)

    def test_get_project_technologies(self):
        query = gql(GQL_GET_PROJECT_TECHNOLOGIES)
        self.client.validate(query)

    def test_get_project_info(self):
        query = gql(GQL_GET_PROJECT_INFO)
        self.client.validate(query)

    def test_gql_create_project(self):
        query = gql(GQL_CREATE_PROJECT)
        self.client.validate(query)

    def test_delete_project(self):
        query = gql(GQL_DELETE_PROJECT)
        self.client.validate(query)
