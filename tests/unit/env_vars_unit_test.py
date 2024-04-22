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

    def test_list_global_env_vars_gql(self):
        query = gql(GQL_LIST_GLOBAL_ENV_VARS)
        self.client.validate(query)

    def test_create_env_var_gql(self):
        query = gql(GQL_CREATE_ENV_VAR)
        self.client.validate(query)

    def test_update_env_var_gql(self):
        query = gql(GQL_UPDATE_ENV_VAR)
        self.client.validate(query)

    def test_delete_env_var_gql(self):
        query = gql(GQL_DELETE_ENV_VAR)
        self.client.validate(query)

    def test_list_project_env_vars_gql(self):
        query = gql(GQL_LIST_PROJECT_ENV_VARS)
        self.client.validate(query)

    def test_list_pipeline_env_vars_gql(self):
        query = gql(GQL_LIST_PIPELINE_ENV_VARS)
        self.client.validate(query)

    def test_create_pipeline_env_vars_gql(self):
        query = gql(GQL_CREATE_PIPELINE_ENV_VAR)
        self.client.validate(query)

    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()
        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    # Test of check_scope
    def test_check_scope_global(self):
        check_scope(scope="GLOBAL", project_id=None, pipeline_id=None)

    def test_check_scope_error(self):
        with pytest.raises(ValueError):
            check_scope(scope="WRONG", project_id=None, pipeline_id=None)

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

    # Test the `list` method
    def test_list_global_vars(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        env_vars = EnvVars(saagie_api_mock)

        # Set up the expected parameters
        scope = "GLOBAL"
        project_id = None
        pipeline_id = None
        scope_only = False
        pprint_result = True

        # Define the expected query
        expected_query = gql(GQL_LIST_GLOBAL_ENV_VARS)

        # Call the function under test
        env_vars.list(scope, project_id, pipeline_id, scope_only, pprint_result)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(query=expected_query, pprint_result=pprint_result)

    def test_list_project_vars(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        env_vars = EnvVars(saagie_api_mock)

        # Set up the expected parameters
        scope = "PROJECT"
        project_id = "MY_PROJECT_ID"
        pipeline_id = None
        scope_only = False
        pprint_result = True

        # Define the expected query
        expected_query = gql(GQL_LIST_PROJECT_ENV_VARS)

        # Call the function under test
        env_vars.list(scope, project_id, pipeline_id, scope_only, pprint_result)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values={"projectId": project_id}, pprint_result=pprint_result
        )

    def test_list_pipeline_vars(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        env_vars = EnvVars(saagie_api_mock)

        # Set up the expected parameters
        scope = "PIPELINE"
        project_id = "MY_PROJECT_ID"
        pipeline_id = "MY_PIPELINE_ID"
        scope_only = False
        pprint_result = True

        # Define the expected query
        expected_query = gql(GQL_LIST_PIPELINE_ENV_VARS)

        # Call the function under test
        env_vars.list(scope, project_id, pipeline_id, scope_only, pprint_result)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values={"pipelineId": pipeline_id}, pprint_result=pprint_result
        )

    # Test the `create` method
    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    def test_create_global_variable(self, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars

        name = "env_var1"
        value = "value1"
        description = "description1"
        is_password = False
        scope = "GLOBAL"

        result = instance.create(scope=scope, name=name, value=value, description=description, is_password=is_password)

        # Assertions
        check_scope_mock.assert_called_with(scope, None, None)
        arg1 = saagie_api_mock.client.execute.call_args.kwargs["query"]
        assert arg1 == gql(GQL_CREATE_ENV_VAR)
        assert "saveEnvironmentVariable" in result
        assert "id" in result["saveEnvironmentVariable"]
        assert isinstance(result["saveEnvironmentVariable"]["id"], str)

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    def test_create_project_variable(self, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars

        # Set up the expected parameters
        name = "env_var1"
        value = "value1"
        description = "description1"
        is_password = False
        scope = "PROJECT"
        project_id = "MY_PROJECT_ID"

        result = instance.create(
            scope=scope, name=name, value=value, description=description, project_id=project_id, is_password=is_password
        )

        # Assertions
        check_scope_mock.assert_called_with(scope, project_id, None)
        arg1 = saagie_api_mock.client.execute.call_args.kwargs["query"]
        assert arg1 == gql(GQL_CREATE_ENV_VAR)
        assert "saveEnvironmentVariable" in result
        assert "id" in result["saveEnvironmentVariable"]
        assert isinstance(result["saveEnvironmentVariable"]["id"], str)

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    def test_create_pipeline_variable(self, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars

        # Set up the expected parameters
        name = "env_var1"
        value = "value1"
        description = "description1"
        is_password = False
        scope = "PIPELINE"
        pipeline_id = "MY_PIPELINE_ID"
        project_id = "MY_PROJECT_ID"

        result = instance.create(
            scope=scope,
            name=name,
            value=value,
            description=description,
            project_id=project_id,
            pipeline_id=pipeline_id,
            is_password=is_password,
        )

        # Assertions
        check_scope_mock.assert_called_with(scope, project_id, pipeline_id)
        arg1 = saagie_api_mock.client.execute.call_args.kwargs["query"]
        assert arg1 == gql(GQL_CREATE_ENV_VAR)
        assert "saveEnvironmentVariable" in result
        assert "id" in result["saveEnvironmentVariable"]
        assert isinstance(result["saveEnvironmentVariable"]["id"], str)

    def test_create_pipeline_env_vars_error(self, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        with pytest.raises(ValueError):
            instance.create(scope="PIPELINE", name="env_var1", value="value1")

    def test_create_project_env_vars_error(self, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        with pytest.raises(ValueError):
            instance.create(scope="PROJECT", name="env_var_proj_1", value="value1")

    # Test the `delete` method
    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "env_var1",
                "value": "value1",
                "description": "description1",
                "scope": "GLOBAL",
            }
        ],
    )
    def test_delete_env_var(self, env_list_mock, check_scope_mock, saagie_api_mock):
        # Set up the expected parameters
        instance = EnvVars(saagie_api_mock)
        mock_env_vars = {"deleteEnvironmentVariable": True}
        saagie_api_mock.client.execute.return_value = mock_env_vars
        scope = "GLOBAL"
        name = "env_var1"

        # Test
        env_var_result = instance.delete(scope=scope, name=name)

        # Assertions
        check_scope_mock.assert_called_with(scope, None, None)
        env_list_mock.assert_called_with(scope, None, None, scope_only=True, pprint_result=False)
        arg1 = saagie_api_mock.client.execute.call_args.kwargs["query"]
        assert arg1 == gql(GQL_DELETE_ENV_VAR)
        assert "deleteEnvironmentVariable" in env_var_result

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "env_var1",
                "value": "value1",
                "description": "description1",
                "scope": "GLOBAL",
            }
        ],
    )
    def test_delete_env_var_not_exists(self, env_list_mock, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        scope = "GLOBAL"
        name = "NON_EXISTING_VARIABLE"

        # Assert that the result is as expected
        with pytest.raises(ValueError):
            instance.delete(scope=scope, name=name)
        check_scope_mock.assert_called_with(scope, None, None)
        env_list_mock.assert_called_with(scope, None, None, scope_only=True, pprint_result=False)
        saagie_api_mock.client.execute.assert_not_called()

    # Test the `update` method
    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "TEST_VARIABLE",
                "value": "value1",
                "description": "description1",
                "scope": "GLOBAL",
                "isPassword": False,
            }
        ],
    )
    def test_update_existing_global_variable(self, env_list_mock, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        # Parameters
        scope = "GLOBAL"
        name = "TEST_VARIABLE"
        value = "new value"

        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars

        result = instance.update(scope=scope, name=name, value=value)

        # Assert that the result is as expected
        check_scope_mock.assert_called_with(scope, None, None)
        env_list_mock.assert_called_with(scope, None, None, scope_only=True, pprint_result=False)
        assert "saveEnvironmentVariable" in result

        # Test the `update` method

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "TEST_VARIABLE",
                "value": "value1",
                "description": "description1",
                "scope": "GLOBAL",
                "isPassword": True,
            }
        ],
    )
    def test_update_existing_global_password_variable(self, env_list_mock, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        # Parameters
        scope = "GLOBAL"
        name = "TEST_VARIABLE"
        value = "new value"

        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars

        result = instance.update(scope=scope, name=name, value=value, is_password=True)

        # Assert that the result is as expected
        check_scope_mock.assert_called_with(scope, None, None)
        env_list_mock.assert_called_with(scope, None, None, scope_only=True, pprint_result=False)
        assert "saveEnvironmentVariable" in result

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "TEST_VARIABLE",
                "value": "value1",
                "description": "description1",
                "scope": "PROJECT",
                "isPassword": False,
            }
        ],
    )
    def test_update_existing_project_variable(self, env_list_mock, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        # Parameters
        scope = "PROJECT"
        name = "TEST_VARIABLE"
        value = "new value"
        project_id = "MY_PROJECT_ID"

        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars
        # Act
        result = instance.update(scope=scope, name=name, value=value, project_id=project_id)

        # Assert that the result is as expected
        check_scope_mock.assert_called_with(scope, project_id, None)
        env_list_mock.assert_called_with(scope, project_id, None, scope_only=True, pprint_result=False)
        assert "saveEnvironmentVariable" in result

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "TEST_VARIABLE",
                "value": "value1",
                "description": "description1",
                "scope": "PROJECT",
                "isPassword": False,
            }
        ],
    )
    def test_update_existing_project_variable_name(self, env_list_mock, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        # Parameters
        scope = "PROJECT"
        name = "TEST_VARIABLE"
        new_name = "NEW_TEST_VARIABLE"
        value = "new value"
        project_id = "MY_PROJECT_ID"
        new_description = "new description for tests purpose"

        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars
        # Act
        result = instance.update(
            scope=scope, name=name, value=value, project_id=project_id, new_name=new_name, description=new_description
        )

        # Assert that the result is as expected
        check_scope_mock.assert_called_with(scope, project_id, None)
        env_list_mock.assert_called_with(scope, project_id, None, scope_only=True, pprint_result=False)
        assert "saveEnvironmentVariable" in result

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "TEST_VARIABLE",
                "value": "value1",
                "description": "description1",
                "scope": "PIPELINE",
                "isPassword": False,
            }
        ],
    )
    def test_update_existing_pipeline_variable(self, env_list_mock, check_scope_mock, saagie_api_mock):
        instance = EnvVars(saagie_api_mock)
        # Parameters
        scope = "PIPELINE"
        name = "TEST_VARIABLE"
        value = "new value"
        project_id = "MY_PROJECT_ID"
        pipeline_id = "MY_PIPELINE_ID"
        # Mocks
        mock_env_vars = {"saveEnvironmentVariable": {"id": "env_var_id"}}
        saagie_api_mock.client.execute.return_value = mock_env_vars

        # Act
        result = instance.update(scope=scope, name=name, value=value, project_id=project_id, pipeline_id=pipeline_id)

        # Assert that the result is as expected
        check_scope_mock.assert_called_with(scope, project_id, pipeline_id)
        env_list_mock.assert_called_with(scope, project_id, pipeline_id, scope_only=True, pprint_result=False)
        assert "saveEnvironmentVariable" in result

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[
            {
                "id": "env_var_id",
                "name": "TEST_VARIABLE",
                "value": "value1",
                "description": "description1",
                "scope": "PROJECT",
                "isPassword": False,
            }
        ],
    )
    def test_update_non_existing_variable(self, env_list_mock, check_scope_mock, saagie_api_mock):
        # Arrange
        scope = "PROJECT"
        name = "NON_EXISTING_VARIABLE"
        project_id = "MY_PROJECT_ID"

        instance = EnvVars(saagie_api_mock)

        # Act and Assert
        with pytest.raises(ValueError):
            instance.update(scope=scope, name=name, project_id=project_id)
        check_scope_mock.assert_called_with(scope, project_id, None)
        env_list_mock.assert_called_with(scope, project_id, None, scope_only=True, pprint_result=False)

    # Test the `get` method
    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[{"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}],
    )
    def test_get_valid_env_var(self, env_list_mock, check_scope_mock, saagie_api_mock):
        scope = "GLOBAL"
        name = "TEST_VARIABLE"
        instance = EnvVars(saagie_api_mock)

        result = instance.get(scope, name)

        # Assert that the result is as expected
        assert isinstance(result, dict)
        assert result["name"] == name
        assert result["scope"] == scope
        check_scope_mock.assert_called_with(scope, None, None)
        env_list_mock.assert_called_with(scope, None, None, False, None)

    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[{"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}],
    )
    def test_get_invalid_env_var(self, env_list_mock, check_scope_mock, saagie_api_mock):
        # Define the input parameters for the `get` method
        scope = "GLOBAL"
        name = "INVALID_ENV_VAR"
        instance = EnvVars(saagie_api_mock)

        result = instance.get(scope, name)

        # Assert that the result is None since the environment variable does not exist
        assert result is None
        check_scope_mock.assert_called_with(scope, None, None)
        env_list_mock.assert_called_with(scope, None, None, False, None)

    # Test the `create_or_update` method
    @patch("saagieapi.env_vars.env_vars.EnvVars.update", return_value=True)
    @patch("saagieapi.env_vars.env_vars.EnvVars.create", return_value=True)
    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[{"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}],
    )
    def test_create_new_variable_with_create_or_update(
        self, env_list_mock, check_scope_mock, create_env_mock, update_env_mock, saagie_api_mock
    ):
        # Set up the parameters for the create_or_update method
        scope = "PROJECT"
        name = "NEW_VARIABLE"
        value = "new value"
        description = None
        is_password = True
        project_id = "PROJECT_ID"
        pipeline_id = None

        instance = EnvVars(saagie_api_mock)

        # Call the method being tested
        instance.create_or_update(
            scope=scope,
            name=name,
            value=value,
            description=description,
            is_password=is_password,
            project_id=project_id,
            pipeline_id=pipeline_id,
        )

        # Assertions
        env_list_mock.assert_called_with(scope, project_id, pipeline_id, scope_only=True, pprint_result=False)
        create_env_mock.assert_called_once_with(
            scope=scope, name=name, value=value, is_password=is_password, project_id=project_id
        )
        check_scope_mock.assert_called_with(scope, project_id, pipeline_id)
        update_env_mock.assert_not_called()

    @patch("saagieapi.env_vars.env_vars.EnvVars.update", return_value=True)
    @patch("saagieapi.env_vars.env_vars.EnvVars.create", return_value=True)
    @patch("saagieapi.env_vars.env_vars.check_scope", return_value=True)
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[{"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "GLOBAL"}],
    )
    def test_update_existing_variable_with_create_or_update(
        self, env_list_mock, check_scope_mock, create_env_mock, update_env_mock, saagie_api_mock
    ):
        # Test case to update an existing environment variable
        instance = EnvVars(saagie_api_mock)

        # Set up the parameters for the create_or_update method
        scope = "GLOBAL"
        name = "TEST_VARIABLE"  # Updating an existing variable
        value = "updated value"
        description = None
        is_password = False
        project_id = None
        pipeline_id = None

        # Call the method being tested
        instance.create_or_update(
            scope=scope,
            name=name,
            value=value,
            description=description,
            is_password=is_password,
            project_id=project_id,
            pipeline_id=pipeline_id,
        )

        # Assertions
        env_list_mock.assert_called_with(scope, project_id, pipeline_id, scope_only=True, pprint_result=False)
        update_env_mock.assert_called_once_with(
            scope=scope,
            name=name,
            value=value,
            description=description,
            new_name=None,
            is_password=is_password,
            project_id=project_id,
            pipeline_id=pipeline_id,
        )
        create_env_mock.assert_not_called()
        check_scope_mock.assert_called_with(scope, project_id, pipeline_id)

    # Test the `bulk_create_for_pipeline` method
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

    # Test the `export` method
    @patch("logging.info")
    @patch("saagieapi.utils.folder_functions.create_folder")
    @patch("saagieapi.utils.folder_functions.write_to_json_file")
    @patch("saagieapi.utils.folder_functions.write_error")
    @patch("saagieapi.env_vars.env_vars.EnvVars.list", return_value=[])
    def test_export_project_without_var(
        self,
        env_list_mock,
        write_error_mock,
        write_to_json_file_mock,
        create_folder_mock,
        logging_info_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)

        # Call the method being tested
        result = instance.export(project_id, output_folder, error_folder, project_only)

        # Assertions
        assert result is True
        env_list_mock.assert_called_once_with(scope="PROJECT", project_id=project_id, scope_only=True)
        create_folder_mock.assert_not_called()
        write_to_json_file_mock.assert_not_called()
        write_error_mock.assert_not_called()
        logging_info_mock.assert_called_once_with(
            "✅ The project [%s] doesn't have any environment variable", project_id
        )

    @patch("logging.warning")
    @patch("logging.error")
    @patch("saagieapi.utils.folder_functions.create_folder")
    @patch("saagieapi.utils.folder_functions.write_to_json_file")
    @patch("saagieapi.utils.folder_functions.write_error")
    @patch("saagieapi.env_vars.env_vars.EnvVars.list", side_effect=Exception("Error getting environment variables"))
    def test_export_list_exception(
        self,
        env_list_mock,
        write_error_mock,
        write_to_json_file_mock,
        create_folder_mock,
        logging_error_mock,
        logging_warning_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)

        # Call the method being tested
        result = instance.export(project_id, output_folder, error_folder, project_only)

        # Assertions
        assert not result
        env_list_mock.assert_called_once_with(scope="PROJECT", project_id=project_id, scope_only=True)
        create_folder_mock.assert_not_called()
        write_to_json_file_mock.assert_not_called()
        write_error_mock.assert_not_called()
        logging_warning_mock.assert_called_once_with(
            "Cannot get the information of environment variable of the project [%s]", project_id
        )
        arg1 = logging_error_mock.call_args[0][0]
        arg2 = logging_error_mock.call_args[0][1]
        assert arg1 == "Something went wrong %s"
        assert isinstance(arg2, Exception)
        assert str(arg2) == "Error getting environment variables"

    @patch("logging.info")
    @patch("logging.error")
    @patch("saagieapi.env_vars.env_vars.create_folder")
    @patch("saagieapi.env_vars.env_vars.write_to_json_file")
    @patch("saagieapi.env_vars.env_vars.write_error")
    @patch(
        "saagieapi.env_vars.env_vars.EnvVars.list",
        return_value=[{"id": "env_var_id", "name": "TEST_VARIABLE", "value": "value1", "scope": "PROJECT"}],
    )
    def test_export_project(
        self,
        env_list_mock,
        write_error_mock,
        write_to_json_file_mock,
        create_folder_mock,
        logging_error_mock,
        logging_info_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)

        result = instance.export(project_id, output_folder, error_folder, project_only)

        # Assertions
        assert result is True
        write_error_mock.assert_not_called()
        env_list_mock.assert_called_once_with(scope="PROJECT", project_id=project_id, scope_only=True)
        logging_info_mock.assert_called_with(
            "✅ Environment variables of the project [%s] have been successfully exported", project_id
        )
        logging_error_mock.assert_not_called()
        create_folder_mock.assert_called()
        write_to_json_file_mock.assert_called()

    @patch("logging.error")
    @patch("logging.warning")
    @patch("saagieapi.env_vars.env_vars.create_folder", side_effect=Exception("Exception raised"))
    @patch("saagieapi.env_vars.env_vars.write_to_json_file")
    @patch("saagieapi.env_vars.env_vars.write_error")
    def test_export_folder_exception(
        self,
        write_error_mock,
        write_to_json_file_mock,
        create_folder_mock,
        logging_warning_mock,
        logging_error_mock,
        saagie_api_mock,
    ):
        project_id = "50033e21-83c2-4431-a723-d54c2693b964"
        output_folder = "./output/env_vars/"
        error_folder = "./output/error/"
        project_only = True
        instance = EnvVars(saagie_api_mock)
        mock_existing_env_var = [
            {
                "id": "334c2e0e-e8ea-4639-911e-757bf36bc91b",
                "name": "TEST_PASSWORD",
                "scope": "PROJECT",
                "value": None,
                "description": "This is a password",
                "isPassword": True,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None,
            }
        ]

        instance.list = MagicMock(return_value=mock_existing_env_var)

        result = instance.export(project_id, output_folder, error_folder, project_only)

        # Assertions
        assert not result
        instance.list.assert_called_once_with(scope="PROJECT", project_id=project_id, scope_only=True)
        create_folder_mock.assert_called()
        write_to_json_file_mock.assert_not_called()
        write_error_mock.assert_called()
        logging_warning_mock.assert_called_once_with(
            "❌ Environment variables of the project [%s] have not been successfully exported", project_id
        )
        arg1 = logging_error_mock.call_args[0][0]
        arg2 = logging_error_mock.call_args[0][1]
        assert arg1 == "Something went wrong %s"
        assert isinstance(arg2, Exception)
        assert str(arg2) == "Exception raised"

    @patch("logging.info")
    def test_import_from_json_success(self, logging_info_mock, saagie_api_mock):
        # Prepare test data and environment
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
