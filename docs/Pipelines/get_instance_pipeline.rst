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
            ]
        }
    }
