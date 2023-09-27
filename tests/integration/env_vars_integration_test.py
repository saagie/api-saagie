# pylint: disable=attribute-defined-outside-init
import os
from datetime import datetime

import pytest


class TestIntegrationEnvVars:
    @pytest.fixture
    @staticmethod
    def create_global_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API" + str(datetime.timestamp(datetime.now())).replace(".", "_")
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        conf.saagie_api.env_vars.create(
            scope="GLOBAL", name=name, value=value, description=description, is_password=False
        )

        return name

    @pytest.fixture
    @staticmethod
    def create_global_env_var_password(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API_PASSWORD" + str(datetime.timestamp(datetime.now())).replace(".", "_")
        value = "VALUE_TEST_VIA_API_PASSWORD"
        description = "DESCRIPTION_TEST_VIA_API_PASSWORD"

        conf.saagie_api.env_vars.create(
            scope="GLOBAL", name=name, value=value, description=description, is_password=True
        )

        return name

    @pytest.fixture
    @staticmethod
    def create_then_delete_global_env_var(create_global_env_var, create_global_project):
        conf = create_global_project
        name = create_global_env_var

        yield name

        conf.saagie_api.env_vars.delete(scope="GLOBAL", name=name)

    @pytest.fixture
    @staticmethod
    def create_then_delete_global_env_var_password(create_global_env_var_password, create_global_project):
        conf = create_global_project
        name = create_global_env_var_password

        yield name

        conf.saagie_api.env_vars.delete(scope="GLOBAL", name=name)

    @staticmethod
    def test_create_global_env_var(create_then_delete_global_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_global_env_var

        global_envs = conf.saagie_api.env_vars.list(scope="GLOBAL")

        global_envs_names = [env["name"] for env in global_envs]

        assert name in global_envs_names

    @staticmethod
    def test_get_global_env_var(create_then_delete_global_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_global_env_var

        env = conf.saagie_api.env_vars.get(scope="GLOBAL", name=name)

        assert env["name"] == name

    @staticmethod
    def test_delete_global_env_var(create_global_env_var, create_global_project):
        conf = create_global_project
        name = create_global_env_var

        result = conf.saagie_api.env_vars.delete(scope="GLOBAL", name=name)

        assert result == {"deleteEnvironmentVariable": True}

    @staticmethod
    def test_update_global_env_var(create_then_delete_global_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_global_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        conf.saagie_api.env_vars.update(
            scope="GLOBAL",
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(env_var for env_var in conf.saagie_api.env_vars.list(scope="GLOBAL") if env_var["name"] == name)

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

        conf.saagie_api.env_vars.update(
            scope="GLOBAL", name=name, description=env_var_input["description"], is_password=env_var_input["isPassword"]
        )

        env_var = next(env_var for env_var in conf.saagie_api.env_vars.list(scope="GLOBAL") if env_var["name"] == name)

        to_validate = {"description": env_var["description"], "isPassword": env_var["isPassword"]}

        assert env_var_input == to_validate

    @staticmethod
    def test_create_or_update_global_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API_CREATE_OR_UPDATE"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # First call to create the variable
        conf.saagie_api.env_vars.create_or_update(
            scope="GLOBAL",
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(env_var for env_var in conf.saagie_api.env_vars.list(scope="GLOBAL") if env_var["name"] == name)

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update(
            scope="GLOBAL",
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(env_var for env_var in conf.saagie_api.env_vars.list(scope="GLOBAL") if env_var["name"] == name)

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete(scope="GLOBAL", name=name)

    @pytest.fixture
    @staticmethod
    def create_project_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API"
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        conf.saagie_api.env_vars.create(
            scope="PROJECT",
            project_id=conf.project_id,
            name=name,
            value=value,
            description=description,
            is_password=False,
        )

        return name

    @pytest.fixture
    @staticmethod
    def create_then_delete_project_env_var(create_project_env_var, create_global_project):
        conf = create_global_project
        name = create_project_env_var

        yield name

        conf.saagie_api.env_vars.delete(scope="PROJECT", project_id=conf.project_id, name=name)

    @staticmethod
    def test_create_project_env_var(create_then_delete_project_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_project_env_var

        project_envs = conf.saagie_api.env_vars.list(scope="PROJECT", project_id=conf.project_id)
        project_env_names = [env["name"] for env in project_envs]

        assert name in project_env_names

    @staticmethod
    def test_get_project_env_var(create_then_delete_project_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_project_env_var

        env = conf.saagie_api.env_vars.get(scope="PROJECT", name=name, project_id=conf.project_id)

        assert env["name"] == name

    @staticmethod
    def test_delete_project_env_var(create_project_env_var, create_global_project):
        conf = create_global_project
        name = create_project_env_var

        result = conf.saagie_api.env_vars.delete(scope="PROJECT", project_id=conf.project_id, name=name)

        assert result == {"deleteEnvironmentVariable": True}

    @staticmethod
    def test_update_project_env_var(create_then_delete_project_env_var, create_global_project):
        conf = create_global_project
        name = create_then_delete_project_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        conf.saagie_api.env_vars.update(
            scope="PROJECT",
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PROJECT", project_id=conf.project_id)
            if env_var["name"] == name
        )
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
            conf.saagie_api.env_vars.update(
                scope="PROJECT",
                project_id=conf.project_id,
                name=name,
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
        conf.saagie_api.env_vars.create_or_update(
            scope="PROJECT",
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PROJECT", project_id=conf.project_id)
            if env_var["name"] == name
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update(
            scope="PROJECT",
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PROJECT", project_id=conf.project_id)
            if env_var["name"] == name
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete(scope="PROJECT", project_id=conf.project_id, name=name)

    @staticmethod
    def test_create_or_update_project_env_var_with_existing_global_env_var(create_global_project):
        conf = create_global_project
        name = "TEST_VIA_API_CREATE_OR_UPDATE_PROJECT"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # Create a global env with the same name
        conf.saagie_api.env_vars.create(
            scope="GLOBAL",
            name=name,
            value=env_var_input["value"],
            is_password=env_var_input["isPassword"],
            description=env_var_input["description"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PROJECT", project_id=conf.project_id)
            if env_var["name"] == name
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # call to overwrite the variable in the project
        conf.saagie_api.env_vars.create_or_update(
            scope="PROJECT",
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PROJECT", project_id=conf.project_id)
            if env_var["name"] == name and env_var["scope"] == "PROJECT"
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update(
            scope="PROJECT",
            project_id=conf.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PROJECT", project_id=conf.project_id)
            if env_var["name"] == name and env_var["scope"] == "PROJECT"
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete(scope="PROJECT", project_id=conf.project_id, name=name)
        conf.saagie_api.env_vars.delete(scope="GLOBAL", name=name)

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
        path = os.path.join(conf.import_dir, "env_vars", "GLOBAL", "variable.json")
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
            os.path.join(conf.import_dir, "project", "env_vars", "PROJECT", "variable.json"),
            conf.project_id,
        )

        assert result

    @staticmethod
    def test_import_wrong_env_var_from_json(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.env_vars.import_from_json(
            os.path.join(conf.import_dir, "env_vars", "WRONG", "variable.json"),
            conf.project_id,
        )

        assert not result

    @pytest.fixture
    @staticmethod
    def create_pipeline_env_var(create_global_project, create_graph_pipeline):
        conf = create_global_project
        pipeline_id, job_id = create_graph_pipeline
        name = "TEST_PIPELINE_VIA_API"
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        conf.saagie_api.env_vars.create(
            scope="PIPELINE",
            pipeline_id=pipeline_id,
            name=name,
            value=value,
            description=description,
            is_password=False,
        )

        yield pipeline_id, name

        conf.saagie_api.pipelines.delete(pipeline_id=pipeline_id)
        conf.saagie_api.jobs.delete(job_id=job_id)

    @pytest.fixture
    @staticmethod
    def create_then_delete_pipeline_env_var(create_pipeline_env_var, create_global_project):
        conf = create_global_project
        pipeline_id, name = create_pipeline_env_var

        yield pipeline_id, name

        conf.saagie_api.env_vars.delete(scope="PIPELINE", pipeline_id=pipeline_id, name=name)

    @staticmethod
    def test_create_pipeline_env_var(create_then_delete_pipeline_env_var, create_global_project):
        conf = create_global_project
        pipeline_id, name = create_then_delete_pipeline_env_var

        pipeline_envs = conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id, scope_only=True)

        assert name in [env["name"] for env in pipeline_envs]

    @staticmethod
    def test_get_pipeline_env_var(create_then_delete_pipeline_env_var, create_global_project):
        conf = create_global_project
        pipeline_id, name = create_then_delete_pipeline_env_var

        env = conf.saagie_api.env_vars.get(scope="PIPELINE", name=name, pipeline_id=pipeline_id, scope_only=True)

        assert env["name"] == name

    @staticmethod
    def test_delete_pipeline_env_var(create_pipeline_env_var, create_global_project):
        conf = create_global_project
        pipeline_id, name = create_pipeline_env_var

        result = conf.saagie_api.env_vars.delete(scope="PIPELINE", pipeline_id=pipeline_id, name=name)

        assert result == {"deleteEnvironmentVariable": True}

    @staticmethod
    def test_update_pipeline_env_var(create_then_delete_pipeline_env_var, create_global_project):
        conf = create_global_project
        pipeline_id, name = create_then_delete_pipeline_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        conf.saagie_api.env_vars.update(
            scope="PIPELINE",
            pipeline_id=pipeline_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id, scope_only=True)
            if env_var["name"] == name
        )
        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

    @staticmethod
    def test_update_pipeline_env_var_not_exist(
        create_then_delete_pipeline_env_var, create_global_project, create_then_delete_global_env_var
    ):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_pipeline_env_var
        name = create_then_delete_global_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        with pytest.raises(ValueError) as rte:
            conf.saagie_api.env_vars.update(
                scope="PIPELINE",
                pipeline_id=pipeline_id,
                name=name,
                value=env_var_input["value"],
                description=env_var_input["description"],
                is_password=env_var_input["isPassword"],
            )
        assert str(rte.value) == f"❌ Environment variable {name} does not exists"

    @staticmethod
    def test_create_or_update_pipeline_env_var(create_global_project, create_graph_pipeline):
        conf = create_global_project
        pipeline_id, job_id = create_graph_pipeline
        name = "TEST_VIA_API_CREATE_OR_UPDATE_PIPELINE"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # First call to create the variable
        conf.saagie_api.env_vars.create_or_update(
            scope="PIPELINE",
            pipeline_id=pipeline_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id)
            if env_var["name"] == name
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update(
            scope="PIPELINE",
            pipeline_id=pipeline_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id)
            if env_var["name"] == name
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete(scope="PIPELINE", pipeline_id=pipeline_id, name=name)
        conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

    @staticmethod
    def test_create_or_update_pipeline_env_var_with_existing_global_env_var(
        create_global_project, create_graph_pipeline
    ):
        conf = create_global_project
        pipeline_id, job_id = create_graph_pipeline
        name = "TEST_VIA_API_CREATE_OR_UPDATE_PIPELINE"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # Create a global env with the same name
        conf.saagie_api.env_vars.create(
            scope="GLOBAL",
            name=name,
            value=env_var_input["value"],
            is_password=env_var_input["isPassword"],
            description=env_var_input["description"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id)
            if env_var["name"] == name
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # call to overwrite the variable in the project
        conf.saagie_api.env_vars.create_or_update(
            scope="PIPELINE",
            pipeline_id=pipeline_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id)
            if env_var["name"] == name and env_var["scope"] == "PIPELINE"
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        conf.saagie_api.env_vars.create_or_update(
            scope="PIPELINE",
            pipeline_id=pipeline_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = next(
            env_var
            for env_var in conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id)
            if env_var["name"] == name and env_var["scope"] == "PIPELINE"
        )

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        conf.saagie_api.env_vars.delete(scope="PIPELINE", pipeline_id=pipeline_id, name=name)
        conf.saagie_api.env_vars.delete(scope="GLOBAL", name=name)
        conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

    @staticmethod
    def test_bulk_create_pipeline_env_var(create_global_project, create_pipeline_env_var):
        conf = create_global_project
        pipeline_id, name = create_pipeline_env_var

        env_vars = {"TEST_PIPELINE_BULK1": "TOTO", "TEST_PIPELINE_BULK2": "TATA"}

        conf.saagie_api.env_vars.bulk_create_for_pipeline(pipeline_id=pipeline_id, env_vars=env_vars)

        env_list = conf.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id)

        assert name not in env_list
