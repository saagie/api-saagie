# pylint: disable=attribute-defined-outside-init
import pytest
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

    def test_create_app_catalog(self):
        query = gql(GQL_CREATE_APP_CATALOG)
        self.client.validate(query)

    def test_create_app_scratch(self):
        query = gql(GQL_CREATE_APP_SCRATCH)
        self.client.validate(query)

    def test_edit_app(self):
        query = gql(GQL_EDIT_APP)
        self.client.validate(query)

    def test_upgrade_app(self):
        query = gql(GQL_UPDATE_APP)
        self.client.validate(query)

    def test_run_app(self):
        query = gql(GQL_RUN_APP)
        self.client.validate(query)

    def test_stop_app(self):
        query = gql(GQL_STOP_APP)
        self.client.validate(query)

    def test_delete_app(self):
        query = gql(GQL_DELETE_APP)
        self.client.validate(query)

    def test_rollback_app(self):
        query = gql(GQL_ROLLBACK_APP_VERSION)
        self.client.validate(query)

    @staticmethod
    def test_check_exposed_ports():
        valid_exposed_ports = [
            {
                "number": 80,
                "basePathVariableName": "my-variable",
                "isRewriteUrl": False,
                "scope": "PROJECT",
            }
        ]

        invalid_exposed_ports = valid_exposed_ports + [
            {
                "ports": 80,
                "basePathVariableName": "my-variable",
                "isRewriteUrl": False,
                "scope": "PROJECT",
            }
        ]

        invalid_keys = valid_exposed_ports + [
            {
                "number": 81,
                "basePathVariableName": "my-variable2",
                "isRewriteUrl": True,
                "isAuthenticationRequired": True,
            }
        ]
        assert Apps.check_exposed_ports(valid_exposed_ports)
        assert not Apps.check_exposed_ports([])
        assert not Apps.check_exposed_ports(invalid_exposed_ports)
        assert not Apps.check_exposed_ports(invalid_keys)

    @staticmethod
    def test_check_app_alerting():
        params = {}
        emails = ["email1@saagie.com", "email2@saagie.com"]
        logins = ["login1", "login2"]
        status_list = ["STARTED", "FAILED"]

        # Test a valid and complete app alerting
        result = Apps.check_alerting(params, emails, logins, status_list)
        assert result["emails"] == emails
        assert result["logins"] == logins
        assert result["statusList"] == status_list

        # Test with a a missing logins parameter
        assert Apps.check_alerting(params, status_list=status_list, emails=emails)

        # Check that check_alerting keeps old values if no new ones are provided
        params["emails"] = emails
        assert Apps.check_alerting(params, status_list=status_list)

        # Test with a wrong status_list parameter
        with pytest.raises(RuntimeError) as rte:
            Apps.check_alerting(params, status_list=["FAILED", "RUNNING", "WRONGSTATUS"])
        assert str(rte.value).startswith("❌ The following status are not valid: ['RUNNING', 'WRONGSTATUS']")

        # Test without emails or logins
        with pytest.raises(RuntimeError) as rte:
            Apps.check_alerting({}, status_list=status_list)
        assert str(rte.value) == (
            "❌ You must provide a status list and either an email or a login to enable the alerting"
        )
