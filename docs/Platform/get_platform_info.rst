Getting platform info
-------------------------

**saagieapi.get_platform_info**

Example :

.. code:: python

   saagieapi.get_platform_info()

Response payload example :

.. code:: python

    {
        "platform": {
            "id": 1,
            "counts": {
                "projects": 21, 
                "jobs": 111, 
                "apps": 59, 
                "pipelines": 17
            }
        }
    }