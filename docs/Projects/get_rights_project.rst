Getting rights information for a project
---------------------------

**saagieapi.projects.get_info**

Example :

.. code:: python

   saagieapi.projects.get_rights(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")

Response payload example :

.. code:: python

   {
       'rights': [
           {
               'name': 'manager_group',
               'role': 'ROLE_PROJECT_MANAGER',
               'isAllProjects': True
           },
           {
               'name': 'my_group',
               'role': 'ROLE_PROJECT_MANAGER',
               'isAllProjects': False
           }
       ]
   }