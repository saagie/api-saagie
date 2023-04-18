Creating a project
----------

**saagieapi.projects.create**

Example :

.. code:: python

   saagie_client.projects.create(name="Project_A",
                                  groups_and_roles=[{"my_group": "Manager"}],
                                  jobs_technologies_allowed={"saagie": ["python", "spark"]},
                                  apps_technologies_allowed={"saagie": ["Jupyter Notebook"]})

Response payload example :

.. code:: python

   {
       'createProject': {
           'id': '09515109-e8d3-4ed0-9ab7-5370efcb6cb5',
           'name': 'Project_A',
           'creator': 'toto.tata'
       }
   }