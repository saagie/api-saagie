**saagieapi.repositories.revert_last_synchronization**

Reverting to last synchronization
---------------------------------

Example :

.. code:: python

   saagieapi.repositories.revert_last_synchronization(repository_id="163360ba-3254-490e-9eec-ccd1dc096fd7")

Response payload example :

.. code:: python

   {'revertLastSynchronization': {'report': {'id': 'f40650aa-73c0-4388-9742-331f8147b1a9',
                                             'trigger': {'author': 'hello.world', 'type': 'URL_UPDATE'},
                                             'endedAt': '2022-09-21T12:04:41.551Z',
                                             'startedAt': '2022-09-21T12:04:41.551Z'},
                                  'repositoryName': 'new name repo',
                                  'repositoryId': '163360ba-3254-490e-9eec-ccd1dc096fd7'}}