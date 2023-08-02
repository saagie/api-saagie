Deleting instances of a job by using a filter
---------------------------------------------

**saagieapi.jobs.delete_instances_by_selector**

Example :

.. code:: python

    saagie_api.jobs.delete_instances_by_selector(
        job_id=job_id, 
        selector="FAILED",
        exclude_instances_id=["478d48d4-1609-4bf0-883d-097d43709aa8"],
        include_instances_id=["47d3df2c-5a38-4a5e-a49e-5405ad8f1699"]
    )

Response payload example :

.. code:: python

    {
        'deleteJobInstancesBySelector': 1
    }