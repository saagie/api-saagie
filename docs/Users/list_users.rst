Listing users
-----------------------

*NB: You can only use this function if you have the admin role on the platform.*

**saagieapi.users.list**

Example :

.. code:: python

   saagieapi.users.list()


Response payload example :

.. code:: python

    [
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
       },
       {
           "login": "customer_admin",
           "roles": [
               "ROLE_ADMIN"
           ],
           "platforms": [],
           "groups": [
               "administrators"
           ],
           "protected": True
       }
   ]

