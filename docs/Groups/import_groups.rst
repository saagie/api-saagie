Importing groups
----------

*NB: You can only use this function if you have the admin role on the platform.*

*All protected (created at platform installation) groups will not be imported.*
*For the moment, authorizations of groups are not imported, so if you want the same authorization,
you have to set up manually.*

**saagieapi.groups.import_from_json**

Example :

.. code:: python

   saagieapi.groups.import_from_json(path_to_folder="/path/to/the/group/folder",
                                     error_folder="/path/to/the/error/folder")

Response payload example :

.. code:: python

   True