# pylint: disable=attribute-defined-outside-init
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.jobs import Jobs
from saagieapi.jobs.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestJobs:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()

        # saagie_api_mock.projects.get_id.return_value = "project_id"
        # saagie_api_mock.projects.get_jobs_technologies.return_value = {
        #     "technologiesByCategory": [{"jobCategory": "Processing", "technologies": [{"id": "python"}, {"id": "spark"}]}]
        # }
        # saagie_api_mock.get_runtimes.return_value = {"technology": {"contexts": [{"id": "3.10", "available": True}]}}
        # saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        # saagie_api_mock.__launch_request.return_value = {"data": {"createJob": {"job": {"name": "test_job"}}}}
        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_project_jobs_gql(self):
        self.client.validate(gql(GQL_LIST_JOBS_FOR_PROJECT))

    def test_list_project_jobs(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        return_value = {
            "jobs": [
                {"name": "job1", "id": 1, "alias": "job1_alias"},
                {"name": "job2", "id": 2, "alias": "job2_alias"},
            ]
        }

        saagie_api_mock.client.execute.return_value = return_value
        job_result = instance.list_for_project(project_id="project_id")

        assert job_result == return_value

    def test_list_project_jobs_minimal_gql(self):
        self.client.validate(gql(GQL_LIST_JOBS_FOR_PROJECT_MINIMAL))

    def test_list_project_jobs_minimal(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        return_value = {
            "jobs": [
                {"name": "job1", "id": 1, "alias": "job1_alias"},
                {"name": "job2", "id": 2, "alias": "job2_alias"},
            ]
        }

        saagie_api_mock.client.execute.return_value = return_value
        job_result = instance.list_for_project_minimal(project_id="project_id")

        assert job_result == return_value

    def test_get_job_instance_gql(self):
        self.client.validate(gql(GQL_GET_JOB_INSTANCE))

    def test_get_job_instance(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        return_value = {
            "jobInstance": {"id": "befe73b2-81ab-418f-bc2f-9d012102a895", "number": 1, "status": "SUCCEEDED"},
        }

        saagie_api_mock.client.execute.return_value = return_value
        job_result = instance.get_instance(job_instance_id="project_id")

        assert job_result == return_value

    def test_get_id_job_exists(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        with patch.object(instance, "list_for_project_minimal") as list_min:
            list_min.return_value = {
                "jobs": [
                    {"name": "job1", "id": 1, "alias": "job1_alias"},
                    {"name": "job2", "id": 2, "alias": "job2_alias"},
                ]
            }
            res = instance.get_id("job2", "project_id")

        assert res == 2

    def test_get_id_job_does_not_exist(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)
        with patch.object(instance, "list_for_project_minimal") as list_min:
            list_min.return_value = {
                "jobs": [
                    {"name": "job1", "id": 1, "alias": "job1_alias"},
                    {"name": "job2", "id": 2, "alias": "job2_alias"},
                ]
            }
            with pytest.raises(NameError):
                instance.get_id("non_existent_job", "project_id")

    def test_get_id_empty_list(self, saagie_api_mock):
        saagie_api_mock.jobs.list_for_project_minimal.return_value = {"jobs": []}
        instance = Jobs(saagie_api_mock)
        with pytest.raises(NameError):
            instance.get_id("job1", "project_id")

    def test_gql_get_info_job_gql(self):
        self.client.validate(gql(GQL_GET_JOB_INFO))

    def test_gql_get_info_job(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        return_value = {
            "job": {
                "id": "befe73b2-81ab-418f-bc2f-9d012102a895",
                "name": "Python test job",
                "description": "Amazing python job",
            },
        }

        saagie_api_mock.client.execute.return_value = return_value
        job_result = instance.get_info(job_id="job_id")

        assert job_result == return_value

    def test_get_info_job_by_alias_gql(self):
        self.client.validate(gql(GQL_GET_JOB_INFO_BY_ALIAS))

    def test_get_info_job_by_alias(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        return_value = {
            "jobByAlias": {
                "id": "befe73b2-81ab-418f-bc2f-9d012102a895",
                "name": "Python test job",
                "description": "Amazing python job",
            },
        }

        saagie_api_mock.client.execute.return_value = return_value
        job_result = instance.get_info_by_alias(project_id="project_id", job_alias="alias")

        assert job_result == return_value

    def test_create_job_gql(self):
        self.client.validate(gql(GQL_CREATE_JOB))

    def test_create_job(self, saagie_api_mock):
        saagie_api_mock.projects.get_jobs_technologies.return_value = {
            "technologiesByCategory": [
                {"jobCategory": "Processing", "technologies": [{"id": "python"}, {"id": "spark"}]}
            ]
        }
        saagie_api_mock.get_runtimes.return_value = {"technology": {"contexts": [{"id": "3.10", "available": True}]}}
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        # saagie_api_mock.check_alerting.return_value = {"alerting": {"emails": ["e.mail@test.com"], "statusList": ["FAILED", "KILLED"]}}
        # saagie_api_mock.check_scheduling.return_value = {"alerting": {"emails": ["e.mail@test.com"], "statusList": ["FAILED", "KILLED"]}}
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
            "emails": ["e.mail@test.com"],
            "status_list": ["FAILED", "KILLED"],
            "cron_scheduling": "0 0 * * *",
            "schedule_timezone": "Europe/Paris",
        }
        # Patch the self.__launch_request method to avoid calling the API
        with patch.object(instance, "_Jobs__launch_request") as launch_request:
            launch_request.return_value = {"data": {"createJob": {"job": {"name": "test_job"}}}}
            job_result = instance.create(**job_params)

        assert "name" in job_result["data"]["createJob"]["job"]
        assert job_result["data"]["createJob"]["job"]["name"] == job_params["job_name"]

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

    def test_create_job_invalid_runtime(self, saagie_api_mock):
        saagie_api_mock.projects.get_jobs_technologies.return_value = {
            "technologiesByCategory": [
                {"jobCategory": "Processing", "technologies": [{"id": "python"}, {"id": "spark"}]}
            ]
        }
        saagie_api_mock.get_runtimes.return_value = {"technology": {"contexts": [{"id": "3.10", "available": True}]}}
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        instance = Jobs(saagie_api_mock)
        job_params = {
            "job_name": "test_job",
            "project_id": "project_id",
            "description": "Test job",
            "category": "Processing",  # Invalid category
            "technology": "python",
            "runtime_version": "3.2",
            "command_line": "python test.py",
            "release_note": "Initial version",
        }
        with pytest.raises(RuntimeError):
            instance.create(**job_params)

    def test_create_job_with_extra_techno(self, saagie_api_mock):
        saagie_api_mock.projects.get_jobs_technologies.return_value = {
            "technologiesByCategory": [
                {"jobCategory": "Processing", "technologies": [{"id": "python"}, {"id": "spark"}]}
            ]
        }
        saagie_api_mock.get_runtimes.return_value = {
            "technology": {
                "contexts": [
                    {"id": "2.4", "label": "2.4", "available": True},
                    {"id": "3.0", "label": "3.0", "available": True},
                    {"id": "3.1", "label": "3.1", "available": True},
                    {"id": "3.1-aws", "label": "3.1 AWS", "available": True},
                ]
            }
        }
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        instance = Jobs(saagie_api_mock)
        job_params = {
            "job_name": "test_job",
            "project_id": "project_id",
            "description": "Test job",
            "category": "Processing",
            "technology": "spark",
            "runtime_version": "3.1",
            "command_line": "python test.py",
            "release_note": "Initial version",
            "extra_technology": "python",
            "extra_technology_version": "3.9",
        }

        with patch.object(instance, "_Jobs__launch_request") as launch_request:
            launch_request.return_value = {"data": {"createJob": {"job": {"name": "test_job"}}}}
            job_result = instance.create(**job_params)

        assert "name" in job_result["data"]["createJob"]["job"]
        assert job_result["data"]["createJob"]["job"]["name"] == job_params["job_name"]

    def test_edit_job_gql(self):
        self.client.validate(gql(GQL_EDIT_JOB))

    def test_edit_job(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "job_name": "newnamejob",
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
        with patch.object(instance, "get_info") as get_info:
            get_info.return_value = {
                "job": {
                    "name": "Test name",
                    "description": "Test job",
                    "resources": "1",
                    "isScheduled": False,
                    "emails": "",
                    "alerting": "",
                }
            }
            job_result = instance.edit(**job_params)

        assert job_result == return_value

    def test_edit_non_existing_job(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

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

        with patch.object(instance, "get_info") as get_info, pytest.raises(RuntimeError):
            get_info.return_value = {"job": None}
            instance.edit(**job_params)

    def test_edit_job_without_scheduled(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "job_name": "newname",
            "description": "new desc",
            "is_scheduled": False,
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
                "resources": job_params["resources"],
                "alerting": {"emails": job_params["emails"], "statusList": job_params["status_list"]},
            }
        }
        saagie_api_mock.client.execute.return_value = return_value

        with patch.object(instance, "get_info") as get_info:
            get_info.return_value = {
                "job": {
                    "name": "Test name",
                    "description": "Test job",
                    "resources": "1",
                    "isScheduled": True,
                    "emails": "",
                    "alerting": "",
                }
            }
            job_result = instance.edit(**job_params)

        assert job_result == return_value

    def test_edit_job_with_no_scheduled_update(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "job_name": "newname",
            "description": "new desc",
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
                "resources": job_params["resources"],
                "alerting": {"emails": job_params["emails"], "statusList": job_params["status_list"]},
            }
        }
        saagie_api_mock.client.execute.return_value = return_value

        with patch.object(instance, "get_info") as get_info:
            get_info.return_value = {
                "job": {
                    "name": "Test name",
                    "description": "Test job",
                    "resources": "1",
                    "isScheduled": True,
                    "cronScheduling": "0 * * * *",
                    "scheduleTimezone": "Europe/Paris",
                    "emails": "",
                    "alerting": "",
                }
            }
            job_result = instance.edit(**job_params)

        assert job_result == return_value

    @patch(
        "saagieapi.jobs.jobs.Jobs.get_info",
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
    )
    def test_edit_job_without_email(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "job_name": "newname",
            "description": "new desc",
            "is_scheduled": True,
            "cron_scheduling": "0 * * * *",
            "schedule_timezone": "Europe/Paris",
            "resources": {"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}},
            "emails": [],
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
            }
        }
        saagie_api_mock.client.execute.return_value = return_value

        job_result = instance.edit(**job_params)

        assert job_result == return_value

    @patch(
        "saagieapi.jobs.jobs.Jobs.get_info",
        return_value={
            "job": {
                "name": "Test name",
                "description": "Test job",
                "resources": "1",
                "isScheduled": False,
                "emails": "",
                "alerting": {"emails": ["my.super@email.com"], "loginEmails": [], "statusList": ["FAILED"]},
            }
        },
    )
    def test_edit_job_with_no_email_update(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "job_name": "newname",
            "description": "new desc",
            "is_scheduled": True,
            "cron_scheduling": "0 * * * *",
            "schedule_timezone": "Europe/Paris",
            "resources": {"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}},
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
            }
        }
        saagie_api_mock.client.execute.return_value = return_value

        job_result = instance.edit(**job_params)

        assert job_result == return_value

    def test_upgrade_job_gql(self):
        self.client.validate(gql(GQL_UPGRADE_JOB))

    def test_upgrade_job(self, saagie_api_mock):
        saagie_api_mock.get_runtimes.return_value = {"technology": {"contexts": [{"id": "3.10", "available": True}]}}
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "source_url": "http://my.super.source.url",
        }
        # Mock the return value
        return_value = {"data": {"addJobVersion": {"number": 2, "__typename": "JobVersion"}}}
        saagie_api_mock.client.execute.return_value = return_value
        # Patch the self.__launch_request and self.get_info methods to avoid calling the API
        with patch.object(instance, "get_info") as get_info, patch.object(
            instance, "_Jobs__launch_request"
        ) as launch_request:
            get_info.return_value = {
                "job": {
                    "id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
                    "name": "test upgrade job",
                    "description": "super description for test upgrade job",
                    "technology": {"id": "0db6d0a7-ad4b-45cd-8082-913a192daa25"},
                    "versions": [
                        {
                            "runtimeVersion": "3.10",
                            "commandLine": "python {file} arg1 arg2",
                            "packageInfo": {
                                "name": "test.py",
                                "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/f5fce22d-2152-4a01-8c6a-4c2eb4808b6d/version/1/artifact/test.py",
                            },
                        }
                    ],
                }
            }
            launch_request.return_value = return_value
            job_result = instance.upgrade(**job_params)

        assert job_result == return_value

    def test_upgrade_job_with_bad_runtime(self, saagie_api_mock):
        saagie_api_mock.get_runtimes.return_value = {"technology": {"contexts": [{"id": "3.9", "available": True}]}}
        instance = Jobs(saagie_api_mock)

        job_params = {"job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db", "runtime_version": "3.10"}
        # Mock the return value
        return_value = {"data": {"addJobVersion": {"number": 2, "__typename": "JobVersion"}}}
        saagie_api_mock.client.execute.return_value = return_value
        # Patch the self.__launch_request and self.get_info methods to avoid calling the API
        with patch.object(instance, "get_info") as get_info, pytest.raises(RuntimeError):
            get_info.return_value = {
                "job": {
                    "id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
                    "name": "test upgrade job",
                    "description": "super description for test upgrade job",
                    "technology": {"id": "0db6d0a7-ad4b-45cd-8082-913a192daa25"},
                    "versions": [
                        {
                            "runtimeVersion": "3.10",
                            "commandLine": "python {file} arg1 arg2",
                            "packageInfo": {
                                "name": "test.py",
                                "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/f5fce22d-2152-4a01-8c6a-4c2eb4808b6d/version/1/artifact/test.py",
                            },
                        }
                    ],
                }
            }
            instance.upgrade(**job_params)

    def test_upgrade_job_with_extra_techno(self, saagie_api_mock):
        saagie_api_mock.get_runtimes.return_value = {
            "technology": {
                "contexts": [
                    {"id": "2.4", "label": "2.4", "available": True},
                    {"id": "3.0", "label": "3.0", "available": True},
                    {"id": "3.1", "label": "3.1", "available": True},
                    {"id": "3.1-aws", "label": "3.1 AWS", "available": True},
                ]
            }
        }
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "source_url": "http://my.super.source.url",
            "extra_technology": "python",
            "extra_technology_version": "3.9",
        }
        # Mock the return value
        return_value = {"data": {"addJobVersion": {"number": 2, "__typename": "JobVersion"}}}
        saagie_api_mock.client.execute.return_value = return_value
        # Patch the self.__launch_request and self.get_info methods to avoid calling the API
        with patch.object(instance, "get_info") as get_info, patch.object(
            instance, "_Jobs__launch_request"
        ) as launch_request:
            get_info.return_value = {
                "job": {
                    "id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
                    "name": "test upgrade job",
                    "description": "super description for test upgrade job",
                    "technology": {"id": "0db6d0a7-ad4b-45cd-8082-913a192daa25"},
                    "versions": [
                        {
                            "runtimeVersion": "3.1",
                            "commandLine": "python {file} arg1 arg2",
                            "packageInfo": {
                                "name": "test.py",
                                "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/f5fce22d-2152-4a01-8c6a-4c2eb4808b6d/version/1/artifact/test.py",
                            },
                        }
                    ],
                }
            }
            launch_request.return_value = return_value
            job_result = instance.upgrade(**job_params)

        assert job_result == return_value

    def test_upgrade_by_name(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_name": "test upgrade job by name",
            "project_name": "project test",
        }

        return_value = {"data": {"addJobVersion": {"number": 2, "__typename": "JobVersion"}}}

        with patch.object(instance, "get_id") as get_id, patch.object(instance, "upgrade") as upgrade:
            get_id.return_value = "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d"
            upgrade.return_value = return_value
            job_result = instance.upgrade_by_name(**job_params)

        assert job_result == return_value

    def test_create_or_upgrade_create(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_name": "job3",
            "project_id": "project_id",
        }

        return_value = {
            "data": {
                "createJob": {
                    "id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
                    "versions": [{"number": 1, "__typename": "JobVersion"}],
                    "__typename": "Job",
                }
            }
        }

        with patch.object(instance, "list_for_project_minimal") as list_min, patch.object(instance, "create") as create:
            list_min.return_value = {
                "jobs": [
                    {"name": "job1", "id": 1, "alias": "job1_alias"},
                    {"name": "job2", "id": 2, "alias": "job2_alias"},
                ]
            }
            create.return_value = return_value
            job_result = instance.create_or_upgrade(**job_params)

        assert job_result == return_value

    def test_create_or_upgrade_upgrade(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_name": "job2",
            "project_id": "project_id",
        }

        upgrade_return = {"data": {"addJobVersion": {"number": 2}}}
        edit_return = {
            "editJob": {
                "id": 2,
                "name": "job2",
            }
        }

        return_value = {
            "addJobVersion": upgrade_return["data"]["addJobVersion"],
            "editJob": edit_return["editJob"],
        }

        with patch.object(instance, "list_for_project_minimal") as list_min, patch.object(
            instance, "upgrade"
        ) as upgrade, patch.object(instance, "edit") as edit:
            list_min.return_value = {
                "jobs": [
                    {"name": "job1", "id": 1, "alias": "job1_alias"},
                    {"name": "job2", "id": 2, "alias": "job2_alias"},
                ]
            }
            upgrade.return_value = upgrade_return
            edit.return_value = edit_return
            job_result = instance.create_or_upgrade(**job_params)

        assert job_result == return_value

    def test_rollback_job(self):
        self.client.validate(gql(GQL_ROLLBACK_JOB_VERSION))

    def test_delete_job(self):
        self.client.validate(gql(GQL_DELETE_JOB))

    def test_run_job(self):
        self.client.validate(gql(GQL_RUN_JOB))

    def test_run_job_with_callback_succeeded(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
            "freq": 1,
        }

        return_value = ("SUCCEEDED", "5b9fc971-1c4e-4e45-a978-5851caef0162")

        with patch.object(instance, "run") as run, patch.object(instance, "get_instance") as get_inst:
            run.return_value = {"runJob": {"id": "5b9fc971-1c4e-4e45-a978-5851caef0162", "status": "REQUESTED"}}
            get_inst.side_effect = [{"jobInstance": {"status": "RUNNING"}}, {"jobInstance": {"status": "SUCCEEDED"}}]

            job_result = instance.run_with_callback(**job_params)

        assert job_result == return_value

    def test_run_job_with_callback_failed(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
            "freq": 1,
            "timeout": 10,
        }

        return_value = ("FAILED", "5b9fc971-1c4e-4e45-a978-5851caef0162")

        with patch.object(instance, "run") as run, patch.object(instance, "get_instance") as get_inst:
            run.return_value = {"runJob": {"id": "5b9fc971-1c4e-4e45-a978-5851caef0162", "status": "REQUESTED"}}
            get_inst.side_effect = [{"jobInstance": {"status": "RUNNING"}}, {"jobInstance": {"status": "FAILED"}}]

            job_result = instance.run_with_callback(**job_params)

        assert job_result == return_value

    def test_run_job_with_callback_timeout(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
            "freq": 1,
            "timeout": 2,
        }

        with patch.object(instance, "run") as run, patch.object(instance, "get_instance") as get_inst, pytest.raises(
            TimeoutError
        ):
            run.return_value = {"runJob": {"id": "5b9fc971-1c4e-4e45-a978-5851caef0162", "status": "REQUESTED"}}
            get_inst.side_effect = [
                {"jobInstance": {"status": "RUNNING"}},
                {"jobInstance": {"status": "RUNNING"}},
                {"jobInstance": {"status": "RUNNING"}},
            ]

            instance.run_with_callback(**job_params)

    def test_stop_job(self):
        self.client.validate(gql(GQL_STOP_JOB_INSTANCE))

    # def test_export(self, saagie_api_mock):
    #     saagie_api_mock.get_technology_name_by_id.return_value = ("Saagie", "Python")
    #     instance = Jobs(saagie_api_mock)

    #     job_params = {
    #         "job_id": "5b9fc971-1c4e-4e45-a978-5851caef0162",
    #         "output_folder": "/tmp",
    #     }

    #     with patch.object(instance, "get_info") as get_info:
    #         get_info.return_value = {
    #             "job": {
    #                 "id": "",
    #                 "name": "test export job",
    #                 "technology": {
    #                     "id": ""
    #                 }
    #             }
    #         }

    #         job_result = instance.export(**job_params)

    #     assert job_result == True

    def test_delete_instances(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCE))

    def test_delete_instances_by_selector(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCES_BY_SELECTOR))

    def test_delete_instances_by_date_gql(self):
        self.client.validate(gql(GQL_DELETE_JOB_INSTANCES_BY_DATE))

    def test_delete_instances_by_date_correct_format(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "5b9fc971-1c4e-4e45-a978-5851caef0162",
            "date_before": "2023-06-01T00:00:00+01:00",
        }

        return_value = {"deleteJobInstancesByDate": 1}

        saagie_api_mock.client.execute.return_value = return_value
        job_result = instance.delete_instances_by_date(**job_params)

        assert job_result == return_value

    def test_delete_instances_by_date_incorrect_format(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "5b9fc971-1c4e-4e45-a978-5851caef0162",
            "date_before": "20230601 00:00:00+01:00",
        }

        # return_value = {"deleteJobInstancesByDate": 1}

        # saagie_api_mock.client.execute.return_value = return_value
        with pytest.raises(ValueError):
            instance.delete_instances_by_date(**job_params)

    def test_delete_versions(self):
        self.client.validate(gql(GQL_DELETE_JOB_VERSION))

    def test_duplicate(self):
        self.client.validate(gql(GQL_DUPLICATE_JOB))

    def test_count_deletable_instances_by_status(self):
        self.client.validate(gql(GQL_COUNT_INSTANCES_BY_SELECTOR))

    def test_count_deletable_instances_by_date(self):
        self.client.validate(gql(GQL_COUNT_INSTANCES_BY_DATE))

    def test_count_deletable_instances_by_date_correct_format(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "5b9fc971-1c4e-4e45-a978-5851caef0162",
            "date_before": "2023-06-01T00:00:00+01:00",
        }

        return_value = {"countJobInstancesByDate": 1}

        saagie_api_mock.client.execute.return_value = return_value
        job_result = instance.count_deletable_instances_by_date(**job_params)

        assert job_result == return_value

    def test_count_deletable_instances_by_date_incorrect_format(self, saagie_api_mock):
        instance = Jobs(saagie_api_mock)

        job_params = {
            "job_id": "5b9fc971-1c4e-4e45-a978-5851caef0162",
            "date_before": "20230601 00:00:00+01:00",
        }

        with pytest.raises(ValueError):
            instance.count_deletable_instances_by_date(**job_params)

    def test_move_job(self):
        self.client.validate(gql(GQL_MOVE_JOB))

    def test_generate_description_by_ai(self):
        self.client.validate(gql(GQL_GENERATE_JOB_DESCRIPTION))
