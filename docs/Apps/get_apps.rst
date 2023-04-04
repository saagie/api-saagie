**saagieapi.apps.get_info**

Getting apps information
------------------------

Example :

.. code:: python

   saagieapi.apps.get_info(app_id = your_app_id)

**Since version 2.0.0**:

Response payload example :

.. code:: python

   {'app': {'id': 'b6e846d7-d871-46db-b858-7d39d6b60123',
            'name': 'Jupyter lab',
            'creationDate': '2022-05-09T14:12:31.819Z',
            'technology': {'id': '7d3f247c-b5a9-4a34-a0a2-f6b209bc2b63'},
            'project': {'id': '96a74193-303d-43cf-adb2-a7300d5bb9df',
                        'name': 'Saagie testing tool '},
            'description': '',
            'currentVersion': {'number': 1,
                               'creator': 'toto.hi',
                               'creationDate': '2022-05-09T14:12:31.819Z',
                               'releaseNote': 'First version of Jupyter Notebook with Spark 3.1 into Saagie.',
                               'dockerInfo': None,
                               'runtimeContextId': 'jupyter-spark-3.1',
                               'ports': [{'name': 'Notebook',
                                          'number': 8888,
                                          'isRewriteUrl': False,
                                          'basePathVariableName': 'SAAGIE_BASE_PATH',
                                          'scope': 'PROJECT',
                                          'internalUrl': 'http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8888'},
                                         {'name': 'SparkUI',
                                          'number': 8080,
                                          'isRewriteUrl': False,
                                          'basePathVariableName': 'SPARK_UI_PATH',
                                          'scope': 'PROJECT',
                                          'internalUrl': 'http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8080'}],
                               'volumesWithPath': [{'path': '/notebooks-dir',
                                                    'volume': {'id': 'c163216a-b024-4cb1-8aae-0664bf2f58b4',
                                                               'name': 'storage Jupyter lab',
                                                               'creator': 'toto.hi',
                                                               'description': 'Automatically created by migration from app c163216a-b024-4cb1-8aae-0664bf2f58b4',
                                                               'size': '128 MB',
                                                               'projectId': '96a74193-303d-43cf-adb2-a7300d5bb9df',
                                                               'creationDate': '2022-05-09T14:12:31.819Z',
                                                               'linkedApp': {'id': 'b6e846d7-d871-46db-b858-7d39d6b60146',
                                                                             'name': 'Jupyter lab'}}}],
                               'isMajor': False},
            'history': {'id': '4f60dd23-4ec2-4996-b4da-d95376d72387',
                        'currentStatus': 'STARTED',
                        'currentExecutionId': 'f2d81d93-e1ae-4b09-a77e-4e50c13971ce',
                        'currentDockerInfo': {'image': 'saagie/jupyter-python-nbk:pyspark-3.1.1-1.111.0',
                                              'dockerCredentialsId': None},
                        'startTime': '2022-09-21T09:47:27.342Z',
                        'events': [{'event': {'recordAt': '2022-06-21T12:57:22.734Z',
                                              'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                              'versionNumber': 1,
                                              'author': 'user.test'}},
                                   {'event': {'recordAt': '2022-06-21T12:57:22.9Z',
                                              'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                              'status': 'STARTING'}},
                                   {'event': {'recordAt': '2022-06-21T12:57:35.443Z',
                                              'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                              'status': 'STARTED'}},
                                   {'event': {'recordAt': '2022-06-24T14:28:01.647Z',
                                              'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                              'author': 'user.test'}},
                                   {'event': {'recordAt': '2022-06-24T14:28:01.726Z',
                                              'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                              'status': 'STOPPING'}},
                                   {'event': {'recordAt': '2022-06-24T14:28:01.81Z',
                                              'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                              'status': 'STOPPED'}},
                                   {'event': {'recordAt': '2022-06-29T07:41:41.713Z',
                                              'executionId': '9e525435-684f-470e-9818-fb865776da09',
                                              'versionNumber': 1,
                                              'author': 'user.test'}},
                                   {'event': {'recordAt': '2022-06-29T07:41:41.912Z',
                                              'executionId': '9e525435-684f-470e-9818-fb865776da09',
                                              'status': 'STARTING'}},
                                   {'event': {'recordAt': '2022-06-29T07:48:22.359Z',
                                              'executionId': '9e525435-684f-470e-9818-fb865776da09',
                                              'status': 'STARTED'}}
                                   ]},
            'isGenericApp': False,
            'alerting': None,
            'resources': None,
            'linkedVolumes': [{'size': '128 MB'}]}}

**Until version 1.1.4**:

.. code:: python

   {
       "labWebApp":
           {
               "id": "your_app_id",
               "name": "test apps",
               "description": "",
               "countJobInstance": 2,
               'instances': [{'id': '56c6b19f-9890-4762-b682-e9c569b3d631',
                              'status': 'KILLED',
                              'statusDetails': None,
                              'startTime': '2022-03-21T11:10:01.497Z',
                              'endTime': '2022-03-25T13:30:14.615Z'},
                             {'id': 'be94118b-7aa9-4aae-8652-93bdc2c5a24f',
                              'status': 'KILLED',
                              'statusDetails': None,
                              'startTime': '2022-03-21T11:09:11.293Z',
                              'endTime': '2022-03-21T11:09:55.46Z'}],
               "versions": [
                   {
                       "number": 1,
                       "creationDate": "2022-04-27T09:48:46.867Z",
                       "releaseNote": "",
                       "runtimeVersion": None,
                       "commandLine": None,
                       "isMajor": False,
                       "isCurrent": True,
                       "dockerInfo": {
                           "image": "saagie/xxxx",
                           "dockerCredentialsId": None
                       },
                       "exposedPorts": [],
                       "storagePaths": []
                   }
               ],
               "category": "",
               "technology": {"id": "36912c68-xxxx-xxxx-xxxx-b5ded8eb7b13"},
               "alerting": None,
               "creationDate": "2022-04-27T09:48:46.867Z",
               "isDeletable": True,
               "graphPipelines": [],
               "storageSizeInMB": 128,
               "doesUseGPU": False,
               "resources": None
           }
   }