.. raw:: html

   <p align="center">

.. raw:: html

   </p>

Presentation
============

The ``saagieapi`` python package implements python API wrappers to
easily interact with the Saagie platform in python.

Installing
==========

.. code:: bash

   pip install saagieapi==<version>

Compatibility with your Saagie platform
---------------------------------------

=========================== ======================
**Saagie platform version** **saagie-api release**
=========================== ======================
< 2.2.0                     < 0.6.0
>= 2.2.0                    >= 0.6.0
>= 2023.01                  >= 2.4.0
=========================== ======================

Usage
=====

Connecting to your platform
---------------------------

There are 2 options to connect to your platform :

1. using the default constructor :

.. code:: python

   saagie = SaagieApi(url_saagie="<url>",
                      id_platform="1",
                      user="<saagie-user-name>",
                      password="<saagie-user-password>",
                      realm="saagie")

2. Using the ``easy_connect`` alternative constructor which uses the
   complete URL (eg:
   https://mysaagie-workspace.prod.saagie.com/projects/platform/6/) and
   will parse it in order to retrieve the platform URL, platform id and
   the realm.

.. code:: python

   saagie = SaagieApi.easy_connect(url_saagie_platform="<url>",
                      user="<saagie-user-name>",
                      password="<saagie-user-password>")

Using the different endpoints
-----------------------------

Once connected with one of the 2 methods explained above, you can now
use the different endpoints to interact with : - projects :
``saagie.projects.xxx``, see the list of methods available
`here <wiki/2---Projects>`__ - jobs : ``saagie.jobs.xxx``, see the list
of methods available `here <wiki/3---Jobs>`__ - apps :
``saagie.apps.xxx``, see the list of methods available
`here <wiki/4---Apps>`__ - pipelines : ``saagie.pipelines.xxx``, see the
list of methods available `here <wiki/5---Pipelines>`__ - environment
variables : ``saagie.env_vars.xxx``, see the list of methods available
`here <wiki/6---Environment-variables>`__ - docker credentials :
``saagie.docker_credentials.xxx``, see the list of methods available
`here <wiki/7---Docker-credentials>`__

Finding your platform, project, job and instances ids
-----------------------------------------------------

Your Saagie projects homepage has the following structure
``https://<REALM>-workspace.me.saagie.com/projects/platform/<PLATFORM_ID>/``

   ``https://mysaagie-workspace.me.saagie.com/projects/platform/1/``
   would give : - ``platform_id`` = 1 - ``realm`` = mysaagie

**Project id** can be found in the project URL after the ``/project``

   ``https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs``
   would give : - ``project_id`` = 8321e13c-892a-4481-8552-5be4b6cc5df4

**Job id** can be found in the project URL after the ``/job``

   ``https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b``
   would give : - ``job_id`` = a85ac3db-bca1-4f15-b8f7-44731fba874b

**App id** can be found in the project URL after the ``/app``

   ``https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/app/02c01d47-8a29-47d0-a53c-235add43c885``
   would give : - ``app_id`` = 02c01d47-8a29-47d0-a53c-235add43c885

**Pipeline id** can be found in the project URL after the ``/pipeline``

   ``https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/pipeline/4da29f25-e7c9-4410-869e-40b9ba0074d1``
   would give : - ``pipeline_id`` = 4da29f25-e7c9-4410-869e-40b9ba0074d1

**Job instance id** can be found in the project URL after the
``/instances``

   ``https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b/instances/6ff448ae-3770-4639-b0f8-079e5c614ab6``
   would give : - ``job_instance_id`` =
   6ff448ae-3770-4639-b0f8-079e5c614ab6
