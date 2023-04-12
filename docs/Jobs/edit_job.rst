Editing a job
--------

**saagieapi.jobs.edit**

Example :

.. code:: python

    saagieapi.jobs.edit(job_id="60f46dce-c869-40c3-a2e5-1d7765a806db",
                        job_name="newname",
                        description="new desc",
                        is_scheduled=True,
                        cron_scheduling='0 * * * *',
                        schedule_timezone='Europe/Paris',
                        resources={"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}},
                        emails=['email1@saagie.io'],
                        status_list=["FAILED", "QUEUED"]
                        )

Response payload example :

.. code:: python

    {
        "editJob": {
            "id": "60f46dce-c869-40c3-a2e5-1d7765a806db",
            "name": "newname",
            "alias": "newname",
            "description": "new desc",
            "isScheduled": True,
            "cronScheduling": "0 * * * *",
            "scheduleTimezone": "Europe/Paris",
            "resources": {
                "cpu": {
                    "request": 1.5,
                    "limit": 2.2
                },
                "memory": {
                    "request": 2.0,
                    "limit": None
                }
            },
            "alerting": {
                "emails": [
                    "email1@saagie.io"
                ],
                "statusList": [
                    "FAILED",
                    "QUEUED"
                ]
            }
        }
    }
