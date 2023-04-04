Stopping a pipeline
-------------------

**saagieapi.pipelines.stop**

Example :

.. code:: python

   saagie.pipelines.stop(pipeline_instance_id="8e9b9f16-4a5d-4188-a967-1a96b88e4358")

Response payload example :

.. code:: python

   {
       "stopPipelineInstance":{
           "id":"0a83faaa-c4e9-4141-82d0-c434fcfb0f10",
           "number":1,
           "status":"KILLING",
           "startTime":"2022-04-28T14:30:17.734Z",
           "endTime":None,
           "pipelineId":"ca79c5c8-2e57-4a35-bcfc-5065f0ee901c"
       }
   }