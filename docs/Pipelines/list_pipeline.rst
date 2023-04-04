**saagieapi.pipelines.list_for_project**

Listing pipelines for a project
-------------------------------


Example :

.. code:: python

   saagieapi.pipelines.list_for_project(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771")

Response payload example :

.. code:: python

   {
       "project": {
           "pipelines": [
               {
                   "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                   "name": "Pipeline A",
                   "description": "My Pipeline A",
                   "alerting": None,
                   "pipelineInstanceCount": 0,
                   "instances": [],
                   "versions": [{"number": 1,
                                 "releaseNote": None,
                                 "graph": {"jobNodes": [{"id": "00000000-0000-0000-0000-000000000000",
                                                         "job": {"id": "6f56e714-37e4-4596-ae20-7016a1d954e9", "name": "Spark 2.4 java"},
                                                         "position": None,
                                                         "nextNodes": ["00000000-0000-0000-0000-000000000001"]},
                                                        {"id": "00000000-0000-0000-0000-000000000001",
                                                         "job": {"id": "6ea1b022-db8b-4af7-885b-56ddc9ba764a", "name": "bash"},
                                                         "position": None,
                                                         "nextNodes": []}],
                                           "conditionNodes": []},
                                 "creationDate": "2022-01-31T10:36:42.327Z",
                                 "creator": "john.doe",
                                 "isCurrent": True,
                                 "isMajor": False
                                 }],
                   "creationDate": "2022-01-31T10:36:42.327Z",
                   "creator": "john.doe",
                   "isScheduled": False,
                   "cronScheduling": None,
                   "scheduleStatus": None,
                   "scheduleTimezone": "UTC",
                   "isLegacyPipeline": False
               },
               {
                   "id": "9a2642df-550c-4c69-814f-1008f177b0e1",
                   "name": "Pipeline B",
                   "description": None,
                   "alerting": None,
                   "pipelineInstanceCount": 2,
                   "instances": [
                       {
                           "id": "cc11c32a-66c5-43ad-b176-444cee7079ff",
                           "status": "SUCCEEDED",
                           "startTime": "2022-03-15T11:42:07.559Z",
                           "endTime": "2022-03-15T11:43:17.716Z"
                       },
                       {
                           "id": "d7aba110-3bd9-4505-b70c-84c4d212345",
                           "status": "SUCCEEDED",
                           "startTime": "2022-02-04T00:00:00.062Z",
                           "endTime": "2022-02-04T00:00:27.249Z"
                       }
                   ],
                   "versions": [{"number": 1,
                                 "releaseNote": None,
                                 "graph": {"jobNodes": [{"id": "00000000-0000-0000-0000-000000000002",
                                                         "job": {"id": "6f56e714-37e4-4596-ae20-7016a1d459e9", "name": "Job test 1"},
                                                         "position": None,
                                                         "nextNodes": ["00000000-0000-0000-0000-000000000001"]},
                                                        {"id": "00000000-0000-0000-0000-000000000003",
                                                         "job": {"id": "6ea1b022-db8b-4af7-885b-56ddc9ba647a", "name": "Job test 2"},
                                                         "position": None,
                                                         "nextNodes": []}],
                                           "conditionNodes": []},
                                 "creationDate": "2022-02-03T14:41:39.422Z",
                                 "creator": "john.doe",
                                 "isCurrent": True,
                                 "isMajor": False
                                 }],
                   "creationDate": "2022-02-03T14:41:39.422Z",
                   "creator": "john.doe",
                   "isScheduled": False,
                   "cronScheduling": None,
                   "scheduleStatus": None,
                   "scheduleTimezone": "UTC",
                   "isLegacyPipeline": False
               }
           ]
       }
   }