Rollback a job
--------------

**saagieapi.jobs.rollback**

Example :

.. code:: python

    saagie_api.jobs.rollback(job_id="58870149-5f1c-45e9-93dc-04b2b30a732c", version_number=3)

Response payload example :

.. code:: python

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
