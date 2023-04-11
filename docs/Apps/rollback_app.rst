Rollback an app
--------------

**saagieapi.apps.rollback**

Example :

.. code:: python

    saagie_api.apps.rollback(app_id="39c56012-0f59-4f51-9852-29a182eff13a", version_number=1)

Response payload example :

.. code:: python

    {
        "rollbackAppVersion": {
            "id": "39c56012-0f59-4f51-9852-29a182eff13a",
            "versions": [
                {
                    "number": 2
                }, 
                {
                    "number": 1
                }
            ],
            "currentVersion": {
                "number": 1
            }
        }
    }


