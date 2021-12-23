import time
import urllib3

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(dir_path + '/..')

import pytest
from saagieapi.projects import SaagieApi


class TestIntegrationProjectCreationAndDeletion():
    """Test Project creation and deletion
    """

    def setup_class(cls):
        # Disable urllib3 InsecureRequestsWarnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        url_saagie = os.environ['URL_TEST_SAAGIE']
        id_platform = os.environ['ID_PLATFORM_TEST_SAAGIE']
        user = os.environ['USER_TEST_SAAGIE']
        password = os.environ['PWD_TEST_SAAGIE']
        realm = os.environ['REALM_TEST_SAAGIE']

        cls.saagie = SaagieApi(url_saagie=url_saagie,
                               id_platform=id_platform,
                               user=user,
                               password=password,
                               realm=realm)

        cls.group = os.environ['USER_GROUP_TEST_SAAGIE']
        cls.project_name = 'Integration_test_Saagie_API'

    @pytest.fixture
    def create_project(self):
        # Disable urllib3 InsecureRequestsWarnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        result = self.saagie.create_project(name=self.project_name,
                                            group=self.group,
                                            role="Manager",
                                            description="For integration test")

        project_id = result['createProject']['id']

        return project_id

    @pytest.fixture
    def create_then_delete_project(self, create_project):
        project_id = create_project

        yield

        self.saagie.delete_project(project_id)

    def test_create_project(self, create_then_delete_project):
        projects = self.saagie.get_projects_info()['projects']
        projects_names = [project['name'] for project in projects]

        assert self.project_name in projects_names

    def test_delete_project(self, create_project):
        project_id = create_project

        result = self.saagie.delete_project(project_id)

        assert result == {'archiveProject': True}


class TestIntegrationProject:
    def setup_class(cls):
        # Disable urllib3 InsecureRequestsWarnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        url_saagie = os.environ['URL_TEST_SAAGIE']
        id_platform = os.environ['ID_PLATFORM_TEST_SAAGIE']
        user = os.environ['USER_TEST_SAAGIE']
        password = os.environ['PWD_TEST_SAAGIE']
        realm = os.environ['REALM_TEST_SAAGIE']

        cls.saagie = SaagieApi(url_saagie=url_saagie,
                               id_platform=id_platform,
                               user=user,
                               password=password,
                               realm=realm)

        # Create a test project
        cls.group = os.environ['USER_GROUP_TEST_SAAGIE']
        cls.project_name = 'Integration_test_Saagie_API'

        result = cls.saagie.create_project(name=cls.project_name,
                                           group=cls.group,
                                           role="Manager",
                                           description="For integration test")
        cls.project_id = result['createProject']['id']

        # Waiting for the project to be ready
        project_status = cls.saagie \
            .get_project_info(project_id=cls.project_id)['project']['status']
        waiting_time = 0

        # Safety: wait for 5min max for project initialisation
        while project_status != 'READY' and waiting_time <= 300:
            time.sleep(10)
            project_status = cls.saagie \
                .get_project_info(cls.project_id)['project']['status']
            waiting_time += 10

    @pytest.fixture
    def create_job(self):
        # Disable urllib3 InsecureRequestsWarnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        job_name = 'python_test'
        file = dir_path + '/hello_world.py'

        job = self.saagie.create_job(job_name=job_name,
                                     project_id=self.project_id,
                                     file=file,
                                     description='',
                                     category='Processing',
                                     technology='python',
                                     runtime_version='3.6',
                                     command_line='python {file} arg1 arg2',
                                     release_note='',
                                     extra_technology='',
                                     extra_technology_version='')

        print(job)

        job_id = job['data']['createJob']['id']

        print(job_id)

        return job_id

    @pytest.fixture
    def create_then_delete_job(self, create_job):
        job_id = create_job

        yield job_id

        self.saagie.delete_job(job_id)

    def test_create_python_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        project_jobs = self.saagie.get_project_jobs(project_id=self.project_id,
                                                    instances_limit=0)

        project_jobs_ids = [job['id'] for job in project_jobs['jobs']]

        assert job_id in project_jobs_ids

    def test_delete_job(self, create_job):
        job_id = create_job

        result = self.saagie.delete_job(job_id)

        assert result == {'archiveJob': True}

    def test_run_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        job_before_run = self.saagie.get_project_job(job_id=job_id)
        num_instances_before_run = job_before_run['job']['countJobInstance']

        self.saagie.run_job_callback(job_id=job_id,
                                     freq=10,
                                     timeout=-1)

        job_after_run = self.saagie.get_project_job(job_id=job_id)
        num_instances_after_run = job_after_run['job']['countJobInstance']

        assert num_instances_after_run == (num_instances_before_run + 1)

    def test_stop_job(self, create_then_delete_job):
        job_id = create_then_delete_job

        runjob = self.saagie.run_job(job_id)
        job_instance_id = runjob['runJob']['id']

        self.saagie.stop_job(job_instance_id)

        job_instance_status = self.saagie \
            .get_job_instance(job_instance_id)['jobInstance']['status']

        assert job_instance_status in ['KILLED', 'KILLING']

    @pytest.fixture
    def create_global_env_var(self):
        # Disable urllib3 InsecureRequestsWarnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        name = 'TEST_VIA_API'
        value = 'VALUE_TEST_VIA_API'
        description = 'DESCRIPTION_TEST_VIA_API'

        self.saagie.create_global_env_var(name=name,
                                          value=value,
                                          description=description,
                                          is_password=False)

        return name

    @pytest.fixture
    def create_then_delete_global_env_var(self, create_global_env_var):
        name = create_global_env_var

        yield name

        self.saagie.delete_global_env_var(name)

    def test_create_global_env_var(self, create_then_delete_global_env_var):
        name = create_then_delete_global_env_var

        global_envs = self.saagie \
            .get_global_env_vars()['globalEnvironmentVariables']

        global_envs_names = [env['name'] for env in global_envs]

        assert name in global_envs_names

    def test_delete_global_env_var(self, create_global_env_var):
        name = create_global_env_var

        result = self.saagie.delete_global_env_var(name)

        assert result == {'deleteEnvironmentVariable': True}

    @pytest.fixture
    def create_project_env_var(self):
        # Disable urllib3 InsecureRequestsWarnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        name = 'TEST_VIA_API'
        value = 'VALUE_TEST_VIA_API'
        description = 'DESCRIPTION_TEST_VIA_API'

        self.saagie.create_project_env_var(project_id=self.project_id,
                                           name=name,
                                           value=value,
                                           description=description,
                                           is_password=False)

        return name

    @pytest.fixture
    def create_then_delete_project_env_var(self, create_project_env_var):
        name = create_project_env_var

        yield name

        self.saagie.delete_project_env_var(project_id=self.project_id,
                                           name=name)

    def test_create_project_env_var(self, create_then_delete_project_env_var):
        name = create_then_delete_project_env_var

        project_envs = self.saagie \
            .get_project_env_vars(self.project_id)
        project_env_names = [env['name'] for env
                             in project_envs['projectEnvironmentVariables']]

        assert name in project_env_names

    def test_delete_project_env_var(self, create_project_env_var):
        name = create_project_env_var

        result = self.saagie.delete_project_env_var(self.project_id, name)

        assert result == {'deleteEnvironmentVariable': True}

    def teardown_class(cls):
        # Delete Project
        cls.saagie.delete_project(cls.project_id)
