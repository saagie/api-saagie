**saagieapi.repositories.create**

Creating a repository from uploaded file
----------------------------------------


Example :

.. code:: python

   saagie.repositories.create(name="hello world repo", file="./test_input/technologies.zip")

Response payload example :

.. code:: python

   {'addRepository': {'count': 1,
                      'objects': [{'id': 'd04e578f-546a-41bf-bb8c-790e99a4f6c8',
                                   'name': 'hello world repo'}]}}