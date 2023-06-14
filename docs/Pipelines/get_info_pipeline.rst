Getting pipeline information
----------------------------

**saagieapi.pipelines.get_info**

Example :

.. code:: python

    saagieapi.pipelines.get_info(pipeline_id="5d1999f5-fa70-47d9-9f41-55ad48333629")

Response payload example :

.. code:: python

    {
        "graphPipeline": {
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
                        "conditionNodes":     {
                            "graphPipeline": {
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
                                                "id": "00000000-0000-0000-0000-000000000001",
                                                "conditionNodeId": "c2f23720-e361-11ed-894d-6b696861cc8f",
                                                "isSuccess": True,
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
                                                    "id": "00000000-0000-0000-0000-000000000002",
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
                                            ],
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
