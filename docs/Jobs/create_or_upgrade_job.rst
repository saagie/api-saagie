Creating or upgrading a job
----------

**saagieapi.jobs.create_or_upgrade**

Example :

.. code:: python

   saagieapi.jobs.create_or_upgrade(job_name="my job",
                                    project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                                    file="/tmp/test.py",
                                    use_previous_artifact=False,
                                    description='My description',
                                    category='Extraction',
                                    technology='python',# technology id corresponding to your context.id in your technology catalog definition
                                    technology_catalog='Saagie',
                                    runtime_version='3.9',
                                    command_line='python {file}',
                                    release_note='First release',
                                    extra_technology='',
                                    extra_technology_version='',
                                    cron_scheduling='0 0 * * *',
                                    schedule_timezone='Europe/Paris',
                                    resources={"cpu": {"request": 0.5, "limit": 2.6}, "memory": {"request": 1.0}},
                                    emails=['email1@saagie.io', 'email2@saagie.io'],
                                    status_list=["FAILED", "KILLED"]
                                    )

Response payload example :

.. code:: python

   {
       "data":{
           "createJob":{
               "id":"60f46dce-c869-40c3-a2e5-1d7765a806db",
               "versions":[
                   {
                       "number":1,
                       "__typename":"JobVersion"
                   }
               ],
               "__typename":"Job"
           }
       }
   }