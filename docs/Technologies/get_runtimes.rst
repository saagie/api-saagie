Getting runtimes by technology ID
------------------------

**saagieapi.get_runtimes**

Example :

.. code:: python

   saagieapi.get_runtimes(technology_id="11d63963-0a74-4821-b17b-8fcec4882863")

Response payload example :

.. code:: python

   {
       'technology': {
           '__typename': 'AppTechnology',
           'id': '11d63963-0a74-4821-b17b-8fcec4882863',
           'label': 'Jupyter Notebook',
           'available': True,
           'appContexts': [
               {
                   'id': 'jupyter-spark-3.1',
                   'available': True,
                   'deprecationDate': None,
                   'description': None,
                   'dockerInfo': {
                       'image': 'saagie/jupyter-python-nbk',
                       'version': 'pyspark-3.1.1-1.111.0'
                   },
                   'facets': [],
                   'label': 'JupyterLab Spark 3.1',
                   'lastUpdate': '2023-02-07T09:43:08.057Z',
                   'ports': [
                       {
                           'basePath': 'SAAGIE_BASE_PATH',
                           'name': 'Notebook',
                           'port': 8888,
                           'rewriteUrl': False,
                           'scope': 'PROJECT'
                       },
                       {
                           'basePath': 'SPARK_UI_PATH',
                           'name': 'SparkUI',
                           'port': 8080,
                           'rewriteUrl': False,
                           'scope': 'PROJECT'
                       }
                   ],
                   'missingFacets': [],
                   'recommended': False,
                   'trustLevel': 'Stable',
                   'volumes': [
                       {
                           'path': '/notebooks-dir',
                           'size': '64 MB'
                       }
                   ]
               },
               {
                   'id': 'jupyterlab-3.8-3.9',
                   'available': True,
                   'deprecationDate': None,
                   'description': None,
                   'dockerInfo': {
                       'image': 'saagie/jupyterlab-python-nbk',
                       'version': '3.8-3.9-1.139.0'
                   },
                   'facets': [],
                   'label': 'JupyterLab Python 3.8 / 3.9 / 3.10',
                   'lastUpdate': '2023-02-07T09:43:08.057Z',
                   'ports': [
                       {
                           'basePath': 'SAAGIE_BASE_PATH',
                           'name': 'Notebook',
                           'port': 8888,
                           'rewriteUrl': False,
                           'scope': 'PROJECT'
                       }
                   ],
                   'missingFacets': [],
                   'recommended': True,
                   'trustLevel': 'Stable',
                   'volumes': [
                       {
                           'path': '/notebooks-dir',
                           'size': '64 MB'
                       }
                   ]
               }
           ]
       }
   }
