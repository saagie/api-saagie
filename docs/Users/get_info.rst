Getting user information
--------

*NB: You can only use this function if you have the admin role on the platform.*

**saagieapi.users.get_info**

Example :

.. code:: python

    saagieapi.users.get_info(user_name="test_user")

Response payload example :

.. code:: python

    {
       "login": "test_user",
       "roles": [
           "ROLE_READER"
       ],
       "platforms": [],
       "groups": [
           "test_group"
       ],
       "protected": False
    }