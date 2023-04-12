Creating pipeline environment variables
--------------------------------------

**saagie.env_vars.create_for_pipeline**

Example :

.. code:: python

   saagieapi.env_vars.create_for_pipeline(pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
                                          name="TEST_PASSWORD",
                                          value="test",
                                          description="This is a password",
                                          is_password=True,
                                          )

Response payload example :

.. code:: python

    {
        "saveEnvironmentVariable": {
            "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
        }
    }
