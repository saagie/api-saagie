from gql import gql
from .saagie_api_unit_test import create_gql_client
from saagieapi.jobs.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(dir_path + '/..')


class TestJobs:

    def setup_method(self):
        self.client = create_gql_client()

    def test_create_job(self):
        query = gql(gql_create_job)
        self.client.validate(query)

    def test_upgrade_job(self):
        query = gql(gql_upgrade_job)
        self.client.validate(query)

    def test_list_project_jobs(self):
        query = gql(gql_list_jobs_for_project)
        self.client.validate(query)

    def test_list_project_jobs_minimal(self):
        query = gql(gql_list_jobs_for_project_minimal)
        self.client.validate(query)

    def test_gql_get_info_job(self):
        query = gql(gql_get_job_info)
        self.client.validate(query)

    def test_get_job_instance(self):
        query = gql(gql_get_job_instance)
        self.client.validate(query)

    def test_run_job(self):
        query = gql(gql_run_job)
        self.client.validate(query)

    def test_stop_job(self):
        query = gql(gql_stop_job_instance)
        self.client.validate(query)

    def test_edit_job(self):
        query = gql(gql_edit_job)
        self.client.validate(query)

    def test_delete_job(self):
        query = gql(gql_delete_job)
        self.client.validate(query)
