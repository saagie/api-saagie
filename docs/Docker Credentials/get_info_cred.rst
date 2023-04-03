**saagieapi.docker_credentials.get_info**

Getting credentials information
-------------------------------

Example :

.. code:: python

   saagieapi.docker_credentials.get_info(project_id="860b8dc8-e734-4c98-b2e7-f9ec32ab4771", credential_id="0cb2662f-84eb-4a7d-93cb-2340f7773bce")

Response payload example :

.. code:: python

   {
      "dockerCredentials":{
         "id":"0cb2662f-84eb-4a7d-93cb-2340f7773bce",
         "registry":None,
         "username":"myuser",
         "lastUpdate":"2022-04-27T08:15:41.023Z",
         "jobs":[
            
         ]
      }
   }
