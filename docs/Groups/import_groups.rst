Importing groups
----------

**saagieapi.groups.import_from_json**

*NB: You can only use this function if you have the admin role on the platform.*

*All protected groups will not be imported*

Example :

.. code:: python

   saagieapi.groups.import_from_json(path_to_folder="/path/to/the/group/folder",
                                     error_folder="/path/to/the/error/folder")

Response payload example :

.. code:: python

   True