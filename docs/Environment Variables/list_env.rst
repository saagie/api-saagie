Listing environment variables
=============================

**saagie.env_vars.list**
------------------------ 

Get environment variables
NB: You can only list environment variables if you have at least the
viewer role on the project

Parameters :
~~~~~~~~~~~~
    **scope** :
        | Type : str
        | Expected values : GLOBAL, PROJECT, PIPELINE
    **project_id** :
        | Type : str
        | Default value : None
    **pipeline_id** :
        | Type : str
        | Default value : None
    **scope_only** :
        | Type : bool
        | Default value : False
    **pprint_result** :
        | Type : Optional[bool]
        | Default value : None

Example :
~~~~~~~~~

.. code:: python

   saagieapi.env_vars.list(scope='GLOBAL')

Response payload example :
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    {
        "globalEnvironmentVariables": [
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
                "name": "PORT_WEBHDFS",
                "scope": "GLOBAL",
                "value": "50070",
                "description": "",
                "isPassword": False,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            }
        ]
    }
