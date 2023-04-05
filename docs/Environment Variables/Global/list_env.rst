Listing global environment variables
------------------------------------

**saagie.env_vars.list_globals**

Example :

.. code:: python

   saagieapi.env_vars.list_globals()

Response payload example :

.. code:: python

   {
       "globalEnvironmentVariables": [
           {
               "id": "334c2e0e-e8ea-4639-911e-757bf36bc91b",
               "name": "TEST_PASSWORD",
               "scope": "GLOBAL",
               "value": None,
               "description": "This is a password",
               "isPassword": True
           },
           {
               "id": "eb430066-551a-47f3-97c6-e56a9272fbd0",
               "name": "PORT_WEBHDFS",
               "scope": "GLOBAL",
               "value": "50070",
               "description": "",
               "isPassword": False
           }
       ]
   }
