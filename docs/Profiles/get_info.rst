Getting user's profile information
--------

**saagieapi.profiles.get_info**

*NB: You can only use this function if you have the admin role on the platform.*

Example :

.. code:: python

    saagieapi.profiles.get_info(user_name="test_user")

Response payload example :

.. code:: python

    {
       "login": "test_user",
       "job": "DATA_ENGINEER",
       "email": "test_user@gmail.com"
    }