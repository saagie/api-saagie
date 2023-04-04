.. _stop job 

Stop Job
--------

**saagieapi.jobs.stop**

Example :

.. code:: python

   saagieapi.jobs.stop(job_instance_id="8e9b9f16-4a5d-4188-a967-1a96b88e4358")

Response payload example :

.. code:: python

   {
       "stopJobInstance":{
           "id":"8e9b9f16-4a5d-4188-a967-1a96b88e4358",
           "number":17,
           "status":"KILLING",
           "startTime":"2022-04-29T08:38:49.344Z",
           "endTime":None,
           "jobId":"e92ed472-50d6-4041-bba9-098a8e16f444"
       }
   }