Creating app from catalog
-------------------------

**saagieapi.apps.create_from_catalog**

**Since version 2.0.0**:

Example :

.. code:: python

   saagieapi.apps.create_from_catalog(project_id=your_project_id, context="7.15.1", technology_name="kibana")

Response payload example :

.. code:: python

   {
       'installApp': {
           'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e',
           'name': 'Kibana'
       }
   }


**Until version 1.1.4**:

Example :

.. code:: python

   saagieapi.apps.create_from_catalog(project_id=your_project_id, app_name="App_Example_Scratch",
                                      technology="Kibana", technology_catalog="Saagie",
                                      context="7.6.2" )

Response payload example :

.. code:: python

   {
       "createJob": {
           "id": "2606b940-3537-40ac-8f3c-9f3f383b6bfe",
           "versions": [
               {
                   "number": 1,
                   "__typename": "JobVersion"
               }
           ],
           "__typename": "Job"
       }
   }
