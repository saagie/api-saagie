Getting available technologies by catalog
------------------------

**saagieapi.get_available_technologies**

Example :

.. code:: python

   saagieapi.get_available_technologies(catalog="Saagie")

Response payload example :

.. code:: python

   [
       {
           'id': 'a3a5e5ea-7af1-47db-b9ca-fed722a123b1',
           'label': 'Apache Superset',
           'available': True,
           '__typename': 'AppTechnology'
       },
       {
           'id': '19d446bd-bf31-462b-9c0b-023123f5dc4a',
           'label': 'CloudBeaver',
           'available': True,
           '__typename': 'AppTechnology'
       },
       {
           'id': 'a55afd45-3938-4ee3-8d16-e93227c76b93',
           'label': 'Dash',
           'available': True,
           '__typename': 'AppTechnology'
       }
       ,
       {
           'id': '4adb934e-8ee7-4942-9951-fd461b6769b1',
           'label': 'Bash',
           'available': True,
           '__typename': 'JobTechnology'
       },
       {
           'id': '1669e3ca-9fcf-1234-be11-cc2f3afabb1d',
           'label': 'Generic',
           'available': True,
           '__typename': 'JobTechnology'
       },
       {
           'id': '7f7c5c02-e187-448c-8552-99eed6af2001',
           'label': 'Java/Scala',
           'available': True,
           '__typename': 'JobTechnology'
       },
       {
           'id': '9bb93cad-69a5-4a9d-b059-811c6cde589e',
           'label': 'Python',
           'available': True,
           '__typename': 'JobTechnology'
       }
   ]