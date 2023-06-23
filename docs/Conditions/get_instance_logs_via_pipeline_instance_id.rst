Get a condition instance logs via pipeline instance ID
---------------
NB: Only available for environment variable condition

Streams is a list of logs files name to see, available values are: `ENVVARS_STDOUT`,
`ENVVARS_STDERR`, `ORCHESTRATION_STDOUT`, `ORCHESTRATION_STDERR`, `STDERR` & `STDOUT`


**saagieapi.get_condition_instance_logs_by_condition**

Example :

.. code:: python

    saagieapi.get_condition_instance_logs_by_condition(condition_id="condition_node_id",
                                                       project_id="project_id",
                                                       pipeline_instance_id="pipeline_instance_id",
                                                       streams=["STDOUT"]
                                                       )

Response payload example :

.. code:: python

    {
      "data": {
        "conditionPipelineByNodeIdFilteredLogs": {
          "count": 4,
          "content": [
            {
              "index": 0,
              "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Condition: 'tube_name.contains(\"Tube\") ||",
              "stream": "STDOUT"
            },
            {
              "index": 1,
              "value": "double(diameter) > 1.0'",
              "stream": "STDOUT"
            },
            {
              "index": 2,
              "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Condition evaluation took: 4.736725ms",
              "stream": "STDOUT"
            },
            {
              "index": 3,
              "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Result: true",
              "stream": "STDOUT"
            }
          ]
        }
      }
    }






