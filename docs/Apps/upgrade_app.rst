Upgrading an app
-------------------------

**saagieapi.apps.upgrade**

Example :

.. code:: python

   saagie_client.apps.upgrade(app_id="97ec670f-8b11-479f-9cd2-c8904ef45b7f",
                              exposed_ports=[{"basePathVariableName": "SAAGIE_BASE_PATH",
                                                "isRewriteUrl": True,
                                                "scope": "PROJECT",
                                                "number": 80,
                                                "name": "Test Port"}],
                              storage_paths=[{"path": "/home",
                                                "volumeId": "00f5d5d4-1975-478b-81f3-2003b7cff4c2"}]
                              )

Response payload example :

.. code:: python

   {
       'addAppVersion': {
           'number': 2,
           'releaseNote': '',
           'dockerInfo': None,
           'ports': [
               {
                   'number': 80,
                   'name': 'Test Port',
                   'basePathVariableName': 'SAAGIE_BASE_PATH',
                   'isRewriteUrl': True,
                   'scope': 'PROJECT'
               }
           ],
           'volumesWithPath': [
               {
                   'path': '/home',
                   'volume': {
                       'id': '62f5d5d4-9546-478b-81f3-1970b7cff4c2',
                       'name': 'storage 64MB',
                       'size': '64 MB',
                       'creator': 'titi.tata'
                   }
               }
           ]
       }
   }