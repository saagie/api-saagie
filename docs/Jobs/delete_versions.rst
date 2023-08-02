Deleting versions of a job
--------------------------

**saagieapi.jobs.delete_versions**

Example :

.. code:: python

    saagie_api.jobs.delete_versions(job_id=job_id, versions=["1"])

Response payload example :

.. code:: python

    {
        'deleteJobVersions': [
            {'number': 1, 'success': True}
        ]
    }