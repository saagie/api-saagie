from gql import gql
from .saagie_api_unit_test import create_gql_client
from saagieapi.env_vars.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(dir_path + '/..')


class TestEnvVars:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_global_env_vars(self):
        query = gql(gql_list_global_env_vars)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_env_var(self):
        query = gql(gql_create_env_var)
        self.client.validate(query)

    def test_delete_env_var(self):
        query = gql(gql_delete_env_var)
        self.client.validate(query)

    def test_list_project_env_vars(self):
        query = gql(gql_list_project_env_vars)
        self.client.validate(query)

    def test_update_env_var(self):
        query = gql(gql_update_env_var)
        result = self.client.validate(query)
        expected = None
        assert result == expected
