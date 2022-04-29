from gql import gql

from saagieapi.apps.apps import Apps
from saagieapi.apps.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestApps:
    def setup_method(self):
        self.client = create_gql_client()

    def test_list_apps_for_project(self):
        query = gql(GQL_LIST_APPS_FOR_PROJECT)
        self.client.validate(query)

    def test_get_app_info(self):
        query = gql(GQL_GET_APP_INFO)
        self.client.validate(query)

    def test_create_app(self):
        query = gql(GQL_CREATE_APP)
        self.client.validate(query)

    def test_edit_app(self):
        query = gql(GQL_EDIT_APP)
        self.client.validate(query)

    def test_run_app(self):
        query = gql(GQL_RUN_APP)
        self.client.validate(query)

    def test_stop_app(self):
        query = gql(GQL_STOP_APP_INSTANCE)
        self.client.validate(query)

    def test_delete_app(self):
        query = gql(GQL_DELETE_APP)
        self.client.validate(query)

    @staticmethod
    def test_check_exposed_ports():
        valid_exposed_ports = [
            {
                "port": "80",
                "basePathVariableName": "my-variable",
                "isRewriteUrl": "false",
                "isAuthenticationRequired": "true",
            }
        ]

        invalid_exposed_ports = [
            {
                "ports": "80",
                "basePathVariableName": "my-variable",
                "isRewriteUrl": "false",
                "isAuthenticationRequired": "true",
            }
        ]
        result_valid = Apps.check_exposed_ports(valid_exposed_ports)
        result_invalid = Apps.check_exposed_ports(invalid_exposed_ports)

        assert result_valid is True
        assert result_invalid is False
