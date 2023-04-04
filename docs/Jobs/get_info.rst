Getting job information
--------

**saagieapi.jobs.get_info**

Example :

.. code:: python

   saagieapi.jobs.get_info(job_id="f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
                           instances_limit=2)

Response payload example :

.. code:: python

   {
       "job": {
           "id": "f5fce22d-2152-4a01-8c6a-4c2eb4808b6d",
           "name": "Python test job",
           "description": "Amazing python job",
           "alerting": None,
           "countJobInstance": 5,
           "instances": [
               {
                   "id": "61f6175a-fd38-4fac-9fa9-a7b63554f14e",
                   "status": "SUCCEEDED",
                   "startTime": "2022-04-19T13:46:40.045Z",
                   "endTime": "2022-04-19T13:46:47.708Z",
                   "version": {
                       "number": 1,
                       "releaseNote": "",
                       "runtimeVersion": "3.7",
                       "commandLine": "python {file} arg1 arg2",
                       "isMajor": False,
                       "doesUseGPU": False
                   }
               },
               {
                   "id": "befe73b2-81ab-418f-bc2f-9d012102a895",
                   "status": "SUCCEEDED",
                   "startTime": "2022-04-19T13:45:49.783Z",
                   "endTime": "2022-04-19T13:45:57.388Z",
                   "version":{
                       "number": 1,
                       "releaseNote": "",
                       "runtimeVersion": "3.7",
                       "commandLine": "python {file} arg1 arg2",
                       "isMajor": False,
                       "doesUseGPU": False
                   }
               }
           ],
           "versions": [
               {
                   "number": 1,
                   "creationDate": "2022-04-26T08:16:20.681Z",
                   "releaseNote": "",
                   "runtimeVersion": "3.7",
                   "commandLine": "python {file} arg1 arg2",
                   "packageInfo": {
                       "name": "test.py",
                       "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/f5fce22d-2152-4a01-8c6a-4c2eb4808b6d/version/1/artifact/test.py"
                   },
                   "dockerInfo": None,
                   "extraTechnology": None,
                   "isCurrent": True,
                   "isMajor": False
               }
           ],
           "category": "Extraction",
           "technology": {
               "id": "0db6d0a7-ad4b-45cd-8082-913a192daa25"
           },
           "isScheduled": False,
           "cronScheduling": None,
           "scheduleStatus": None,
           "scheduleTimezone": "UTC",
           "isStreaming": False,
           "creationDate": "2022-04-26T08:16:20.681Z",
           "migrationStatus": None,
           "migrationProjectId": None,
           "isDeletable": True,
           "graphPipelines": [],
           "doesUseGPU": False,
           "resources": None
       }
   }