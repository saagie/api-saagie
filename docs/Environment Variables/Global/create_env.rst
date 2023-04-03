**saagie.env_vars.create_global**

Creating global environment variables
-------------------------------------

Example :

.. code:: python

   saagieapi.env_vars.create_global(
       name="TEST_PASSWORD",
       value="test",
       description="This is a password",
       is_password=True
   )

Response payload example :

.. code:: python

   {
       "saveEnvironmentVariable": {
           "id": "069f3bf2-da1a-4106-acb4-3c7cc37367a3"
       }
   }