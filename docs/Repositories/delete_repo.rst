Deleting a repository
---------------------

**saagieapi.repositories.delete**

Example :

.. code:: python

   saagieapi.repositories.delete(repository_id="163360ba-3254-490e-9eec-ccd1dc096fd7")

Response payload example :

.. code:: python

   {
       'removeRepository': {
           'id': '163360ba-3254-490e-9eec-ccd1dc096fd7',
           'name': 'new name repo'
       }
   }
