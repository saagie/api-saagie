**saagie.repositories.list**

Listing repositories
--------------------

Example :

.. code:: python

   saagieapi.repositories.list()

Response payload example :

.. code:: python

   {'repositories': [{'id': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
      'name': 'Saagie',
      'synchronizationReports': {'lastReversibleId': 'a17c73ed-fca1-4f25-a343-914c7ac23bae',
       'count': 1,
       'list': [{'endedAt': '2022-09-12T10:27:44.549Z',
         'issues': [],
         'revert': None}]},
      'technologies': [
       {'available': True,
        'id': '9f188511-d49f-4129-9d6d-f4d451f42acd',
        'label': 'Java/Scala'},
       {'available': True,
        'id': '46cede50-c22a-4b95-9088-3251d0466458',
        'label': 'SQOOP'},
       {'available': True,
        'id': '0db6d0a7-ad4b-45cd-8082-913a192daa25',
        'label': 'Python'},
       {'available': True,
        'id': 'db34c9b9-47c7-4dc6-8c3c-2d8ccf5afa11',
        'label': 'AWS Lambda'}],
      'source': {'url': 'https://github.com/saagie/technologies/releases/latest/download/technologies.zip'}}
   ]}
