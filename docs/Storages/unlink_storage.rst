Unlinking a storage
-------------------

**saagieapi.storages.unlink**

Example :

.. code:: python

   saagieapi.storages.unlink(storage_id="fdb43a11-ccec-4b10-9690-2b83fbd7eb93",
                             project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771")

Response payload example :

.. code:: python

   {
       "unlinkVolume":{
           "id":"fdb43a11-ccec-4b10-9690-2b83fbd7eb93",
           "name":"storage new name",
       }
   }