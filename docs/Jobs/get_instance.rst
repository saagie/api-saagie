Getting job instance information
------------

**saagieapi.jobs.get_instance**

Example :

.. code:: python

   saagieapi.jobs.get_instance(job_instance_id="befe73b2-81ab-418f-bc2f-9d012102a895")

Response payload example :

.. code:: python

   {
       "jobInstance":{
           "id":"befe73b2-81ab-418f-bc2f-9d012102a895",
           "number": 1,
           "status":"SUCCEEDED",
           "startTime": "2022-04-19T13:45:49.783Z",
           "endTime": "2022-04-19T13:45:57.388Z",
           "jobId": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
           "version":{
               "number": 1,
               "releaseNote":"",
               "runtimeVersion":"3.7",
               "commandLine":"python {file} arg1 arg2",
               "isMajor":False,
               "isCurrent":True
           }
       }
   }