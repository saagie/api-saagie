**saagieapi.repositories.synchronize** 

Synchronizing a repository
--------------------------

If you want synchronize manually a repository or if you want change the
uploaded zip file for a specific repository, please use this function.

Example :

.. code:: python

   saagie.repositories.synchronize(repository_id="d04e578f-546a-41bf-bb8c-790e99a4f6c8", file="./test_input/new_technologies.zip")

Response payload example :

.. code:: python

   {'synchronizeRepository': {'count': 5,
                              'report': {'id': '47589bad-729d-4afe-99e8-05824dd66858',
                                         'endedAt': '2022-09-21T12:15:50.513Z',
                                         'startedAt': '2022-09-21T12:15:50.513Z',
                                         'trigger': {'author': 'hello.world', 'type': 'MANUAL'},
                                         'technologyReports': [{'status': 'DELETED', 'technologyId': 'aws-batch'},
                                                               {'status': 'DELETED', 'technologyId': 'aws-emr'},
                                                               {'status': 'DELETED', 'technologyId': 'aws-glue'},
                                                               {'status': 'DELETED', 'technologyId': 'aws-lambda'},
                                                               {'status': 'UNCHANGED', 'technologyId': 'cloudbeaver'},
                                                               {'status': 'UNCHANGED', 'technologyId': 'dash'}],
                                         'issues': []},
                              'repositoryId': '0e09c160-7f68-402e-9156-0d414e53318b',
                              'repositoryName': 'hello world repo'}}
