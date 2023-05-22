Editing a group's permission
--------

**saagieapi.groups.edit_permission**

Example :

.. code:: python

    saagieapi.groups.edit_permission(group_name="group_reader",
                                     authorizations=[
                                         {
                                             "platformId": 1,
                                             "platformName": "Dev",
                                             "permissions": [
                                                 {
                                                     "artifact": {
                                                         "id": "project_id",
                                                         "type": "PROJECT"
                                                     },
                                                     "role": "ROLE_PROJECT_VIEWER"
                                                 }
                                             ]
                                         }
                                     ],
                                     realm_authorization={
                                         "permissions": [
                                             {
                                                 "artifact": {
                                                     "type": "TECHNOLOGY_CATALOG"
                                                 },
                                                 "role": "ROLE_ACCESS"
                                             }
                                        ]
                                     }
                                    )


Response payload example :

.. code:: python

    True

