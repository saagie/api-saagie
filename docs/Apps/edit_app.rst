Editing an app
--------------

**saagieapi.apps.edit**

Example :

.. code:: python

   saagieapi.apps.edit(app_id="a6de6956-4038-493e-bbd3-f7b3616df39e",
                       app_name="App_Example_Catalog_modify",
                       emails=["hello.world@gmail.com"],
                       status_list=["FAILED"])

**Since version 2.0.0**:

Response payload example :

.. code:: python

   {
       'editApp': {
           'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e'
       }
   }
**Until version 1.1.4**:

.. code:: python

   {
       "editJob": {
           "id": "befeacff-8b3b-4269-bf6d-73b5f369313a",
           "name": "App_Example_Scratch_modify",
           "description": "",
           "creationDate": "2022-04-28T10:33:22.329Z",
           "technology": {
               "id": "36912c68-d084-43b9-9fda-b5ded8eb7b13"
           },
           "alerting": None
       }
   }