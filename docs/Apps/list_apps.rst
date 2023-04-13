Listing apps for a project
-----------------------

**saagieapi.apps.list_for_project**

Example :

.. code:: python

   saagieapi.apps.list_for_project(project_id="your_project_id")

**Since version 2.0.0**:

Response payload example :

.. code:: python

   {
       'project': {
           'apps': [
               {
                   'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                   'name': 'Jupyter Notebook',
                   'description': '',
                   'creationDate': '2022-02-23T08:50:24.326Z',
                   'creator': 'user.test',
                   'versions': [
                       {
                           'number': 1,
                           'creationDate': '2022-02-23T08:50:24.327Z',
                           'releaseNote': '',
                           'dockerInfo': None,
                           'runtimeContextId': 'jupyter-notebook-v2',
                           'creator': 'user.test',
                           'ports': [
                               {
                                   'name': 'Notebook',
                                   'number': 8888,
                                   'isRewriteUrl': False,
                                   'basePathVariableName': 'SAAGIE_BASE_PATH',
                                   'scope': 'PROJECT',
                                   'internalUrl': 'http://app-d0d6a466-10d9-4120-8101-56e46563e05a:8888'
                               }
                           ],
                           'isMajor': False,
                           'volumesWithPath': [
                               {
                                   'path': '/notebooks-dir',
                                   'volume': {
                                       'id': '68a50c6b-3737-4b68-b033-464eedd02eb1',
                                       'name': 'storage jupyter notebook',
                                       'creator': 'user.test',
                                       'description': 'Automatically created by migration from app 68a50c6b-3737-4b68-b033-464eedd02eb1',
                                       'size': '128 MB',
                                       'projectId': '96a12345-303d-43cf-adb2-a7300d5bb9df',
                                       'creationDate': '2022-02-23T08:50:24.327Z',
                                       'linkedApp': {
                                           'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                                           'name': 'jupyter notebook'
                                       }
                                   }
                               }
                           ]
                       }
                   ],
                   'currentVersion': {
                       'number': 1,
                       'creationDate': '2022-02-23T08:50:24.327Z',
                       'releaseNote': '',
                       'dockerInfo': None,
                       'runtimeContextId': 'jupyter-notebook-v2',
                       'creator': 'user.test',
                       'ports': [
                           {
                               'name': 'Notebook',
                               'number': 8888,
                               'isRewriteUrl': False,
                               'basePathVariableName': 'SAAGIE_BASE_PATH',
                               'scope': 'PROJECT',
                               'internalUrl': 'http://app-d0d6a466-10d9-4120-8101-56e46563e05a:8888'
                           }
                       ],
                       'isMajor': False,
                       'volumesWithPath': [
                           {
                               'path': '/notebooks-dir',
                               'volume': {
                                   'id': '68a50c6b-3737-4b68-b033-464eedd02eb1',
                                   'name': 'storage jupyter notebook',
                                   'creator': 'user.test',
                                   'description': 'Automatically created by migration from app 68a50c6b-3737-4b68-b033-464eedd02eb1',
                                   'size': '128 MB',
                                   'projectId': '96a12345-303d-43cf-adb2-a7300d5bb9df',
                                   'creationDate': '2022-02-23T08:50:24.327Z',
                                   'linkedApp': {
                                       'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                                       'name': 'jupyter notebook'
                                   }
                               }
                           }
                       ]
                   },
                   'technology': {
                       'id': '7d3f247c-b5a9-4a34-a0a2-f6b209bc2b63'
                   },
                   'linkedVolumes': [
                       {
                           'id': '68a50c6b-3737-4b68-b033-464eedd02eb1',
                           'name': 'storage jupyter notebook',
                           'creator': 'user.test',
                           'description': 'Automatically created by migration from app 68a50c6b-3737-4b68-b033-464eedd02eb1',
                           'size': '128 MB',
                           'creationDate': '2022-02-23T08:50:24.327Z'
                       }
                   ],
                   'isGenericApp': False,
                   'history': {
                       'id': 'affea4dd-d894-4742-bbd2-dd3a09c92020',
                       'events': [
                           {
                               'event': {
                                   'recordAt': '2022-06-29T07:40:19.754Z',
                                   'executionId': '5980d8cf-7cb6-4340-bd84-d3d17bdb5ab6'
                               },
                               'transitionTime': '2022-06-29T07:40:19.754Z'
                           },
                           {
                               'event': {
                                   'recordAt': '2022-06-29T07:40:19.974Z',
                                   'executionId': '5980d8cf-7cb6-4340-bd84-d3d17bdb5ab6'
                               },
                               'transitionTime': '2022-06-29T07:40:19.974Z'
                           }
                       ],
                       'runningVersionNumber': 1,
                       'currentDockerInfo': {
                           'image': 'saagie/jupyter-python-nbk:v2-1.95.0',
                           'dockerCredentialsId': None
                       },
                       'currentStatus': 'STOPPED',
                       'currentExecutionId': 'f29c940f-4622-4263-8cec-41ae68513885',
                       'startTime': '2022-06-29T08:14:49.205Z',
                       'stopTime': '2022-06-29T08:19:59.946Z'
                   },
                   'alerting': None,
                   'resources': None
               }
           ]
       }
   }

**Until version 1.1.4:**

.. code:: python

   {
       "labWebApps": [
           {
               "id": "7bf350fc-xxxx-xxxx-xxxx-3bf9298b27fa",
               "name": "test apps",
               "description": "",
               "countJobInstance": 0,
               'instances': [
                   {
                       'id': '56c6b19f-9890-4762-b682-e9c569b3d631',
                       'status': 'KILLED',
                       'statusDetails': None,
                       'startTime': '2022-03-21T11:10:01.497Z',
                       'endTime': '2022-03-25T13:30:14.615Z'
                   },
                   {
                       'id': 'be94118b-7aa9-4aae-8652-93bdc2c5a24f',
                       'status': 'KILLED',
                       'statusDetails': None,
                       'startTime': '2022-03-21T11:09:11.293Z',
                       'endTime': '2022-03-21T11:09:55.46Z'
                   }
               ],
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
                           "image": "saagie/",
                           "dockerCredentialsId": None
                       },
                       "exposedPorts": [],
                       "storagePaths": []
                   }
               ],
               "category": "",
               "technology": {
                   "id": "36912c68-xxxx-xxxx-xxxx-b5ded8eb7b13"
               },
               "alerting": None,
               "creationDate": "2022-04-27T09:48:46.867Z",
               "isDeletable": True,
               "graphPipelines": [],
               "storageSizeInMB": 128,
               "doesUseGPU": False,
               "resources": None
           },
           {
               "id": "7bf350fc-xxxx-xxxx-xxxx-3bf9298b27fa",
               "name": "test apps2",
               "description": "",
               "countJobInstance": 0,
               ..........
               ..........
           }
       ]
   }
