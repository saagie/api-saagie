**saagieapi.apps.create_from_scratch**

Creating app from Docker image
------------------------------

**Since version 2.0.0**:

Example :

.. code:: python

   saagieapi.apps.create_from_scratch(project_id=project_id, app_name="App Example Scratch", image="saagie/ttyd-saagie:1.0", 
                                      exposed_ports=[{"basePathVariableName":"SAAGIE_BASE_PATH",
                                                      "isRewriteUrl":True,
                                                      "scope":"PROJECT",
                                                      "number":7681,
                                                      "name":"ttyd"}])

Response payload example :

.. code:: python

   {'createApp': {'id': '1221f83e-52de-4beb-89a0-1505de4e875f'}}

**Until version 1.1.4**:

Example:

.. code:: python

   saagieapi.apps.create_from_scratch(project_id=project_id, app_name="App Example Scratch", image="saagie/ttyd-saagie:1.0", 
                                      exposed_ports=[{"basePathVariableName":"SAAGIE_BASE_PATH",
                                                      "isRewriteUrl":True,
                                                      "isAuthenticationRequired":True,
                                                      "port":7681,
                                                      "name":"ttyd"}])

Response payload example :

.. code:: python

   {
       "createJob":
           {
               "id": "befeacff-8b3b-4269-bf6d-73b5f369313a",
               "versions": [
                   {
                       "number": 1,
                       "__typename": "JobVersion"
                   }
               ],
               "__typename": "Job"
           }
   }