# pylint: disable=attribute-defined-outside-init
from gql import gql

from saagieapi.jobs.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestJobs:
    def setup_method(self):
        self.client = create_gql_client()

    def test_create_job(self):
        self.client.validate(gql(GQL_CREATE_JOB))

    def test_upgrade_job(self):
        self.client.validate(gql(GQL_UPGRADE_JOB))

    def test_list_project_jobs(self):
        self.client.validate(gql(GQL_LIST_JOBS_FOR_PROJECT))

    def test_list_project_jobs_minimal(self):
        self.client.validate(gql(GQL_LIST_JOBS_FOR_PROJECT_MINIMAL))

    def test_gql_get_info_job(self):
        self.client.validate(gql(GQL_GET_JOB_INFO))

    def test_get_info_job_by_alias(self):
        self.client.validate(gql(GQL_GET_JOB_INFO_BY_ALIAS))

    def test_get_job_instance(self):
        self.client.validate(gql(GQL_GET_JOB_INSTANCE))

    def test_run_job(self):
        self.client.validate(gql(GQL_RUN_JOB))

    def test_stop_job(self):
        self.client.validate(gql(GQL_STOP_JOB_INSTANCE))

    def test_edit_job(self):
        self.client.validate(gql(GQL_EDIT_JOB))

    def test_delete_job(self):
        self.client.validate(gql(GQL_DELETE_JOB))

    def test_rollback_job(self):
        self.client.validate(gql(GQL_ROLLBACK_JOB_VERSION))

    def test_delete_instances(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCE))

    def test_delete_instances_by_selector(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCES_BY_SELECTOR))

    def test_delete_instances_by_date(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCES_BY_DATE))

    def test_delete_versions(self):
        self.client.validate(gql(GQL_DELETE_JOB_VERSION))

    def test_duplicate(self):
        self.client.validate(gql(GQL_DUPLICATE_JOB))

    def test_count_instances_by_status(self):
        self.client.validate(gql(GQL_COUNT_INSTANCES_BY_SELECTOR))

    def test_count_instances_by_date(self):
        self.client.validate(gql(GQL_COUNT_INSTANCES_BY_DATE))

    def test_move_job(self):
        self.client.validate(gql(GQL_MOVE_JOB))

    def test_generate_description_by_ai(self):
        self.client.validate(gql(GQL_GENERATE_JOB_DESCRIPTION))
