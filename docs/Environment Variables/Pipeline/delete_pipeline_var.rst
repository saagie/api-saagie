Deleting pipeline environment variables
--------------------------------------

**saagie.env_vars.delete_for_pipeline**

Example :

.. code:: python

   saagieapi.env_vars.delete_for_pipeline(pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
                                          name="TEST_PASSWORD",
                                          )

Response payload example :

.. code:: python

   {
       "deleteEnvironmentVariable": True
   }