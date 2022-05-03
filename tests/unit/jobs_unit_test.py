# pylint: disable=attribute-defined-outside-init
import os
import sys

from gql import gql

from saagieapi.jobs.gql_queries import *

from .saagie_api_unit_test import create_gql_client

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(dir_path + "/..")


class TestJobs:
    def setup_method(self):
        self.client = create_gql_client()

    def test_create_job(self):
        query = gql(GQL_CREATE_JOB)
        self.client.validate(query)

    def test_upgrade_job(self):
        query = gql(GQL_UPGRADE_JOB)
        self.client.validate(query)

    def test_list_project_jobs(self):
        query = gql(GQL_LIST_JOBS_FOR_PROJECT)
        self.client.validate(query)

    def test_list_project_jobs_minimal(self):
        query = gql(GQL_LIST_JOBS_FOR_PROJECT_MINIMAL)
        self.client.validate(query)

    def test_gql_get_info_job(self):
        query = gql(GQL_GET_JOB_INFO)
        self.client.validate(query)

    def test_get_job_instance(self):
        query = gql(GQL_GET_JOB_INSTANCE)
        self.client.validate(query)

    def test_run_job(self):
        query = gql(GQL_RUN_JOB)
        self.client.validate(query)

    def test_stop_job(self):
        query = gql(GQL_STOP_JOB_INSTANCE)
        self.client.validate(query)

    def test_edit_job(self):
        query = gql(GQL_EDIT_JOB)
        self.client.validate(query)

    def test_delete_job(self):
        query = gql(GQL_DELETE_JOB)
        self.client.validate(query)
