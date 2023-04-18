Listing pipelines for a project (with minimal information)
-------------------------------

**saagieapi.pipelines.list_for_project_minimal**


Example :

.. code:: python

    saagieapi.pipelines.list_for_project_minimal(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771")

Response payload example :

.. code:: python

    {
        "project": {
            "pipelines": [
                {
                    "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                    "name": "Pipeline A"
                },
                {
                    "id": "9a2642df-550c-4c69-814f-1008f177b0e1",
                    "name": "Pipeline B"
                }
            ]
        }
    }