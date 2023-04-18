Getting available app technologies for a project
----------------------------

**saagieapi.projects.get_apps_technologies**

Example :

.. code:: python

   saagieapi.projects.get_apps_technologies(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")

Response payload example :

::

   {
       'appTechnologies': [
           {
               'id': '11d63963-0a74-4821-b17b-8fcec4882863'
           },
           {
               'id': '56ad4996-7285-49a6-aece-b9525c57c619'
           },
           {
               'id': 'd0b55623-9dc0-4e03-89c7-6a2494387a4f'
           }
       ]
   }