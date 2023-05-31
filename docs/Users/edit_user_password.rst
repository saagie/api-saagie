Editing an user's password
--------

*NB: You can only use this function if you have the admin role on the platform.*

**saagieapi.users.edit_password**

Example :

.. code:: python

    saagieapi.users.edit_password(user_name="test_user",
                                  previous_pwd="A123456#a",
                                  new_pwd="NewPwd123!"
                                 )

Response payload example :

.. code:: python

    True

