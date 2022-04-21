from gql import gql
from .saagie_api_unit_test import create_gql_client
from saagieapi.projects.gql_queries import *


class TestProjects:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_projects(self):
        query = gql(gql_list_projects)
        self.client.validate(query)

    def test_get_project_info(self):
        project_id = "1234"
        query = gql(gql_get_project_info.format(project_id))
        self.client.validate(query)

    def test_gql_create_project_without_group_block(self):
        name = "test_project"
        description = ""
        technologies = ['{id: "{1234}"}']
        group_block = ""
        query = gql(gql_create_project.format(name,
                                              description,
                                              group_block,
                                              ', '.join(technologies)))
        self.client.validate(query)

    def test_create_project_with_group_block(self):
        name = "test_project"
        description = ""
        technologies = ['{id: "{1234}"}']
        group = "test_group"
        role = "ROLE_PROJECT_VIEWER"
        group_block = group_block_template.format(group, role)
        query = gql(gql_create_project.format(name,
                                              description,
                                              group_block,
                                              ', '.join(technologies)))
        self.client.validate(query)

    def test_delete_project(self):
        job_id = "1234"
        query = gql(gql_delete_project.format(job_id))
        self.client.validate(query)
