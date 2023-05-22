Importing users
----------

**saagieapi.users.import_from_json**

*NB: You can only use this function if you have the admin role on the platform.*

*All protected users will not be imported*

Example :

.. code:: python

   saagieapi.users.import_from_json(json_file="/path/to/the/json/file.json",
                                    temp_pwd="NewPwd123!",
                                    error_folder="/path/to/the/error/folder")

Response payload example :

.. code:: python

   True