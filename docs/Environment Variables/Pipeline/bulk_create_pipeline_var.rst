Bulk creating pipeline environment variables
--------------------------------------

**saagie.env_vars.bulk_create_for_pipeline**

Example :

.. code:: python

    saagie_api.env_vars.bulk_create_for_pipeline(pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1", 
                                                 env_vars={"BULK1": "HELLO", "BULK2": "WORLD"}
                                                 )

Response payload example :

.. code:: python

    {
        "replaceEnvironmentVariablesByRawForScope": [
            {
                "id": "750c5366-caea-4d1f-ad38-fa6089ea2015",
                "scope": "PIPELINE",
                "name": "BULK1",
                "value": "HELLO"
            },
            {
                "id": "ce5f098e-4750-40b1-8c10-11b118ebc23a",
                "scope": "PIPELINE",
                "name": "BULK2",
                "value": "WORLD"
            }
        ]
    }
