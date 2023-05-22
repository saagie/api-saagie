Listing groups
-----------------------

**saagieapi.groups.list**

*NB: You can only use this function if you have the admin role on the platform.*

Example :

.. code:: python

   saagieapi.groups.list()


Response payload example :

.. code:: python

    [
       {
           "name": "administrators",
           "protected": True
       },
       {
           "name": "test_group",
           "protected": False
       }
   ]

