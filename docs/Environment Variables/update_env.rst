Updating environment variables
--------------------------------------

**saagie.env_vars.update** 

Example :

.. code:: python

   saagieapi.env_vars.update(name="TEST_PASSWORD",
                                         value="new value",
                                         description="This is a new password",
                                         is_password=True,
                                         project_id="50033e21-83c2-4431-a723-d54c2693b964"
                                         )

Response payload example :

.. code:: python

   {
       "saveEnvironmentVariable": {
           "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
       }
   }