Deleting project environment variables
--------------------------------------

**saagie.env_vars.delete_for_project** *(deprecated)*

Example :

.. code:: python

   saagieapi.env_vars.delete_for_project(name="TEST_PASSWORD",
                                         project_id="50033e21-83c2-4431-a723-d54c2693b964"
                                         )

Response payload example :

.. code:: python

   {
       "deleteEnvironmentVariable": True
   }
