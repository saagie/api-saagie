Duplicating a job
-----------------

**saagieapi.jobs.duplicate**

Example :

.. code:: python

    saagie_api.jobs.duplicate(job_id=job_id)

Response payload example :

.. code:: python

    {
        'duplicateJob': {
            'id': '29cf1b80-6b9c-47bc-a06c-c20897257097',
            'name': 'Copy of my_job 2'
        }
    }