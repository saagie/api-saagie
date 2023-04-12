Rollback a pipeline
--------------

**saagieapi.pipelines.rollback**

Example :

.. code:: python

    saagie_api.pipelines.rollback(pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1", version_number=1)

Response payload example :

.. code:: python

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
