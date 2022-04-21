from gql import gql
from .saagie_api_unit_test import create_gql_client
from saagieapi.env_vars.gql_queries import *


class TestEnvVars:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_global_env_vars(self):
        query = gql(gql_list_global_env_vars)
        self.client.validate(query)

    def test_create_global_env_var(self):
        name = 'test'
        value = 'test'
        description = ''
        is_password = False
        query = gql(gql_create_global_env_var.format(name, value, description,
                                                     str(is_password).lower()))
        self.client.validate(query)

    def test_delete_env_var(self):
        env_var_id = '1234'
        query = gql(gql_delete_env_var.format(env_var_id))
        self.client.validate(query)

    def test_list_project_env_vars(self):
        project_id = "1234"
        query = gql(gql_list_project_env_vars.format(project_id))
        self.client.validate(query)

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
        self.client.validate(query)

    def test_update_env_var(self):
        query = gql(gql_update_env_var)
        self.client.validate(query)
