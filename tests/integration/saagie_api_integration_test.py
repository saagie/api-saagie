# pylint: disable=attribute-defined-outside-init
import json
import os
import shutil
import time
from datetime import datetime
from typing import List

import pytest
import urllib3

from saagieapi import SaagieApi
from saagieapi.pipelines.graph_pipeline import ConditionNode, GraphPipeline, JobNode


@pytest.fixture(autouse=True)
def my_fixture():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TestIntegrationProjectCreationAndDeletion:
    """Test Project creation and deletion"""

    def setup_class(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        url_saagie = os.environ["URL_TEST_SAAGIE"]
        id_platform = os.environ["ID_PLATFORM_TEST_SAAGIE"]
        user = os.environ["USER_TEST_SAAGIE"]
        password = os.environ["PWD_TEST_SAAGIE"]
        realm = os.environ["REALM_TEST_SAAGIE"]

        self.saagie_api = SaagieApi(
            url_saagie=url_saagie, id_platform=id_platform, user=user, password=password, realm=realm
        )

        self.group = os.environ["USER_GROUP_TEST_SAAGIE"]
        self.project_name = "Integration_test_Saagie_API " + str(datetime.timestamp(datetime.now()))

    @pytest.fixture
    def create_project(self):
        result = self.saagie_api.projects.create(
            name=self.project_name, group=self.group, role="Manager", description="For integration test"
        )

        project_id = result["createProject"]["id"]

        # Waiting for the project to be ready
        project_status = self.saagie_api.projects.get_info(project_id=project_id)["project"]["status"]
        waiting_time = 0

        # Safety: wait for 5min max for project initialisation
        project_creation_timeout = 400
        while project_status != "READY" and waiting_time <= project_creation_timeout:
            time.sleep(10)
            project_status = self.saagie_api.projects.get_info(project_id)["project"]["status"]
            waiting_time += 10
        if project_status != "READY":
            raise TimeoutError(
                f"Project creation is taking longer than usual, "
                f"aborting integration tests after {project_creation_timeout} seconds"
            )

        return project_id

    def test_delete_project(self, create_project):
        project_id = create_project

        result = self.saagie_api.projects.delete(project_id)

        assert result == {"deleteProject": True}


class TestIntegrationProject:
    def setup_class(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        url_saagie = os.environ["URL_TEST_SAAGIE"]
        id_platform = os.environ["ID_PLATFORM_TEST_SAAGIE"]
        user = os.environ["USER_TEST_SAAGIE"]
        password = os.environ["PWD_TEST_SAAGIE"]
        realm = os.environ["REALM_TEST_SAAGIE"]

        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.import_dir = os.path.join(self.dir_path, "resources", "import")
        self.output_dir = os.path.join(os.getcwd(), "output")
        self.output_dir_present = os.path.isdir(self.output_dir)

        self.saagie_api = SaagieApi(
            url_saagie=url_saagie, id_platform=id_platform, user=user, password=password, realm=realm
        )

        # Create a test project
        self.group = os.environ["USER_GROUP_TEST_SAAGIE"]
        self.project_name = "Integration_test_Saagie_API " + str(datetime.timestamp(datetime.now()))

        result = self.saagie_api.projects.create(
            name=self.project_name,
            group=self.group,
            role="Manager",
            description="For integration test",
            jobs_technologies_allowed={"saagie": ["python", "spark"]},
        )
        self.project_id = result["createProject"]["id"]

        # Waiting for the project to be ready
        project_status = self.saagie_api.projects.get_info(project_id=self.project_id)["project"]["status"]
        waiting_time = 0

        # Safety: wait for 5min max for project initialisation
        project_creation_timeout = 400
        while project_status != "READY" and waiting_time <= project_creation_timeout:
            time.sleep(10)
            project_status = self.saagie_api.projects.get_info(self.project_id)["project"]["status"]
            waiting_time += 10
        if project_status != "READY":
            raise TimeoutError(
                f"Project creation is taking longer than usual, "
                f"aborting integration tests after {project_creation_timeout} seconds"
            )

    ############################################################################
    ################################# PROJECTS #################################
    ############################################################################

    def test_get_project_id(self):
        expected_project_id = self.project_id
        output_project_id = self.saagie_api.projects.get_id(self.project_name)
        assert expected_project_id == output_project_id

    def test_get_project_technologies(self):
        jobs_technologies = self.saagie_api.projects.get_jobs_technologies(self.project_id)
        apps_technologies = self.saagie_api.projects.get_apps_technologies(self.project_id)
        assert isinstance(jobs_technologies["technologiesByCategory"], List)
        assert len(jobs_technologies["technologiesByCategory"]) == 2  # Only python for Extraction and Processing
        assert isinstance(apps_technologies["appTechnologies"], List)
        assert len(apps_technologies["appTechnologies"]) > 2  # All Apps from saagie official catalog

    def test_get_project_rights(self):
        rights = self.saagie_api.projects.get_rights(self.project_id)
        expected_right_all_project = {"name": self.group, "role": "ROLE_PROJECT_MANAGER", "isAllProjects": True}
        expected_right_project = {"name": self.group, "role": "ROLE_PROJECT_MANAGER", "isAllProjects": False}
        assert isinstance(rights["rights"], list)
        assert expected_right_all_project in rights["rights"] or expected_right_project in rights["rights"]

    def test_edit_project(self):
        project_input = {
            "description": "new description",
            "jobs_technologies_allowed": {"saagie": ["python", "spark", "r"]},
        }

        self.saagie_api.projects.edit(
            project_id=self.project_id,
            description=project_input["description"],
            jobs_technologies_allowed=project_input["jobs_technologies_allowed"],
            groups_and_roles=[{self.group: "Manager"}],
        )
        project_info = self.saagie_api.projects.get_info(self.project_id)
        technologies_allowed = self.saagie_api.projects.get_jobs_technologies(self.project_id)[
            "technologiesByCategory"
        ][0]

        to_validate = {
            "description": project_info["project"]["description"],
        }

        assert project_input["description"] == to_validate["description"]
        assert len(technologies_allowed["technologies"]) == 3  # R and Spark and Python for extraction

    def test_export_project(self):
        result = self.saagie_api.projects.export(self.project_id, os.path.join(self.output_dir, "projects"))
        to_validate = True
        assert result == to_validate

    ############################################################################
    ################################## JOBS ####################################
    ############################################################################

    @pytest.fixture
    def create_job(self):
        job_name = "python_test"
        file = os.path.join(self.dir_path, "resources", "hello_world.py")

        job = self.saagie_api.jobs.create(
            job_name=job_name,
            project_id=self.project_id,
            file=file,
            description="",
            category="Processing",
            technology="python",
            technology_catalog="Saagie",
            runtime_version="3.9",
            command_line="python {file} arg1 arg2",
            release_note="",
            extra_technology="",
            extra_technology_version="",
        )

        job_id = job["data"]["createJob"]["id"]

        return job_id

    @pytest.fixture
    def create_then_delete_job(self, create_job):
        job_id = create_job

        yield job_id

        self.saagie_api.jobs.delete(job_id)

    @pytest.fixture
    def delete_job(self):
        job_name = "python_test_upgrade"

        yield job_name

        job_id = self.saagie_api.jobs.get_id(job_name, self.project_name)

        self.saagie_api.jobs.delete(job_id)

    def test_create_python_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        project_jobs = self.saagie_api.jobs.list_for_project(project_id=self.project_id, instances_limit=0)

        project_jobs_ids = [job["id"] for job in project_jobs["jobs"]]

        assert job_id in project_jobs_ids

    def test_create_spark_job(self):
        job = self.saagie_api.jobs.create(
            job_name="job_name",
            project_id=self.project_id,
            file=os.path.join(self.dir_path, "resources", "hello_world.py"),
            description="",
            category="Extraction",
            technology_catalog="Saagie",
            technology="spark",
            runtime_version="2.4",
            command_line="spark-submit",
            release_note="release_note",
            extra_technology="Python",
            extra_technology_version="3.7",
        )
        job_id = job["data"]["createJob"]["id"]
        project_jobs = self.saagie_api.jobs.list_for_project(project_id=self.project_id, instances_limit=0)

        project_jobs_ids = [job["id"] for job in project_jobs["jobs"]]

        assert job_id in project_jobs_ids
        self.saagie_api.jobs.delete(job_id)

    def test_get_job_id(self, create_then_delete_job):
        job_id = create_then_delete_job

        job_name = "python_test"
        output_job_id = self.saagie_api.jobs.get_id(job_name, self.project_name)
        assert job_id == output_job_id

    def test_delete_job(self, create_job):
        job_id = create_job

        result = self.saagie_api.jobs.delete(job_id)

        assert result == {"deleteJob": True}

    def test_run_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        job_before_run = self.saagie_api.jobs.get_info(job_id=job_id)
        num_instances_before_run = job_before_run["job"]["countJobInstance"]

        self.saagie_api.jobs.run_with_callback(job_id=job_id, freq=10, timeout=-1)

        job_after_run = self.saagie_api.jobs.get_info(job_id=job_id)
        num_instances_after_run = job_after_run["job"]["countJobInstance"]

        assert num_instances_after_run == (num_instances_before_run + 1)

    def test_stop_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        runjob = self.saagie_api.jobs.run(job_id)
        job_instance_id = runjob["runJob"]["id"]

        self.saagie_api.jobs.stop(job_instance_id)

        job_instance_status = self.saagie_api.jobs.get_instance(job_instance_id)["jobInstance"]["status"]

        assert job_instance_status in ["KILLED", "KILLING"]

    def test_edit_job(self, create_then_delete_job):
        job_id = create_then_delete_job
        job_input = {
            "name": "new_name",
            "description": "new description",
            "is_scheduled": True,
            "cron_scheduling": "0 0 * * *",
            "schedule_timezone": "UTC",
            "alerting": None,
        }
        self.saagie_api.jobs.edit(
            job_id,
            job_name=job_input["name"],
            description=job_input["description"],
            is_scheduled=job_input["is_scheduled"],
            cron_scheduling=job_input["cron_scheduling"],
            schedule_timezone=job_input["schedule_timezone"],
        )
        job_info = self.saagie_api.jobs.get_info(job_id)
        to_validate = {
            "name": job_info["job"]["name"],
            "description": job_info["job"]["description"],
            "alerting": None,
            "is_scheduled": job_info["job"]["isScheduled"],
            "cron_scheduling": job_info["job"]["cronScheduling"],
            "schedule_timezone": job_info["job"]["scheduleTimezone"],
        }

        assert job_input == to_validate

    def test_export_job(self, create_then_delete_job):
        job_id = create_then_delete_job
        result = self.saagie_api.jobs.export(job_id, os.path.join(self.output_dir, "jobs"))
        to_validate = True
        assert result == to_validate

    def test_import_job_from_json(self):
        result = self.saagie_api.jobs.import_from_json(
            os.path.join(self.import_dir, "job", "job.json"),
            self.project_id,
            os.path.join(self.import_dir, "job", "hello_world.py"),
        )

        to_validate = True
        assert result == to_validate

    def test_import_job_spark_from_json(self):
        result = self.saagie_api.jobs.import_from_json(
            os.path.join(self.import_dir, "job_spark", "job.json"),
            self.project_id,
            os.path.join(self.import_dir, "job_spark", "Documents_empty.txt"),
        )

        to_validate = True
        assert result == to_validate

    def test_upgrade_job(self, create_then_delete_job):
        job_id = create_then_delete_job
        job_input = {"command_line": "python {file}", "release_note": "hello_world", "runtime_version": "3.9"}
        self.saagie_api.jobs.upgrade(
            job_id,
            use_previous_artifact=True,
            runtime_version=job_input["runtime_version"],
            command_line=job_input["command_line"],
            release_note=job_input["release_note"],
        )
        job_info = self.saagie_api.jobs.get_info(job_id)
        version = job_info["job"]["versions"][0]
        to_validate = {
            "command_line": version["commandLine"],
            "release_note": version["releaseNote"],
            "runtime_version": version["runtimeVersion"],
        }

        assert job_input == to_validate

    def test_create_or_upgrade_job(self, delete_job):
        job_name = delete_job
        file = os.path.join(self.dir_path, "resources", "hello_world.py")

        job_create = self.saagie_api.jobs.create_or_upgrade(
            job_name=job_name,
            project_id=self.project_id,
            file=file,
            description="",
            category="Processing",
            technology="python",
            technology_catalog="Saagie",
            runtime_version="3.9",
            command_line="python {file} arg1 arg2",
            release_note="",
            extra_technology="",
            extra_technology_version="",
        )

        job_id = job_create["data"]["createJob"]["id"]

        assert job_id is not None

        job_upgrade = self.saagie_api.jobs.create_or_upgrade(
            job_name=job_name,
            project_id=self.project_id,
            file=file,
            description="",
            category="Processing",
            technology="python",
            technology_catalog="Saagie",
            runtime_version="3.9",
            command_line="python {file} arg1 arg2",
            release_note="",
            extra_technology="",
            extra_technology_version="",
        )

        assert "addJobVersion" in job_upgrade
        assert "editJob" in job_upgrade

    ############################################################################
    ########################## ENVIRONMENT VARIABLES ###########################
    ############################################################################

    @pytest.fixture
    def create_global_env_var(self):
        name = "TEST_VIA_API" + str(datetime.timestamp(datetime.now()))
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        self.saagie_api.env_vars.create_global(name=name, value=value, description=description, is_password=False)

        return name

    @pytest.fixture
    def create_global_env_var_password(self):
        name = "TEST_VIA_API_PASSWORD" + str(datetime.timestamp(datetime.now()))
        value = "VALUE_TEST_VIA_API_PASSWORD"
        description = "DESCRIPTION_TEST_VIA_API_PASSWORD"

        self.saagie_api.env_vars.create_global(name=name, value=value, description=description, is_password=True)

        return name

    @pytest.fixture
    def create_then_delete_global_env_var(self, create_global_env_var):
        name = create_global_env_var

        yield name

        self.saagie_api.env_vars.delete_global(name)

    @pytest.fixture
    def create_then_delete_global_env_var_password(self, create_global_env_var_password):
        name = create_global_env_var_password

        yield name

        self.saagie_api.env_vars.delete_global(name)

    def test_create_global_env_var(self, create_then_delete_global_env_var):
        name = create_then_delete_global_env_var

        global_envs = self.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]

        global_envs_names = [env["name"] for env in global_envs]

        assert name in global_envs_names

    def test_delete_global_env_var(self, create_global_env_var):
        name = create_global_env_var

        result = self.saagie_api.env_vars.delete_global(name)

        assert result == {"deleteEnvironmentVariable": True}

    def test_update_global_env_var(self, create_then_delete_global_env_var):
        name = create_then_delete_global_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        self.saagie_api.env_vars.update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

    def test_update_global_env_var_password(self, create_then_delete_global_env_var_password):
        name = create_then_delete_global_env_var_password
        env_var_input = {"description": "new description", "isPassword": True}

        self.saagie_api.env_vars.update_global(
            name, description=env_var_input["description"], is_password=env_var_input["isPassword"]
        )

        env_var = [
            env_var
            for env_var in self.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {"description": env_var["description"], "isPassword": env_var["isPassword"]}

        assert env_var_input == to_validate

    def test_create_or_update_global_env_var(self):
        name = "TEST_VIA_API_CREATE_OR_UPDATE"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # First call to create the variable
        self.saagie_api.env_vars.create_or_update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        self.saagie_api.env_vars.create_or_update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        self.saagie_api.env_vars.delete_global(name)

    @pytest.fixture
    def create_project_env_var(self):
        name = "TEST_VIA_API"
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        self.saagie_api.env_vars.create_for_project(
            project_id=self.project_id, name=name, value=value, description=description, is_password=False
        )

        return name

    @pytest.fixture
    def create_then_delete_project_env_var(self, create_project_env_var):
        name = create_project_env_var

        yield name

        self.saagie_api.env_vars.delete_for_project(project_id=self.project_id, name=name)

    def test_create_project_env_var(self, create_then_delete_project_env_var):
        name = create_then_delete_project_env_var

        project_envs = self.saagie_api.env_vars.list_for_project(self.project_id)
        project_env_names = [env["name"] for env in project_envs["projectEnvironmentVariables"]]

        assert name in project_env_names

    def test_delete_project_env_var(self, create_project_env_var):
        name = create_project_env_var

        result = self.saagie_api.env_vars.delete_for_project(self.project_id, name)

        assert result == {"deleteEnvironmentVariable": True}

    def test_update_project_env_var(self, create_then_delete_project_env_var):
        name = create_then_delete_project_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        self.saagie_api.env_vars.update_for_project(
            self.project_id,
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie_api.env_vars.list_for_project(self.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]
        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

    def test_create_or_update_project_env_var(self):
        name = "TEST_VIA_API_CREATE_OR_UPDATE_PROJECT"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # First call to create the variable
        self.saagie_api.env_vars.create_or_update_for_project(
            project_id=self.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie_api.env_vars.list_for_project(self.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        self.saagie_api.env_vars.create_or_update_for_project(
            project_id=self.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie_api.env_vars.list_for_project(self.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        self.saagie_api.env_vars.delete_for_project(self.project_id, name=name)

    def test_export_variable(self, create_then_delete_project_env_var):
        name = create_then_delete_project_env_var
        export_dir = os.path.join(self.output_dir, "variables")
        result = self.saagie_api.env_vars.export(self.project_id, export_dir)
        env_var_folder_exist = os.path.isdir(os.path.join(export_dir, name))
        to_validate = True
        assert result == to_validate
        assert env_var_folder_exist is True

    @staticmethod
    def delete_test_global_env_var(self_obj):
        path = os.path.join(self_obj.import_dir, "env_var", "global_variable.json")
        # Delete variable if it already exist
        with open(path, encoding="utf-8") as json_file:
            var_name = json.load(json_file)["name"]
        var_list = [var["name"] for var in self_obj.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]]
        if var_name in var_list:
            self_obj.saagie_api.env_vars.delete_global(var_name)

    def test_import_global_env_var_from_json(self):
        path = os.path.join(self.import_dir, "env_var", "global_variable.json")
        self.delete_test_global_env_var(self)

        result = self.saagie_api.env_vars.import_from_json(
            path,
            self.project_id,
        )

        assert result

    def test_import_project_env_var_from_json(self):
        result = self.saagie_api.env_vars.import_from_json(
            os.path.join(self.import_dir, "env_var", "project_variable.json"),
            self.project_id,
        )

        assert result

    def test_import_wrong_env_var_from_json(self):
        result = self.saagie_api.env_vars.import_from_json(
            os.path.join(self.import_dir, "env_var", "wrong_variable.json"),
            self.project_id,
        )

        assert not result

    ############################################################################
    ################################## DOCKER ##################################
    ############################################################################

    @pytest.fixture
    def create_docker_credential(self):
        cred = self.saagie_api.docker_credentials.create(
            project_id=self.project_id, username="myuser", registry="test-registry", password="mypassword"
        )

        return cred["createDockerCredentials"]["id"]

    @pytest.fixture
    def create_then_delete_docker_credential(self, create_docker_credential):
        cred_id = create_docker_credential

        yield cred_id

        self.saagie_api.docker_credentials.delete(project_id=self.project_id, credential_id=cred_id)

    def test_create_docker_credential(self, create_then_delete_docker_credential):
        cred_id = create_then_delete_docker_credential

        cred = self.saagie_api.docker_credentials.get_info(self.project_id, cred_id)

        assert cred["dockerCredentials"]["username"] == "myuser"

    def test_delete_docker_credential(self, create_docker_credential):
        cred_id = create_docker_credential
        result = self.saagie_api.docker_credentials.delete(self.project_id, cred_id)
        all_creds = self.saagie_api.docker_credentials.list_for_project(self.project_id)

        assert result == {"deleteDockerCredentials": True}
        assert len(all_creds["allDockerCredentials"]) == 0

    def test_upgrade_docker_credential(self, create_then_delete_docker_credential):
        cred_id = create_then_delete_docker_credential

        result = self.saagie_api.docker_credentials.upgrade(
            self.project_id, cred_id, username="myuser", password="mypassword", registry="new-registry"
        )
        cred = self.saagie_api.docker_credentials.get_info(self.project_id, cred_id)
        assert result["updateDockerCredentials"]["id"] == cred_id
        assert cred["dockerCredentials"]["registry"] == "new-registry"

    def test_delete_docker_credential_for_username(self, create_docker_credential):
        _ = create_docker_credential
        result = self.saagie_api.docker_credentials.delete_for_username(
            self.project_id, username="myuser", registry="test-registry"
        )
        all_creds = self.saagie_api.docker_credentials.list_for_project(self.project_id)

        assert result == {"deleteDockerCredentials": True}
        assert len(all_creds["allDockerCredentials"]) == 0

    def test_upgrade_docker_credential_for_username(self, create_then_delete_docker_credential):
        cred_id = create_then_delete_docker_credential

        result = self.saagie_api.docker_credentials.upgrade_for_username(
            self.project_id, username="myuser", password="newpassword", registry="test-registry"
        )
        cred = self.saagie_api.docker_credentials.get_info_for_username(
            self.project_id, username="myuser", registry="test-registry"
        )
        assert result["updateDockerCredentials"]["id"] == cred_id
        assert cred["registry"] == "test-registry"

    ############################################################################
    ################################# PIPELINES ################################
    ############################################################################

    @pytest.fixture
    def create_graph_pipeline(self, create_job):
        job_id = create_job
        job_node1 = JobNode(job_id)
        job_node2 = JobNode(job_id)
        condition_node_1 = ConditionNode()
        job_node1.add_next_node(condition_node_1)
        condition_node_1.add_success_node(job_node2)
        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        name = "TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"
        cron_scheduling = "0 0 * * *"
        schedule_timezone = "Pacific/Fakaofo"
        result = self.saagie_api.pipelines.create_graph(
            project_id=self.project_id,
            graph_pipeline=graph_pipeline,
            name=name,
            description=description,
            cron_scheduling=cron_scheduling,
            schedule_timezone=schedule_timezone,
        )
        return result["createGraphPipeline"]["id"], job_id

    @pytest.fixture
    def create_then_delete_graph_pipeline(self, create_graph_pipeline):
        pipeline_id, job_id = create_graph_pipeline

        yield pipeline_id, job_id

        self.saagie_api.pipelines.delete(pipeline_id)
        self.saagie_api.jobs.delete(job_id)

    @pytest.fixture
    def delete_pipeline(self):
        pipeline_name = "pipeline_upgrade_test"

        yield pipeline_name

        pipeline_id = self.saagie_api.pipelines.get_id(pipeline_name, self.project_name)

        self.saagie_api.pipelines.delete(pipeline_id)

    def test_create_graph_pipeline(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        list_pipelines = self.saagie_api.pipelines.list_for_project(self.project_id)
        list_pipelines_id = [pipeline["id"] for pipeline in list_pipelines["project"]["pipelines"]]

        assert pipeline_id in list_pipelines_id

    def test_get_graph_pipeline_id(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        pipeline_name = "TEST_VIA_API"
        output_pipeline_id = self.saagie_api.pipelines.get_id(pipeline_name, self.project_name)
        assert pipeline_id == output_pipeline_id

    def test_run_graph_pipeline(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        output_pipeline_run_status = self.saagie_api.pipelines.run(pipeline_id)["runPipeline"]["status"]
        assert output_pipeline_run_status == "REQUESTED"

    def test_stop_graph_pipeline(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        output_pipeline_run_id = self.saagie_api.pipelines.run(pipeline_id)["runPipeline"]["id"]
        output_pipeline_stop_status = self.saagie_api.pipelines.stop(output_pipeline_run_id)["stopPipelineInstance"][
            "status"
        ]
        assert output_pipeline_stop_status == "KILLING"

    def test_delete_graph_pipeline(self, create_graph_pipeline):
        pipeline_id, job_id = create_graph_pipeline

        result = self.saagie_api.pipelines.delete(pipeline_id)
        self.saagie_api.jobs.delete(job_id)

        assert result == {"deletePipeline": True}

    def test_edit_graph_pipeline(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        pipeline_input = {
            "name": "test_edit_graph_pipeline",
            "description": "test_edit_graph_pipeline",
            "is_scheduled": True,
            "cron_scheduling": "0 0 * * *",
            "schedule_timezone": "UTC",
            "alerting": None,
        }
        self.saagie_api.pipelines.edit(
            pipeline_id,
            name=pipeline_input["name"],
            description=pipeline_input["description"],
            is_scheduled=pipeline_input["is_scheduled"],
            cron_scheduling=pipeline_input["cron_scheduling"],
            schedule_timezone=pipeline_input["schedule_timezone"],
        )
        pipeline_info = self.saagie_api.pipelines.get_info(pipeline_id)
        to_validate = {
            "name": pipeline_info["graphPipeline"]["name"],
            "description": pipeline_info["graphPipeline"]["description"],
            "alerting": None,
            "is_scheduled": pipeline_info["graphPipeline"]["isScheduled"],
            "cron_scheduling": pipeline_info["graphPipeline"]["cronScheduling"],
            "schedule_timezone": pipeline_info["graphPipeline"]["scheduleTimezone"],
        }

        assert pipeline_input == to_validate

    def test_export_pipeline(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        result = self.saagie_api.pipelines.export(pipeline_id, os.path.join(self.output_dir, "pipelines"))
        to_validate = True
        assert result == to_validate

    def test_import_pipeline_from_json_with_non_existing_jobs(self):
        result = self.saagie_api.pipelines.import_from_json(
            os.path.join(self.import_dir, "pipeline", "pipeline_non_existing_jobs.json"),
            self.project_id,
        )
        assert not result

    def test_import_pipeline_from_json_with_existing_jobs(self):
        job_name = "test_job_python"
        jobs = self.saagie_api.jobs.list_for_project_minimal(self.project_id)["jobs"]
        job = list(filter(lambda j: j["name"] == job_name, jobs))
        print(job)
        if len(job) == 0:
            self.saagie_api.jobs.import_from_json(
                os.path.join(self.import_dir, "job", "job.json"),
                self.project_id,
                os.path.join(self.import_dir, "job", "hello_world.py"),
            )

        result = self.saagie_api.pipelines.import_from_json(
            os.path.join(self.import_dir, "pipeline", "pipeline_existing_jobs.json"),
            self.project_id,
        )
        assert result

    def test_upgrade_graph_pipeline(self, create_then_delete_graph_pipeline):
        pipeline_id, job_id = create_then_delete_graph_pipeline

        job_node1 = JobNode(job_id)
        job_node2 = JobNode(job_id)
        job_node3 = JobNode(job_id)
        condition_node_1 = ConditionNode()
        job_node1.add_next_node(condition_node_1)
        job_node2.add_next_node(job_node3)
        condition_node_1.add_success_node(job_node2)
        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        release_note = "amazing new version !"

        pipeline_version_info = self.saagie_api.pipelines.upgrade(pipeline_id, graph_pipeline, release_note)

        job_nodes_id = [
            job_node["id"] for job_node in pipeline_version_info["addGraphPipelineVersion"]["graph"]["jobNodes"]
        ]

        result = (str(job_node3.uid) in job_nodes_id) and (
            pipeline_version_info["addGraphPipelineVersion"]["releaseNote"] == release_note
        )

        assert result

    def test_create_or_upgrade_pipeline(self, delete_pipeline, create_job):
        pipeline_name = delete_pipeline

        job_id = create_job
        job_node1 = JobNode(job_id)
        job_node2 = JobNode(job_id)
        condition_node_1 = ConditionNode()
        job_node1.add_next_node(condition_node_1)
        condition_node_1.add_success_node(job_node2)
        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        pipeline_create = self.saagie_api.pipelines.create_or_upgrade(
            name=pipeline_name,
            project_id=self.project_id,
            description="Description pipeline dev test",
            release_note="First release",
            emails=["example@test.com"],
            status_list=["FAILED"],
            is_scheduled=True,
            cron_scheduling="5 12 5 * *",
            schedule_timezone="Europe/Paris",
            graph_pipeline=graph_pipeline,
        )

        pipeline_id = pipeline_create["createGraphPipeline"]["id"]

        assert pipeline_id is not None

        pipeline_upgrade = self.saagie_api.pipelines.create_or_upgrade(
            name=pipeline_name,
            project_id=self.project_id,
            description="Description pipeline dev test",
            release_note="Second release",
            emails=["example@test.com"],
            status_list=["FAILED"],
            is_scheduled=True,
            cron_scheduling="5 12 5 * *",
            schedule_timezone="Europe/Paris",
            graph_pipeline=graph_pipeline,
        )

        assert "editPipeline" in pipeline_upgrade
        assert "addGraphPipelineVersion" in pipeline_upgrade

    ############################################################################
    ################################### APPS ###################################
    ############################################################################

    @pytest.fixture
    def create_app_from_scratch(self):
        app_name = "hello_world" + str(datetime.now())
        app = self.saagie_api.apps.create_from_scratch(
            project_id=self.project_id,
            app_name=app_name,
            image="httpd:2.4.54-alpine",
            description="Be happy",
            exposed_ports=[{"number": 80, "isRewriteUrl": True, "scope": "PROJECT"}],
        )
        return app["createApp"]["id"]

    @pytest.fixture
    def create_then_delete_app_from_scratch(self, create_app_from_scratch):
        app_id = create_app_from_scratch

        yield app_id

        self.saagie_api.apps.delete(app_id=app_id)

    def test_create_app_from_scratch(self, create_app_from_scratch):
        app_id = create_app_from_scratch
        app = self.saagie_api.apps.get_info(app_id)

        assert app["app"]["description"] == "Be happy"

    def export_app(self, create_then_delete_app_from_scratch):
        app_id = create_then_delete_app_from_scratch
        result = self.saagie_api.apps.export(app_id, os.path.join(self.output_dir, "apps"))
        to_validate = True
        assert result == to_validate

    def test_run_app(self, create_then_delete_app_from_scratch):
        app_id = create_then_delete_app_from_scratch

        app_info = self.saagie_api.apps.get_info(app_id=app_id)
        if app_info["app"]["history"]["currentStatus"].startswith("START"):
            self.saagie_api.apps.stop(app_id=app_id)
            tries = 60
            while app_info["app"]["history"]["currentStatus"] != "STOPPED" and tries > 0:
                app_info = self.saagie_api.apps.get_info(app_id=app_id)
                time.sleep(1)
                tries -= 1
            if tries == 0:
                raise Exception("App is not stopped")

        self.saagie_api.apps.run(app_id=app_id)

        app_after_run = self.saagie_api.apps.get_info(app_id=app_id)

        assert app_after_run["app"]["history"]["currentStatus"].startswith("START")

    def test_stop_app(self, create_then_delete_app_from_scratch):
        app_id = create_then_delete_app_from_scratch

        self.saagie_api.apps.stop(app_id=app_id)

        app_after_run = self.saagie_api.apps.get_info(app_id=app_id)

        assert app_after_run["app"]["history"]["currentStatus"].startswith("STOP")

    def test_edit_app(self, create_then_delete_app_from_scratch):
        app_id = create_then_delete_app_from_scratch

        app_input = {
            "name": "hi new name",
            "description": "new description",
            "alerting": {
                "emails": ["hello.world@gmail.com"],
                "statusList": ["FAILED", "STOPPED"],
            },
        }
        self.saagie_api.apps.edit(
            app_id,
            app_name=app_input["name"],
            description=app_input["description"],
            emails=app_input["alerting"]["emails"],
            status_list=app_input["alerting"]["statusList"],
        )

        app_info = self.saagie_api.apps.get_info(app_id)
        to_validate = {
            "name": app_info["app"]["name"],
            "description": app_info["app"]["description"],
            "alerting": app_info["app"]["alerting"],
        }
        del to_validate["alerting"]["loginEmails"]
        assert app_input == to_validate

    @pytest.fixture
    def create_app_from_catalog(self):
        app = self.saagie_api.apps.create_from_catalog(
            project_id=self.project_id,
            technology_name="Kibana",
            context="7.15.1",
        )

        return app["installApp"]["id"]

    @pytest.fixture
    def create_then_delete_app_from_catalog(self, create_app_from_catalog):
        app_id = create_app_from_catalog

        yield app_id

        self.saagie_api.apps.delete(app_id=app_id)

    def test_create_app_from_catalog(self, create_app_from_catalog):
        app_id = create_app_from_catalog

        app = self.saagie_api.apps.get_info(app_id)

        assert app["app"]["name"] == "Kibana"

    def test_delete_app_from_catalog(self, create_app_from_catalog):
        app_id = create_app_from_catalog
        result = self.saagie_api.apps.delete(app_id)

        assert result == {"deleteApp": {"id": app_id}}

    def teardown_class(self):
        # Delete output directory if it wasn't present before
        if not self.output_dir_present:
            shutil.rmtree(self.output_dir)

        # Delete global environment variable
        self.delete_test_global_env_var(self)

        # Delete Project
        self.saagie_api.projects.delete(self.project_id)
