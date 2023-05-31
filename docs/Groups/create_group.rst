Creating a group
----------

*NB: You can only use this function if you have the admin role on the platform.*

**saagieapi.groups.create**

Example :

.. code:: python

   saagieapi.groups.create(group_name="group_reader",
                           users=["user1", "user2"]
                          )

Response payload example :

.. code:: python

   True