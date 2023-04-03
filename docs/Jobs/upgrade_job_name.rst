.. _upgrade job by name

Upgrade Job (by name)
---------------------

**saagieapi.jobs.upgrade_by_name**

Example :

.. code:: python

   saagieapi.jobs.upgrade_by_name(job_name="my job",
                      project_name="My project",
                       use_previous_artifact=True,
                       runtime_version='3.8',
                       command_line='python {file} new_arg',
                       release_note="Second version"
                       )

Response payload example :

.. code:: python

   {
      "data":{
         "addJobVersion":{
            "number":3,
            "__typename":"JobVersion"
         }
      }
   }
