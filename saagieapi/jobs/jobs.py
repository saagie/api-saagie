import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import deprecation
import requests
from gql import gql

from ..utils.folder_functions import (
    create_folder,
    remove_slash_folder_path,
    write_error,
    write_request_response_to_file,
    write_to_json_file,
)
from ..utils.rich_console import console
from .gql_queries import *


def handle_write_error(msg, job_id, error_folder):
    logging.warning(msg, job_id)
    write_error(error_folder, "jobs", job_id)
    return False


def handle_log_error(msg, exception):
    logging.warning(msg)
    logging.error("Something went wrong %s", exception)
    return False


class Jobs:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list_for_project(
        self,
        project_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """List jobs in the given project with their instances.
        NB: You can only list jobs if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per job. Fetch from most recent
            to oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of jobs information

        Examples
        --------
        >>> saagieapi.jobs.list_for_project(
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
        ...     instances_limit=2
        ... )
        {
            "jobs": [
                {
                    "id": "fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10",
                    "name": "Python test job 1",
                    "description": "Amazing python job",
                    "alerting": None,
                    "countJobInstance": 0,
                    "instances": [],
                    "versions": [
                        {
                            "number": 1,
                            "creationDate": "2022-04-26T12:08:15.286Z",
                            "releaseNote": "",
                            "runtimeVersion": "3.7",
                            "commandLine": "python {file} arg1 arg2",
                            "packageInfo": {
                                "name": "_tmp_test.py",
                                "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10/version/1/artifact/_tmp_test.py"
                            },
                            "dockerInfo": None,
                            "extraTechnology": None,
                            "isCurrent": True,
                            "isMajor": False
                        }
                    ],
                    "category": "Extraction",
                    "technology": {
                        "id": "0db6d0a7-ad4b-45cd-8082-913a192daa25"
                    },
                    "isScheduled": False,
                    "cronScheduling": None,
                    "scheduleTimezone": "UTC",
                    "scheduleStatus": None,
                    "isStreaming": False,
                    "creationDate": "2022-04-26T12:08:15.286Z",
                    "migrationStatus": None,
                    "migrationProjectId": None,
                    "isDeletable": True,
                    "pipelines": [],
                    "graphPipelines": [],
                    "doesUseGPU": False,
                    "resources": None
                }
            ]
        }
        """  # pylint: disable=line-too-long
        params = {
            "projectId": project_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_JOBS_FOR_PROJECT), variable_values=params, pprint_result=pprint_result
        )

    def list_for_project_minimal(self, project_id: str) -> Dict:
        """List only job names and ids in the given project .
        NB: You can only list jobs if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of jobs ids and names

        Examples
        --------
        >>> saagieapi.jobs.list_for_project_minimal(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771")
        {
            "jobs": [
                {
                    "id": "fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10",
                    "name": "Python test job 1",
                    "alias": "Python_test_job_1"
                },
                {
                    "id": "e92ed170-50d6-4041-bba9-098a8e16f444",
                    "name": "Python test job 2",
                    "alias": "Python_test_job_2"
                }
            ]
        }
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_JOBS_FOR_PROJECT_MINIMAL), variable_values={"projectId": project_id}
        )

    def get_instance(self, job_instance_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """Get the given job instance

        Parameters
        ----------
        job_instance_id : str
            UUID of your job instance (see README on how to find it)
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of instance information

        Examples
        --------
        >>> saagieapi.jobs.get_instance(job_instance_id="befe73b2-81ab-418f-bc2f-9d012102a895")
        {
            "jobInstance": {
                "id": "befe73b2-81ab-418f-bc2f-9d012102a895",
                "number": 1,
                "status": "SUCCEEDED",
                "history": {
                    "currentStatus": {
                        "status": "SUCCEEDED",
                        "details": None,
                        "reason": None
                    }
                },
                "startTime": "2022-04-19T13:45:49.783Z",
                "endTime": "2022-04-19T13:45:57.388Z",
                "jobId": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
                "version":{
                    "number": 1,
                    "releaseNote": "",
                    "runtimeVersion": "3.7",
                    "commandLine": "python {file} arg1 arg2",
                    "isMajor": False,
                    "isCurrent": True
                }
                "executionGlobalVariablesInput": [
                    {
                        "key": "TEST_PASSWORD",
                        "value": None,
                        "isPassword": True
                    },
                    {
                        "key": "TEST_PROJECT",
                        "value": "TEST_PROJECT",
                        "isPassword": False
                    }
                ],
                "executionVariablesInput": [
                    {
                        "parentJobInstanceId": None,
                        "parentJobId": None,
                        "parentJobAlias": None,
                        "isDirectParent": None,
                        "executionVariables": [
                            {
                                "key": "TEST_PASSWORD",
                                "value": None,
                                "isPassword": True
                            },
                            {
                                "key": "TEST_PROJECT",
                                "value": "TEST_PROJECT",
                                "isPassword": False
                            }
                        ],
                        "isGlobalVariables": True
                    }
                ],
                "executionVariablesOutput": None,
                "executionVariablesByKey": []
            }
        }
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_GET_JOB_INSTANCE),
            variable_values={"jobInstanceId": job_instance_id},
            pprint_result=pprint_result,
        )

    def get_id(self, job_name: str, project_name: str) -> str:
        """Get the job id with the job name and project name

        Parameters
        ----------
        job_name : str
            Name of your job
        project_name : str
            Name of your project

        Returns
        -------
        str
            Job UUID

        Examples
        --------
        >>> saagieapi.jobs.get_id(
        ...     project_name="Test project",
        ...     job_name="Python test job"
        ... )
        "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d"
        """
        jobs = self.list_for_project_minimal(self.saagie_api.projects.get_id(project_name))["jobs"]
        if job := next((j for j in jobs if j["name"] == job_name), None):
            return job["id"]
        raise NameError(f"❌ Job {job_name} does not exist.")

    def get_info(
        self,
        job_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get job's info

        Parameters
        ----------
        job_id : str
            UUID of your job
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per job. Fetch from most recent
            to oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of job's info

        Examples
        --------
        >>> saagieapi.jobs.get_info(
        ...     job_id="f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
        ...     instances_limit=2
        ... )
        {
            "job": {
                "id": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
                "name": "Python test job",
                "description": "Amazing python job",
                "alerting": None,
                "countJobInstance": 5,
                "instances": [
                    {
                        "id": "61f6175a-fd38-4fac-9fa9-a7b63554f14e",
                        "status": "SUCCEEDED",
                        "history": {
                            "currentStatus": {
                                "status": "SUCCEEDED",
                                "details": None,
                                "reason": None
                            }
                        },
                        "startTime": "2022-04-19T13:46:40.045Z",
                        "endTime": "2022-04-19T13:46:47.708Z",
                        "version": {
                            "number": 1,
                            "releaseNote": "",
                            "runtimeVersion": "3.7",
                            "commandLine": "python {file} arg1 arg2",
                            "isMajor": False,
                            "doesUseGPU": False
                        }
                    },
                    {
                        "id": "befe73b2-81ab-418f-bc2f-9d012102a895",
                        "status": "SUCCEEDED",
                        "history": {
                            "currentStatus": {
                                "status": "SUCCEEDED",
                                "details": None,
                                "reason": None
                            }
                        },
                        "startTime": "2022-04-19T13:45:49.783Z",
                        "endTime": "2022-04-19T13:45:57.388Z",
                        "version":{
                            "number": 1,
                            "releaseNote": "",
                            "runtimeVersion": "3.7",
                            "commandLine": "python {file} arg1 arg2",
                            "isMajor": False,
                            "doesUseGPU": False
                        }
                    }
                ],
                "versions": [
                    {
                        "number": 1,
                        "creationDate": "2022-04-26T08:16:20.681Z",
                        "releaseNote": "",
                        "runtimeVersion": "3.7",
                        "commandLine": "python {file} arg1 arg2",
                        "packageInfo": {
                            "name": "test.py",
                            "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/f5fce22d-2152-4a01-8c6a-4c2eb4808b6d/version/1/artifact/test.py"
                        },
                        "dockerInfo": None,
                        "extraTechnology": None,
                        "isCurrent": True,
                        "isMajor": False
                    }
                ],
                "category": "Extraction",
                "technology": {
                    "id": "0db6d0a7-ad4b-45cd-8082-913a192daa25"
                },
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isStreaming": False,
                "creationDate": "2022-04-26T08:16:20.681Z",
                "migrationStatus": None,
                "migrationProjectId": None,
                "isDeletable": True,
                "graphPipelines": [],
                "doesUseGPU": False,
                "resources": None
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "jobId": job_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_GET_JOB_INFO), variable_values=params, pprint_result=pprint_result
        )

    def get_info_by_alias(
        self,
        project_id: str,
        job_alias: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get job's info

        Parameters
        ----------
        project_id : str
            UUID of the project of your job
        job_alias : str
            Alias of your job
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per job. Fetch from most recent
            to oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of job's info

        Examples
        --------
        >>> saagieapi.jobs.get_info_by_alias(
        ...     project_id="7c199d29-676a-483f-b28b-112ec71fcf81",
        ...     job_alias="Python_test_job"
        ...     instances_limit=2
        ... )
        {
            "jobByAlias": {
                "id": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
                "name": "Python test job",
                "description": "Amazing python job",
                "alerting": None,
                "countJobInstance": 5,
                "instances": [
                    {
                        "id": "61f6175a-fd38-4fac-9fa9-a7b63554f14e",
                        "status": "SUCCEEDED",
                        "history": {
                            "currentStatus": {
                                "status": "SUCCEEDED",
                                "details": None,
                                "reason": None
                            }
                        },
                        "startTime": "2022-04-19T13:46:40.045Z",
                        "endTime": "2022-04-19T13:46:47.708Z",
                        "version": {
                            "number": 1,
                            "releaseNote": "",
                            "runtimeVersion": "3.7",
                            "commandLine": "python {file} arg1 arg2",
                            "isMajor": False,
                            "doesUseGPU": False
                        }
                    },
                    {
                        "id": "befe73b2-81ab-418f-bc2f-9d012102a895",
                        "status": "SUCCEEDED",
                        "history": {
                            "currentStatus": {
                                "status": "SUCCEEDED",
                                "details": None,
                                "reason": None
                            }
                        },
                        "startTime": "2022-04-19T13:45:49.783Z",
                        "endTime": "2022-04-19T13:45:57.388Z",
                        "version":{
                            "number": 1,
                            "releaseNote": "",
                            "runtimeVersion": "3.7",
                            "commandLine": "python {file} arg1 arg2",
                            "isMajor": False,
                            "doesUseGPU": False
                        }
                    }
                ],
                "versions": [
                    {
                        "number": 1,
                        "creationDate": "2022-04-26T08:16:20.681Z",
                        "releaseNote": "",
                        "runtimeVersion": "3.7",
                        "commandLine": "python {file} arg1 arg2",
                        "packageInfo": {
                            "name": "test.py",
                            "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/f5fce22d-2152-4a01-8c6a-4c2eb4808b6d/version/1/artifact/test.py"
                        },
                        "dockerInfo": None,
                        "extraTechnology": None,
                        "isCurrent": True,
                        "isMajor": False
                    }
                ],
                "category": "Extraction",
                "technology": {
                    "id": "0db6d0a7-ad4b-45cd-8082-913a192daa25"
                },
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isStreaming": False,
                "creationDate": "2022-04-26T08:16:20.681Z",
                "migrationStatus": None,
                "migrationProjectId": None,
                "isDeletable": True,
                "graphPipelines": [],
                "doesUseGPU": False,
                "resources": None
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "projectId": project_id,
            "alias": job_alias,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_GET_JOB_INFO_BY_ALIAS), variable_values=params, pprint_result=pprint_result
        )

    def create(
        self,
        job_name: str,
        project_id: str,
        file: str = None,
        description: str = "",
        category: str = "Processing",
        technology: str = "python",
        technology_catalog: str = "Saagie",
        runtime_version: str = "3.10",
        command_line: str = "python {file} arg1 arg2",
        release_note: str = "",
        extra_technology: str = None,
        extra_technology_version: str = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        resources: Dict = None,
        emails: List = None,
        status_list: List = None,
        source_url: str = "",
        docker_info: Dict = None,
    ) -> Dict:
        """Create job in given project

        NOTE
        ----
        - Only work for gql>=3.0.0

        Parameters
        ----------
        job_name : str
            Name of the job. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        file : str, optional
            Local path of the file to upload
        description : str, optional
            Description of the job
        category : str, optional
            Category to create the job into. Must be 'Extraction', 'Processing'
            or 'Smart App'
        technology : str, optional
            Technology label of the job to create.
        technology_catalog : str, optional
            Technology catalog containing the technology to use for this job
        runtime_version : str, optional
            Technology version of the job, the ID of the context
        command_line : str, optional
            Command line of the job
        release_note : str, optional
            Release note of the job
        extra_technology : str, optional
            Extra technology when needed (spark jobs). If not needed, leave to
            empty string or the request will not work
        extra_technology_version : str, optional
            Version of the extra technology. Leave to empty string when not
            needed
        cron_scheduling : str, optional
            Scheduling CRON format
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        resources : dict, optional
            CPU, memory limit and requests
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        source_url: str, optional
            URL of the source code used for the job (link to the commit for example)
        docker_info: dict (optional)
            Docker information for the job
            Example: {"image": "my_image", "dockerCredentialsId": "MY_CREDENTIALS_ID"}

        Returns
        -------
        dict
            Dict of job information

        Examples
        --------
        >>> saagieapi.jobs.create(
        ...     job_name="my job",
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
        ...     file="/tmp/test.py",
        ...     description='My description',
        ...     category='Extraction',
        ...     technology='python',# technology id corresponding to your context.id in your technology catalog definition
        ...     technology_catalog='Saagie',
        ...     runtime_version='3.9',
        ...     command_line='python {file}',
        ...     release_note='First release',
        ...     extra_technology='',
        ...     extra_technology_version='',
        ...     cron_scheduling='0 0 * * *',
        ...     schedule_timezone='Europe/Paris',
        ...     resources={"cpu": {"request": 0.5, "limit": 2.6}, "memory": {"request": 1.0}},
        ...     emails=['email1@saagie.io', 'email2@saagie.io'],
        ...     status_list=["FAILED", "KILLED"],
        ...     source_url="",
        ... )
        {
            "data":{
                "createJob":{
                    "id":"60f46dce-c869-40c3-a2e5-1d7765a806db",
                    "versions":[
                        {
                            "number":1,
                            "__typename":"JobVersion"
                        }
                    ],
                    "__typename":"Job"
                }
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "projectId": project_id,
            "name": job_name,
            "description": description,
            "category": category,
            "releaseNote": release_note,
            "runtimeVersion": runtime_version,
            "commandLine": command_line,
        }

        if category not in ("Extraction", "Processing", "Smart App"):
            raise RuntimeError(
                f"❌ Category {category} does not exist in Saagie. "
                f"Please specify either Extraction, Processing or Smart App"
            )

        technos_project = self.saagie_api.projects.get_jobs_technologies(project_id, pprint_result=False)[
            "technologiesByCategory"
        ]

        technos_project_category = [
            tech["id"]
            for tech in next(tech["technologies"] for tech in technos_project if tech["jobCategory"] == category)
        ]
        params = self.saagie_api.check_technology(params, technology, technology_catalog, technos_project_category)
        available_runtimes = [
            tech["id"]
            for tech in self.saagie_api.get_runtimes(params["technologyId"])["technology"]["contexts"]
            if tech["available"] is True
        ]
        if runtime_version not in available_runtimes:
            raise RuntimeError(
                f"❌ Runtime {runtime_version} for technology {technology} does not exist "
                f"in the catalog {technology_catalog} or is deprecated"
            )
        if extra_technology is not None and extra_technology != "":
            params["extraTechnology"] = {"language": extra_technology, "version": extra_technology_version}

        if emails:
            params.update(self.saagie_api.check_alerting(emails, status_list))

        if cron_scheduling:
            params.update(self.saagie_api.check_scheduling(cron_scheduling, schedule_timezone))
        else:
            params["isScheduled"] = False

        if resources:
            params["resources"] = resources

        if source_url:
            params["sourceUrl"] = source_url

        if docker_info:
            params["dockerInfo"] = docker_info

        result = self.__launch_request(file, GQL_CREATE_JOB, params)
        logging.info("✅ Job [%s] successfully created", job_name)
        return result

    def edit(
        self,
        job_id: str,
        job_name: str = None,
        description: str = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        resources: Dict = None,
        emails: List = None,
        status_list: List = None,
    ) -> Dict:  # sourcery skip: remove-redundant-if, simplify-boolean-comparison
        # pylint: disable=singleton-comparison
        """Edit a job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        job_name : str, optional
            Job name
            If not filled, defaults to current value, else it will change the job's name
        description : str, optional
            Description of job
            if not filled, defaults to current value, else it will change the description of the pipeline
        is_scheduled : bool, optional
            True if the job is scheduled, else False
            if not filled, defaults to current value
        cron_scheduling : str, optional
            Scheduling CRON format
            When is_scheduled is set to True, it will be mandatory to fill this value
            if not filled, defaults to current value
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        resources : dict, optional
            CPU, memory limit and requests
            if not filled, defaults to current value
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"

        Returns
        -------
        dict
            Dict of job information

        Examples
        --------
        >>> saagieapi.jobs.edit(
        ...     job_id="60f46dce-c869-40c3-a2e5-1d7765a806db",
        ...     job_name="newname",
        ...     description="new desc",
        ...     is_scheduled=True,
        ...     cron_scheduling='0 * * * *',
        ...     schedule_timezone='Europe/Paris',
        ...     resources={"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}},
        ...     emails=['email1@saagie.io'],
        ...     status_list=["FAILED", "QUEUED"]
        ... )
        {
            "editJob": {
                "id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
                "name": "newname",
                "alias": "newname",
                "description": "new desc",
                "isScheduled": True,
                "cronScheduling": "0 * * * *",
                "scheduleTimezone": "Europe/Paris",
                "resources": {
                    "cpu": {
                        "request": 1.5,
                        "limit": 2.2
                    },
                    "memory": {
                        "request": 2.0,
                        "limit": None
                    }
                },
                "alerting": {
                    "emails": [
                        "email1@saagie.io"
                    ],
                    "statusList": [
                        "FAILED",
                        "QUEUED"
                    ]
                }
            }
        }
        """
        previous_job_version = self.get_info(job_id, pprint_result=False)["job"]
        if not previous_job_version:
            raise RuntimeError(f"❌ The job {job_id} you're trying to edit does not exist")

        params = {
            "jobId": job_id,
            "name": job_name or previous_job_version["name"],
            "description": description or previous_job_version["description"],
            "resources": resources or previous_job_version["resources"],
        }

        if is_scheduled:
            params.update(self.saagie_api.check_scheduling(cron_scheduling, schedule_timezone))
        elif is_scheduled == False:
            params["isScheduled"] = False
        else:
            params["isScheduled"] = previous_job_version["isScheduled"]
            params["cronScheduling"] = previous_job_version["cronScheduling"]
            params["scheduleTimezone"] = previous_job_version["scheduleTimezone"]

        if emails:
            params.update(self.saagie_api.check_alerting(emails, status_list))
        elif isinstance(emails, List):
            params["alerting"] = None
        elif previous_alerting := previous_job_version["alerting"]:
            params["alerting"] = {
                "emails": previous_alerting["emails"],
                "statusList": previous_alerting["statusList"],
            }

        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_JOB), variable_values=params)
        logging.info("✅ Job [%s] successfully edited", job_id)
        return result

    def upgrade(
        self,
        job_id: str,
        file: str = None,
        use_previous_artifact: bool = True,
        runtime_version: str = None,
        command_line: str = None,
        release_note: str = "",
        extra_technology: str = None,
        extra_technology_version: str = None,
        source_url: str = "",
        docker_info: dict = None,
    ) -> Dict:
        """Upgrade a job

        Parameters
        ----------
        job_id : str
            UUID of your job
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        runtime_version: str (optional)
            Runtime version, the ID of the context
            Example: "3.10"
        command_line: str (optional)
            Command line used to run the job
            Example: "python3 {file} arg1 arg2"
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            None or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to None when not needed
        source_url: str (optional)
            URL of the source code used for the job (link to the commit for example)
        docker_info: dict (optional)
            Docker information for the job
            Example: {"image": "my_image", "dockerCredentialsId": "MY_CREDENTIALS_ID"}

        Returns
        -------
        dict
            Dict with version number

        Examples
        --------
        >>> saagieapi.jobs.upgrade(
        ...     job_id="60f46dce-c869-40c3-a2e5-1d7765a806db",
        ...     use_previous_artifact=True,
        ...     runtime_version='3.8',
        ...     command_line='python {file} new_arg',
        ...     release_note="Second version"
        ... )
        {
            "data":{
                "addJobVersion":{
                    "number":2,
                    "__typename":"JobVersion"
                }
            }
        }
        """

        # Get the job's current informations
        job_info = self.get_info(job_id, instances_limit=1, versions_only_current=True, pprint_result=False)["job"]

        # Verify if specified runtime exists
        technology_id = job_info["technology"]["id"]
        available_runtimes = [
            tech["id"]
            for tech in self.saagie_api.get_runtimes(technology_id)["technology"]["contexts"]
            if tech["available"] is True
        ]
        if runtime_version is not None and runtime_version not in available_runtimes:
            raise RuntimeError(
                f"❌ Specified runtime does not exist ({runtime_version}). "
                f"Available runtimes : {','.join(available_runtimes)}."
            )

        if file and use_previous_artifact:
            logging.warning(
                "You can not specify a file and use the previous artifact. "
                "By default, the specified file will be used."
            )

        # Create the params dict with new values when specified or old values otherwise
        params = {
            "jobId": job_id,
            "releaseNote": release_note,
            "runtimeVersion": runtime_version or job_info["versions"][0]["runtimeVersion"],
            "commandLine": command_line or job_info["versions"][0]["commandLine"],
            "usePreviousArtifact": bool(use_previous_artifact and job_info["versions"][0]["packageInfo"]),
            "dockerInfo": docker_info or job_info["versions"][0]["dockerInfo"],
        }

        # Add extra technology parameter if needed
        if extra_technology is not None:
            params["extraTechnology"] = {"language": extra_technology, "version": extra_technology_version}

        if source_url:
            params["sourceUrl"] = source_url

        result = self.__launch_request(file, GQL_UPGRADE_JOB, params)
        logging.info("✅ Job [%s] successfully upgraded", job_id)
        return result

    def upgrade_by_name(
        self,
        job_name: str,
        project_name: str,
        file=None,
        use_previous_artifact: bool = True,
        runtime_version: str = None,
        command_line: str = None,
        release_note: str = None,
        extra_technology: str = None,
        extra_technology_version: str = None,
        source_url: str = "",
    ) -> Dict:
        """Upgrade a job

        Parameters
        ----------
        job_name : str
            Name of your job
        project_name : str
            Name of your project
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        runtime_version: str (optional)
            Runtime version
        command_line: str (optional)
            Command line
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to None or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to None when not needed
        source_url: str (optional)
            URL of the source code used for the job (link to the commit for example)

        Returns
        -------
        dict
            Dict with version number

        Examples
        --------
        >>> saagieapi.jobs.upgrade_by_name(
        ...     job_name="my job",
        ...     project_name="My project",
        ...     use_previous_artifact=True,
        ...     runtime_version='3.8',
        ...     command_line='python {file} new_arg',
        ...     release_note="Second version"
        ... )
        {
            "data":{
                "addJobVersion":{
                    "number":3,
                    "__typename":"JobVersion"
                }
            }
        }
        """
        return self.upgrade(
            job_id=self.get_id(job_name, project_name),
            file=file,
            use_previous_artifact=use_previous_artifact,
            runtime_version=runtime_version,
            command_line=command_line,
            release_note=release_note,
            extra_technology=extra_technology,
            extra_technology_version=extra_technology_version,
            source_url=source_url,
        )

    def create_or_upgrade(
        self,
        job_name: str,
        project_id: str,
        file: str = None,
        use_previous_artifact: bool = True,
        description: str = None,
        category: str = None,
        technology: str = None,
        technology_catalog: str = None,
        runtime_version: str = None,
        command_line: str = None,
        release_note: str = None,
        extra_technology: str = None,
        extra_technology_version: str = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        resources: Dict = None,
        emails: List = None,
        status_list: List = None,
        source_url: str = "",
        docker_info: dict = None,
    ) -> Dict:
        """Create or upgrade a job

        Parameters
        ----------
        job_name : str
            Name of your job
        project_id : str
            UUID of your project
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        description: str (optional)
            Description of your job
        category: str (optional)
            Category of your job
        technology: str (optional)
            Technology of your job
        technology_catalog: str (optional)
            Technology catalog of your job
        runtime_version: str (optional)
            Runtime version
        command_line: str (optional)
            Command line
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            None or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to None when not needed
        is_scheduled: bool (optional)
            True if the job is scheduled, False to deactivate scheduling
        cron_scheduling: str (optional)
            Cron scheduling
        schedule_timezone: str (optional)
            Schedule timezone
        resources: dict (optional)
            Resources
        emails: list (optional)
            Emails
        status_list: list (optional)
            Status list
        source_url: str (optional)
            URL of the source code used for the job (link to the commit for example)
        docker_info: dict (optional)
            Docker information for the job
            Example: {"image": "my_image", "dockerCredentialsId": "MY_CREDENTIALS_ID"}

        Returns
        -------
        dict
            Either the same dict as create_job, or the one returned by
            concatenation of upgrade_job and edit_job

        Examples
        --------
        >>> saagieapi.jobs.create_or_upgrade(
        ...     job_name="my job",
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
        ...     file="/tmp/test.py",
        ...     use_previous_artifact=False,
        ...     description='My description',
        ...     category='Extraction',
        ...     technology='python',# technology id corresponding to your context.id in your technology catalog definition
        ...     technology_catalog='Saagie',
        ...     runtime_version='3.9',
        ...     command_line='python {file}',
        ...     release_note='First release',
        ...     extra_technology='',
        ...     extra_technology_version='',
        ...     cron_scheduling='0 0 * * *',
        ...     schedule_timezone='Europe/Paris',
        ...     resources={"cpu": {"request": 0.5, "limit": 2.6}, "memory": {"request": 1.0}},
        ...     emails=['email1@saagie.io', 'email2@saagie.io'],
        ...     status_list=["FAILED", "KILLED"],
        ...     source_url="",
        ...     docker_info=None
        ... )
        {
            "data":{
                "createJob":{
                    "id":"60f46dce-c869-40c3-a2e5-1d7765a806db",
                    "versions":[
                        {
                            "number":1,
                            "__typename":"JobVersion"
                        }
                    ],
                    "__typename":"Job"
                }
            }
        }
        """  # pylint: disable=line-too-long

        job_list = self.list_for_project_minimal(project_id)["jobs"]

        # If the job already exists, upgrade it
        if job_name in [job["name"] for job in job_list]:
            job_id = next(job["id"] for job in job_list if job["name"] == job_name)

            responses = {
                "addJobVersion": self.upgrade(
                    job_id=job_id,
                    file=file,
                    use_previous_artifact=use_previous_artifact,
                    runtime_version=runtime_version,
                    command_line=command_line,
                    release_note=release_note,
                    extra_technology=extra_technology,
                    extra_technology_version=extra_technology_version,
                    source_url=source_url,
                    docker_info=docker_info,
                )["data"]["addJobVersion"]
            }

            responses["editJob"] = self.edit(
                job_id=job_id,
                job_name=job_name,
                description=description,
                is_scheduled=is_scheduled,
                cron_scheduling=cron_scheduling,
                schedule_timezone=schedule_timezone,
                resources=resources,
                emails=emails,
                status_list=status_list,
            )["editJob"]

            return responses

        # If the job does not exist, create it
        args = {
            k: v
            for k, v in {
                "job_name": job_name,
                "project_id": project_id,
                "file": file,
                "description": description,
                "category": category,
                "technology": technology,
                "technology_catalog": technology_catalog,
                "runtime_version": runtime_version,
                "command_line": command_line,
                "release_note": release_note,
                "extra_technology": extra_technology,
                "extra_technology_version": extra_technology_version,
                "cron_scheduling": cron_scheduling,
                "schedule_timezone": schedule_timezone,
                "resources": resources,
                "emails": emails,
                "status_list": status_list,
                "source_url": source_url,
                "docker_info": docker_info,
            }.items()
            if v is not None  # Remove None values from the dict
        }

        return self.create(**args)

    def rollback(self, job_id: str, version_number: str):
        """Rollback a given job to the given version

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        version_number : str
            Number of the version to rollback

        Returns
        -------
        dict
            Dict of rollback job

        Examples
        --------
        >>> saagie_api.jobs.rollback(
        ...     job_id="58870149-5f1c-45e9-93dc-04b2b30a732c",
        ...     version_number=3
        ... )
        {
            "rollbackJobVersion": {
                "id": "58870149-5f1c-45e9-93dc-04b2b30a732c",
                "versions": [
                    {
                        "number": 4,
                        "isCurrent": False
                    },
                    {
                        "number": 3,
                        "isCurrent": True
                    },
                    {
                        "number": 2,
                        "isCurrent": False
                    },
                    {
                        "number": 1,
                        "isCurrent": False
                    }
                ]
            }
        }
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_ROLLBACK_JOB_VERSION), variable_values={"jobId": job_id, "versionNumber": version_number}
        )
        logging.info("✅ Job [%s] successfully rollbacked to version [%s]", job_id, version_number)
        return result

    def delete(self, job_id: str) -> Dict:
        """Delete a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted job

        Examples
        --------
        >>> saagieapi.jobs.delete(job_id="f5fce22d-2152-4a01-8c6a-4c2eb4808b6d")
        {
            "deleteJob": True
        }
        """

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB), variable_values={"jobId": job_id})
        logging.info("✅ Job [%s] successfully deleted", job_id)
        return result

    def run(self, job_id: str) -> Dict:
        """Run a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of the given job information

        Examples
        --------
        >>> saagieapi.jobs.run(job_id="f5fce22d-2152-4a01-8c6a-4c2eb4808b6d")
        {
            "runJob":{
                "id":"5b9fc971-1c4e-4e45-a978-5851caef0162",
                "status":"REQUESTED"
            }
        }
        """

        result = self.saagie_api.client.execute(query=gql(GQL_RUN_JOB), variable_values={"jobId": job_id})
        logging.info("✅ Job [%s] successfully launched", job_id)
        return result

    def run_with_callback(self, job_id: str, freq: int = 10, timeout: int = -1) -> Dict:
        """Run a job and wait for the final status (KILLED, FAILED, UNKNOWN or SUCCESS).
        Regularly check (default to 10s) the job's status.

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        freq : int, optional
            Seconds to wait between two state checks
        timeout : int, optional
            Seconds before timeout for a status check call

        Returns
        -------
        (str, str)
            (Final state of the job, job instance id)

        Raises
        ------
        TimeoutError
            When the status check is not responding

        Examples
        --------
        >>> saagieapi.jobs.run_with_callback(
        ...        job_id="f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
        ...        freq=5,
        ...        timeout=60
        ... )
        ("SUCCEEDED", "5b9fc971-1c4e-4e45-a978-5851caef0162")
        """
        res = self.run(job_id)
        job_instance_id = res.get("runJob").get("id")
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED", "UNKNOWN"]
        job_instance_info = self.get_instance(job_instance_id, pprint_result=False)
        state = job_instance_info.get("jobInstance").get("status")
        sec = 0
        if timeout == -1:
            timeout = float("inf")

        logging.info("⏳ Job id %s with instance %s has just been requested", job_id, job_instance_id)
        while state not in final_status_list:
            with console.status(f"Job is currently {state}", refresh_per_second=100):
                if sec >= timeout:
                    raise TimeoutError(f"❌ Last state known : {state}")
                time.sleep(freq)
                sec += freq
                job_instance_info = self.get_instance(job_instance_id, pprint_result=False)
                state = job_instance_info.get("jobInstance").get("status")
        if state == "SUCCEEDED":
            logging.info("✅ Job id %s with instance %s has the status %s", job_id, job_instance_id, state)
        elif state in ("FAILED", "KILLED", "UNKNOWN"):
            logging.error("❌ Job id %s with instance %s has the status %s", job_id, job_instance_id, state)
        return (state, job_instance_id)

    def stop(self, job_instance_id: str) -> Dict:
        """Stop a given job instance

        Parameters
        ----------
        job_instance_id : str
            UUID of your job instance (see README on how to find it)

        Returns
        -------
        dict
            Job instance information

        Examples
        --------
        >>> saagieapi.jobs.stop(job_instance_id="8e9b9f16-4a5d-4188-a967-1a96b88e4358")
        {
            "stopJobInstance":{
                "id":"8e9b9f16-4a5d-4188-a967-1a96b88e4358",
                "number":17,
                "status":"KILLING",
                "history": {
                    "currentStatus": {
                        "status": "SUCCEEDED",
                        "details": None,
                        "reason": None
                    }
                },
                "startTime":"2022-04-29T08:38:49.344Z",
                "endTime":None,
                "jobId":"e92ed472-50d6-4041-bba9-098a8e16f444"
            }
        }
        """

        result = self.saagie_api.client.execute(
            query=gql(GQL_STOP_JOB_INSTANCE), variable_values={"jobInstanceId": job_instance_id}
        )
        logging.info("✅ Job instance [%s] successfully stopped", job_instance_id)
        return result

    def __launch_request(self, file: str, payload_str: str, params: Dict) -> Dict:
        """Launch a GQL request with specified file, payload and params
        GQL3 needed to use this function
        Parameters
        ----------
        file : str
            Path to your file
        payload_str : str
            Payload to send
        params: dict
            variable values to pass to the GQL request
        Returns
        -------
        dict
            Dict of the request response
        """
        if file:
            file_info = Path(file)
            os.chdir(file_info.parent)
            file = Path(file_info.name)
            with file.open(mode="rb") as file_content:
                params["file"] = file_content
                try:
                    req = self.saagie_api.client.execute(
                        query=gql(payload_str), variable_values=params, upload_files=True
                    )
                    res = {"data": req}
                except Exception as exception:
                    logging.error("Something went wrong %s", exception)
                    raise exception
                return res
        else:
            try:
                return {"data": self.saagie_api.client.execute(query=gql(payload_str), variable_values=params)}
            except Exception as exception:
                logging.error("Something went wrong %s", exception)
                raise exception

    def export(
        self,
        job_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
    ) -> bool:
        """Export the job in a folder

        Parameters
        ----------
        job_id : str
            Job ID
        output_folder : str
            Path to store the exported job
        error_folder : str, optional
            Path to store the job ID in case of error. If not set, job ID is not write
        versions_limit : int, optional
            Maximum limit of versions to fetch per job. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job

        Returns
        -------
        bool
            True if job is exported False otherwise

        Examples
        --------
        >>> saagieapi.jobs.export(
        ...    job_id="f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
        ...    output_folder="./output/job/",
        ...    error_folder="./output/error/",
        ...    versions_only_current=True
        ... )
        True
        """
        job_info = None
        output_folder = Path(output_folder)

        try:
            job_info = self.get_info(
                job_id=job_id,
                instances_limit=1,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )["job"]
        except Exception as exception:
            logging.error("Something went wrong %s", exception)
            return handle_write_error("Cannot get the information of the job [%s]", job_id, error_folder)

        if not job_info:
            return handle_write_error("Cannot get the information of the job [%s]", job_id, error_folder)

        create_folder(output_folder / job_id)
        repo_name, techno_name = self.saagie_api.get_technology_name_by_id(job_info["technology"]["id"])

        if not repo_name:
            return handle_write_error(
                "Cannot export the job: [%s] because the technology used for this job was deleted",
                job_id,
                error_folder,
            )
        job_info["technology"]["name"] = techno_name
        job_info["technology"]["technology_catalog"] = repo_name
        write_to_json_file(output_folder / job_id / "job.json", job_info)

        for version in [version for version in job_info.get("versions", []) if version["packageInfo"]]:
            local_folder = output_folder / job_id / "version" / str(version["number"])
            create_folder(local_folder)
            req = requests.get(
                f'{remove_slash_folder_path(self.saagie_api.url_saagie)}{version["packageInfo"]["downloadUrl"]}',
                auth=self.saagie_api.auth,
                stream=True,
                timeout=60,
            )
            if req.status_code == 200:
                logging.info("Downloading the version %s of the job", version["number"])
                write_request_response_to_file(local_folder / version["packageInfo"]["name"], req)
            else:
                handle_write_error(
                    f"❌ Cannot download the version [{version['number']}] of the job [%s], \
                        please verify if everything is ok",
                    job_id,
                    error_folder,
                )

        logging.info("✅ Job [%s] successfully exported", job_id)
        return True

    def import_from_json(
        self,
        project_id: str,
        path_to_folder: str,
    ) -> bool:
        """Import a job from JSON format

        Parameters
        ----------
        project_id : str
            Project ID to import the job
        path_to_folder : str
            Path to the folder of the job to import

        Returns
        -------
        bool
            True if job is imported False otherwise

        Examples
        --------
        >>> saagieapi.jobs.import_from_json(
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
        ...     path_to_package="/path/to/the/package/of/the/job"
        ... )
        True
        """
        json_file = next(Path(path_to_folder).rglob("job.json"))

        try:
            with json_file.open("r", encoding="utf-8") as file:
                job_info = json.load(file)
        except Exception as exception:
            return handle_log_error(f"Cannot open the JSON file {json_file}", exception)
        try:
            job_name = job_info["name"]

            version = next(version for version in job_info["versions"] if version["isCurrent"])
            version_path = json_file.parent / "version" / str(version["number"])

            if version_path.exists():
                if path_to_package := next(version_path.iterdir(), None):
                    os.chdir(path_to_package.parent)
                    file_name = path_to_package.name
            else:
                file_name = ""

            self.create(
                job_name=job_name,
                project_id=project_id,
                file=file_name,
                description=job_info["description"],
                category=job_info["category"],
                technology=job_info["technology"]["name"],
                technology_catalog=job_info["technology"]["technology_catalog"],
                runtime_version=version["runtimeVersion"],
                command_line=version["commandLine"],
                release_note=version["releaseNote"],
                extra_technology=(version.get("extraTechnology") or {}).get("language", ""),
                extra_technology_version=(version.get("extraTechnology") or {}).get("version", ""),
                cron_scheduling=job_info["cronScheduling"],
                schedule_timezone=job_info["scheduleTimezone"],
                resources=job_info["resources"],
                emails=(job_info.get("alerting") or {}).get("emails", ""),
                status_list=(job_info.get("alerting") or {}).get("statusList", ""),
            )

            logging.info("✅ Job [%s] successfully imported", job_name)
        except Exception as exception:
            return handle_log_error(
                f"❌ Job [in the following file: {json_file}] has not been successfully imported",
                exception,
            )
        return True

    def delete_instances(self, job_id, job_instances_id):
        """Delete given job's instances
        NB: You can only delete an instance not associated to a pipeline instance
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        job_instances_id : [str]
            List of UUID of instances to delete (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted instances

        Examples
        --------
        >>> saagie_api.jobs.delete_instances(
        ...     job_id=job_id,
        ...     job_instances_id=["c8f156bc-78ab-4dda-acff-bbe828237fd9", "7e5549cd-32aa-42c4-88b5-ddf5f3087502"]
        ... )
        {
            'deleteJobInstances': [
                {'id': '7e5549cd-32aa-42c4-88b5-ddf5f3087502', 'success': True},
                {'id': 'c8f156bc-78ab-4dda-acff-bbe828237fd9', 'success': True}
            ]
        }
        """
        params = {"jobId": job_id, "jobInstancesId": job_instances_id}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB_INSTANCE), variable_values=params)
        logging.info("✅ Instances of job [%s] successfully deleted", job_id)
        return result

    def delete_instances_by_selector(
        self, job_id, selector, exclude_instances_id: List = None, include_instances_id: List = None
    ):
        """Delete given job's instances by selector
        NB: You can only delete an instance not associated to a pipeline instance.
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        selector : str
            Name of status to select in this list : ALL, SUCCEEDED, FAILED, STOPPED, UNKNOWN
        exclude_instances_id : [str]
            List of UUID of instances of your job to exclude from the deletion
        include_instances_id: [str]
            List of UUID of instances of your job to include from the deletion

        Returns
        -------
        Dict
            Return the number of instances deleted

        Examples
        --------
        >>> saagie_api.jobs.delete_instances_by_selector(
        ...     job_id=job_id,
        ...     selector="FAILED",
        ...     exclude_instances_id=["478d48d4-1609-4bf0-883d-097d43709aa8"],
        ...     include_instances_id=["47d3df2c-5a38-4a5e-a49e-5405ad8f1699"]
        ... )
        {
            'deleteJobInstancesBySelector': 1
        }
        """
        params = {
            "jobId": job_id,
            "selector": selector,
            "excludeJobInstanceId": exclude_instances_id or [],
            "includeJobInstanceId": include_instances_id or [],
        }
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB_INSTANCES_BY_SELECTOR), variable_values=params)
        logging.info("✅ Instances of job [%s] successfully deleted", job_id)
        return result

    def delete_instances_by_date(
        self, job_id: str, date_before: str, exclude_instances_id: List = None, include_instances_id: List = None
    ):
        """Delete given job's instances by date
        NB: You can only delete an instance not associated to a pipeline instance.
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        date_before : str
            Instances before this date will be deleted. The date must be in this format : '%Y-%m-%dT%H:%M:%S%z'
        exclude_instances_id : [str]
            List of UUID of instances of your job to exclude from the deletion
        include_instances_id: [str]
            List of UUID of instances of your job to include from the deletion

        Returns
        -------
        Dict
            Return the number of instances deleted

        Examples
        --------
        >>> saagie_api.jobs.delete_instances_by_date(
        ...     job_id=job_id,
        ...     date_before="2023-06-01T00:00:00+01:00",
        ...     exclude_instances_id=["478d48d4-1609-4bf0-883d-097d43709aa8"],
        ...     include_instances_id=["47d3df2c-5a38-4a5e-a49e-5405ad8f1699"]
        ... )
        {
            'deleteJobInstancesByDate': 1
        }
        """
        # need to check the date is in this format : 2023-02-01T00:00:00+01:00
        # if not, it will raise an error and stop the call
        try:
            datetime.strptime(date_before, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError as exception:
            raise ValueError(
                "The date must be in this format : '%Y-%m-%dT%H:%M:%S%z'. \
                Please change your date_before parameter"
            ) from exception

        params = {
            "jobId": job_id,
            "beforeAt": date_before,
            "excludeJobInstanceId": exclude_instances_id or [],
            "includeJobInstanceId": include_instances_id or [],
        }
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB_INSTANCES_BY_DATE), variable_values=params)
        logging.info("✅ Instances of job [%s] successfully deleted", job_id)
        return result

    def delete_versions(self, job_id, versions):
        """Delete given job's versions
        NB: You can only delete a version not associated to a pipeline instance

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        versions : [str]
            List of version numbers to delete

        Returns
        -------
        dict
            Dict of deleted versions with their number and success status

        Examples
        --------
        >>> saagie_api.jobs.delete_versions(
        ...     job_id=job_id,
        ...     versions=["1"]
        ... )
        {
            'deleteJobVersions': [
                {'number': 1, 'success': True}
            ]
        }
        """
        params = {"jobId": job_id, "jobVersionsNumber": versions}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB_VERSION), variable_values=params)
        logging.info("✅ Versions of job [%s] successfully deleted", job_id)
        return result

    def duplicate(self, job_id):
        """Duplicate a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of duplicate job with its id and name

        Examples
        --------
        >>> saagie_api.jobs.duplicate(job_id=job_id)
        {
            'duplicateJob': {
                'id': '29cf1b80-6b9c-47bc-a06c-c20897257097',
                'name': 'Copy of my_job 2'
            }
        }
        """
        result = self.saagie_api.client.execute(query=gql(GQL_DUPLICATE_JOB), variable_values={"jobId": job_id})
        logging.info("✅ Job [%s] successfully duplicated", job_id)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`count_deletable_instances_by_status()` instead.",
        deprecated_in="2.9.0",
    )
    def count_instances_by_status(self, job_id):
        """Count deletable job instances by status

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of number of job instances by status

        Examples
        --------
        >>> saagie_api.jobs.count_instances_by_status(job_id=job_id)
        {
            'countJobInstancesBySelector': [
                {'selector': 'ALL', 'count': 0},
                {'selector': 'SUCCEEDED', 'count': 0},
                {'selector': 'FAILED', 'count': 0},
                {'selector': 'STOPPED', 'count': 0},
                {'selector': 'UNKNOWN', 'count': 0}
            ]
        }
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_COUNT_INSTANCES_BY_SELECTOR), variable_values={"jobId": job_id}
        )

    def count_deletable_instances_by_status(self, job_id):
        """Count deletable job instances by status

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of number of job instances by status

        Examples
        --------
        >>> saagie_api.jobs.count_deletable_instances_by_status(job_id=job_id)
        {
            'countJobInstancesBySelector': [
                {'selector': 'ALL', 'count': 0},
                {'selector': 'SUCCEEDED', 'count': 0},
                {'selector': 'FAILED', 'count': 0},
                {'selector': 'STOPPED', 'count': 0},
                {'selector': 'UNKNOWN', 'count': 0}
            ]
        }
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_COUNT_INSTANCES_BY_SELECTOR), variable_values={"jobId": job_id}
        )

    def count_deletable_instances_by_date(self, job_id: str, date_before: str):
        """Count deletable job instances by date

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        date_before : str
            Instances before this date will be counted. The date must be in this format : '%Y-%m-%dT%H:%M:%S%z'

        Returns
        -------
        dict
            Dict of number of job instances before the given date

        Examples
        --------
        >>> saagie_api.jobs.count_deletable_instances_by_date(job_id=job_id, date_before="2023-06-01T00:00:00+01:00")
        {
            'countJobInstancesByDate': 3
        }
        """
        # need to check the date is in this format : 2023-02-01T00:00:00+01:00
        # if not, it will raise an error and stop the call
        try:
            datetime.strptime(date_before, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError as exception:
            raise ValueError(
                "The date must be in this format : '%Y-%m-%dT%H:%M:%S%z'. \
                Please change your date_before parameter"
            ) from exception

        return self.saagie_api.client.execute(
            query=gql(GQL_COUNT_INSTANCES_BY_DATE), variable_values={"jobId": job_id, "beforeAt": date_before}
        )

    def move_job(self, job_id: str, target_platform_id: int, target_project_id: str):
        """Move a job to another project in the same platform or another one

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        target_platform_id : int
            Id of the platform to move the job to
        target_project_id : str
            UUID of the project to move the job to

        Returns
        -------
        dict
            Dict of the moved job with its new id

        Examples
        --------
        >>> saagie_api.jobs.move_job(job_id=job_id, target_platform_id=1, target_project_id=project_id)
        {
            'moveJob': '29cf1b80-6b9c-47bc-a06c-c20897257097',
        }
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_MOVE_JOB),
            variable_values={
                "jobId": job_id,
                "targetPlatformId": target_platform_id,
                "targetProjectId": target_project_id,
            },
        )

    def generate_description_by_ai(self, job_id: str):
        """Generate a description for a job using AI.
        Be careful, by calling this function the code contained in the job package will be sent to OpenAI
        and thus will not be secured anymore by Saagie DataOps Platform.
        Otherwise, the function returns an error if the description is already the one generated by AI.

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of the generated description

        Examples
        --------
        >>> saagie_api.jobs.generate_description_by_ai(job_id=job_id)
        {
            'editJobWithAiGeneratedDescription': {
                'id': 'bfa25e4a-1796-4ebb-8c3d-138f74146973',
                'description': 'The purpose of this code is to display the message "Hello World" on the screen.',
                'aiDescriptionVersionNumber': 1
            }
        }
        """
        # if executed a second time and the description is already the one generated by AI,
        # it will return an error and I don't know how to handle it
        # example : TransportQueryError: {'message': 'Job not valid', 'path': ['editJobWithAiGeneratedDescription'],
        # 'extensions': {'job.description': 'Job description is already generated', 'classification':'ValidationError'}}

        return self.saagie_api.client.execute(
            query=gql(GQL_GENERATE_JOB_DESCRIPTION), variable_values={"jobId": job_id}
        )
