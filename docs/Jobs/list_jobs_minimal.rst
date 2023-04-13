Listing jobs for a project (with minimal information)
-----------------------

**saagieapi.jobs.list_for_project_minimal**

Example :

.. code:: python

   saagieapi.jobs.list_for_project_minimal(project_id="your_project_id")


Response payload example :

.. code:: python

     {
        "jobs": [
            {
                "id": "fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10",
                "name": "Python test job 1",
                "alias": "Python_test_job_1"
            },
            {
                "id": "e92ed170-50d6-4041-bba9-098a8e16f444",
                "name": "Python test job 2",
                "alias": "Python_test_job_2"
            }
        ]
    }

