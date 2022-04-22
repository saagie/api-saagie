from gql import gql
from .saagie_api_unit_test import create_gql_client
from saagieapi.projects.gql_queries import *


class TestProjects:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_projects(self):
        query = gql(gql_list_projects)
        self.client.validate(query)

    def test_get_project_technologies(self):
        query = gql(gql_get_project_technologies)
        self.client.validate(query)

    def test_get_project_info(self):
        query = gql(gql_get_project_info)
        self.client.validate(query)

    def test_gql_create_project(self):
        query = gql(gql_create_project)
        self.client.validate(query)

    def test_delete_project(self):
        query = gql(gql_delete_project)
        self.client.validate(query)
