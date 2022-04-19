from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.apps.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(dir_path + '/..')


class TestApps:

    def setup_method(self):
        self.client = create_gql_client()

    def test_get_project_apps(self):
        query = gql(gql_get_project_apps)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_app(self):
        query = gql(gql_get_project_app)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_app(self):
        query = gql(gql_create_app)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def edit_app(self):
        query = gql(gql_edit_app)
        result = self.client.validate(query)
        expected = None
        assert result == expected