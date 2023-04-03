.. _Getting project information

Getting project information
---------------------------

**saagieapi.projects.get_info**

Example :

.. code:: python

   saagieapi.projects.get_info("8321e13c-892a-4481-8552-5be4d6cc5df4")

Response payload example :

.. code:: python

   {
      "project":{
         "name":"Project A",
         "creator":"john.doe",
         "description":"My project A",
         "jobsCount":49,
         "status":"READY"
      }
   }