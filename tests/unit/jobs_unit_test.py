# pylint: disable=attribute-defined-outside-init
from unittest.mock import Mock, patch

import pytest
from gql import gql

from saagieapi.jobs import Jobs
from saagieapi.jobs.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestJobs:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()
        saagie_api_mock.jobs.list_for_project_minimal.return_value = {
            "jobs": [
                {"name": "job1", "id": 1, "alias": "job1_alias"},
                {"name": "job2", "id": 2, "alias": "job2_alias"},
            ]
        }
        saagie_api_mock.projects.get_id.return_value = "project_id"
        saagie_api_mock.projects.get_jobs_technologies.return_value = {
            "technologiesByCategory": [{"jobCategory": "Processing", "technologies": [{"id": "python"}]}]
        }
        saagie_api_mock.get_runtimes.return_value = {"technology": {"contexts": [{"id": "3.10", "available": True}]}}
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        saagie_api_mock.__launch_request.return_value = {"data": {"createJob": {"job": {"name": "test_job"}}}}
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client()

    def test_create_job_gql(self):
        self.client.validate(gql(GQL_CREATE_JOB))

    def test_create_job(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)
        job_params = {
            "job_name": "test_job",
            "project_id": "project_id",
            "description": "Test job",
            "category": "Processing",
            "technology": "python",
            "runtime_version": "3.10",
            "command_line": "python test.py",
            "release_note": "Initial version",
        }
        # Patch the self.__launch_request method to avoid calling the API
        # Use patch.multiple to patch multiple methods at once
        saagie_api_mock.patch.object(instance, "_Jobs__launch_request", return_value={"name": job_params["job_name"]})
        with patch.object(instance, "_Jobs__launch_request", return_value={"name": job_params["job_name"]}):
            job_result = instance.create(**job_params)
        assert "name" in job_result
        assert job_result["name"] == job_params["job_name"]

    def test_create_job_invalid_category(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)
        job_params = {
            "job_name": "test_job",
            "project_id": "project_id",
            "description": "Test job",
            "category": "InvalidCategory",  # Invalid category
            "technology": "python",
            "runtime_version": "3.10",
            "command_line": "python test.py",
            "release_note": "Initial version",
        }
        with pytest.raises(RuntimeError):
            instance.create(**job_params)

    def test_upgrade_job(self):
        self.client.validate(gql(GQL_UPGRADE_JOB))

    def test_list_project_jobs(self):
        self.client.validate(gql(GQL_LIST_JOBS_FOR_PROJECT))

    def test_list_project_jobs_minimal(self):
        self.client.validate(gql(GQL_LIST_JOBS_FOR_PROJECT_MINIMAL))

    def test_get_id_job_exists(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)
        assert instance.get_id("job2", "project_id") == 2

    def test_get_id_job_does_not_exist(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)
        with pytest.raises(NameError):
            instance.get_id("non_existent_job", "project_id")

    def test_get_id_empty_list(self, saagie_api_mock):
        saagie_api_mock.jobs.list_for_project_minimal.return_value = {"jobs": []}
        instance = Jobs(saagie_api_mock)
        with pytest.raises(NameError):
            instance.get_id("job1", "project_id")

    def test_gql_get_info_job(self):
        self.client.validate(gql(GQL_GET_JOB_INFO))

    def test_get_job_instance(self):
        self.client.validate(gql(GQL_GET_JOB_INSTANCE))

    def test_run_job(self):
        self.client.validate(gql(GQL_RUN_JOB))

    def test_stop_job(self):
        self.client.validate(gql(GQL_STOP_JOB_INSTANCE))

    def test_edit_job_gql(self):
        self.client.validate(gql(GQL_EDIT_JOB))

    def test_edit_job(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)
        # job_params = {
        #     "job_id": "job_id",
        #     "job_name": "test_job",
        #     "description": "Test job",
        #     "is_scheduled": False,
        # }
        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "job_name": "newname",
            "description": "new desc",
            "is_scheduled": True,
            "cron_scheduling": "0 * * * *",
            "schedule_timezone": "Europe/Paris",
            "resources": {"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}},
            "emails": ["email1@saagie.io"],
            "status_list": ["FAILED", "QUEUED"],
        }
        # Mock the return value
        return_value = {
            "editJob": {
                "id": job_params["job_id"],
                "name": job_params["job_name"],
                "alias": job_params["job_name"],
                "description": job_params["description"],
                "isScheduled": job_params["is_scheduled"],
                "cronScheduling": job_params["cron_scheduling"],
                "scheduleTimezone": job_params["schedule_timezone"],
                "resources": job_params["resources"],
                "alerting": {"emails": job_params["emails"], "statusList": job_params["status_list"]},
            }
        }
        saagie_api_mock.client.execute.return_value = return_value
        # Patch the self.__launch_request and self.get_info methods to avoid calling the API
        with patch.object(instance, "_Jobs__launch_request", return_value={"name": job_params["job_name"]}):
            with patch.object(
                instance,
                "get_info",
                return_value={
                    "job": {
                        "name": "Test name",
                        "description": "Test job",
                        "resources": "1",
                        "isScheduled": False,
                        "emails": "",
                        "alerting": "",
                    }
                },
            ):
                job_result = instance.edit(**job_params)

        assert job_result == return_value

    def test_delete_job(self):
        self.client.validate(gql(GQL_DELETE_JOB))

    def test_rollback_job(self):
        self.client.validate(gql(GQL_ROLLBACK_JOB_VERSION))

    def test_delete_instances(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCE))

    def test_delete_instances_by_selector(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCES_BY_SELECTOR))

    def test_delete_versions(self):
        self.client.validate(gql(GQL_DELETE_JOB_VERSION))

    def test_duplicate(self):
        self.client.validate(gql(GQL_DUPLICATE_JOB))

    def test_count_instances_by_status(self):
        self.client.validate(gql(GQL_COUNT_INSTANCES_BY_SELECTOR))
