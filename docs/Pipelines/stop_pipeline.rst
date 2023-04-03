**saagieapi.pipelines.stop**

Stopping a pipeline
-------------------

Example :

.. code:: python

   pipeline_instance_id = saagieapi.pipelines.run(pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c")
   saagie.pipelines.stop(pipeline_instance_id )

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