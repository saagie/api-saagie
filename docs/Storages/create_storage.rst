Creating a storage
------------------

**saagieapi.storages.create**

Example :

.. code:: python

   saagieapi.storages.create(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                             storage_name="storage name",
                             storage_size="128 MB",
                             storage_description="storage description")

Response payload example :

.. code:: python

   {
       "createVolume":{
           "id":"fdb43a11-ccec-4b10-9690-2b83fbd7eb93",
           "name":"storage name",
           "size":"128 MB",
           "description":"storage description",
           "creationDate":"2022-09-12T13:52:19.523Z",
           "creator":"user.name",
           "linkedApp":"None"
       }
   }
