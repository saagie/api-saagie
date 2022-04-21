from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.projects.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(dir_path + '/..')


class TestProjects:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_projects(self):
        query = gql(gql_list_projects)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_info(self):
        query = gql(gql_get_project_info)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_gql_create_project(self):
        query = gql(gql_create_project)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_project(self):
        query = gql(gql_delete_project)
        result = self.client.validate(query)
        expected = None
        assert result == expected
