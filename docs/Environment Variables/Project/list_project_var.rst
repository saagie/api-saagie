Listing project environment variables
-------------------------------------

**saagie.env_vars.list_for_project** *(deprecated)*

Example :

.. code:: python

    saagieapi.env_vars.list_for_project(project_id="50033e21-83c2-4431-a723-d54c2693b964")

Response payload example :

.. code:: python

    {
        "projectEnvironmentVariables": [
            {
                "id": "334c2e0e-e8ea-4639-911e-757bf36bc91b",
                "name": "TEST_PASSWORD",
                "scope": "GLOBAL",
                "value": None,
                "description": "This is a password",
                "isPassword": True,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            },
            {
                "id": "eb430066-551a-47f3-97c6-e56a9272fbd0",
                "name": "RSTUDIO_ADMIN_USER",
                "scope": "PROJECT",
                "value": "rstudio",
                "description": "",
                "isPassword": False
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            }
        ]
    }
