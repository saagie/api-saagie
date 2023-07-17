# pylint: disable=duplicate-code,redefined-outer-name
import json
import os
import shutil
import time
from datetime import datetime

import pytest
import urllib3

from saagieapi import SaagieApi
from saagieapi.pipelines.graph_pipeline import ConditionExpressionNode, ConditionStatusNode, GraphPipeline, JobNode


class Conf:
    pass


@pytest.fixture(autouse=True)
def my_fixture():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture(scope="package")
def create_global_project():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Conf.url_saagie = os.environ["URL_TEST_SAAGIE"]
    Conf.id_platform = os.environ["ID_PLATFORM_TEST_SAAGIE"]
    Conf.user = os.environ["USER_TEST_SAAGIE"]
    Conf.password = os.environ["PWD_TEST_SAAGIE"]
    Conf.realm = os.environ["REALM_TEST_SAAGIE"]

    Conf.dir_path = os.path.dirname(os.path.abspath(__file__))
    Conf.import_dir = os.path.join(Conf.dir_path, "resources", "import")
    Conf.output_dir = os.path.join(os.getcwd(), "output")
    Conf.output_dir_present = os.path.isdir(Conf.output_dir)

    Conf.saagie_api = SaagieApi(
        url_saagie=Conf.url_saagie,
        id_platform=Conf.id_platform,
        user=Conf.user,
        password=Conf.password,
        realm=Conf.realm,
    )

    # Create a test project
    Conf.group = os.environ["USER_GROUP_TEST_SAAGIE"]
    Conf.project_name = f"Integration_test_Saagie_API {str(datetime.timestamp(datetime.now()))}"

    result = Conf.saagie_api.projects.create(
        name=Conf.project_name,
        group=Conf.group,
        role="Manager",
        description="For integration test",
        jobs_technologies_allowed={"saagie": ["python", "spark"]},
    )
    Conf.project_id = result["createProject"]["id"]

    # Waiting for the project to be ready
    project_status = Conf.saagie_api.projects.get_info(project_id=Conf.project_id)["project"]["status"]
    waiting_time = 0

    # Safety: wait for 5min max for project initialisation
    project_creation_timeout = 400
    while project_status != "READY" and waiting_time <= project_creation_timeout:
        time.sleep(10)
        project_status = Conf.saagie_api.projects.get_info(Conf.project_id)["project"]["status"]
        waiting_time += 10
    if project_status != "READY":
        raise TimeoutError(
            f"Project creation is taking longer than usual, "
            f"aborting integration tests after {project_creation_timeout} seconds"
        )

    @staticmethod
    def delete_test_global_env_var(conf):
        path = os.path.join(conf.import_dir, "env_vars", "GLOBAL", "variable.json")
        # Delete variable if it already exist
        with open(path, encoding="utf-8") as json_file:
            var_name = json.load(json_file)["name"]
        var_list = [var["name"] for var in conf.saagie_api.env_vars.list_globals()["globalEnvironmentVariables"]]
        if var_name in var_list:
            conf.saagie_api.env_vars.delete_global(var_name)

    Conf.delete_test_global_env_var = delete_test_global_env_var

    yield Conf

    Conf.saagie_api.projects.delete(Conf.project_id)

    # Delete output directory if it wasn't present before
    if not Conf.output_dir_present:
        shutil.rmtree(Conf.output_dir)

    # Delete global environment variable
    delete_test_global_env_var(Conf)

    # Delete created repository
    try:
        id_repository_from_zip = Conf.saagie_api.repositories.get_id("repository from zip")
        id_repository_from_url = Conf.saagie_api.repositories.get_id("repository from url")
        Conf.saagie_api.repositories.delete(id_repository_from_zip)
        Conf.saagie_api.repositories.delete(id_repository_from_url)
    except NameError:
        print("Test repositories are already cleaned")

    # Delete created group, user
    try:
        Conf.saagie_api.groups.delete("test_api_group_to_delete")
        Conf.saagie_api.users.delete("test_user_api_to_delete")
    except Exception:
        print("Test group and user are already cleaned")


@pytest.fixture
@staticmethod
def create_job(create_global_project):
    conf = create_global_project
    job_name = "python_test"
    file = os.path.join(conf.dir_path, "resources", "hello_world.py")

    job = conf.saagie_api.jobs.create(
        job_name=job_name,
        project_id=conf.project_id,
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

    return job["data"]["createJob"]["id"]


@pytest.fixture
@staticmethod
def create_graph_pipeline(create_job, create_global_project):
    conf = create_global_project
    job_id = create_job

    job_node1 = JobNode(job_id)
    job_node2 = JobNode(job_id)
    job_node3 = JobNode(job_id)
    job_node4 = JobNode(job_id)

    condition_node_1 = ConditionStatusNode()
    condition_node_1.put_at_least_one_success()
    condition_node_1.add_success_node(job_node2)
    condition_node_1.add_failure_node(job_node3)

    job_node1.add_next_node(condition_node_1)

    condition_node_2 = ConditionExpressionNode()
    condition_node_2.set_expression("1 + 1 == 2")
    condition_node_2.add_success_node(job_node4)

    job_node2.add_next_node(condition_node_2)

    graph_pipeline = GraphPipeline()
    graph_pipeline.add_root_node(job_node1)

    name = "TEST_VIA_API"
    description = "DESCRIPTION_TEST_VIA_API"
    cron_scheduling = "0 0 * * *"
    schedule_timezone = "Pacific/Fakaofo"
    has_execution_variables_enabled = False
    result = conf.saagie_api.pipelines.create_graph(
        project_id=conf.project_id,
        graph_pipeline=graph_pipeline,
        name=name,
        description=description,
        cron_scheduling=cron_scheduling,
        schedule_timezone=schedule_timezone,
        has_execution_variables_enabled=has_execution_variables_enabled,
    )
    return result["createGraphPipeline"]["id"], job_id
