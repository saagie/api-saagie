import os
import sys
import time

import pytest
import urllib3

from saagieapi import SaagieApi
from saagieapi.pipelines.graph_pipeline import ConditionNode, GraphPipeline, JobNode

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(dir_path + "/..")


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

        self.saagie = SaagieApi(
            url_saagie=url_saagie, id_platform=id_platform, user=user, password=password, realm=realm
        )

        self.group = os.environ["USER_GROUP_TEST_SAAGIE"]
        self.project_name = "Integration_test_Saagie_API"

    @pytest.fixture
    def create_project(self):
        result = self.saagie.projects.create(
            name=self.project_name, group=self.group, role="Manager", description="For integration test"
        )

        project_id = result["createProject"]["id"]

        return project_id

    @pytest.fixture
    def create_then_delete_project(self, create_project):
        project_id = create_project

        yield

        self.saagie.projects.delete(project_id)

    def test_create_project(self, create_then_delete_project):
        projects = self.saagie.projects.list()["projects"]
        projects_names = [project["name"] for project in projects]

        assert self.project_name in projects_names

    def test_delete_project(self, create_project):
        project_id = create_project

        result = self.saagie.projects.delete(project_id)

        assert result == {"deleteProject": True}


class TestIntegrationProject:
    def setup_class(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        url_saagie = os.environ["URL_TEST_SAAGIE"]
        id_platform = os.environ["ID_PLATFORM_TEST_SAAGIE"]
        user = os.environ["USER_TEST_SAAGIE"]
        password = os.environ["PWD_TEST_SAAGIE"]
        realm = os.environ["REALM_TEST_SAAGIE"]

        self.saagie = SaagieApi(
            url_saagie=url_saagie, id_platform=id_platform, user=user, password=password, realm=realm
        )

        # Create a test project
        self.group = os.environ["USER_GROUP_TEST_SAAGIE"]
        self.project_name = "Integration_test_Saagie_API"

        result = self.saagie.projects.create(
            name=self.project_name,
            group=self.group,
            role="Manager",
            description="For integration test",
            jobs_technologies_allowed={"saagie": ["python"]},
        )
        self.project_id = result["createProject"]["id"]

        # Waiting for the project to be ready
        project_status = self.saagie.projects.get_info(project_id=self.project_id)["project"]["status"]
        waiting_time = 0

        # Safety: wait for 5min max for project initialisation
        project_creation_timeout = 400
        while project_status != "READY" and waiting_time <= project_creation_timeout:
            time.sleep(10)
            project_status = self.saagie.projects.get_info(self.project_id)["project"]["status"]
            waiting_time += 10
        if project_status != "READY":
            raise TimeoutError(
                f"Project creation is taking longer than usual, "
                f"aborting integration tests after {project_creation_timeout} seconds"
            )

    def test_get_project_id(self):
        expected_project_id = self.project_id
        output_project_id = self.saagie.projects.get_id(self.project_name)
        assert expected_project_id == output_project_id

    def test_get_project_technologies(self):
        jobs_technologies = self.saagie.projects.get_jobs_technologies(self.project_id)
        apps_technologies = self.saagie.projects.get_apps_technologies(self.project_id)
        assert type(jobs_technologies["technologiesByCategory"]) is list
        assert len(jobs_technologies["technologiesByCategory"]) == 2  # Only python for Extraction and Processing
        assert type(apps_technologies["appTechnologies"]) is list
        assert len(apps_technologies["appTechnologies"]) > 2  # All Apps from saagie official catalog

    @pytest.fixture
    def create_job(self):
        job_name = "python_test"
        file = dir_path + "/resources/hello_world.py"

        job = self.saagie.jobs.create(
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

        self.saagie.jobs.delete(job_id)

    def test_create_python_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        project_jobs = self.saagie.jobs.list_for_project(project_id=self.project_id, instances_limit=0)

        project_jobs_ids = [job["id"] for job in project_jobs["jobs"]]

        assert job_id in project_jobs_ids

    def test_get_job_id(self, create_then_delete_job):
        job_id = create_then_delete_job
        job_name = "python_test"
        output_job_id = self.saagie.jobs.get_id(job_name, self.project_name)
        assert job_id == output_job_id

    def test_delete_job(self, create_job):
        job_id = create_job

        result = self.saagie.jobs.delete(job_id)

        assert result == {"deleteJob": True}

    def test_run_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        job_before_run = self.saagie.jobs.get_info(job_id=job_id)
        num_instances_before_run = job_before_run["job"]["countJobInstance"]

        self.saagie.jobs.run_with_callback(job_id=job_id, freq=10, timeout=-1)

        job_after_run = self.saagie.jobs.get_info(job_id=job_id)
        num_instances_after_run = job_after_run["job"]["countJobInstance"]

        assert num_instances_after_run == (num_instances_before_run + 1)

    def test_stop_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        runjob = self.saagie.jobs.run(job_id)
        job_instance_id = runjob["runJob"]["id"]

        self.saagie.jobs.stop(job_instance_id)

        job_instance_status = self.saagie.jobs.get_instance(job_instance_id)["jobInstance"]["status"]

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
        self.saagie.jobs.edit(
            job_id,
            job_name=job_input["name"],
            description=job_input["description"],
            is_scheduled=job_input["is_scheduled"],
            cron_scheduling=job_input["cron_scheduling"],
            schedule_timezone=job_input["schedule_timezone"],
        )
        job_info = self.saagie.jobs.get_info(job_id)
        to_validate = {
            "name": job_info["job"]["name"],
            "description": job_info["job"]["description"],
            "alerting": None,
            "is_scheduled": job_info["job"]["isScheduled"],
            "cron_scheduling": job_info["job"]["cronScheduling"],
            "schedule_timezone": job_info["job"]["scheduleTimezone"],
        }

        assert job_input == to_validate

    def test_upgrade_job(self, create_then_delete_job):
        job_id = create_then_delete_job
        job_input = {"command_line": "python {file}", "release_note": "hello_world", "runtime_version": "3.9"}
        self.saagie.jobs.upgrade(
            job_id,
            use_previous_artifact=True,
            runtime_version=job_input["runtime_version"],
            command_line=job_input["command_line"],
            release_note=job_input["release_note"],
        )
        job_info = self.saagie.jobs.get_info(job_id)
        version = job_info["job"]["versions"][0]
        to_validate = {
            "command_line": version["commandLine"],
            "release_note": version["releaseNote"],
            "runtime_version": version["runtimeVersion"],
        }

        assert job_input == to_validate

    @pytest.fixture
    def create_global_env_var(self):
        name = "TEST_VIA_API"
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        self.saagie.env_vars.create_global(name=name, value=value, description=description, is_password=False)

        return name

    @pytest.fixture
    def create_global_env_var_password(self):
        name = "TEST_VIA_API_PASSWORD"
        value = "VALUE_TEST_VIA_API_PASSWORD"
        description = "DESCRIPTION_TEST_VIA_API_PASSWORD"

        self.saagie.env_vars.create_global(name=name, value=value, description=description, is_password=True)

        return name

    @pytest.fixture
    def create_then_delete_global_env_var(self, create_global_env_var):
        name = create_global_env_var

        yield name

        self.saagie.env_vars.delete_global(name)

    @pytest.fixture
    def create_then_delete_global_env_var_password(self, create_global_env_var_password):
        name = create_global_env_var_password

        yield name

        self.saagie.env_vars.delete_global(name)

    def test_create_global_env_var(self, create_then_delete_global_env_var):
        name = create_then_delete_global_env_var

        global_envs = self.saagie.env_vars.list_globals()["globalEnvironmentVariables"]

        global_envs_names = [env["name"] for env in global_envs]

        assert name in global_envs_names

    def test_delete_global_env_var(self, create_global_env_var):
        name = create_global_env_var

        result = self.saagie.env_vars.delete_global(name)

        assert result == {"deleteEnvironmentVariable": True}

    def test_update_global_env_var(self, create_then_delete_global_env_var):
        name = create_then_delete_global_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        self.saagie.env_vars.update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie.env_vars.list_globals()["globalEnvironmentVariables"]
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

        self.saagie.env_vars.update_global(
            name, description=env_var_input["description"], is_password=env_var_input["isPassword"]
        )

        env_var = [
            env_var
            for env_var in self.saagie.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {"description": env_var["description"], "isPassword": env_var["isPassword"]}

        assert env_var_input == to_validate

    def test_create_or_update_global_env_var(self):
        name = "TEST_VIA_API_CREATE_OR_UPDATE"
        env_var_input = {"value": "TEST_VALUE", "description": "Test description", "isPassword": False}

        # First call to create the variable
        self.saagie.env_vars.create_or_update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        self.saagie.env_vars.create_or_update_global(
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie.env_vars.list_globals()["globalEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        self.saagie.env_vars.delete_global(name)

    @pytest.fixture
    def create_project_env_var(self):
        name = "TEST_VIA_API"
        value = "VALUE_TEST_VIA_API"
        description = "DESCRIPTION_TEST_VIA_API"

        self.saagie.env_vars.create_for_project(
            project_id=self.project_id, name=name, value=value, description=description, is_password=False
        )

        return name

    @pytest.fixture
    def create_then_delete_project_env_var(self, create_project_env_var):
        name = create_project_env_var

        yield name

        self.saagie.env_vars.delete_for_project(project_id=self.project_id, name=name)

    def test_create_project_env_var(self, create_then_delete_project_env_var):
        name = create_then_delete_project_env_var

        project_envs = self.saagie.env_vars.list_for_project(self.project_id)
        project_env_names = [env["name"] for env in project_envs["projectEnvironmentVariables"]]

        assert name in project_env_names

    def test_delete_project_env_var(self, create_project_env_var):
        name = create_project_env_var

        result = self.saagie.env_vars.delete_for_project(self.project_id, name)

        assert result == {"deleteEnvironmentVariable": True}

    def test_update_project_env_var(self, create_then_delete_project_env_var):
        name = create_then_delete_project_env_var
        env_var_input = {"value": "newvalue", "description": "new description", "isPassword": False}

        self.saagie.env_vars.update_for_project(
            self.project_id,
            name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie.env_vars.list_for_project(self.project_id)["projectEnvironmentVariables"]
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
        self.saagie.env_vars.create_or_update_for_project(
            project_id=self.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie.env_vars.list_for_project(self.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        # Second call to update the variable
        self.saagie.env_vars.create_or_update_for_project(
            project_id=self.project_id,
            name=name,
            value=env_var_input["value"],
            description=env_var_input["description"],
            is_password=env_var_input["isPassword"],
        )

        env_var = [
            env_var
            for env_var in self.saagie.env_vars.list_for_project(self.project_id)["projectEnvironmentVariables"]
            if env_var["name"] == name
        ][0]

        to_validate = {
            "value": env_var["value"],
            "description": env_var["description"],
            "isPassword": env_var["isPassword"],
        }

        assert env_var_input == to_validate

        self.saagie.env_vars.delete_for_project(self.project_id, name=name)

    @pytest.fixture
    def create_docker_credential(self):
        cred = self.saagie.docker_credentials.create(
            project_id=self.project_id, username="myuser", registry="test-registry", password="mypassword"
        )

        return cred["createDockerCredentials"]["id"]

    @pytest.fixture
    def create_then_delete_docker_credential(self, create_docker_credential):
        cred_id = create_docker_credential

        yield cred_id

        self.saagie.docker_credentials.delete(project_id=self.project_id, credential_id=cred_id)

    def test_create_docker_credential(self, create_then_delete_docker_credential):
        cred_id = create_then_delete_docker_credential

        cred = self.saagie.docker_credentials.get_info(self.project_id, cred_id)

        assert cred["dockerCredentials"]["username"] == "myuser"

    def test_delete_docker_credential(self, create_docker_credential):
        cred_id = create_docker_credential
        result = self.saagie.docker_credentials.delete(self.project_id, cred_id)
        all_creds = self.saagie.docker_credentials.list_for_project(self.project_id)

        assert result == {"deleteDockerCredentials": True}
        assert len(all_creds["allDockerCredentials"]) == 0

    def test_upgrade_docker_credential(self, create_then_delete_docker_credential):
        cred_id = create_then_delete_docker_credential

        result = self.saagie.docker_credentials.upgrade(
            self.project_id, cred_id, username="myuser", password="mypassword", registry="new-registry"
        )
        cred = self.saagie.docker_credentials.get_info(self.project_id, cred_id)
        assert result["updateDockerCredentials"]["id"] == cred_id
        assert cred["dockerCredentials"]["registry"] == "new-registry"

    def test_delete_docker_credential_for_username(self, create_docker_credential):
        cred_id = create_docker_credential
        result = self.saagie.docker_credentials.delete_for_username(
            self.project_id, username="myuser", registry="test-registry"
        )
        all_creds = self.saagie.docker_credentials.list_for_project(self.project_id)

        assert result == {"deleteDockerCredentials": True}
        assert len(all_creds["allDockerCredentials"]) == 0

    def test_upgrade_docker_credential_for_username(self, create_then_delete_docker_credential):
        cred_id = create_then_delete_docker_credential

        result = self.saagie.docker_credentials.upgrade_for_username(
            self.project_id, username="myuser", password="newpassword", registry="test-registry"
        )
        cred = self.saagie.docker_credentials.get_info_for_username(
            self.project_id, username="myuser", registry="test-registry"
        )
        assert result["updateDockerCredentials"]["id"] == cred_id
        assert cred["registry"] == "test-registry"

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
        result = self.saagie.pipelines.create_graph(
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

        self.saagie.pipelines.delete(pipeline_id)
        self.saagie.jobs.delete(job_id)

    def test_create_graph_pipeline(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        list_pipelines = self.saagie.pipelines.list_for_project(self.project_id)
        list_pipelines_id = [pipeline["id"] for pipeline in list_pipelines["project"]["pipelines"]]

        assert pipeline_id in list_pipelines_id

    def test_get_graph_pipeline_id(self, create_then_delete_graph_pipeline):
        pipeline_id, _ = create_then_delete_graph_pipeline
        pipeline_name = "TEST_VIA_API"
        output_pipeline_id = self.saagie.pipelines.get_id(pipeline_name, self.project_name)
        assert pipeline_id == output_pipeline_id

    def test_delete_graph_pipeline(self, create_graph_pipeline):
        pipeline_id, job_id = create_graph_pipeline

        result = self.saagie.pipelines.delete(pipeline_id)
        self.saagie.jobs.delete(job_id)

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
        self.saagie.pipelines.edit(
            pipeline_id,
            name=pipeline_input["name"],
            description=pipeline_input["description"],
            is_scheduled=pipeline_input["is_scheduled"],
            cron_scheduling=pipeline_input["cron_scheduling"],
            schedule_timezone=pipeline_input["schedule_timezone"],
        )
        pipeline_info = self.saagie.pipelines.get_info(pipeline_id)
        to_validate = {
            "name": pipeline_info["graphPipeline"]["name"],
            "description": pipeline_info["graphPipeline"]["description"],
            "alerting": None,
            "is_scheduled": pipeline_info["graphPipeline"]["isScheduled"],
            "cron_scheduling": pipeline_info["graphPipeline"]["cronScheduling"],
            "schedule_timezone": pipeline_info["graphPipeline"]["scheduleTimezone"],
        }

        assert pipeline_input == to_validate

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

        pipeline_version_info = self.saagie.pipelines.upgrade(pipeline_id, graph_pipeline, release_note)

        job_nodes_id = [
            job_node["id"] for job_node in pipeline_version_info["addGraphPipelineVersion"]["graph"]["jobNodes"]
        ]

        result = (str(job_node3.id) in job_nodes_id) and (
            pipeline_version_info["addGraphPipelineVersion"]["releaseNote"] == release_note
        )

        assert result

    @pytest.fixture
    def create_app_from_scratch(self):
        app = self.saagie.apps.create_from_scratch(
            project_id=self.project_id, app_name="hello_world", image="hello-world:latest", description="Be happy"
        )
        return app["createJob"]["id"]

    @pytest.fixture
    def create_then_delete_app_from_scratch(self, create_app_from_scratch):
        app_id = create_app_from_scratch

        yield app_id

        self.saagie.apps.delete(app_id=app_id)

    def test_create_app_from_scratch(self, create_app_from_scratch):
        app_id = create_app_from_scratch
        app = self.saagie.apps.get_info(app_id)

        assert app["labWebApp"]["name"] == "hello_world"

    # def test_run_app(self, create_then_delete_app_from_scratch):
    #     app_id = create_then_delete_app_from_scratch
    #
    #     app_before_run = self.saagie.apps.get_info(app_id=app_id)
    #     num_instances_before_run = app_before_run['job']['countJobInstance']
    #     self.saagie.apps.run(app_id=app_id)
    #
    #     app_after_run = self.saagie.jobs.get_info(app_id=app_id)
    #     num_instances_after_run = app_after_run['job']['countJobInstance']
    #
    #     assert num_instances_after_run == (num_instances_before_run + 1)
    #
    # def test_stop_app(self, create_then_delete_app_from_scratch):
    #     app_id = create_then_delete_app_from_scratch
    #
    #     run_app = self.saagie.apps.run(app_id=app_id)
    #     app_instance_id = run_app['runJob']['id']
    #
    #     self.saagie.jobs.stop(app_instance_id=app_instance_id)
    #
    #     app_instance_status = self.saagie \
    #         .jobs.get_instance(app_instance_id)['jobInstance']['status']
    #
    #     assert app_instance_status in ['KILLED', 'KILLING']

    # def test_edit_app(self, create_then_delete_app_from_scratch):
    #
    #     app_id = create_then_delete_app_from_scratch
    #     app_input = {
    #         'name': "hi new name",
    #         'description': "new description",
    #         "alerting": {
    #             "emails": ["hello.world@gmail.com"],
    #             "statusList": ["FAILED"]
    #         }
    #     }
    #     self.saagie.apps.edit(app_id, app_name=app_input["name"], description=app_input["description"],
    #                           emails=app_input["alerting"]["emails"], status_list=app_input["alerting"]["statusList"])
    #
    #     app_info = self.saagie.apps.get_info(app_id)
    #     to_validate = {'name': app_info["labWebApp"]["name"], 'description': app_info["labWebApp"]["description"],
    #                    'alerting': app_info["labWebApp"]["alerting"]}
    #
    #     assert app_input == to_validate

    @pytest.fixture
    def create_app_from_catalog(self):
        app = self.saagie.apps.create_from_catalog(
            project_id=self.project_id,
            app_name="hello_world2",
            technology="Kibana",
            context="7.15.1",
            description="Be happy ",
        )

        return app["createJob"]["id"]

    @pytest.fixture
    def create_then_delete_app_from_catalog(self, create_app_from_catalog):
        app_id = create_app_from_catalog

        yield app_id

        self.saagie.apps.delete(app_id=app_id)

    def test_create_app_from_catalog(self, create_app_from_catalog):
        app_id = create_app_from_catalog

        app = self.saagie.apps.get_info(app_id)

        assert app["labWebApp"]["name"] == "hello_world2"

    # def test_delete_app_from_catalog(self, create_app_from_catalog):
    #     app_id = create_app_from_catalog
    #     result = self.saagie.apps.delete(app_id)
    #
    #     assert result == {'deleteJob': True}

    def teardown_class(self):
        # Delete Project
        self.saagie.projects.delete(self.project_id)
