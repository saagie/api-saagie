Importing users
----------

*NB: You can only use this function if you have the admin role on the platform.*

*All protected (created at platform installation) users will not be imported.*

**saagieapi.users.import_from_json**

Example :

.. code:: python

   saagieapi.users.import_from_json(json_file="/path/to/the/json/file.json",
                                    temp_pwd="NewPwd123!",
                                    error_folder="/path/to/the/error/folder")

Response payload example :

.. code:: python

   True