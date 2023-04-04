**saagieapi.pipelines.edit**

Editing a pipeline
------------------

Example :

.. code:: python

   saagieapi.pipelines.edit(pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c", name = "Amazing Pipeline 2")

Response payload example :

.. code:: python

   {
       "editPipeline":{
           "id":"ca79c5c8-2e57-4a35-bcfc-5065f0ee901c",
           "name":"Amazing Pipeline 2",
           "description":"",
           "alerting":None,
           "isScheduled":True,
           "cronScheduling":"0 0 1 * *",
           "scheduleTimezone":"UTC"
       }
   }
