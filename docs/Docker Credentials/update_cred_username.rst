**saagieapi.docker_credentials.upgrade_for_username**

Upgrading credentials for username
----------------------------------

Example :

.. code:: python

   saagieapi.docker_credentials.upgrade_for_username(project_id="860b8dc8-e734-4c98-b2e7-f9ec32ab4771", username="myuser", password="mypassword")

Response payload example :

.. code:: python

   {
      "updateDockerCredentials":{
         "id":"0cb2662f-84eb-4a7d-93cb-2340f7773bce",
         "registry":None,
         "username":"myuser",
         "lastUpdate":"2022-04-26T14:20:17.138482Z[UTC]"
      }
   }