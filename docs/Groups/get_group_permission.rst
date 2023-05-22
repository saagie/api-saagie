Getting group's permissions information
--------

**saagieapi.groups.get_permission**

*NB: You can only use this function if you have the admin role on the platform.*

Example :

.. code:: python

    saagieapi.groups.get_permission(group_name="test_group")

Response payload example :

.. code:: python

    {
      "name": "test_group",
      "role": "ROLE_READER",
      "authorizations": [
        {
          "platformId": 1,
          "platformName": "Dev",
          "permissions": [
            {
              "artifact": {
                "type": "PROJECTS_ENVVAR_EDITOR"
              },
              "role": "ROLE_PROJECT_ENVVAR_EDITOR"
            },
            {
              "artifact": {
                "id": "87ad5abb-5ee9-4e7d-8c82-5b40378ad931",
                "type": "PROJECT"
              },
              "role": "ROLE_PROJECT_MANAGER"
            }
          ]
        }
      ],
      "protected": False,
      "realmAuthorization": {
        "permissions": [
          {
            "artifact": {
              "type": "TECHNOLOGY_CATALOG"
            },
            "role": "ROLE_ACCESS"
          }
        ]
      }
    }