Listing profiles
-----------------------

*NB: You can only use this function if you have the admin role on the platform.*

**saagieapi.profiles.list**

Example :

.. code:: python

   saagieapi.profiles.list()


Response payload example :

.. code:: python

    [
       {
           "login": "test_user",
           "job": "DATA_ENGINEER",
           "email": "test_user@gmail.com"
       },
       {
           "login": "customer_admin",
           "job": None,
           "email": None
       }

   ]

