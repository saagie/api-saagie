Getting statuses history of the app
-----------------------------------

**saagieapi.apps.get_history_statuses**

Example :

.. code:: python

   saagieapi.apps.get_history_statuses(history_id="history_app_id", version_number="version_number", start_time="start_date")

Response payload example :

.. code:: python

    {
        'appHistoryStatuses': [
            {'status': 'STARTING', 'recordAt': '2023-08-01T08:38:34.859Z'},
            {'status': 'STARTED', 'recordAt': '2023-08-01T08:38:38.845Z'},
            {'status': 'FAILED', 'recordAt': '2023-08-01T08:38:39.875Z'},
            {'status': 'RECOVERING', 'recordAt': '2023-08-01T08:38:39.875Z'},
            {'status': 'STOPPING', 'recordAt': '2023-08-01T08:38:41.094Z'},
            {'status': 'STOPPED', 'recordAt': '2023-08-01T08:38:41.241Z'}
        ]
    }