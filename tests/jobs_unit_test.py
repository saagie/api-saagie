from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.jobs.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(dir_path + '/..')


class TestJobs:

    def setup_method(self):
        self.client = create_gql_client()

    def test_create_job(self):
        extra_tech = ""
        query = gql(gql_create_job.format(extra_technology=extra_tech))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_upgrade_job(self):
        extra_tech = ""
        query = gql(gql_upgrade_job.format(extra_technology=extra_tech))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_jobs(self):
        project_id = "1234"
        instances_limit = " (limit: 3)"
        query = gql(gql_get_project_jobs.format(project_id, instances_limit))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_gql_get_info_job(self):
        job_id = "1234"
        query = gql(gql_get_info_job.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_job_instance(self):
        job_instance_id = "job_instance_1234"
        query = gql(gql_get_job_instance.format(job_instance_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_run_job(self):
        job_id = "job_1234"
        query = gql(gql_run_job.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_stop_job(self):
        job_id = "job_1234"
        query = gql(gql_stop_job_instance.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_edit_job(self):
        query = gql(gql_edit_job)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_job(self):
        job_id = "1234"
        query = gql(gql_delete_job.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected
