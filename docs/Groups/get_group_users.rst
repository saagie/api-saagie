Getting group's users information
--------

**saagieapi.groups.get_users**

*NB: You can only use this function if you have the admin role on the platform.*

Example :

.. code:: python

    saagieapi.groups.get_users(group_name="test_group")

Response payload example :

.. code:: python

    {
      "name": "test_group",
      "users": ["test_user"],
      "protected": False
    }