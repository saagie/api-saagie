import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from gql import gql

from ..utils.folder_functions import create_folder, write_error, write_to_json_file
from ..utils.rich_console import console
from .gql_queries import *
from .graph_pipeline import GraphPipeline


def handle_error(msg, pipeline_name):
    logging.error("❌ Something went wrong %s", msg)
    logging.warning("❌ Pipeline [%s] has not been successfully imported", pipeline_name)
    return False


def parse_version_conditions(version):
    conditions_found = []
    for condition_node in version["graph"]["conditionNodes"]:
        condition_dict = {
            "id": condition_node["id"],
            "nextNodesSuccess": condition_node["nextNodesSuccess"],
            "nextNodesFailure": condition_node["nextNodesFailure"],
        }
        if "ConditionStatus" in condition_node["condition"]["toString"]:
            # example : ConditionStatus(value=AtLeastOneSuccess)
            condition_dict["condition"] = {
                "status": {"value": condition_node["condition"]["toString"].split("=")[1].split(")")[0]}
            }

        if "ConditionExpression" in condition_node["condition"]["toString"]:
            # example : ConditionExpression(expression=\"1 + 1 == 2\")
            condition_dict["condition"] = {
                "custom": {"expression": condition_node["condition"]["toString"].split('="')[1].split('")')[0]}
            }

        conditions_found.append(condition_dict)
    return conditions_found


def parse_version_jobs(jobs_target_pj, version):
    jobs_not_found = []
    jobs_found = []
    for job_node in version["graph"]["jobNodes"]:
        if job := next((job for job in jobs_target_pj if job["name"] == job_node["job"]["name"]), None):
            node_dict = {
                "id": job_node["id"],
                "job": {"id": job["id"]},
                "nextNodes": job_node["nextNodes"],
            }
            jobs_found.append(node_dict)
        else:
            jobs_not_found.append(job_node["job"]["name"])
    return jobs_not_found, jobs_found


class Pipelines:
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
        """List pipelines of project with their instances.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per pipelines. Fetch from most
            recent to oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        Dict
            Dict of pipelines information

        Examples
        --------
        >>> saagieapi.pipelines.list_for_project(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771")
        {
            "project": {
                "pipelines": [
                    {
                        "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                        "name": "Pipeline A",
                        "description": "My Pipeline A",
                        "alerting": None,
                        "pipelineInstanceCount": 0,
                        "instances": [],
                        "versions": [
                            {
                                "number": 1,
                                "releaseNote": None,
                                "graph": {
                                    "jobNodes": [
                                        {
                                            "id": "00000000-0000-0000-0000-000000000000",
                                            "job": {
                                                "id": "6f56e714-37e4-4596-ae20-7016a1d954e9",
                                                "name": "Spark 2.4 java"
                                            },
                                            "position": None,
                                            "nextNodes": ["00000000-0000-0000-0000-000000000001"]
                                        },
                                        {
                                            "id": "00000000-0000-0000-0000-000000000001",
                                            "job": {
                                                "id": "6ea1b022-db8b-4af7-885b-56ddc9ba764a",
                                                "name": "bash"
                                            },
                                            "position": None,
                                            "nextNodes": []
                                        }
                                    ],
                                    "conditionNodes": []
                                },
                                "creationDate": "2022-01-31T10:36:42.327Z",
                                "creator": "john.doe",
                                "isCurrent": True,
                                "isMajor": False
                            }
                        ],
                        "creationDate": "2022-01-31T10:36:42.327Z",
                        "creator": "john.doe",
                        "isScheduled": False,
                        "cronScheduling": None,
                        "scheduleStatus": None,
                        "scheduleTimezone": "UTC",
                        "isLegacyPipeline": False
                    },
                    {
                        "id": "9a2642df-550c-4c69-814f-1008f177b0e1",
                        "name": "Pipeline B",
                        "description": None,
                        "alerting": None,
                        "pipelineInstanceCount": 2,
                        "instances": [
                            {
                                "id": "cc11c32a-66c5-43ad-b176-444cee7079ff",
                                "status": "SUCCEEDED",
                                "startTime": "2022-03-15T11:42:07.559Z",
                                "endTime": "2022-03-15T11:43:17.716Z",
                                "runWithExecutionVariables": True,
                                "initialExecutionVariables": [
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
                                "jobsInstance": [
                                    {
                                        "id": "f8e77fc3-9c4d-450b-8efd-9d3080b38edb",
                                        "jobId": "9a71afa4-aed4-4061-87d2-b279a3adf8c3",
                                        "number": 80,
                                        "startTime": "2022-03-15T11:42:07.559Z",
                                        "endTime": "2022-03-15T11:43:17.716Z"
                                    }
                                ],
                                "conditionsInstance": [
                                    {
                                        "id": "2292a535-affb-4b1c-973d-690c185d949e",
                                        "conditionNodeId": "c2f23720-e361-11ed-894d-6b696861cc8f",
                                        "isSuccess": true,
                                        "startTime": "2022-03-15T11:42:30.559Z",
                                        "endTime": "2022-03-15T11:42:45.559Z"
                                    }
                                ],
                            },
                            {
                                "id": "d7aba110-3bd9-4505-b70c-84c4d212345",
                                "status": "SUCCEEDED",
                                "startTime": "2022-02-04T00:00:00.062Z",
                                "endTime": "2022-02-04T00:00:27.249Z",
                                "runWithExecutionVariables": False,
                                "initialExecutionVariables": [],
                                "jobsInstance": [],
                                "conditionsInstance": [],
                            }
                        ],
                        "versions": [
                            {
                                "number": 1,
                                "releaseNote": None,
                                "graph": {
                                    "jobNodes": [
                                        {
                                            "id": "00000000-0000-0000-0000-000000000002",
                                            "job": {
                                                "id": "6f56e714-37e4-4596-ae20-7016a1d459e9",
                                                "name": "Job test 1"
                                            },
                                            "position": None,
                                            "nextNodes": ["00000000-0000-0000-0000-000000000001"]
                                        },
                                        {
                                            "id": "00000000-0000-0000-0000-000000000003",
                                            "job": {
                                                "id": "6ea1b022-db8b-4af7-885b-56ddc9ba647a",
                                                "name": "Job test 2"
                                            },
                                            "position": None,
                                            "nextNodes": []
                                        }
                                    ],
                                    "conditionNodes": [
                                        {
                                            "id": "00000000-0000-0000-0000-000000000001",
                                            "position": {
                                                "x": 310.00092,
                                                "y": 75
                                            },
                                            "nextNodesSuccess": [
                                                "00000000-0000-0000-0000-000000000003"
                                            ],
                                            "nextNodesFailure": [],
                                            "condition": {
                                                "toString": "ConditionExpression(expression=\"tube_name.contains(\"Tube\") || double(diameter) > 1.0\")"
                                            }
                                        }
                                    ],
                                },
                                "creationDate": "2022-02-03T14:41:39.422Z",
                                "creator": "john.doe",
                                "isCurrent": True,
                                "isMajor": False
                            }
                        ],
                        "creationDate": "2022-02-03T14:41:39.422Z",
                        "creator": "john.doe",
                        "isScheduled": False,
                        "cronScheduling": None,
                        "scheduleStatus": None,
                        "scheduleTimezone": "UTC",
                        "isLegacyPipeline": False
                    }
                ]
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "projectId": project_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_PIPELINES_FOR_PROJECT), variable_values=params, pprint_result=pprint_result
        )

    def list_for_project_minimal(self, project_id: str) -> Dict:
        """List pipelines ids and names of project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        Dict
            Dict of pipelines ids and names

        Examples
        --------
        >>> saagieapi.pipelines.list_for_project_minimal(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771")
        {
            "project": {
                "pipelines": [
                    {
                        "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                        "name": "Pipeline A"
                    },
                    {
                        "id": "9a2642df-550c-4c69-814f-1008f177b0e1",
                        "name": "Pipeline B"
                    }
                ]
            }
        }
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL), variable_values={"projectId": project_id}
        )

    def get_id(self, pipeline_name: str, project_name: str) -> str:
        """Get the pipeline id with the pipeline name and project name

        Parameters
        ----------
        pipeline_name : str
            Name of your pipeline
        project_name : str
            Name of your project

        Returns
        -------
        str
            Pipeline UUID

        Examples
        --------
        >>> saagieapi.pipelines.get_id(
        ...     project_name="Project A",
        ...     pipeline_name="Pipeline A"
        ... )
        "5d1999f5-fa70-47d9-9f41-55ad48333629"
        """
        project_id = self.saagie_api.projects.get_id(project_name)
        pipelines = self.list_for_project(project_id, instances_limit=1)["project"]["pipelines"]
        if pipeline := list(filter(lambda j: j["name"] == pipeline_name, pipelines)):
            return pipeline[0]["id"]
        raise NameError(f"❌ pipeline {pipeline_name} does not exist.")

    def get_info(
        self,
        pipeline_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get a given pipeline information

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to the oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of pipeline's information

        Examples
        --------
        >>> saagieapi.pipelines.get_info(pipeline_id="5d1999f5-fa70-47d9-9f41-55ad48333629")
        {
            "graphPipeline": {
                "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                "name": "Pipeline A",
                "alias": "Pipeline_A",
                "description": "My Pipeline A",
                "alerting": None,
                "pipelineInstanceCount": 0,
                "instances": [
                    {
                        "id": "cc11c32a-66c5-43ad-b176-444cee7079ff",
                        "status": "SUCCEEDED",
                        "startTime": "2022-03-15T11:42:07.559Z",
                        "endTime": "2022-03-15T11:43:17.716Z",
                        "runWithExecutionVariables": True,
                        "initialExecutionVariables": [
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
                        "jobsInstance": [
                            {
                                "id": "f8e77fc3-9c4d-450b-8efd-9d3080b38edb",
                                "jobId": "9a71afa4-aed4-4061-87d2-b279a3adf8c3",
                                "number": 80,
                                "startTime": "2022-03-15T11:42:07.559Z",
                                "endTime": "2022-03-15T11:43:17.716Z"
                            }
                        ],
                        "conditionsInstance": [
                            {
                                "id": "2292a535-affb-4b1c-973d-690c185d949e",
                                "conditionNodeId": "c2f23720-e361-11ed-894d-6b696861cc8f",
                                "isSuccess": true,
                                "startTime": "2022-03-15T11:42:30.559Z",
                                "endTime": "2022-03-15T11:42:45.559Z"
                            }
                        ],
                    },
                    {
                        "id": "d7aba110-3bd9-4505-b70c-84c4d212345",
                        "status": "SUCCEEDED",
                        "startTime": "2022-02-04T00:00:00.062Z",
                        "endTime": "2022-02-04T00:00:27.249Z",
                        "runWithExecutionVariables": False,
                        "initialExecutionVariables": [],
                        "jobsInstance": [],
                        "conditionsInstance": [],
                    }
                ],
                "versions": [
                    {
                        "number": 1,
                        "releaseNote": None,
                        "graph": {
                            "jobNodes": [
                                {
                                    "id": "00000000-0000-0000-0000-000000000000",
                                    "job": {
                                        "id": "6f56e714-37e4-4596-ae20-7016a1d954e9",
                                        "name": "Spark 2.4 java"
                                    },
                                    "position": None,
                                    "nextNodes": ["00000000-0000-0000-0000-000000000001"]
                                },
                                {
                                    "id": "00000000-0000-0000-0000-000000000001",
                                    "job": {
                                        "id": "6ea1b022-db8b-4af7-885b-56ddc9ba764a", "name": "bash"
                                    },
                                    "position": None,
                                    "nextNodes": []
                                }
                            ],
                            "conditionNodes": [
                                {
                                    "id": "00000000-0000-0000-0000-000000000001",
                                    "position": {
                                        "x": 310.00092,
                                        "y": 75
                                    },
                                    "nextNodesSuccess": [
                                        "00000000-0000-0000-0000-000000000002"
                                    ],
                                    "nextNodesFailure": [],
                                    "condition": {
                                        "toString": "ConditionExpression(expression=\"tube_name.contains(\"Tube\") || double(diameter) > 1.0\")"
                                    }
                                }
                            ]
                        },
                        "creationDate": "2022-01-31T10:36:42.327Z",
                        "creator": "john.doe",
                        "isCurrent": True,
                        "isMajor": False
                    }
                ],
                "creationDate": "2022-01-31T10:36:42.327Z",
                "creator": "john.doe",
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isLegacyPipeline": False
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "id": pipeline_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PIPELINE), variable_values=params, pprint_result=pprint_result
        )

    def get_info_by_name(
        self,
        project_id: str,
        pipeline_name: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get a given pipeline information by giving its name

        Parameters
        ----------
        project_id : str
            UUID of your pipeline  (see README on how to find it)
        pipeline_name : str
            Name of your pipeline
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to the oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of pipeline's information

        Examples
        --------
        >>> saagieapi.pipelines.get_info_by_name(
        ...     project_id=""8321e13c-892a-4481-8552-5be4d6cc5df4",
        ...     pipeline_id="Pipeline A"
        ... )
        {
            "graphPipelineByName": {
                "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                "name": "Pipeline A",
                "description": "My Pipeline A",
                "alerting": "NULL",
                "pipelineInstanceCount": 0,
                "instances": [
                    {
                        "id": "cc11c32a-66c5-43ad-b176-444cee7079ff",
                        "status": "SUCCEEDED",
                        "startTime": "2022-03-15T11:42:07.559Z",
                        "endTime": "2022-03-15T11:43:17.716Z",
                        "runWithExecutionVariables": True,
                        "initialExecutionVariables": [
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
                        "jobsInstance": [
                            {
                                "id": "f8e77fc3-9c4d-450b-8efd-9d3080b38edb",
                                "jobId": "9a71afa4-aed4-4061-87d2-b279a3adf8c3",
                                "number": 80,
                                "startTime": "2022-03-15T11:42:07.559Z",
                                "endTime": "2022-03-15T11:43:17.716Z"
                            }
                        ],
                        "conditionsInstance": [
                            {
                                "id": "2292a535-affb-4b1c-973d-690c185d949e",
                                "conditionNodeId": "c2f23720-e361-11ed-894d-6b696861cc8f",
                                "isSuccess": true,
                                "startTime": "2022-03-15T11:42:30.559Z",
                                "endTime": "2022-03-15T11:42:45.559Z"
                            }
                        ],
                    },
                    {
                        "id": "d7aba110-3bd9-4505-b70c-84c4d212345",
                        "status": "SUCCEEDED",
                        "startTime": "2022-02-04T00:00:00.062Z",
                        "endTime": "2022-02-04T00:00:27.249Z",
                        "runWithExecutionVariables": False,
                        "initialExecutionVariables": [],
                        "jobsInstance": [],
                        "conditionsInstance": [],
                    }
                ],
                "versions": [
                    {
                        "number": 1,
                        "releaseNote": None,
                        "graph": {
                            "jobNodes": [
                                {
                                    "id": "00000000-0000-0000-0000-000000000000",
                                    "job": {
                                        "id": "6f56e714-37e4-4596-ae20-7016a1d954e9",
                                        "name": "Spark 2.4 java"
                                    },
                                    "position": None,
                                    "nextNodes": ["00000000-0000-0000-0000-000000000001"]
                                },
                                {
                                    "id": "00000000-0000-0000-0000-000000000001",
                                    "job": {
                                        "id": "6ea1b022-db8b-4af7-885b-56ddc9ba764a", "name": "bash"
                                    },
                                    "position": None,
                                    "nextNodes": []
                                }
                            ],
                            "conditionNodes": [
                                {
                                    "id": "00000000-0000-0000-0000-000000000001",
                                    "position": {
                                        "x": 310.00092,
                                        "y": 75
                                    },
                                    "nextNodesSuccess": [
                                        "00000000-0000-0000-0000-000000000002"
                                    ],
                                    "nextNodesFailure": [],
                                    "condition": {
                                        "toString": "ConditionExpression(expression=\"tube_name.contains(\"Tube\") || double(diameter) > 1.0\")"
                                    }
                                }
                            ]
                        },
                        "creationDate": "2022-01-31T10:36:42.327Z",
                        "creator": "john.doe",
                        "isCurrent": True,
                        "isMajor": False
                    }
                ],
                "creationDate": "2022-01-31T10:36:42.327Z",
                "creator": "john.doe",
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isLegacyPipeline": False
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "projectId": project_id,
            "pipelineName": pipeline_name,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PIPELINE_BY_NAME), variable_values=params, pprint_result=pprint_result
        )

    def get_info_by_alias(
        self,
        project_id: str,
        pipeline_alias: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get a given pipeline information by giving its alias

        Parameters
        ----------
        project_id : str
            UUID of your pipeline  (see README on how to find it)
        pipeline_alias : str
            Alias of your pipeline
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to the oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of pipeline's information

        Examples
        --------
        >>> saagieapi.pipelines.get_info_by_alias(
        ...     project_id=""8321e13c-892a-4481-8552-5be4d6cc5df4",
        ...     pipeline_id="Pipeline A"
        ... )
        {
            "graphPipelineByAlias": {
                "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                "name": "Pipeline A",
                "description": "My Pipeline A",
                "alerting": "NULL",
                "pipelineInstanceCount": 0,
                "instances": [
                    {
                        "id": "cc11c32a-66c5-43ad-b176-444cee7079ff",
                        "status": "SUCCEEDED",
                        "startTime": "2022-03-15T11:42:07.559Z",
                        "endTime": "2022-03-15T11:43:17.716Z",
                        "runWithExecutionVariables": True,
                        "initialExecutionVariables": [
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
                        "jobsInstance": [
                            {
                                "id": "f8e77fc3-9c4d-450b-8efd-9d3080b38edb",
                                "jobId": "9a71afa4-aed4-4061-87d2-b279a3adf8c3",
                                "number": 80,
                                "startTime": "2022-03-15T11:42:07.559Z",
                                "endTime": "2022-03-15T11:43:17.716Z"
                            }
                        ],
                        "conditionsInstance": [
                            {
                                "id": "2292a535-affb-4b1c-973d-690c185d949e",
                                "conditionNodeId": "c2f23720-e361-11ed-894d-6b696861cc8f",
                                "isSuccess": true,
                                "startTime": "2022-03-15T11:42:30.559Z",
                                "endTime": "2022-03-15T11:42:45.559Z"
                            }
                        ],
                    },
                    {
                        "id": "d7aba110-3bd9-4505-b70c-84c4d212345",
                        "status": "SUCCEEDED",
                        "startTime": "2022-02-04T00:00:00.062Z",
                        "endTime": "2022-02-04T00:00:27.249Z",
                        "runWithExecutionVariables": False,
                        "initialExecutionVariables": [],
                        "jobsInstance": [],
                        "conditionsInstance": [],
                    }
                ],
                "versions": [
                    {
                        "number": 1,
                        "releaseNote": None,
                        "graph": {
                            "jobNodes": [
                                {
                                    "id": "00000000-0000-0000-0000-000000000000",
                                    "job": {
                                        "id": "6f56e714-37e4-4596-ae20-7016a1d954e9",
                                        "name": "Spark 2.4 java"
                                    },
                                    "position": None,
                                    "nextNodes": ["00000000-0000-0000-0000-000000000001"]
                                },
                                {
                                    "id": "00000000-0000-0000-0000-000000000001",
                                    "job": {
                                        "id": "6ea1b022-db8b-4af7-885b-56ddc9ba764a", "name": "bash"
                                    },
                                    "position": None,
                                    "nextNodes": []
                                }
                            ],
                            "conditionNodes": [
                                {
                                    "id": "00000000-0000-0000-0000-000000000001",
                                    "position": {
                                        "x": 310.00092,
                                        "y": 75
                                    },
                                    "nextNodesSuccess": [
                                        "00000000-0000-0000-0000-000000000002"
                                    ],
                                    "nextNodesFailure": [],
                                    "condition": {
                                        "toString": "ConditionExpression(expression=\"tube_name.contains(\"Tube\") || double(diameter) > 1.0\")"
                                    }
                                }
                            ]
                        },
                        "creationDate": "2022-01-31T10:36:42.327Z",
                        "creator": "john.doe",
                        "isCurrent": True,
                        "isMajor": False
                    }
                ],
                "creationDate": "2022-01-31T10:36:42.327Z",
                "creator": "john.doe",
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isLegacyPipeline": False
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "projectId": project_id,
            "pipelineAlias": pipeline_alias,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PIPELINE_BY_ALIAS), variable_values=params, pprint_result=pprint_result
        )

    def get_instance(self, pipeline_instance_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """
        Get the information of a given pipeline instance id

        Parameters
        ----------
        pipeline_instance_id : str
            Pipeline instance id
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of pipeline information

        Examples
        --------
        >>> saagieapi.pipelines.get_instance(pipeline_instance_id="cc11c32a-66c5-43ad-b176-444cee7079ff")
        {
            "pipelineInstance": {
                "id": "cc11c32a-66c5-43ad-b176-444cee7079ff",
                "status": "SUCCEEDED",
                "startTime": "2022-03-15T11:42:07.559Z",
                "endTime": "2022-03-15T11:43:17.716Z",
                "runWithExecutionVariables": True,
                "initialExecutionVariables": [
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
                "jobsInstance": [
                    {
                        "id": "f8e77fc3-9c4d-450b-8efd-9d3080b38edb",
                        "jobId": "9a71afa4-aed4-4061-87d2-b279a3adf8c3",
                        "number": 80,
                        "startTime": "2022-03-15T11:42:07.559Z",
                        "endTime": "2022-03-15T11:43:17.716Z"
                    }
                ],
                "conditionsInstance": [
                    {
                        "id": "00000000-0000-0000-0000-000000000001",
                        "conditionNodeId": "c2f23720-e361-11ed-894d-6b696861cc8f",
                        "isSuccess": True,
                        "startTime": "2022-03-15T11:42:30.559Z",
                        "endTime": "2022-03-15T11:42:45.559Z"
                    }
                ],
            }
        }
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PIPELINE_INSTANCE),
            variable_values={"id": pipeline_instance_id},
            pprint_result=pprint_result,
        )

    def create_graph(
        self,
        name: str,
        project_id: str,
        graph_pipeline: GraphPipeline,
        alias: str,
        description: str = "",
        release_note: str = "",
        emails: List[str] = None,
        status_list: List[str] = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        has_execution_variables_enabled: bool = None,
        source_url: str = "",
    ) -> Dict:
        """
        Create a pipeline in a given project

        Parameters
        ----------
        name : str
            Name of the pipeline. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        graph_pipeline : GraphPipeline
            Example: If you want to create a simple pipeline with 2 jobs that started by job_node_1,
            you can use the following example
                job_node1 = JobNode(job_id_1)
                job_node2 = JobNode(job_id_2)
                job_node1.add_next_node(job_node2) # Indicates that the job_node_1 is followed by job_node_2
                graph_pipeline = GraphPipeline()
                graph_pipeline.add_root_node(job_node1) # Indicates the pipeline will start with job_node1
        alias: str
            Alias of the pipeline
        description : str, optional
            Description of the pipeline
        release_note: str, optional
            Release note of the pipeline
        emails: List[String], optional
            Emails to receive alerts for the pipeline, each item should be a valid email,
        status_list: List[String], optional
            Receive an email when the pipeline status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        cron_scheduling : str, optional
            Scheduling CRON format
        schedule_timezone : str, optional
            Timezone of the scheduling
        has_execution_variables_enabled: bool, optional
            Boolean to activate or desactivate the execution variables
        source_url: str, optional
            URL of the source code used for the pipeline (link to the commit for example)

        Returns
        -------
        dict
            Dict of pipeline information

        Examples
        --------
        >>> job1_id = "7a706539-69dd-4f5d-bba3-4eac6be74d8d"
        >>> job2_id = "3dbbb785-a7f4-4840-9f98-814b105a1a31"
        >>> job3_id = "00000000-0000-0000-0000-000000000001"
        >>> job4_id = "00000000-0000-0000-0000-000000000002"
        >>> # create several JobNode
        >>> job_node1 = JobNode(job1_id)
        >>> job_node2 = JobNode(job2_id)
        >>> job_node3 = JobNode(job_id)
        >>> job_node4 = JobNode(job_id)
        >>> # create a condition node between job_node1 and job_node2 or job_node3
        >>> condition_node_1 = ConditionStatusNode()
        >>> condition_node_1.put_at_least_one_success()
        >>> condition_node_1.add_success_node(job_node2)
        >>> condition_node_1.add_failure_node(job_node3)
        >>> job_node1.add_next_node(condition_node_1)
        >>> # create a condition node between job_node2 and job_node4
        >>> condition_node_2 = ConditionExpressionNode()
        >>> condition_node_2.set_expression("1 + 1 == 2")
        >>> condition_node_2.add_success_node(job_node4)
        >>> job_node2.add_next_node(condition_node_2)
        >>> graph_pipeline = GraphPipeline()
        >>> graph_pipeline.add_root_node(job_node1)
        >>> saagie.pipelines.create_graph(
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
        ...     graph_pipeline=graph_pipeline,
        ...     name="Amazing Pipeline",
        ...     description="new pipeline",
        ...     cron_scheduling="0 0 * * *",
        ...     schedule_timezone="Pacific/Fakaofo",
        ...     emails=["hello.world@gmail.com"],
        ...     status_list=["FAILED"]
        ... )
        {
            "createGraphPipeline": {
                "id": "ca79c5c8-2e57-4a35-bcfc-5065f0ee901c"
            }
        }
        """
        if not graph_pipeline.list_job_nodes:
            graph_pipeline.to_pipeline_graph_input()

        params = {
            "name": name,
            "description": description,
            "projectId": project_id,
            "releaseNote": release_note,
            "jobNodes": graph_pipeline.list_job_nodes,
            "conditionNodes": graph_pipeline.list_conditions_nodes,
            "alias": alias,
        }

        if cron_scheduling:
            params.update(self.saagie_api.check_scheduling(cron_scheduling, schedule_timezone))
        else:
            params["isScheduled"] = False

        if emails:
            params.update(self.saagie_api.check_alerting(emails, status_list))

        if has_execution_variables_enabled:
            params["hasExecutionVariablesEnabled"] = has_execution_variables_enabled

        if source_url:
            params["sourceUrl"] = source_url

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_GRAPH_PIPELINE), variable_values=params)
        logging.info("✅ Pipeline [%s] successfully created", name)
        return result

    def delete(self, pipeline_id: str) -> Dict:
        """Delete a pipeline given pipeline id

        Parameters
        ----------
        pipeline_id : str
            Pipeline id

        Returns
        -------
        dict
            Dict containing status of deletion

        Examples
        --------
        >>> saagieapi.pipelines.delete(pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c")
        {
            "deletePipeline": True
        }
        """

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_PIPELINE), variable_values={"id": pipeline_id})
        logging.info("✅ Pipeline [%s] successfully deleted", pipeline_id)
        return result

    def upgrade(
        self, pipeline_id: str, graph_pipeline: GraphPipeline, release_note: str = "", source_url: str = ""
    ) -> Dict:
        """
        Upgrade a pipeline in a given project

        Parameters
        ----------
        pipeline_id: str,
            UUID of pipeline
        graph_pipeline : GraphPipeline
        release_note: str, optional
            Release note of the pipeline
        source_url: str, optional
            URL of the source code used for the pipeline (link to the commit for example)

        Returns
        -------
        dict
            Dict of pipeline information

        Examples
        --------
        >>> job1_id = "7a706539-69dd-4f5d-bba3-4eac6be74d8d"
        >>> job2_id = "3dbbb785-a7f4-4840-9f98-814b105a1a31"
        >>> job3_id = "e5e9fa38-1af8-42e7-95df-8d983eb78387"
        >>> job_node1 = JobNode(job1_id)
        >>> job_node2 = JobNode(job2_id)
        >>> job_node3 = JobNode(job3_id)
        >>> condition_node_1 = ConditionStatusNode()
        >>> condition_node_1.put_at_least_one_success()
        >>> job_node1.add_next_node(condition_node_1)
        >>> condition_node_1.add_success_node(job_node2)
        >>> condition_node_1.add_failure_node(job_node3)
        >>> graph_pipeline = GraphPipeline()
        >>> graph_pipeline.add_root_node(job_node1)
        >>> saagie.pipelines.upgrade(
        ...     pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c",
        ...     graph_pipeline=graph_pipeline
        ... )
        {
            "addGraphPipelineVersion":{
                "number":4,
                "releaseNote":"",
                "graph":{
                    "jobNodes":[
                        {
                            "id":"82383907-bdd9-4d66-bc00-a84ff3a9caee",
                            "job":{
                                "id":"7a706539-69dd-4f5d-bba3-4eac6be74d8d"
                            }
                        },
                        {
                            "id":"5501eea2-e7af-4b44-a784-387f133b28c6",
                            "job":{
                                "id":"3dbbb785-a7f4-4840-9f98-814b105a1a31"
                            }
                        },
                        {
                            "id":"560d99bb-4e7b-4ab4-a5df-d879d31b4c0a",
                            "job":{
                                "id":"e5e9fa38-1af8-42e7-95df-8d983eb78387"
                            }
                        }
                    ],
                    "conditionNodes":[
                        {
                            "id":"9d0e886c-7771-4aa7-8321-cbccfaf4d3bb"
                        }
                    ]
                },
                "creationDate":"2022-04-28T15:35:32.381215Z[UTC]",
                "creator":"john.doe",
                "isCurrent":True,
                "isMajor":False
            }
        }
        """
        if not graph_pipeline.list_job_nodes:
            graph_pipeline.to_pipeline_graph_input()

        params = {
            "id": pipeline_id,
            "jobNodes": graph_pipeline.list_job_nodes,
            "conditionNodes": graph_pipeline.list_conditions_nodes,
            "releaseNote": release_note,
        }

        if source_url:
            params["sourceUrl"] = source_url

        result = self.saagie_api.client.execute(query=gql(GQL_UPGRADE_PIPELINE), variable_values=params)
        logging.info("✅ Pipeline [%s] successfully upgraded", pipeline_id)
        return result

    def edit(
        self,
        pipeline_id: str,
        name: str = None,
        alias: str = None,
        description: str = None,
        emails: List[str] = None,
        status_list: List[str] = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        has_execution_variables_enabled: bool = None,
    ) -> Dict:  # sourcery skip: remove-redundant-if, simplify-boolean-comparison
        # pylint: disable=singleton-comparison
        """Edit a pipeline
        NB : You can only edit pipeline if you have at least the editor role on the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        name : str, optional
            Pipeline name,
            if not filled, defaults to current value, else it will change the pipeline name
        alias : str, optional
            Alias of the pipeline
            if not filled, defaults to current value, else it will change the alias of the pipeline
        description : str, optional
            Description of the pipeline
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
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        has_execution_variables_enabled: bool, optional
            Boolean to activate or desactivate the execution variables

        Returns
        -------
        dict
            Dict of pipeline information

        Examples
        --------
        >>> saagieapi.pipelines.edit(
        ...     pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c",
        ...     name="Amazing Pipeline 2"
        ... )
        {
            "editPipeline":{
                "id": "ca79c5c8-2e57-4a35-bcfc-5065f0ee901c",
                "name": "Amazing Pipeline 2",
                "alias": "Amazing_Pipeline_2",
                "description": "",
                "alerting": None,
                "isScheduled": True,
                "cronScheduling": "0 0 1 * *",
                "scheduleTimezone": "UTC",
                "hasExecutionVariablesEnabled": False
            }
        }
        """
        previous_pipeline_info = self.get_info(pipeline_id, pprint_result=False)["graphPipeline"]

        params = {
            "id": pipeline_id,
            "name": name or previous_pipeline_info["name"],
            "alias": alias or previous_pipeline_info["alias"],
            "description": description or previous_pipeline_info["description"],
        }

        # cases test : True, False and None
        if is_scheduled:
            params.update(self.saagie_api.check_scheduling(cron_scheduling, schedule_timezone))
        elif is_scheduled == False:
            params["isScheduled"] = False
        else:
            for k in ("isScheduled", "cronScheduling", "scheduleTimezone"):
                params[k] = previous_pipeline_info[k]

        # cases test : List non empty, List empty, None
        if isinstance(emails, List) and emails:
            params.update(self.saagie_api.check_alerting(emails, status_list))
        elif isinstance(emails, List):
            params["alerting"] = None
        elif previous_alerting := previous_pipeline_info["alerting"]:
            params["alerting"] = {
                "emails": previous_alerting["emails"],
                "statusList": previous_alerting["statusList"],
            }

        if has_execution_variables_enabled in {True, False}:
            params["hasExecutionVariablesEnabled"] = has_execution_variables_enabled
        else:
            params["hasExecutionVariablesEnabled"] = previous_pipeline_info["hasExecutionVariablesEnabled"]

        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_PIPELINE), variable_values=params)
        logging.info("✅ Pipeline [%s] successfully edited", name)
        return result

    def create_or_upgrade(
        self,
        name: str,
        alias: str,
        project_id: str,
        graph_pipeline: GraphPipeline,
        description: str = None,
        release_note: str = None,
        emails: List[str] = None,
        status_list: List[str] = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        has_execution_variables_enabled: bool = None,
        source_url: str = None,
    ) -> Dict:
        """Create or upgrade a pipeline in a given project

        Parameters
        ----------
        name : str
            Pipeline name
        alias : str
            Alias of the pipeline
        project_id : str
            UUID of your project (see README on how to find it)
        graph_pipeline : GraphPipeline
            Example: If you want to create a simple pipeline with 2 jobs that started by job_node_1,
            you can use the following example
                job_node1 = JobNode(job_id_1)
                job_node2 = JobNode(job_id_2)
                job_node1.add_next_node(job_node2) # Indicates that the job_node_1 is followed by job_node_2
                graph_pipeline = GraphPipeline()
                graph_pipeline.add_root_node(job_node1) # Indicates the pipeline will start with job_node1
        description : str, optional
            Description of the pipeline
            if not filled, defaults to current value, else it will change the description of the pipeline
        release_note: str, optional
            Release note of the pipeline
        emails: List[String], optional
            Emails to receive alerts for the pipeline, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the pipeline status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        is_scheduled : bool, optional
            True to activate the pipeline scheduling
        cron_scheduling : str, optional
            Scheduling CRON format
            When is_scheduled is set to True, it will be mandatory to fill this value
            if not filled, defaults to current value
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        has_execution_variables_enabled: bool, optional
            Boolean to activate or desactivate the execution variables
        source_url: str, optional
            URL of the source code used for the pipeline (link to the commit for example)

        Returns
        -------
        dict
            Dict of pipeline information

        Examples
        --------
        >>> job1_id = "7a706539-69dd-4f5d-bba3-4eac6be74d8d"
        >>> job2_id = "3dbbb785-a7f4-4840-9f98-814b105a1a31"
        >>> job_node1 = JobNode(job1_id)
        >>> job_node2 = JobNode(job2_id)
        >>> condition_node_1 = ConditionStatusNode()
        >>> condition_node_1.put_at_least_one_success()
        >>> job_node1.add_next_node(condition_node_1)
        >>> condition_node_1.add_success_node(job_node2)
        >>> graph_pipeline = GraphPipeline()
        >>> graph_pipeline.add_root_node(job_node1)
        >>> saagie.pipelines.create_or_upgrade(
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
        ...     graph_pipeline=graph_pipeline,
        ...     name="Amazing Pipeline",
        ...     description="new pipeline",
        ...     cron_scheduling="0 0 * * *",
        ...     schedule_timezone="Pacific/Fakaofo",
        ...     emails=["hello.world@gmail.com"],
        ...     status_list=["FAILED"]
        ... )
        {
            "createGraphPipeline": {
                "id": "ca79c5c8-2e57-4a35-bcfc-5065f0ee901c"
            }
        }
        """
        pipeline_list = self.list_for_project_minimal(project_id)["project"]["pipelines"]

        if name in [pipeline["name"] for pipeline in pipeline_list]:
            pipeline_id = next(pipeline["id"] for pipeline in pipeline_list if pipeline["name"] == name)

            responses = {
                "editPipeline": self.edit(
                    pipeline_id=pipeline_id,
                    name=name,
                    alias=alias,
                    description=description,
                    emails=emails,
                    status_list=status_list,
                    is_scheduled=is_scheduled,
                    cron_scheduling=cron_scheduling,
                    schedule_timezone=schedule_timezone,
                    has_execution_variables_enabled=has_execution_variables_enabled,
                )["editPipeline"]
            }
            responses["addGraphPipelineVersion"] = self.upgrade(pipeline_id, graph_pipeline, release_note, source_url)[
                "addGraphPipelineVersion"
            ]

            return responses

        args = {
            k: v
            for k, v in {
                "name": name,
                "alias": alias,
                "project_id": project_id,
                "graph_pipeline": graph_pipeline,
                "description": description,
                "release_note": release_note,
                "emails": emails,
                "status_list": status_list,
                "cron_scheduling": cron_scheduling,
                "schedule_timezone": schedule_timezone,
                "has_execution_variables_enabled": has_execution_variables_enabled,
                "source_url": source_url,
            }.items()
            if v is not None  # Remove None values from the dict
        }
        return self.create_graph(**args)

    def rollback(self, pipeline_id: str, version_number: str) -> Dict:
        """Rollback a given job to the given version

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        version_number : str
            Number of the version to rollback

        Returns
        -------
        dict
            Dict of rollback pipeline

        Examples
        --------
        >>> saagie_api.pipelines.rollback(
        ...     pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
        ...     version_number=1
        ... )
        {
            "rollbackPipelineVersion": {
                "id": "5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
                "versions": [
                    {
                        "number": 2,
                        "isCurrent": False
                    },
                    {
                        "number": 1,
                        "isCurrent": True
                    }
                ]
            }
        }
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_ROLLBACK_PIPELINE_VERSION),
            variable_values={"pipelineId": pipeline_id, "versionNumber": version_number},
        )
        logging.info("✅ Pipeline [%s] successfully rollbacked to version [%s]", pipeline_id, version_number)
        return result

    def run(self, pipeline_id: str) -> Dict:
        """Run a given pipeline
        NB : You can only run pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline instance's information

        Examples
        --------
        >>> saagieapi.pipelines.run(pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c")
        {
            "runPipeline":{
                "id":"975253ea-1b91-4633-acdf-dd9b09d53b18",
                "status":"REQUESTED"
            }
        }
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_RUN_PIPELINE), variable_values={"pipelineId": pipeline_id}
        )
        logging.info("✅ Pipeline [%s] successfully launched", pipeline_id)
        return result

    def run_with_callback(self, pipeline_id: str, freq: int = 10, timeout: int = -1) -> str:
        """Run a given pipeline and wait for its final status (KILLED, FAILED, UNKNOWN or SUCCESS).
        NB : You can only run pipeline if you have at least the editor role on the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)
        freq : int, optional
            Number of seconds between 2 state checks
        timeout : int, optional
            Number of seconds before timeout

        Returns
        -------
        (str, str)
            (the final state of the pipeline, the pipeline instance id)

        Raises
        ------
        TimeoutError
            the last state known of the pipeline before timeout

        Examples
        --------
        >>> saagieapi.pipelines.run_with_callback(pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c")
        ("SUCCEEDED", "975253ea-1b91-4633-acdf-dd9b09d53b18")
        """
        res = self.run(pipeline_id)
        pipeline_instance_id = res.get("runPipeline").get("id")

        pipeline_instance_info = self.get_instance(pipeline_instance_id, pprint_result=False)
        state = pipeline_instance_info.get("pipelineInstance").get("status")

        sec = 0
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED", "UNKNOWN"]

        logging.info("⏳ Pipeline id %s with instance %s has just been requested", pipeline_id, pipeline_instance_id)

        while state not in final_status_list:
            with console.status(f"Job is currently {state}", refresh_per_second=100):
                t_out = False if timeout == -1 else sec >= timeout
                if t_out:
                    raise TimeoutError(f"❌ Last state known : {state}")
                time.sleep(freq)
                sec += freq
                pipeline_instance_info = self.get_instance(pipeline_instance_id, pprint_result=False)
                state = pipeline_instance_info.get("pipelineInstance").get("status")

        if state == "SUCCEEDED":
            logging.info(
                "✅ Pipeline id %s with instance %s has the status %s", pipeline_id, pipeline_instance_id, state
            )
        elif state in ("FAILED", "KILLED", "UNKNOWN"):
            logging.error(
                "❌ Pipeline id %s with instance %s has the status %s", pipeline_id, pipeline_instance_id, state
            )

        return (state, pipeline_instance_id)

    def stop(self, pipeline_instance_id: str) -> Dict:
        """Stop a given pipeline instance
        NB : You can only stop pipeline instance if you have at least the
        editor role on the project.

        Parameters
        ----------
        pipeline_instance_id : str
            UUID of your pipeline instance  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline's instance information

        Examples
        --------
        >>> saagie.pipelines.stop(pipeline_instance_id="8e9b9f16-4a5d-4188-a967-1a96b88e4358")
        {
            "stopPipelineInstance":{
                "id":"0a83faaa-c4e9-4141-82d0-c434fcfb0f10",
                "number":1,
                "status":"KILLING",
                "startTime":"2022-04-28T14:30:17.734Z",
                "endTime":None,
                "pipelineId":"ca79c5c8-2e57-4a35-bcfc-5065f0ee901c"
            }
        }
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_STOP_PIPELINE_INSTANCE), variable_values={"pipelineInstanceId": pipeline_instance_id}
        )
        logging.info("✅ Pipeline instance [%s] successfully stopped", pipeline_instance_id)
        return result

    def export(
        self,
        pipeline_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        env_var_scope: str = "PIPELINE",
    ) -> bool:
        """Export the pipeline in a folder

        Parameters
        ----------
        pipeline_id : str
            Pipeline ID
        output_folder : str
            Path to store the exported pipeline
        error_folder : str, optional
            Path to store the pipeline ID in case of error. If not set, pipeline ID is not write
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        env_var_scope : str, optional
            Scope of the environment variables to export. Can be "GLOBAL", "PROJECT" or "PIPELINE"
            Default value is "PIPELINE".

        Returns
        -------
        bool
            True if pipeline is exported

        Examples
        --------
        >>> saagieapi.pipelines.export(
        ...     pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c",
        ...     output_folder="./output/pipeline/",
        ...     error_folder="./output/error/pipeline/",
        ...     versions_only_current=True
        ... )
        True
        """
        output_folder = Path(output_folder)
        try:
            pipeline_info = self.get_info(
                pipeline_id,
                instances_limit=1,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )["graphPipeline"]

            pipeline_folder = output_folder / pipeline_id
            create_folder(pipeline_folder)
            write_to_json_file(pipeline_folder / "pipeline.json", pipeline_info)

            scope_mapping = {
                "GLOBAL": ["PIPELINE", "PROJECT", "GLOBAL"],
                "PROJECT": ["PIPELINE", "PROJECT"],
                "PIPELINE": ["PIPELINE"],
            }

            if env_var_scope in scope_mapping:
                scopes = scope_mapping[env_var_scope]
            else:
                raise NameError("Invalid scope")

            env_vars = self.saagie_api.env_vars.list(scope="PIPELINE", pipeline_id=pipeline_id)
            env_vars = [env for env in env_vars if env["scope"] in scopes]

            for env in env_vars:
                create_folder(pipeline_folder / "env_vars" / env["name"])
                write_to_json_file(pipeline_folder / "env_vars" / env["name"] / "variable.json", env)

            logging.info("✅ Pipeline [%s] successfully exported", pipeline_id)
        except Exception as exception:
            logging.warning("Cannot get the information of the pipeline [%s]", pipeline_id)
            logging.error("Something went wrong %s", exception)
            logging.warning("❌ Pipeline [%s] has not been successfully exported", pipeline_id)
            write_error(error_folder, "pipelines", pipeline_id)
            return False

        return True

    def import_from_json(self, json_file: str, project_id: str) -> bool:
        """Import pipeline from JSON format

        Parameters
        ----------
        json_file : str
            Path to the JSON file that contains pipeline information
        project_id : str
            Project ID

        Returns
        -------
        bool
            True if pipelines are imported False otherwise

        Examples
        --------
        >>> saagieapi.pipelines.import_from_json(
        ...     json_file="/path/to/the/json/file.json",
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        ... )
        True
        """
        json_file = Path(json_file)
        env_vars_folder = json_file.parent / "env_vars"
        try:
            with json_file.open("r", encoding="utf-8") as file:
                pipeline_info = json.load(file)
        except Exception as exception:
            return handle_error(f"Cannot open the JSON file {json_file}", exception)

        try:
            pipeline_name = pipeline_info["name"]

            version = next((version for version in pipeline_info["versions"] if version["isCurrent"]), None)
            if not version:
                return handle_error("❌ Current version not found", pipeline_name)

            jobs_target_pj = self.saagie_api.jobs.list_for_project_minimal(project_id)["jobs"]

            jobs_not_found, jobs_found = parse_version_jobs(jobs_target_pj, version)

            if jobs_not_found:
                not_found = "".join(f"{job}, " for job in jobs_not_found)
                return handle_error(
                    f"❌ Import aborted, in target project (id : {project_id}), \
                        the following jobs were not found: {not_found}",
                    pipeline_name,
                )

            graph_pipeline = GraphPipeline()
            graph_pipeline.list_job_nodes = jobs_found
            graph_pipeline.list_conditions_nodes = parse_version_conditions(version)
            res = self.create_graph(
                name=pipeline_name,
                alias=pipeline_info["alias"],
                project_id=project_id,
                graph_pipeline=graph_pipeline,
                description=pipeline_info["description"],
                release_note=version["releaseNote"],
                emails=(pipeline_info.get("alerting") or {}).get("emails", ""),
                status_list=(pipeline_info.get("alerting") or {}).get("statusList", ""),
                cron_scheduling=pipeline_info["cronScheduling"],
                schedule_timezone=pipeline_info["scheduleTimezone"],
                has_execution_variables_enabled=pipeline_info["hasExecutionVariablesEnabled"],
            )
            if res["createGraphPipeline"] is None:
                return handle_error(res, pipeline_name)

            # check if env_var_folder exists
            if env_vars_folder.exists():
                for env_var_folder in env_vars_folder.iterdir():
                    with (env_var_folder / "variable.json").open("r", encoding="utf-8") as file:
                        env_var_info = json.load(file)
                    res_env = self.saagie_api.env_vars.create(
                        scope=env_var_info["scope"],
                        name=env_var_info["name"],
                        value=env_var_info["value"] or "",
                        description=env_var_info["description"],
                        is_password=env_var_info["isPassword"],
                        project_id=project_id,
                        pipeline_id=res["createGraphPipeline"]["id"],
                    )
                    if res_env["saveEnvironmentVariable"] is None:
                        return handle_error(res_env, pipeline_name)
        except Exception as exception:
            return handle_error(exception, pipeline_name)

        logging.info("✅ Pipeline [%s] has been successfully imported", pipeline_name)
        return True

    def count_deletable_instances_by_status(self, pipeline_id: str) -> Dict:
        """Count deletable instances of pipeline by status

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)

        Returns
        -------
        dict
            Dict of number of deletable instances of pipeline by status

        Examples
        --------
        >>> saagie_api.pipelines.count_deletable_instances_by_status(pipeline_id=pipeline_id)
        {
            'countDeletablePipelineInstancesByStatus': [
                {'selector': 'ALL', 'count': 0},
                {'selector': 'SUCCEEDED', 'count': 0},
                {'selector': 'FAILED', 'count': 0},
                {'selector': 'STOPPED', 'count': 0},
                {'selector': 'UNKNOWN', 'count': 0}
            ]
        }
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_STATUS), variable_values={"pipelineId": pipeline_id}
        )

    def count_deletable_instances_by_date(self, pipeline_id: str, date_before: str) -> Dict:
        """Count deletable instances of pipeline by status

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        date_before : str
            Instances before this date will be counted. The date must be in this format : '%Y-%m-%dT%H:%M:%S%z'

        Returns
        -------
        dict
            Dict of number of deletable instances of pipeline by status

        Examples
        --------
        >>> saagie_api.pipelines.count_deletable_instances_by_date(
        ...     pipeline_id=pipeline_id,
        ...     date_before="2023-10-01T00:00:00+01:00"
        ... )
        {
            "countDeletablePipelineInstancesByDate": 6
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
            query=gql(GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_DATE),
            variable_values={"pipelineId": pipeline_id, "beforeAt": date_before},
        )

    def delete_versions(self, pipeline_id: str, versions: [int]):
        """Delete given pipeline's versions and associated instances
        NB: You can only delete a version with terminated instances

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        versions : [int]
            List of version numbers to delete

        Returns
        -------
        dict
            Dict of deleted versions with their number and success status

        Examples
        --------
        >>> saagie_api.pipelines.delete_versions(
        ...     pipeline_id=pipeline_id,
        ...     versions=[1]
        ... )
        {
            "deletePipelineVersions": [
                {
                    "number": 1,
                    "success": true
                }
            ]
        }
        """
        params = {"pipelineId": pipeline_id, "versions": versions}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_PIPELINE_VERSION), variable_values=params)
        logging.info("✅ Versions of pipeline [%s] successfully deleted", pipeline_id)
        return result

    def delete_instances(self, pipeline_id: str, pipeline_instances_id: [str]) -> int:
        """Delete given pipeline's instances
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        pipeline_instances_id : [str]
            List of UUID of instances to delete (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted instances

        Examples
        --------
        >>> saagie_api.pipelines.delete_instances(
        ...     pipeline_id=pipeline_id,
        ...     pipeline_instances_id=["c8f156bc-78ab-4dda-acff-bbe828237fd9", "7e5549cd-32aa-42c4-88b5-ddf5f3087502"]
        ... )
        {
            'deletePipelineInstances': [
                {'id': '7e5549cd-32aa-42c4-88b5-ddf5f3087502', 'success': True},
                {'id': 'c8f156bc-78ab-4dda-acff-bbe828237fd9', 'success': True}
            ]
        }
        """
        params = {"pipelineId": pipeline_id, "pipelineInstancesId": pipeline_instances_id}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_PIPELINE_INSTANCE), variable_values=params)
        logging.info("✅ Instances of pipeline [%s] successfully deleted", pipeline_id)
        return result

    def delete_instances_by_selector(
        self, pipeline_id: str, selector, exclude_instances_id: List = None, include_instances_id: List = None
    ) -> int:
        """Delete given pipeline's instances by selector
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        selector : str
            Name of status to select in this list : ALL, SUCCEEDED, FAILED, STOPPED, UNKNOWN
        exclude_instances_id : [str]
            List of UUID of instances of your pipeline to exclude from the deletion
        include_instances_id: [str]
            List of UUID of instances of your pipeline to include from the deletion

        Returns
        -------
        Dict
            Return the number of instances deleted

        Examples
        --------
        >>> saagie_api.pipelines.delete_instances_by_selector(
        ...     pipeline_id=pipeline_id,
        ...     selector="FAILED",
        ...     exclude_instances_id=["478d48d4-1609-4bf0-883d-097d43709aa8"],
        ...     include_instances_id=["47d3df2c-5a38-4a5e-a49e-5405ad8f1699"]
        ... )
        {
            'deletePipelineInstancesByStatusSelector': 1
        }
        """
        params = {
            "pipelineId": pipeline_id,
            "selector": selector,
            "excludePipelineInstanceId": exclude_instances_id or [],
            "includePipelineInstanceId": include_instances_id or [],
        }
        result = self.saagie_api.client.execute(
            query=gql(GQL_DELETE_PIPELINE_INSTANCE_BY_SELECTOR), variable_values=params
        )
        logging.info("✅ Instances of pipeline [%s] successfully deleted", pipeline_id)
        return result

    def delete_instances_by_date(
        self, pipeline_id: str, date_before: str, exclude_instances_id: List = None, include_instances_id: List = None
    ) -> int:
        """Delete given pipeline's instances by selector
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        date_before : str
            Instances before this date will be counted. The date must be in this format : '%Y-%m-%dT%H:%M:%S%z'
        exclude_instances_id : [str]
            List of UUID of instances of your pipeline to exclude from the deletion
        include_instances_id: [str]
            List of UUID of instances of your pipeline to include from the deletion

        Returns
        -------
        Dict
            Return the number of instances deleted

        Examples
        --------
        >>> saagie_api.pipelines.delete_instances_by_date(
        ...     pipeline_id=pipeline_id,
        ...     beforeAt="2023-10-01T00:00:00+01:00",
        ...     exclude_instances_id=["478d48d4-1609-4bf0-883d-097d43709aa8"],
        ...     include_instances_id=["47d3df2c-5a38-4a5e-a49e-5405ad8f1699"]
        ... )
        {
            'deletePipelineInstancesByDateSelector': 1
        }
        """
        # need to check if the date is in this format : 2023-02-01T00:00:00+01:00
        # if not, it will raise an error and stop the call
        try:
            datetime.strptime(date_before, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError as exception:
            raise ValueError(
                "The date must be in this format : '%Y-%m-%dT%H:%M:%S%z'. \
                Please change your date_before parameter"
            ) from exception

        params = {
            "pipelineId": pipeline_id,
            "beforeAt": date_before,
            "excludePipelineInstanceId": exclude_instances_id or [],
            "includePipelineInstanceId": include_instances_id or [],
        }
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_PIPELINE_INSTANCE_BY_DATE), variable_values=params)
        logging.info("✅ Instances of pipeline [%s] successfully deleted", pipeline_id)
        return result

    def duplicate(self, pipeline_id, duplicate_jobs: bool = False) -> Dict:
        """Duplicate a given pipeline

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        duplicate_jobs : bool, optional
            If True, duplicate the jobs of the pipeline, else only the pipeline

        Returns
        -------
        dict
            Dict of duplicate pipeline with its id and name

        Examples
        --------
        >>> saagie_api.pipelines.duplicate(pipeline_id=pipeline_id)
        {
            'duplicatePipeline': {
                'id': '29cf1b80-6b9c-47bc-a06c-c20897257097',
                'name': 'Copy of my_pipeline 2'
            }
        }
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_DUPLICATE_PIPELINE),
            variable_values={"pipelineId": pipeline_id, "duplicateJobs": duplicate_jobs},
        )
        logging.info("✅ Pipeline [%s] successfully duplicated", pipeline_id)
        return result
