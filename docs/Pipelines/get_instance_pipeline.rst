Getting pipeline instance information
-------------------------------------

**saagieapi.pipelines.get_instance**

Example :

.. code:: python

    saagieapi.pipelines.get_instance(pipeline_instance_id="cc11c32a-66c5-43ad-b176-444cee7079ff")

Response payload example :

.. code:: python

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
