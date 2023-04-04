.. _Listing Projects

Listing projects
----------------

**saagieapi.projects.list**

Example :

.. code:: python

   saagieapi.projects.list()

Response payload example :

.. code:: python

   {
       "projects":[
           {
               "id":"8321e13c-892a-4481-8552-5be4d6cc5df4",
               "name":"Project A",
               "creator":"john.doe",
               "description":"My project A",
               "jobsCount":49,
               "status":"READY"
           },
           {
               "id":"33b70e1b-3111-4376-a839-12d2f93c323b",
               "name":"Project B",
               "creator":"john.doe",
               "description":"My project B",
               "jobsCount":1,
               "status":"READY"
           }
       ]
   }