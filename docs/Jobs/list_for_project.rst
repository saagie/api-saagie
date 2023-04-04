Listing jobs for a project
-------------

**saagieapi.jobs.list_for_project**

Example :

.. code:: python

   saagieapi.jobs.list_for_project(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771", instances_limit=2)

Response payload example :

.. code:: python

   {
       "jobs": [
           {
               "id": "fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10",
               "name": "Python test job 1",
               "description": "Amazing python job",
               "alerting": None,
               "countJobInstance": 0,
               "instances": [],
               "versions": [
                   {
                       "number": 1,
                       "creationDate": "2022-04-26T12:08:15.286Z",
                       "releaseNote": "",
                       "runtimeVersion": "3.7",
                       "commandLine": "python {file} arg1 arg2",
                       "packageInfo": {"name": "_tmp_test.py",
                                       "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10/version/1/artifact/_tmp_test.py"},
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
               "scheduleTimezone": "UTC",
               "scheduleStatus": None,
               "isStreaming": False,
               "creationDate": "2022-04-26T12:08:15.286Z",
               "migrationStatus": None,
               "migrationProjectId": None,
               "isDeletable": True,
               "pipelines": [],
               "graphPipelines": [],
               "doesUseGPU": False,
               "resources": None
           },
           {
               "id": "e92ed170-50d6-4041-bba9-098a8e16f444",
               "name": "Python test job 2",
               "description": "Amazing python job 2",
               "alerting": None,
               "countJobInstance": 2,
               "instances": [
                   {
                       "id": "61f6175a-fd38-4fac-9fa9-a7b63554f14e",
                       "status": "SUCCEEDED",
                       "startTime": "2022-04-19T13:46:40.045Z",
                       "endTime": "2022-04-19T13:46:47.708Z"
                   },
                   {
                       "id": "befe73b2-81ab-418f-bc2f-9d012102a895",
                       "status": "SUCCEEDED",
                       "startTime": "2022-04-19T13:45:49.783Z",
                       "endTime": "2022-04-19T13:45:57.388Z"
                   }
               ],
               "versions": [
                   {
                       "number": 1,
                       "creationDate": "2022-04-19T13:13:09.091Z",
                       "releaseNote": "",
                       "runtimeVersion": "3.7",
                       "commandLine": "python {file} arg1 arg2",
                       "packageInfo": {"name": "test.py",
                                       "downloadUrl": "/projects/api/platform/6/project/860b8dc8-e634-4c98-b2e7-f9ec32ab4771/job/e92ed170-50d6-4041-bba9-098a8e16f444/version/1/artifact/test.py"},
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
               "scheduleTimezone": "UTC",
               "scheduleStatus": None,
               "isStreaming": False,
               "creationDate": "2022-04-19T13:13:09.091Z",
               "migrationStatus": None,
               "migrationProjectId": None,
               "isDeletable": True,
               "pipelines": [],
               "graphPipelines": [],
               "doesUseGPU": False,
               "resources": None
           }
       ]
   }

