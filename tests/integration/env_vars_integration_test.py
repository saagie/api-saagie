# pylint: disable=attribute-defined-outside-init
import os
from datetime import datetime

import pytest


class TestIntegrationEnvVars:
    @pytest.fixture
    @staticmethod
    def create_global_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API" + str(datetime.timestamp(datetime.now()))
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        conf.saagie_api.env_vars.create_global(name=name, value=value, description=description, is_password=False)

        return name

    @pytest.fixture
    @staticmethod
    def create_global_env_var_password(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API_PASSWORD" + str(datetime.timestamp(datetime.now()))
        value = "VALUE_TEST_VIA_API_PASSWORD"
        description = "DESCRIPTION_TEST_VIA_API_PASSWORD"

        conf.saagie_api.env_vars.create_global(name=name, value=value, description=description, is_password=True)

        return name

    @pytest.fixture
    @staticmethod
    def create_then_delete_global_env_var(create_global_env_var, create_global_project):
        conf = create_global_project
        name = create_global_env_var

        yield name

        conf.saagie_api.env_vars.delete_global(name)

    @pytest.fixture
    @staticmethod
    def create_then_delete_global_env_var_password(create_global_env_var_password, create_global_project):
        conf = create_global_project
        name = create_global_env_var_password

        yield name

        conf.saagie_api.env_vars.delete_global(name)

    @staticmethod
    def test_create_global_env_var(create_then_delete_global_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_global_env_var

        global_envs = conf.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]

        global_envs_names = [env["name"] for env in global_envs]

        assert name in global_envs_names

    @staticmethod
    def test_delete_global_env_var(create_global_env_var, create_global_project):
        conf = create_global_project
        name = create_global_env_var

        result = conf.saagie_api.env_vars.delete_global(name)

        assert result == {"deleteEnvironmentVariable": True}

    @staticmethod
    def test_update_global_env_var(create_then_delete_global_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_global_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        conf.saagie_api.env_vars.update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

    @staticmethod
    def test_update_global_env_var_password(create_then_delete_global_env_var_password, create_global_project):
        conf = create_global_project
        name = create_then_delete_global_env_var_password
        env_var_input = {"description": "new description", "isPassword": True}

        conf.saagie_api.env_vars.update_global(
            name, description=env_var_input["description"], is_password=env_var_input["isPassword"]
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {"description": env_var["description"], "isPassword": env_var["isPassword"]}

        assert env_var_input == to_validate

    @staticmethod
    def test_create_or_update_global_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API_CREATE_OR_UPDATE"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # First call to create the variable
        conf.saagie_api.env_vars.create_or_update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete_global(name)

    @pytest.fixture
    @staticmethod
    def create_project_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API"
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        conf.saagie_api.env_vars.create_for_project(
            project_id=conf.project_id, name=name, value=value, description=description, is_password=False
        )

        return name

    @pytest.fixture
    @staticmethod
    def create_then_delete_project_env_var(create_project_env_var, create_global_project):
        conf = create_global_project
        name = create_project_env_var

        yield name

        conf.saagie_api.env_vars.delete_for_project(project_id=conf.project_id, name=name)

    @staticmethod
    def test_create_project_env_var(create_then_delete_project_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_project_env_var

        project_envs = conf.saagie_api.env_vars.list_for_project(conf.project_id)
        project_env_names = [env["name"] for env in project_envs["projectEnvironmentVariables"]]

        assert name in project_env_names

    @staticmethod
    def test_delete_project_env_var(create_project_env_var, create_global_project):
        conf = create_global_project
        name = create_project_env_var

        result = conf.saagie_api.env_vars.delete_for_project(conf.project_id, name)

        assert result == {"deleteEnvironmentVariable": True}

    @staticmethod
    def test_update_project_env_var(create_then_delete_project_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_project_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        conf.saagie_api.env_vars.update_for_project(
            conf.project_id,
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_for_project(conf.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]
        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

    @staticmethod
    def test_update_project_env_var_not_exist(create_then_delete_global_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_global_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        with pytest.raises(ValueError) as rte:
            conf.saagie_api.env_vars.update_for_project(
                conf.project_id,
                name,
                value=env_var_input["value"],
                description=env_var_input["description"],
                is_password=env_var_input["isPassword"],
            )
        assert str(rte.value) == f"❌ Environment variable {name} does not exists"

    @staticmethod
    def test_create_or_update_project_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API_CREATE_OR_UPDATE_PROJECT"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # First call to create the variable
        conf.saagie_api.env_vars.create_or_update_for_project(
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_for_project(conf.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update_for_project(
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_for_project(conf.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete_for_project(conf.project_id, name=name)

    @staticmethod
    def test_create_or_update_project_env_var_with_existing_global_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API_CREATE_OR_UPDATE_PROJECT"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # Create a global env with the same name
        conf.saagie_api.env_vars.create_global(
            name=name,
            value=env_var_input["value"],
            is_password=env_var_input["isPassword"],
            description=env_var_input["description"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_for_project(conf.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # call to overwrite the variable in the project
        conf.saagie_api.env_vars.create_or_update_for_project(
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_for_project(conf.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name and env_var["scope"] == "PROJECT"
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update_for_project(
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in conf.saagie_api.env_vars.list_for_project(conf.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name and env_var["scope"] == "PROJECT"
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete_for_project(conf.project_id, name=name)
        conf.saagie_api.env_vars.delete_global(name=name)

    @staticmethod
    def test_export_variable(create_then_delete_project_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_project_env_var
        export_dir = os.path.join(conf.output_dir, "variables")
        result = conf.saagie_api.env_vars.export(conf.project_id, export_dir)
        env_var_folder_exist = os.path.isdir(os.path.join(export_dir, name))
        to_validate = True
        assert result == to_validate
        assert env_var_folder_exist is True

    @staticmethod
    def test_import_global_env_var_from_json(create_global_project):
        conf = create_global_project
        path = os.path.join(conf.import_dir, "env_var", "global_variable.json")
        conf.delete_test_global_env_var(conf)

        result = conf.saagie_api.env_vars.import_from_json(
            path,
            conf.project_id,
        )

        assert result

    @staticmethod
    def test_import_project_env_var_from_json(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.env_vars.import_from_json(
            os.path.join(conf.import_dir, "env_var", "project_variable.json"),
            conf.project_id,
        )

        assert result

    @staticmethod
    def test_import_wrong_env_var_from_json(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.env_vars.import_from_json(
            os.path.join(conf.import_dir, "env_var", "wrong_variable.json"),
            conf.project_id,
        )

        assert not result
