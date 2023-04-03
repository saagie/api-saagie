**saagieapi.apps.run**

Running an app
--------------

Example :

.. code:: python

   saagieapi.apps.run(app_id="a6de6956-4038-493e-bbd3-f7b3616df39e")

**Since version 2.0.0**:

Response payload example :

.. code:: python

   {'runApp': {'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e',
     'versions': [{'number': 1}],
     'history': {'id': 'ba494615-88b7-4c54-ad57-34a90461c407',
      'currentDockerInfo': {'image': 'saagie/kibana:7.15.1-1.108.0',
       'dockerCredentialsId': None},
      'runningVersionNumber': 1,
      'currentStatus': 'STOPPED'}}}

**Until version 1.1.4**:

.. code:: python

   {
       "runJob":
       {
           "id": "6bd314a7-f929-4e55-ab1e-0ade7d91a607",
           "status": "REQUESTED"
       }
   }