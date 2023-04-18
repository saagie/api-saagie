Getting available jobs technologies for a project
----------------------------

**saagieapi.projects.get_jobs_technologies**

Example :

.. code:: python

   saagieapi.projects.get_jobs_technologies(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")

Response payload example :

::

   {
       'technologiesByCategory': [
           {
               'jobCategory': 'Extraction',
               'technologies': [
                   {
                       'id': '9bb75cad-69a5-4a9d-b059-811c6cde589e',
                       '__typename': 'Technology'
                   },
                   {
                       'id': 'f267085d-cc52-4ae8-ad9e-af8721c81127',
                       '__typename': 'Technology'
                   }
               ]
           },
           {
               'jobCategory': 'Processing',
               'technologies': [
                   {
                       'id': '9bb75cad-69a5-4a9d-b059-811c6cde589e',
                       '__typename': 'Technology'
                   }
               ]
           },
           {
               'jobCategory': 'Smart App',
               'technologies': []
           }
       ]
   }