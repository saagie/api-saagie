Listing credentials
-------------------

**saagieapi.docker_credentials.list_for_project**

Example :

.. code:: python

   saagieapi.docker_credentials.list_for_project(project_id="860b8dc8-e734-4c98-b2e7-f9ec32ab4771")

Response payload example :

.. code:: python

   {
       "allDockerCredentials":[
           {
               "id":"0cb2662f-84eb-4a7d-93cb-2340f7773bce",
               "registry":None,
               "username":"myuser",
               "lastUpdate":"2022-04-26T14:20:17.118Z",
               "jobs":[]
           }
       ]
   }