Editing a repository fetch from url
-----------------------------------

**saagieapi.repositories.edit**

Example :

.. code:: python

   saagieapi.repositories.edit(repository_id="163360ba-3254-490e-9eec-ccd1dc096fd7", 
                               name="new name repo", 
                               url="https://github.com/saagie/technologies-community/releases/download/0.62.0/technologies.zip", 
                               trigger_synchronization=True)

Response payload example :

.. code:: python

   {
       'editRepository': {
           'count': 1,
           'objects': [
               {
                   'name': 'new name repo',
                   'source': {
                       'url': 'https://github.com/saagie/technologies-community/releases/download/0.62.0/technologies.zip'
                   },
                   'id': '163360ba-3254-490e-9eec-ccd1dc096fd7'
               }
           ]
       }
   }
