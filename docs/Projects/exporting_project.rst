Exporting a project
-------------------

**saagieapi.projects.export**

Example :

.. code:: python

   saagieapi.projects.export(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4",
                             output_folder="./output/",
                             error_folder= "./error/",
                             versions_only_current = True,
                             project_only_env_vars = True)

Response payload example :

.. code:: python

   True
