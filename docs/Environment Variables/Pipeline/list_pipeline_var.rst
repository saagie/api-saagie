Listing pipeline environment variables
-------------------------------------

**saagie.env_vars.list_for_pipeline** *(deprecated)*

Example :

.. code:: python

   saagieapi.env_vars.list_for_pipeline(pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1")

Response payload example :

.. code:: python

   {
        "pipelineEnvironmentVariables": [
            {
                "id": "40a7dd59-538f-4c55-a983-8a554525b060",
                "scope": "GLOBAL",
                "name": "TEST_GLOBAL",
                "value": "TEST_GLOBAL",
                "description": "",
                "isPassword": False,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            },
            {
                "id": "3f4a8d8f-6f45-480f-8907-2f66ddf26e01",
                "scope": "PROJECT",
                "name": "TEST_PROJECT",
                "value": "TEST_PROJECT",
                "description": "",
                "isPassword": False,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            },
            {
                "id": "750c5366-caea-4d1f-ad38-fa6089ea2015",
                "scope": "PIPELINE",
                "name": "BLK1",
                "value": None,
                "description": "This is a new password",
                "isPassword": True,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            }
        ]
    }
