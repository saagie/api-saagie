Creating an user
----------

*NB: You can only use this function if you have the admin role on the platform.*

**saagieapi.users.create**

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