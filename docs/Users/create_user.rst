Creating an user
----------

**saagieapi.users.create**

*NB: You can only use this function if you have the admin role on the platform.*

Example :

.. code:: python

   saagieapi.users.create(user_name="user_reader",
                          password="A123456#a",
                          roles=["ROLE_READER"],
                          groups=["reader_group"]
                         )

Response payload example :

.. code:: python

   True