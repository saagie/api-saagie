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
                    ]
                },
                {
                    "id": "d7aba110-3bd9-4505-b70c-84c4d212345",
                    "status": "SUCCEEDED",
                    "startTime": "2022-02-04T00:00:00.062Z",
                    "endTime": "2022-02-04T00:00:27.249Z",
                    "runWithExecutionVariables": False,
                    "initialExecutionVariables": []
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
        }
    }
