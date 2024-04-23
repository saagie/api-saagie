# pylint: disable=attribute-defined-outside-init
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.env_vars.env_vars import EnvVars, check_scope
from saagieapi.env_vars.gql_queries import *

from .saagie_api_unit_test import create_gql_client

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(f"{dir_path}/..")


class TestEnvVars:
    def setup_method(self):
        self.client = create_gql_client()

    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()
        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def test_check_scope_global(self):
        check_scope(scope="GLOBAL", project_id=None, pipeline_id=None, app_id=None)

    def test_check_scope_error(self):
        with pytest.raises(ValueError):
            check_scope(scope="WRONG", project_id=None, pipeline_id=None, app_id=None)

    def test_check_scope_project_success(self):
        check_scope(scope="PROJECT", project_id="project_id", pipeline_id=None, app_id=None)

    def test_check_scope_project_error(self):
        with pytest.raises(ValueError):
            check_scope(scope="PROJECT", project_id=None, pipeline_id=None, app_id=None)

    def test_check_scope_pipeline_success(self):
        check_scope(scope="PIPELINE", project_id=None, pipeline_id="pipeline_id", app_id=None)

    def test_check_scope_pipeline_error(self):
        with pytest.raises(ValueError):
            check_scope(scope="PIPELINE", project_id=None, pipeline_id=None, app_id=None)

    def test_list_global_env_vars_gql(self):
        query = gql(GQL_LIST_GLOBAL_ENV_VARS)
        self.client.validate(query)

    def test_list_global_vars(self, saagie_api_mock):
        env_vars = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        scope_only = False
        pprint_result = True

        expected_query = gql(GQL_LIST_GLOBAL_ENV_VARS)

        env_vars.list(scope=scope, scope_only=scope_only, pprint_result=pprint_result)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, pprint_result=pprint_result)

    def test_list_project_env_vars_gql(self):
        query = gql(GQL_LIST_PROJECT_ENV_VARS)
        self.client.validate(query)

    def test_list_project_vars(self, saagie_api_mock):
        env_vars = EnvVars(saagie_api_mock)

        scope = "PROJECT"
        project_id = "MY_PROJECT_ID"
        scope_only = False
        pprint_result = True

        expected_query = gql(GQL_LIST_PROJECT_ENV_VARS)

        env_vars.list(scope=scope, project_id=project_id, scope_only=scope_only, pprint_result=pprint_result)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values={"projectId": project_id}, pprint_result=pprint_result
        )

    def test_list_pipeline_env_vars_gql(self):
        query = gql(GQL_LIST_PIPELINE_ENV_VARS)
        self.client.validate(query)

    def test_list_pipeline_vars(self, saagie_api_mock):
        env_vars = EnvVars(saagie_api_mock)

        scope = "PIPELINE"
        pipeline_id = "MY_PIPELINE_ID"
        scope_only = False
        pprint_result = True

        expected_query = gql(GQL_LIST_PIPELINE_ENV_VARS)

        env_vars.list(scope=scope, pipeline_id=pipeline_id, scope_only=scope_only, pprint_result=pprint_result)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values={"pipelineId": pipeline_id}, pprint_result=pprint_result
        )

    def test_list_app_env_vars_gql(self):
        query = gql(GQL_LIST_APP_ENV_VARS)
        self.client.validate(query)

    def test_list_app_vars(self, saagie_api_mock):
        env_vars = EnvVars(saagie_api_mock)

        scope = "APP"
        app_id = "MY_APP_ID"
        scope_only = False
        pprint_result = True

        expected_query = gql(GQL_LIST_APP_ENV_VARS)

        env_vars.list(scope=scope, app_id=app_id, scope_only=scope_only, pprint_result=pprint_result)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values={"appId": app_id}, pprint_result=pprint_result
        )

    def test_get_valid_env_var(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        name = "TEST_VARIABLE"

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}
            ]
            result = instance.get(scope, name)

        assert result["name"] == name

    def test_get_invalid_env_var(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        name = "INVALID_ENV_VAR"

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}
            ]
            result = instance.get(scope, name)

        assert result is None

    def test_create_env_var_gql(self):
        query = gql(GQL_CREATE_ENV_VAR)
        self.client.validate(query)

    def test_create_global_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        name = "env_var1"
        value = "value1"
        description = "description1"
        is_password = False
        scope = "GLOBAL"

        params = {
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": scope,
            },
        }

        expected_query = gql(GQL_CREATE_ENV_VAR)

        instance.create(scope=scope, name=name, value=value, description=description, is_password=is_password)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_project_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        name = "env_var1"
        value = "value1"
        description = "description1"
        is_password = False
        scope = "PROJECT"
        project_id = "MY_PROJECT_ID"

        params = {
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": scope,
            },
            "entityId": project_id,
        }

        expected_query = gql(GQL_CREATE_ENV_VAR)

        instance.create(
            scope=scope, name=name, value=value, description=description, project_id=project_id, is_password=is_password
        )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_project_env_vars_error(self, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        with pytest.raises(ValueError):
            instance.create(scope="PROJECT", name="env_var_proj_1", value="value1")

    def test_create_pipeline_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        name = "env_var1"
        value = "value1"
        description = "description1"
        is_password = False
        scope = "PIPELINE"
        pipeline_id = "MY_PIPELINE_ID"

        params = {
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": scope,
            },
            "entityId": pipeline_id,
        }

        expected_query = gql(GQL_CREATE_ENV_VAR)

        instance.create(
            scope=scope,
            name=name,
            value=value,
            description=description,
            pipeline_id=pipeline_id,
            is_password=is_password,
        )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_pipeline_env_vars_error(self, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        with pytest.raises(ValueError):
            instance.create(scope="PIPELINE", name="env_var1", value="value1")

    def test_create_app_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        name = "env_var1"
        value = "value1"
        description = "description1"
        is_password = False
        scope = "APP"
        app_id = "MY_APP_ID"

        params = {
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": scope,
            },
            "entityId": app_id,
        }

        expected_query = gql(GQL_CREATE_ENV_VAR)

        instance.create(
            scope=scope,
            name=name,
            value=value,
            description=description,
            app_id=app_id,
            is_password=is_password,
        )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_update_env_var_gql(self):
        query = gql(GQL_UPDATE_ENV_VAR)
        self.client.validate(query)

    def test_update_existing_global_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        name = "TEST_VARIABLE"
        value = "new value"

        params = {
            "envVar": {
                "id": "env_var_id",
                "name": name,
                "value": value,
                "description": "description1",
                "isPassword": False,
                "scope": scope,
            },
        }

        expected_query = gql(GQL_UPDATE_ENV_VAR)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "TEST_VARIABLE",
                    "value": "value1",
                    "description": "description1",
                    "scope": "GLOBAL",
                    "isPassword": False,
                }
            ]
            instance.update(scope=scope, name=name, value=value)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_update_existing_global_password_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        name = "TEST_VARIABLE"
        value = "new value"

        params = {
            "envVar": {
                "id": "env_var_id",
                "name": name,
                "value": value,
                "description": "description1",
                "isPassword": True,
                "scope": scope,
            },
        }

        expected_query = gql(GQL_UPDATE_ENV_VAR)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "TEST_VARIABLE",
                    "value": "value1",
                    "description": "description1",
                    "scope": "GLOBAL",
                    "isPassword": True,
                }
            ]
            instance.update(scope=scope, name=name, value=value)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_update_existing_project_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "PROJECT"
        name = "TEST_VARIABLE"
        new_name = "NEW_TEST_VARIABLE"
        value = "new value"
        desc = "new description"
        project_id = "MY_PROJECT_ID"

        params = {
            "envVar": {
                "id": "env_var_id",
                "name": new_name,
                "value": value,
                "description": desc,
                "isPassword": False,
                "scope": scope,
            },
            "entityId": project_id,
        }

        expected_query = gql(GQL_UPDATE_ENV_VAR)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "TEST_VARIABLE",
                    "value": "value1",
                    "description": "description1",
                    "scope": "PROJECT",
                    "isPassword": False,
                }
            ]
            instance.update(
                scope=scope, name=name, new_name=new_name, value=value, description=desc, project_id=project_id
            )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_update_existing_pipeline_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "PIPELINE"
        name = "TEST_VARIABLE"
        value = "new value"
        pipeline_id = "MY_PIPELINE_ID"

        params = {
            "envVar": {
                "id": "env_var_id",
                "name": name,
                "value": value,
                "description": "description1",
                "isPassword": True,
                "scope": scope,
            },
            "entityId": pipeline_id,
        }

        expected_query = gql(GQL_UPDATE_ENV_VAR)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "TEST_VARIABLE",
                    "value": "value1",
                    "description": "description1",
                    "scope": "PIPELINE",
                    "isPassword": False,
                }
            ]
            instance.update(scope=scope, name=name, value=value, is_password=True, pipeline_id=pipeline_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_update_existing_app_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "APP"
        name = "TEST_VARIABLE"
        value = "new value"
        app_id = "MY_APP_ID"

        params = {
            "envVar": {
                "id": "env_var_id",
                "name": name,
                "value": value,
                "description": "description1",
                "isPassword": True,
                "scope": scope,
            },
            "entityId": app_id,
        }

        expected_query = gql(GQL_UPDATE_ENV_VAR)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "TEST_VARIABLE",
                    "value": "value1",
                    "description": "description1",
                    "scope": "APP",
                    "isPassword": False,
                }
            ]
            instance.update(scope=scope, name=name, value=value, is_password=True, app_id=app_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_update_non_existing_variable(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "PROJECT"
        name = "NON_EXISTING_VARIABLE"
        project_id = "MY_PROJECT_ID"

        with patch.object(instance, "list") as list_env, pytest.raises(ValueError):
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "TEST_VARIABLE",
                    "value": "value1",
                    "description": "description1",
                    "scope": "PROJECT",
                    "isPassword": False,
                }
            ]
            instance.update(scope=scope, name=name, project_id=project_id)

    def test_create_or_update_env_var_create(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "PROJECT"
        name = "NEW_VARIABLE"
        value = "new value"
        description = None
        is_password = True
        project_id = "PROJECT_ID"

        create_res = {"saveEnvironmentVariable": {"id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"}}

        with patch.object(instance, "list") as list_env, patch.object(instance, "create") as create_env:
            list_env.return_value = [
                {"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}
            ]
            create_env.return_value = create_res
            res = instance.create_or_update(
                scope=scope,
                name=name,
                value=value,
                description=description,
                is_password=is_password,
                project_id=project_id,
            )

        assert res == create_res

    def test_create_or_update_env_var_update(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        name = "TEST_VARIABLE"
        value = "updated value"
        description = None
        is_password = False
        project_id = None
        pipeline_id = None

        update_res = {"saveEnvironmentVariable": {"id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"}}

        with patch.object(instance, "list") as list_env, patch.object(instance, "update") as update_env:
            list_env.return_value = [
                {"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}
            ]
            update_env.return_value = update_res
            res = instance.create_or_update(
                scope=scope,
                name=name,
                value=value,
                description=description,
                is_password=is_password,
                project_id=project_id,
                pipeline_id=pipeline_id,
            )

        assert res == update_res

    def test_delete_env_var_gql(self):
        query = gql(GQL_DELETE_ENV_VAR)
        self.client.validate(query)

    def test_delete_env_var(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        name = "env_var1"

        expected_query = gql(GQL_DELETE_ENV_VAR)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "env_var1",
                    "value": "value1",
                    "description": "description1",
                    "scope": "GLOBAL",
                }
            ]
            instance.delete(scope=scope, name=name)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values={"id": "env_var_id"})

    def test_delete_env_var_not_exists(self, saagie_api_mock):
        saagie_api_mock.env_vars.env_vars.check_scope.return_value = True
        instance = EnvVars(saagie_api_mock)

        scope = "GLOBAL"
        name = "NON_EXISTING_VARIABLE"

        with patch.object(instance, "list") as list_env, pytest.raises(ValueError):
            list_env.return_value = [
                {
                    "id": "env_var_id",
                    "name": "env_var1",
                    "value": "value1",
                    "description": "description1",
                    "scope": "GLOBAL",
                }
            ]
            instance.delete(scope=scope, name=name)

    def test_create_pipeline_env_vars_gql(self):
        query = gql(GQL_CREATE_PIPELINE_ENV_VAR)
        self.client.validate(query)

    def test_bulk_create(self, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        mock_env_vars = {
            "replaceEnvironmentVariablesByRawForScope": [
                {"id": "env_var_id", "name": "BULK1", "value": "HELLO", "scope": "PIPELINE"},
                {"id": "env_var_id2", "name": "BULK2", "value": "WORLD", "scope": "PIPELINE"},
            ]
        }
        saagie_api_mock.client.execute.return_value = mock_env_vars

        env_vars = {"BULK1": "HELLO", "BULK2": "WORLD"}
        pipeline_id = "MY_PIPELINE_ID"

        result = instance.bulk_create_for_pipeline(pipeline_id, env_vars)

        # Assertions
        arg1 = saagie_api_mock.client.execute.call_args.kwargs["query"]
        assert arg1 == gql(GQL_CREATE_PIPELINE_ENV_VAR)
        assert "replaceEnvironmentVariablesByRawForScope" in result
        assert result["replaceEnvironmentVariablesByRawForScope"][0]["id"] == "env_var_id"
        assert result["replaceEnvironmentVariablesByRawForScope"][0]["name"] == "BULK1"

    @patch("logging.info")
    def test_export_project_without_var(
        self,
        logging_info_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = []
            result = instance.export(project_id, output_folder, error_folder, project_only)

        assert result is True
        logging_info_mock.assert_called_once_with(
            "✅ The project [%s] doesn't have any environment variable", project_id
        )

    @patch("logging.warning")
    def test_export_list_exception(
        self,
        logging_warning_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)

        with patch.object(instance, "list") as list_env:
            list_env.side_effect = Exception("Error getting environment variables")
            result = instance.export(project_id, output_folder, error_folder, project_only)

        assert not result
        logging_warning_mock.assert_called_once_with(
            "Cannot get the information of environment variable of the project [%s]", project_id
        )

    @patch("logging.info")
    def test_export_project(
        self,
        logging_info_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "PROJECT"}
            ]
            result = instance.export(project_id, output_folder, error_folder, project_only)

        # Assertions
        assert result is True
        logging_info_mock.assert_called_with(
            "✅ Environment variables of the project [%s] have been successfully exported", project_id
        )

    @patch("logging.warning")
    @patch("saagieapi.env_vars.env_vars.create_folder", side_effect=Exception("Exception raised"))
    @patch("saagieapi.env_vars.env_vars.write_error")
    def test_export_folder_exception(
        self,
        write_error_mock,
        create_folder_mock,
        logging_warning_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)

        with patch.object(instance, "list") as list_env:
            list_env.return_value = [
                {"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "PROJECT"}
            ]
            result = instance.export(project_id, output_folder, error_folder, project_only)

        assert not result
        create_folder_mock.assert_called()
        write_error_mock.assert_called()
        logging_warning_mock.assert_called_once_with(
            "❌ Environment variables of the project [%s] have not been successfully exported", project_id
        )

    @patch("logging.info")
    def test_import_from_json_success(self, logging_info_mock, saagie_api_mock):
        json_file = "/path/to/the/json/file.json"
        project_id = "MY_PROJECT_ID"
        instance = EnvVars(saagie_api_mock)
        instance.create = MagicMock(return_value={"saveEnvironmentVariable": True})

        # Patch any external dependencies
        with patch("saagieapi.env_vars.env_vars.Path.open"), patch(
            "saagieapi.env_vars.env_vars.json.load"
        ) as mock_load:
            # Configure mocks
            mock_load.return_value = {
                "scope": "GLOBAL",
                "name": "variable_name",
                "value": "variable_value",
                "description": "variable_description",
                "isPassword": False,
            }

            # Execute the function to be tested
            result = instance.import_from_json(json_file, project_id)

        # Assert the expected behavior
        assert result is True
        mock_load.assert_called()
        instance.create.assert_called_once_with(
            scope="GLOBAL",
            name="variable_name",
            value="variable_value",
            description="variable_description",
            is_password=False,
            project_id=project_id,
        )
        logging_info_mock.assert_called_with(
            "✅ Environment variables of the project [%s] have been successfully imported", "MY_PROJECT_ID"
        )

    @patch("saagieapi.env_vars.env_vars.handle_error", return_value=False)
    def test_import_from_json_exception_load_file(self, handle_error_mock, saagie_api_mock):
        # Prepare test data and environment
        json_file = "/path/to/nonexistent/file.json"
        project_id = "MY_PROJECT_ID"
        instance = EnvVars(saagie_api_mock)
        my_mock_open = MagicMock()
        my_mock_open.side_effect = FileNotFoundError("File not found")
        exception = "File not found"

        # Patch any external dependencies
        with patch("saagieapi.env_vars.env_vars.Path.open", my_mock_open, create=True) as mock_file:
            # Execute the function to be tested
            result = instance.import_from_json(json_file, project_id)

        # Assert the expected behavior
        assert result is False
        assert mock_file.call_count == 1
        # Assert how you handle the error within the function
        if os.name == "nt":
            json_file = json_file.replace("/", "\\")
            handle_error_mock.assert_called_once_with(
                f"{exception}\n Cannot open the JSON file {json_file}", project_id
            )
        else:
            handle_error_mock.assert_called_once_with(
                f"{exception}\n Cannot open the JSON file {json_file}", project_id
            )

    @patch("saagieapi.env_vars.env_vars.handle_error", return_value=False)
    def test_import_from_json_exception_save(self, handle_error_mock, saagie_api_mock):
        # Prepare test data and environment
        json_file = "/path/to/the/json/file.json"
        project_id = "MY_PROJECT_ID"
        instance = EnvVars(saagie_api_mock)
        instance.create = MagicMock(return_value={"saveEnvironmentVariable": None})

        # Patch any external dependencies
        with patch("saagieapi.env_vars.env_vars.Path.open"), patch(
            "saagieapi.env_vars.env_vars.json.load"
        ) as mock_load:
            # Configure mocks
            mock_load.return_value = {
                "scope": "GLOBAL",
                "name": "variable_name",
                "value": "variable_value",
                "description": "variable_description",
                "isPassword": False,
            }

            # Execute the function to be tested
            result = instance.import_from_json(json_file, project_id)

        # Assert the expected behavior
        assert result is False
        mock_load.assert_called()
        instance.create.assert_called_once_with(
            scope="GLOBAL",
            name="variable_name",
            value="variable_value",
            description="variable_description",
            is_password=False,
            project_id=project_id,
        )
        handle_error_mock.assert_called_once_with({"saveEnvironmentVariable": None}, project_id)

    @patch("saagieapi.env_vars.env_vars.handle_error", return_value=False)
    def test_import_from_json_exception_create(self, handle_error_mock, saagie_api_mock):
        # Prepare test data and environment
        json_file = "/path/to/the/json/file.json"
        project_id = "MY_PROJECT_ID"
        instance = EnvVars(saagie_api_mock)
        instance.create = MagicMock(side_effect=Exception("Error while creating the variable"))

        # Patch any external dependencies
        with patch("saagieapi.env_vars.env_vars.Path.open"), patch(
            "saagieapi.env_vars.env_vars.json.load"
        ) as mock_load:
            # Configure mocks
            mock_load.return_value = {
                "scope": "GLOBAL",
                "name": "variable_name",
                "value": "variable_value",
                "description": "variable_description",
                "isPassword": False,
            }

            # Execute the function to be tested
            result = instance.import_from_json(json_file, project_id)

        # Assert the expected behavior
        assert result is False
        mock_load.assert_called()
        instance.create.assert_called_once_with(
            scope="GLOBAL",
            name="variable_name",
            value="variable_value",
            description="variable_description",
            is_password=False,
            project_id=project_id,
        )
        arg1 = handle_error_mock.call_args[0][0]
        arg2 = handle_error_mock.call_args[0][1]
        assert isinstance(arg1, Exception)
        assert str(arg1) == "Error while creating the variable"
        assert arg2 == project_id
