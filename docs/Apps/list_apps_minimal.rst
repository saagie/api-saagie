Listing apps for a project (with minimal information)
-----------------------

**saagieapi.apps.list_for_project_minimal**

Example :

.. code:: python

   saagieapi.apps.list_for_project_minimal(project_id="your_project_id")


Response payload example :

.. code:: python

   {
       'project': {
           'apps': [
               {
                   'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                   'name': 'Jupyter Notebook'
               }
           ]
       }
   }

