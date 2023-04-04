Deleting a storage
------------------

**saagieapi.storages.delete**

Example :

.. code:: python

   saagieapi.storages.delete(storage_id="fdb43a11-ccec-4b10-9690-2b83fbd7eb93",
                             project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771")

Response payload example :

.. code:: python

   {
       "deleteVolume":{
           "id":"fdb43a11-ccec-4b10-9690-2b83fbd7eb93",
           "name":"storage new name",
       }
   }