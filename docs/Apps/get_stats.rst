Getting stats of the app
------------------------

**saagieapi.apps.get_stats**

Example :

.. code:: python

   saagieapi.apps.get_stats(history_id="history_app_id", version_number="version_number", start_time="start_date")

Response payload example :

.. code:: python

    {
        'appStats': {
            'uptimePercentage': 0.04,
            'downtimePercentage': 99.96,
            'recoveredCount': 0
        }
    }