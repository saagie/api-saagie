Count number of logs line for an instance of a condition
---------------
NB: Only available for environment variable condition

Streams is a list of logs files name to see, available values are: `ENVVARS_STDOUT`,
`ENVVARS_STDERR`, `ORCHESTRATION_STDOUT`, `ORCHESTRATION_STDERR`, `STDERR` & `STDOUT`

**saagieapi.count_condition_logs**

Example :

.. code:: python

   saagieapi.count_condition_logs(condition_instance_id="your_condition_instance_id",
                                  project_id="your_project_id",
                                  streams=["STDOUT"])

Response payload example :

.. code:: python

    {
        "data": {
            "conditionPipelineCountFilteredLogs": 4
        }
    }






