from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.env_vars.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(dir_path + '/..')


class TestEnvVars:

    def setup_method(self):
        self.client = create_gql_client()

    def test_get_global_env_vars(self):
        query = gql(gql_get_global_env_vars)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_global_env_var(self):
        name = 'test'
        value = 'test'
        description = ''
        is_password = False
        query = gql(gql_create_global_env_var.format(name, value, description,
                                                     str(is_password).lower()))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_env_var(self):
        env_var_id = '1234'
        query = gql(gql_delete_env_var.format(env_var_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_env_vars(self):
        project_id = "1234"
        query = gql(gql_get_project_env_vars.format(project_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_project_env_var(self):
        project_id = '1234'
        name = 'test'
        value = 'test'
        description = ''
        is_password = False
        query = gql(gql_create_project_env_var.format(
            project_id,
            name,
            value, description,
            str(is_password).lower()
        ))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_update_env_var(self):
        query = gql(gql_update_env_var)
        result = self.client.validate(query)
        expected = None
        assert result == expected
