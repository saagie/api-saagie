Counting instances of a job
---------------------------

**saagieapi.jobs.count_instances_by_status**

Example :

.. code:: python

    saagie_api.jobs.count_instances_by_status(job_id=job_id)

Response payload example :

.. code:: python

    {
        'countJobInstancesBySelector': [
            {'selector': 'ALL', 'count': 0},
            {'selector': 'SUCCEEDED', 'count': 0},
            {'selector': 'FAILED', 'count': 0},
            {'selector': 'STOPPED', 'count': 0},
            {'selector': 'UNKNOWN', 'count': 0}
        ]
    }