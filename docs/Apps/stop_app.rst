Stopping an app
---------------

**saagieapi.apps.stop**

**Since version 2.0.0**:

Example :

.. code:: python

   saagie_api.apps.stop(app_id = "a6de6956-4038-493e-bbd3-f7b3616df39e")

Response payload example :

.. code:: python

   {
       'stopApp': {
           'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e',
           'history': {
               'id': 'ba494615-88b7-4c54-ad57-34a90461c407',
               'runningVersionNumber': 1,
               'currentStatus': 'STARTED'
           }
       }
   }


**Until version 1.1.4**:

Example :

.. code:: python

   saagie_api.apps.stop(app_instance_id=your_app_instance_id)

Response payload example :

.. code:: python

   {
       "stopJobInstance": {
           "id": "9a9b5ff1-b97d-4a81-adc2-a3e392647a8f",
           "number": 1,
           "status": "KILLING",
           "startTime": "2022-04-28T10:48:35.331Z",
           "endTime": None,
           "jobId": "2606b940-3537-40ac-8f3c-9f3f383b6bfe"
       }
   }