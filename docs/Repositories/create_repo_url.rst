**saagieapi.repositories.create**

Creating a repository fetch from url
------------------------------------

Example :

.. code:: python

   saagie.repositories.create(name="hello world2 repo", url= "https://github.com/saagie/technologies-community/releases/download/0.64.0/technologies.zip")

Response payload example :

.. code:: python

   {'addRepository': {'count': 1,
     'objects': [{'id': '163360ba-3254-490e-9eec-ccd1dc096fd7',
       'name': 'hello world2 repo'}]}}