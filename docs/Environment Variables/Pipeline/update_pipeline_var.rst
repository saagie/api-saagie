Updating pipeline environment variables
--------------------------------------

**saagie.env_vars.update_for_pipeline** *(deprecated)*

Example :

.. code:: python

    saagie_api.env_vars.update_for_pipeline(pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1", 
                                            name="TEST_PASSWORD",
                                            new_name="TEST_PWD",
                                            value="new value",
                                            description="This is a new password",
                                            is_password=True,
                                            )

Response payload example :

.. code:: python

    {
        "saveEnvironmentVariable": {
            "id": "750c5366-caea-4d1f-ad38-fa6089ea2015"
        }
    }
