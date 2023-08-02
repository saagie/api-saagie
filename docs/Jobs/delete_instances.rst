Deleting instances of a job
---------------------------

**saagieapi.jobs.delete_instances**

Example :

.. code:: python

    saagie_api.jobs.delete_instances(
        job_id=job_id, 
        job_instances_id=["c8f156bc-78ab-4dda-acff-bbe828237fd9", "7e5549cd-32aa-42c4-88b5-ddf5f3087502"]
    )

Response payload example :

.. code:: python

    {
        'deleteJobInstances': [
            {'id': '7e5549cd-32aa-42c4-88b5-ddf5f3087502', 'success': True},
            {'id': 'c8f156bc-78ab-4dda-acff-bbe828237fd9', 'success': True}
        ]
    }