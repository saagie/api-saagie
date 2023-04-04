**saagieapi.repositories.get_info**

Getting repository information
------------------------------

Example :

.. code:: python

   saagieapi.repositories.get_info(repository_id="9fcbddfe-a7b7-4d25-807c-ad030782c923")

Response payload example :

.. code:: python

   {'repository': {'creationDate': '2020-07-28T08:14:03.134Z',
                   'creator': 'Saagie',
                   'editor': 'Saagie',
                   'id': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
                   'modificationDate': '2020-07-28T08:14:03.134Z',
                   'name': 'Saagie',
                   'readOnly': True,
                   'source': {'url': 'https://github.com/saagie/technologies/releases/latest/download/technologies.zip'},
                   'synchronizationReports': {'count': 6,
                                              'list': [{'source': {'url': 'https://github.com/saagie/technologies/releases/latest/download/technologies.zip'},
                                                        'endedAt': '2022-09-12T10:27:44.549Z',
                                                        'startedAt': '2022-09-12T10:27:44.549Z',
                                                        'trigger': {'author': 'hello.world', 'type': 'MANUAL'},
                                                        'technologyReports': [
                                                            {'status': 'UNCHANGED', 'technologyId': 'java-scala', 'message': None},
                                                            {'status': 'UNCHANGED', 'technologyId': 'python', 'message': None},
                                                            {'status': 'UNCHANGED', 'technologyId': 'r', 'message': None},
                                                            {'status': 'UNCHANGED', 'technologyId': 'spark', 'message': None},
                                                            {'status': 'UNCHANGED', 'technologyId': 'sqoop', 'message': None},
                                                            {'status': 'UNCHANGED', 'technologyId': 'talend', 'message': None}],
                                                        'issues': [],
                                                        'revert': None}],
                                              'lastReversibleId': 'a17c73ed-fca1-4f25-a343-914c7ac23bae'},
                   'connectionTypes': [{'id': '5b4b8ffb-9228-4f7a-9d39-67fd3c2862d3',
                                        'label': 'AWS Connection',
                                        'actions': {'checkConnection': {'scriptId': '9359e392-58a0-42db-9ce9-b68679aa9131'}}}],
                   'technologies': [
                       {'id': '1bf79f1d-7e2d-4daf-976d-8702114ab507',
                        'technologyId': 'generic',
                        'label': 'Generic',
                        'icon': 'docker',
                        'repositoryId': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
                        'available': True,
                        'missingFacets': [],
                        'description': 'A generic Docker image that can be used to execute code in a Docker container.',
                        'contexts': [{'id': 'docker',
                                      'label': 'Docker',
                                      'available': True,
                                      'missingFacets': [],
                                      'description': None,
                                      'recommended': False,
                                      'dockerInfo': None,
                                      'trustLevel': 'Stable',
                                      'deprecationDate': None,
                                      'lastUpdate': '2022-02-21T14:35:41.692Z'}]},
                       {'id': 'db34c9b9-47c7-4dc6-8c3c-2d8ccf5afa11',
                        'technologyId': 'aws-lambda',
                        'label': 'AWS Lambda',
                        'icon': 'aws-lambda',
                        'repositoryId': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
                        'available': True,
                        'missingFacets': [],
                        'description': 'Run code without thinking about servers. Pay only for the compute time you consume',
                        'iconUrl': None,
                        'contexts': [{'id': 'functions',
                                      'label': 'Functions',
                                      'available': True,
                                      'missingFacets': [],
                                      'description': 'AWS Lambda Functions',
                                      'recommended': False,
                                      'trustLevel': 'Experimental',
                                      'deprecationDate': None,
                                      'lastUpdate': '2022-08-31T13:05:32.031Z',
                                      'connectionTypeUUID': '5b4b8ffb-9228-4f7a-9d39-67fd3c2862d3',
                                      'actions': {'getStatus': {'scriptId': '50794533-091b-4d66-9463-96f0ce255785'},
                                                  'start': {'scriptId': '50794533-091b-4d66-9463-96f0ce255785'},
                                                  'stop': None,
                                                  'getLogs': {'scriptId': '50794533-091b-4d66-9463-96f0ce255785'}}}]}]}}