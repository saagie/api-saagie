# pylint: disable=duplicate-code
import json
import os
import shutil
import time
from datetime import datetime

import pytest
import urllib3

from saagieapi import SaagieApi


class Conf:
    pass


@pytest.fixture(autouse=True)
def my_fixture():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture(scope="package")
def create_global_project():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url_saagie = os.environ["URL_TEST_SAAGIE"]
    id_platform = os.environ["ID_PLATFORM_TEST_SAAGIE"]
    user = os.environ["USER_TEST_SAAGIE"]
    password = os.environ["PWD_TEST_SAAGIE"]
    realm = os.environ["REALM_TEST_SAAGIE"]

    Conf.dir_path = os.path.dirname(os.path.abspath(__file__))
    Conf.import_dir = os.path.join(Conf.dir_path, "resources", "import")
    Conf.output_dir = os.path.join(os.getcwd(), "output")
    Conf.output_dir_present = os.path.isdir(Conf.output_dir)

    Conf.saagie_api = SaagieApi(
        url_saagie=url_saagie, id_platform=id_platform, user=user, password=password, realm=realm
    )

    # Create a test project
    Conf.group = os.environ["USER_GROUP_TEST_SAAGIE"]
    Conf.project_name = "Integration_test_Saagie_API " + str(datetime.timestamp(datetime.now()))

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
        path = os.path.join(conf.import_dir, "env_var", "global_variable.json")
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


@pytest.fixture
@staticmethod
def create_job():
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

    job_id = job["data"]["createJob"]["id"]

    return job_id
