# pylint: disable=attribute-defined-outside-init
import os
import sys

import pytest
from gql import gql

from saagieapi.env_vars.env_vars import check_scope
from saagieapi.env_vars.gql_queries import *

from .saagie_api_unit_test import create_gql_client

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(f"{dir_path}/..")


class TestEnvVars:
    def setup_method(self):
        self.client = create_gql_client()

    def test_list_global_env_vars(self):
        query = gql(GQL_LIST_GLOBAL_ENV_VARS)
        self.client.validate(query)

    def test_create_env_var(self):
        query = gql(GQL_CREATE_ENV_VAR)
        self.client.validate(query)

    def test_delete_env_var(self):
        query = gql(GQL_DELETE_ENV_VAR)
        self.client.validate(query)

    def test_list_project_env_vars(self):
        query = gql(GQL_LIST_PROJECT_ENV_VARS)
        self.client.validate(query)

    def test_update_env_var(self):
        query = gql(GQL_UPDATE_ENV_VAR)
        self.client.validate(query)

    def test_list_pipeline_env_vars(self):
        query = gql(GQL_LIST_PIPELINE_ENV_VARS)
        self.client.validate(query)

    def test_create_pipeline_env_vars(self):
        query = gql(GQL_CREATE_PIPELINE_ENV_VAR)
        self.client.validate(query)

    def test_check_scope_global(self):
        check_scope(scope="GLOBAL", project_id=None, pipeline_id=None)

    def test_check_scope_project_success(self):
        check_scope(scope="PROJECT", project_id="project_id", pipeline_id=None)

    def test_check_scope_project_error(self):
        with pytest.raises(ValueError):
            check_scope(scope="PROJECT", project_id=None, pipeline_id=None)

    def test_check_scope_pipeline_success(self):
        check_scope(scope="PIPELINE", project_id=None, pipeline_id="pipeline_id")

    def test_check_scope_pipeline_error(self):
        with pytest.raises(ValueError):
            check_scope(scope="PIPELINE", project_id=None, pipeline_id=None)
