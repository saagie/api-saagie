.. _run job with callback 

Run Job with Callback
---------------------

**saagieapi.jobs.run_with_callback**

Example :

.. code:: python

   saagieapi.jobs.run_with_callback(job_id="f5fce22d-2152-4a01-8c6a-4c2eb4808b6d", freq=5, timeout=60)

Response example :

::

   27/04/2022 12:02:45 [INFO] Job id f5fce22d-2152-4a01-8c6a-4c2eb4808b6d with instance 8e9b9f16-4a5d-4188-a967-1a96b88e4358 is currently : QUEUED
   27/04/2022 12:02:50 [INFO] Job id f5fce22d-2152-4a01-8c6a-4c2eb4808b6d with instance 8e9b9f16-4a5d-4188-a967-1a96b88e4358 is currently : QUEUED
   27/04/2022 12:02:56 [INFO] Job id f5fce22d-2152-4a01-8c6a-4c2eb4808b6d with instance 8e9b9f16-4a5d-4188-a967-1a96b88e4358 is currently : SUCCEEDED
   SUCCEEDED
