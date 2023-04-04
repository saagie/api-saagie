.. _upgrade job by id

Upgrade Job (by id)
-------------------

**saagieapi.jobs.upgrade**

Example :

.. code:: python

   saagieapi.jobs.upgrade(job_id="60f46dce-c869-40c3-a2e5-1d7765a806db",
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
               "number":2,
               "__typename":"JobVersion"
           }
       }
   }
