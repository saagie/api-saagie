from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.apps.gql_queries import *
from saagieapi.apps.apps import Apps

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(dir_path + '/..')


class TestApps:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_apps_for_project(self):
        query = gql(gql_list_apps_for_project)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_app_info(self):
        query = gql(gql_get_app_info)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_app(self):
        query = gql(gql_create_app)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_edit_app(self):
        query = gql(gql_edit_app)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_check_exposed_ports(self):
        valid_exposed_ports = [
            {
                "port": "80",
                "basePathVariableName": "youpi",
                "isRewriteUrl": "false",
                "isAuthenticationRequired": "true"
            }
        ]

        invalid_exposed_ports = [
            {
                "ports": "80",
                "basePathVariableName": "youpi",
                "isRewriteUrl": "false",
                "isAuthenticationRequired": "true"
            }
        ]
        result_valid = Apps.check_exposed_ports(valid_exposed_ports)
        result_invalid = Apps.check_exposed_ports(invalid_exposed_ports)

        assert result_valid is True
        assert result_invalid is False
