Editing a project
--------

**saagieapi.projects.edit**

Example :

.. code:: python

   saagie_client.projects.edit(project_id="9a261ae0-fd73-400c-b9b6-b4b63ac113eb",
                               name="PROJECT B",
                               groups_and_roles=[{"my_group": "Viewer"}],
                               description="new desc",
                               jobs_technologies_allowed={"saagie": ["r"]},
                               apps_technologies_allowed={"saagie": ["Dash"]}
                              )

Response payload example :

.. code:: python

   {
       'editProject': {
           'id': '9a261ae0-fd73-400c-b9b6-b4b63ac113eb',
           'name': 'PROJECT B',
           'creator': 'toto.tata'
       }
   }