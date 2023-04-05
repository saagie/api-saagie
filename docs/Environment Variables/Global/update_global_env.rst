Updating global environment variables
-------------------------------------

**saagie.env_vars.update_global**

Example :

.. code:: python

   saagieapi.env_vars.update_global(name="TEST_PASSWORD",
                                    value="new value",
                                    description="This is a new password",
                                    is_password=True
                                    )

Response payload example :

.. code:: python

   {
       "saveEnvironmentVariable": {
           "id": "069f3bf2-da1a-4106-acb4-3c7cc37367a3"
       }
   }
