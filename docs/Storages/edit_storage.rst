**saagieapi.storages.edit**

Editing a storage
-----------------

Example :

.. code:: python

   saagieapi.storages.edit(storage_id="fdb43a11-ccec-4b10-9690-2b83fbd7eb93",
                           storage_name="storage new name",
                           storage_description="storage new description")

Response payload example :

.. code:: python

   {
       "editVolume":{
           "id":"fdb43a11-ccec-4b10-9690-2b83fbd7eb93",
           "name":"storage new name",
       }
   }