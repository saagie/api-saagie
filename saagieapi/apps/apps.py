import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from gql import gql

from ..utils.folder_functions import create_folder, write_error, write_to_json_file
from .gql_queries import *

LIST_EXPOSED_PORT_FIELD = ["basePathVariableName", "isRewriteUrl", "scope", "number", "name"]
LIST_EXPOSED_PORT_MANDATORY = ["isRewriteUrl", "scope", "number"]


def handle_error(msg, exception):
    logging.warning(msg)
    logging.error("Something went wrong %s", exception)
    return False


class Apps:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_for_project(
        self,
        project_id: str,
        minimal: Optional[bool] = False,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """List apps of project.
        NB: You can only list apps if you have at least the viewer role on
        the project.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        minimal : bool, optional
            Whether to only return the app's name and id, default to False
        versions_only_current : bool, optional
            Whether to only fetch the current version of each app
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of app information

        Examples
        --------
        >>> saagieapi.apps.list_for_project(project_id="your_project_id")
        {
            'project': {
                'apps': [
                    {
                        'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                        'name': 'Jupyter Notebook',
                        'description': '',
                        'creationDate': '2022-02-23T08:50:24.326Z',
                        'creator': 'user.test',
                        'versions': [
                            {
                                'number': 1,
                                'creationDate': '2022-02-23T08:50:24.327Z',
                                'releaseNote': '',
                                'dockerInfo': None,
                                'runtimeContextId': 'jupyter-notebook-v2',
                                'creator': 'user.test',
                                'ports': [
                                    {
                                        'name': 'Notebook',
                                        'number': 8888,
                                        'isRewriteUrl': False,
                                        'basePathVariableName': 'SAAGIE_BASE_PATH',
                                        'scope': 'PROJECT',
                                        'internalUrl': 'http://app-d0d6a466-10d9-4120-8101-56e46563e05a:8888'
                                    }
                                ],
                                'isMajor': False,
                                'volumesWithPath': [
                                    {
                                        'path': '/notebooks-dir',
                                        'volume': {
                                            'id': '68a50c6b-3737-4b68-b033-464eedd02eb1',
                                            'name': 'storage jupyter notebook',
                                            'creator': 'user.test',
                                            'description': 'Automatically created by migration from app 68a50c6b-3737-4b68-b033-464eedd02eb1',
                                            'size': '128 MB',
                                            'projectId': '96a12345-303d-43cf-adb2-a7300d5bb9df',
                                            'creationDate': '2022-02-23T08:50:24.327Z',
                                            'linkedApp': {
                                                'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                                                'name': 'jupyter notebook'
                                            }
                                        }
                                    }
                                ]
                            }
                        ],
                        'currentVersion': {
                            'number': 1,
                            'creationDate': '2022-02-23T08:50:24.327Z',
                            'releaseNote': '',
                            'dockerInfo': None,
                            'runtimeContextId': 'jupyter-notebook-v2',
                            'creator': 'user.test',
                            'ports': [
                                {
                                    'name': 'Notebook',
                                    'number': 8888,
                                    'isRewriteUrl': False,
                                    'basePathVariableName': 'SAAGIE_BASE_PATH',
                                    'scope': 'PROJECT',
                                    'internalUrl': 'http://app-d0d6a466-10d9-4120-8101-56e46563e05a:8888'
                                }
                            ],
                            'isMajor': False,
                            'volumesWithPath': [
                                {
                                    'path': '/notebooks-dir',
                                    'volume': {
                                        'id': '68a50c6b-3737-4b68-b033-464eedd02eb1',
                                        'name': 'storage jupyter notebook',
                                        'creator': 'user.test',
                                        'description': 'Automatically created by migration from app 68a50c6b-3737-4b68-b033-464eedd02eb1',
                                        'size': '128 MB',
                                        'projectId': '96a12345-303d-43cf-adb2-a7300d5bb9df',
                                        'creationDate': '2022-02-23T08:50:24.327Z',
                                        'linkedApp': {
                                            'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                                            'name': 'jupyter notebook'
                                        }
                                    }
                                }
                            ]
                        },
                        'technology': {
                            'id': '7d3f247c-b5a9-4a34-a0a2-f6b209bc2b63'
                        },
                        'linkedVolumes': [
                            {
                                'id': '68a50c6b-3737-4b68-b033-464eedd02eb1',
                                'name': 'storage jupyter notebook',
                                'creator': 'user.test',
                                'description': 'Automatically created by migration from app 68a50c6b-3737-4b68-b033-464eedd02eb1',
                                'size': '128 MB',
                                'creationDate': '2022-02-23T08:50:24.327Z'
                            }
                        ],
                        'isGenericApp': False,
                        'history': {
                            'id': 'affea4dd-d894-4742-bbd2-dd3a09c92020',
                            'events': [
                                {
                                    'event': {
                                        'recordAt': '2022-06-29T07:40:19.754Z',
                                        'executionId': '5980d8cf-7cb6-4340-bd84-d3d17bdb5ab6'
                                    },
                                    'transitionTime': '2022-06-29T07:40:19.754Z'
                                },
                                {
                                    'event': {
                                        'recordAt': '2022-06-29T07:40:19.974Z',
                                        'executionId': '5980d8cf-7cb6-4340-bd84-d3d17bdb5ab6'
                                    },
                                    'transitionTime': '2022-06-29T07:40:19.974Z'
                                }
                            ],
                            'runningVersionNumber': 1,
                            'currentDockerInfo': {
                                'image': 'saagie/jupyter-python-nbk:v2-1.95.0',
                                'dockerCredentialsId': None
                            },
                            'currentStatus': 'STOPPED',
                            'currentExecutionId': 'f29c940f-4622-4263-8cec-41ae68513885',
                            'startTime': '2022-06-29T08:14:49.205Z',
                            'stopTime': '2022-06-29T08:19:59.946Z'
                        },
                        'alerting': None,
                        'resources': None
                    }
                ]
            }
        }
        """  # pylint: disable=line-too-long

        params = {
            "id": project_id,
            "minimal": minimal,
            "versionsOnlyCurrent": versions_only_current,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_APPS_FOR_PROJECT), variable_values=params, pprint_result=pprint_result
        )

    def list_for_project_minimal(self, project_id: str) -> Dict:
        """List only app names and ids in the given project .
        NB: You can only list apps if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of apps ids and names

        Examples
        --------
        >>> saagieapi.apps.list_for_project_minimal(project_id="your_project_id")
        {
            'project': {
                'apps': [
                    {
                        'id': 'd0d6a466-10d9-4120-8101-56e46563e05a',
                        'name': 'Jupyter Notebook'
                    }
                ]
            }
        }
        """

        params = {
            "id": project_id,
            "minimal": True,
            "versionsOnlyCurrent": True,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_APPS_FOR_PROJECT), variable_values=params, pprint_result=False
        )

    def get_info(
        self,
        app_id: str,
        versions_only_current: bool = True,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get app with given UUID.

        Parameters
        ----------
        app_id : str
            UUID of your app
        versions_only_current : bool, optional
            Whether to only fetch the current version of each app
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of app information

        Examples
        --------
        >>> saagieapi.apps.get_info(app_id="your_app_id")
        {
            'app': {
                'id': 'b6e846d7-d871-46db-b858-7d39d6b60123',
                'name': 'Jupyter lab',
                'creationDate': '2022-05-09T14:12:31.819Z',
                'technology': {
                    'id': '7d3f247c-b5a9-4a34-a0a2-f6b209bc2b63'
                },
                'project': {
                    'id': '96a74193-303d-43cf-adb2-a7300d5bb9df',
                    'name': 'Saagie testing tool '
                },
                'description': '',
                'currentVersion': {
                    'number': 1,
                    'creator': 'toto.hi',
                    'creationDate': '2022-05-09T14:12:31.819Z',
                    'releaseNote': 'First version of Jupyter Notebook with Spark 3.1 into Saagie.',
                    'dockerInfo': None,
                    'runtimeContextId': 'jupyter-spark-3.1',
                    'ports': [
                        {
                            'name': 'Notebook',
                            'number': 8888,
                            'isRewriteUrl': False,
                            'basePathVariableName': 'SAAGIE_BASE_PATH',
                            'scope': 'PROJECT',
                            'internalUrl': 'http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8888'
                        },
                        {
                            'name': 'SparkUI',
                            'number': 8080,
                            'isRewriteUrl': False,
                            'basePathVariableName': 'SPARK_UI_PATH',
                            'scope': 'PROJECT',
                            'internalUrl': 'http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8080'
                        }
                    ],
                    'volumesWithPath': [
                        {
                            'path': '/notebooks-dir',
                            'volume': {
                                'id': 'c163216a-b024-4cb1-8aae-0664bf2f58b4',
                                'name': 'storage Jupyter lab',
                                'creator': 'toto.hi',
                                'description': 'Automatically created by migration from app c163216a-b024-4cb1-8aae-0664bf2f58b4',
                                'size': '128 MB',
                                'projectId': '96a74193-303d-43cf-adb2-a7300d5bb9df',
                                'creationDate': '2022-05-09T14:12:31.819Z',
                                'linkedApp': {
                                    'id': 'b6e846d7-d871-46db-b858-7d39d6b60146',
                                    'name': 'Jupyter lab'
                                }
                            }
                        }
                    ],
                    'isMajor': False
                },
                'history': {
                    'id': '4f60dd23-4ec2-4996-b4da-d95376d72387',
                    'currentStatus': 'STARTED',
                    'currentExecutionId': 'f2d81d93-e1ae-4b09-a77e-4e50c13971ce',
                    'currentDockerInfo': {
                        'image': 'saagie/jupyter-python-nbk:pyspark-3.1.1-1.111.0',
                        'dockerCredentialsId': None
                    },
                    'startTime': '2022-09-21T09:47:27.342Z',
                    'events': [
                        {
                            'event': {
                                'recordAt': '2022-06-21T12:57:22.734Z',
                                'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                'versionNumber': 1,
                                'author': 'user.test'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-21T12:57:22.9Z',
                                'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                'status': 'STARTING'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-21T12:57:35.443Z',
                                'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                'status': 'STARTED'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-24T14:28:01.647Z',
                                'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                'author': 'user.test'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-24T14:28:01.726Z',
                                'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                'status': 'STOPPING'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-24T14:28:01.81Z',
                                'executionId': '7eb4649c-2bcf-4062-a7d2-528a9d950e6d',
                                'status': 'STOPPED'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-29T07:41:41.713Z',
                                'executionId': '9e525435-684f-470e-9818-fb865776da09',
                                'versionNumber': 1,
                                'author': 'user.test'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-29T07:41:41.912Z',
                                'executionId': '9e525435-684f-470e-9818-fb865776da09',
                                'status': 'STARTING'
                            }
                        },
                        {
                            'event': {
                                'recordAt': '2022-06-29T07:48:22.359Z',
                                'executionId': '9e525435-684f-470e-9818-fb865776da09',
                                'status': 'STARTED'
                            }
                        }
                    ]},
                'isGenericApp': False,
                'alerting': None,
                'resources': None,
                'linkedVolumes': [
                    {
                        'size': '128 MB'
                    }
                ]
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "id": app_id,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_APP_INFO), variable_values=params, pprint_result=pprint_result
        )

    def create_from_scratch(
        self,
        project_id: str,
        app_name: str,
        image: str = "",
        description: str = "",
        exposed_ports: List[Dict] = None,
        storage_paths: List[Dict] = None,
        release_note: str = "",
        docker_credentials_id: str = None,
        emails: List = None,
        logins: List = None,
        status_list: List = None,
        resources: Dict = None,
        technology_id: str = None,
        technology_context: str = None,
    ) -> Dict:
        """
        Create an app in a specific project.

        Parameters
        ----------
        project_id : str
            ID of the project.
        app_name : str
            Name of the app.
        description : str
            Description of the app.
        image : str
            Tag of the Docker Image.
            Incompatible with parameters technology_id & technology_context.
            Example: 'hello-world:nanoserver-ltc2022'.
        docker_credentials_id : str
            Credentials's ID for the image if the image is not public.
            Incompatible with parameters technology_id & technology_context.
        exposed_ports : list of dict
            List of dictionaries of exposed ports. Each dict should contain 'port' as key.
            Example: [{"basePathVariableName": "SAAGIE_BASE_PATH",
                       "isRewriteUrl": True,
                       "scope": "PROJECT",
                       "number": 5000,
                       "name": "Test Port"}].
        storage_paths : list of dict, optional
            List of dictionaries indicating the volume path to the persistent storage and:
            - the id of the volume to be associated with the app.
              Example: [{"path": "/home", "volumeId": "cb70ad1d-7883-48ac-8740-2c8e5c5166ee"}]
            - or the information needed to create the volume.
              Example: [{"path": "/home", "volume": {"name": "storage name",
                                                    "size": "64 MB",
                                                    "description": "storage description"}}].
        release_note : str, optional
            Release note for the app version.
        emails : list of str, optional
            Emails to receive alerts for the app. Each item should be a valid email.
        logins : list of str, optional
            Logins to receive alerts for the app. Each item should be a valid login.
        status_list : list of str, optional
            Receive an email when the app status changes to a specific status.
            Each item of the list should be one of these following values:
            "STARTING", "STARTED", "ROLLING_BACK", "UPGRADING", "RECOVERING",
            "RESTARTING", "STOPPING", "STOPPED", "FAILED".
        resources : dict, optional
            Resources CPU, RAM & GPU limited and guaranteed for the app.
        technology_id : str, optional
            Technology id of the app.
            Incompatible with parameters image & docker_credentials_id.
        technology_context : str, optional
            Context version of the app.
            Incompatible with parameters image & docker_credentials_id.

        Returns
        -------
        dict
            Dict of app information.

        Examples
        --------
        >>> saagieapi.apps.create_from_scratch(
        ...     project_id="project_id",
        ...     app_name="App Example Scratch",
        ...     image="saagie/ttyd-saagie:1.0",
        ...     exposed_ports=[
        ...         {
        ...             "basePathVariableName": "SAAGIE_BASE_PATH",
        ...             "isRewriteUrl": True,
        ...             "scope": "PROJECT",
        ...             "number": 7681,
        ...             "name": "ttyd"
        ...         }
        ...     ]
        ... )
        {
            'createApp': {
                'id': '1221f83e-52de-4beb-89a0-1505de4e875f'
            }
        }
        """
        if storage_paths is None:
            storage_paths = []
        if exposed_ports is None:
            exposed_ports = []

        check_format_exposed_port = self.check_exposed_ports(exposed_ports)

        if not check_format_exposed_port:
            raise ValueError(
                "❌ The parameter 'exposed_ports' should be a list of dict. Each dict should contains the key 'number'."
                f"All accept key of each dict is: '{LIST_EXPOSED_PORT_FIELD}'"
            )

        for storage in (s for s in storage_paths if "volume" in s):
            result = self.saagie_api.storages.create(
                project_id,
                storage["volume"]["name"],
                storage["volume"]["size"],
                storage["volume"]["description"],
            )["createVolume"]
            storage["volumeId"] = result["id"]
            del storage["volume"]

        params = {
            "projectId": project_id,
            "name": app_name,
            "description": description,
            "version": {
                "dockerInfo": {
                    "image": image,
                },
                "ports": exposed_ports,
                "releaseNote": release_note,
                "volumesWithPath": storage_paths,
            },
        }
        # in case of catalog app imported
        if technology_id:
            techno_id = technology_id
            del params["version"]["dockerInfo"]
            params["version"]["runtimeContextId"] = technology_context
        else:
            repos = self.saagie_api.get_repositories_info()["repositories"]
            # Find Saagie repository
            repos = next(repo for repo in repos if repo["name"] == "Saagie")["technologies"]
            # Find docker technology id
            techno_id = next(techno["id"] for techno in repos if techno["label"] == "Docker image")
        params["technologyId"] = techno_id

        if docker_credentials_id:
            params["version"]["dockerInfo"]["dockerCredentialsId"] = docker_credentials_id

        if emails or logins or status_list:
            params["alerting"] = self.check_alerting(emails, logins, status_list)

        if resources:
            params["resources"] = resources

        # Add the app layer in params object
        params = {"app": params}

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_APP_SCRATCH), variable_values=params)
        logging.info("✅ App [%s] successfully created", app_name)
        return result

    def create_from_catalog(
        self,
        project_id: str,
        context: str,
        technology_id: str = None,
        technology_catalog: str = "Saagie",
        technology_name: str = None,
    ) -> Dict:
        """Create an app in a specific project. \
        If technology_id is provided, the catalog and name will be ignored.

        Parameters
        ----------
        project_id : str
            ID of the project
        context: str
            Name of the context
        technology_id: str, optional
            ID of the app technology
        technology_catalog: str, optional
            Name of the technology catalog
        technology_name: str, optional
            Name of the app technology

        Returns
        -------
        dict
            Dict of app information

        Examples
        --------
        >>> saagieapi.apps.create_from_catalog(
        ...     project_id="your_project_id",
        ...     context="7.15.1",
        ...     technology_name="kibana"
        ... )
        {
            'installApp': {
                'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e',
                'name': 'Kibana'
            }
        }
        """
        # Initialize parameters to request GQL Graph
        params = {"projectId": project_id}

        # If the user has set a technology_id, we don't look at the name
        if technology_id:
            params["technologyId"] = technology_id
        else:
            # Get all id technologies in our project
            techs_project = [
                tech["id"] for tech in self.saagie_api.projects.get_apps_technologies(project_id)["appTechnologies"]
            ]

            # Check if the technology exist
            technology_id = self.saagie_api.check_technology(
                params, technology_name, technology_catalog, techs_project
            )["technologyId"]

        # Get different runtimes of app
        runtimes = self.saagie_api.get_runtimes(technology_id)["technology"]["appContexts"]
        # Check if runtime is available
        available_runtimes = [app for app in runtimes if app["available"] is True]
        context_app = [app for app in available_runtimes if app["label"] == context]

        if not context_app:
            available_contexts = [app["label"] for app in available_runtimes]
            raise ValueError(
                f"❌ Runtime '{context}' of the app '{technology_id}' doesn't exist or is not available in the project: "
                f"'{project_id}'. Available runtimes are: '{available_contexts}'"
            )

        params["contextId"] = context_app[0]["id"]

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_APP_CATALOG), variable_values=params)
        label = technology_name or technology_id
        logging.info("✅ App [%s] successfully created", label)
        return result

    def edit(
        self,
        app_id: str,
        app_name: str = None,
        description: str = None,
        emails: List = None,
        logins: List = None,
        status_list: List = None,
        resources: Dict = None,
    ) -> Dict:
        """Edit an app. \
        Each optional parameter can be set to change the value of the corresponding field.

        Parameters
        ----------
        app_id : str
            UUID of your app
        app_name : str, optional
            App name
            If not filled, defaults to current value, else it will change the app's name
        description : str, optional
            Description of app
            if not filled, defaults to current value, else it will change the description of the app
        emails: List[String], optional
            Emails to receive alerts for the app, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        logins: List[String], optional
            Logins to receive alerts for the app, each item should be a valid login,
            If you want to remove alerting, please set logins to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the app status change to a specific status.
            Each item of the list should be one of these following values: "STARTING","STARTED",
            "ROLLING_BACK","UPGRADING","RECOVERING","RESTARTING","STOPPING","STOPPED","FAILED"
        resources : dict, optional
            Resources CPU, RAM & GPU limited and guaranteed for the app.

        Returns
        -------
        dict
            Dict of app information

        Examples
        --------
        >>> saagieapi.apps.edit(
        ...     app_id="a6de6956-4038-493e-bbd3-f7b3616df39e",
        ...     app_name="App_Example_Catalog_modify",
        ...     emails=["hello.world@gmail.com"],
        ...     status_list=["FAILED"]
        ... )
        {
            'editApp': {
                'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e'
            }
        }
        """
        params = {
            "id": app_id,
        }

        if app_name:
            params["name"] = app_name

        if description:
            params["description"] = description

        params["alerting"] = self.get_info(app_id)["app"]["alerting"]
        if emails or logins or status_list:
            params["alerting"] = self.check_alerting(emails, logins, status_list)

        if resources:
            params["resources"] = resources

        params = {"app": params}
        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_APP), variable_values=params)
        logging.info("✅ App [%s] successfully edited", app_id)
        return result

    def delete(self, app_id: str) -> Dict:
        """Delete a given app

        Parameters
        ----------
        app_id : str
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted app

        Examples
        --------
        >>> saagieapi.apps.delete(app_id="a6de6956-4038-493e-bbd3-f7b3616df39e")
        {
            'deleteApp': {
                'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e'
            }
        }
        """
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_APP), variable_values={"appId": app_id})
        logging.info("✅ App [%s] successfully deleted", app_id)
        return result

    def run(self, app_id: str) -> Dict:
        """Run a given app

        Parameters
        ----------
        app_id : str
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of the given app information

        Examples
        --------
        >>> saagieapi.apps.run(app_id="a6de6956-4038-493e-bbd3-f7b3616df39e")
        {
            'runApp': {
                'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e',
                'versions': [
                    {
                        'number': 1
                    }
                ],
                'history': {
                    'id': 'ba494615-88b7-4c54-ad57-34a90461c407',
                    'currentDockerInfo': {
                        'image': 'saagie/kibana:7.15.1-1.108.0',
                        'dockerCredentialsId': None
                    },
                    'runningVersionNumber': 1,
                    'currentStatus': 'STOPPED'
                }
            }
        }
        """
        result = self.saagie_api.client.execute(query=gql(GQL_RUN_APP), variable_values={"id": app_id})
        logging.info("✅ App [%s] successfully started", app_id)
        return result

    def stop(self, app_id: str) -> Dict:
        """Stop a given app instance

        Parameters
        ----------
        app_id : str
            UUID of your app

        Returns
        -------
        dict
            app instance information

        Examples
        --------
        >>> saagie_api.apps.stop(app_id="a6de6956-4038-493e-bbd3-f7b3616df39e")
        {
            'stopApp': {
                'id': 'a6de6956-4038-493e-bbd3-f7b3616df39e',
                'history': {
                    'id': 'ba494615-88b7-4c54-ad57-34a90461c407',
                    'runningVersionNumber': 1,
                    'currentStatus': 'STARTED'
                }
            }
        }
        """
        result = self.saagie_api.client.execute(query=gql(GQL_STOP_APP), variable_values={"id": app_id})
        logging.info("✅ App [%s] successfully stopped", app_id)
        return result

    @staticmethod
    def check_exposed_ports(exposed_ports: List[Dict]):
        """
        Check if exposed ports are valid

        Parameters
        ----------
        exposed_ports: List[Dict]
            List of exposed ports, each item of the list should be a dict and each dict must have
            'number' (int), 'scope' ('GLOBAL' or 'PROJECT'), and 'isRewriteUrl' (Boolean) as key,
            and only contain valid keys

        Returns
        -------
        bool
            True if all exposed port are in a valid format
            False otherwise
        """

        return bool(
            isinstance(exposed_ports, List)  # Exposed_ports is a list
            and exposed_ports  # Exposed_ports is not empty
            and all(isinstance(ep, Dict) for ep in exposed_ports)  # Exposed_ports is a list of dict
            # Mandatory keys are present in each dict
            and all((LIST_EXPOSED_PORT_MANDATORY - ep.keys()) == set() for ep in exposed_ports)
            # All keys are valid
            and all(set(ep.keys()).issubset(LIST_EXPOSED_PORT_FIELD) for ep in exposed_ports)
        )

    @staticmethod
    def check_alerting(emails: List = None, logins: List = None, status_list: List = None) -> Dict:
        """
        Check if the alerting is enabled for the given app and if so, check alerting and status_list.
        If any parameter is missing, it will be set to the current value.

        Parameters
        ----------
        emails : list, optional
            List of emails to send the alert
        logins : list, optional
            List of logins to send the alert
        status_list : list, optional
            Status list of the alert

        Returns
        -------
        dict
            Dict containing alert config

        Raises
        ------
        RunTimeError
            When the statut list is not valid
        """

        valid_status_list = [
            "STARTING",
            "STARTED",
            "ROLLING_BACK",
            "UPGRADING",
            "RECOVERING",
            "RESTARTING",
            "STOPPING",
            "STOPPED",
            "FAILED",
        ]

        alerting = {}

        if status_list:
            wrong_status_list = [item for item in status_list if item not in valid_status_list]
            alerting["statusList"] = status_list

            if wrong_status_list:
                raise RuntimeError(
                    f"❌ The following status are not valid: {wrong_status_list}. "
                    f"Please make sure that each item of the parameter status_list should be "
                    f"one of the following values: {valid_status_list}"
                )

        if emails:
            alerting["emails"] = emails

        if "emails" in alerting:
            alerting["emails"] = [item for item in alerting["emails"] if item]

        if logins:
            alerting["logins"] = logins

        # If alerting object doesn't contain both a status list and either an email or a login,
        # raise an error
        if "statusList" not in alerting or ("emails" not in alerting and "logins" not in alerting):
            raise RuntimeError("❌ You must provide a status list and either an email or a login to enable the alerting")

        return alerting

    # doublenous with the saagie_api.get_runtime_label_by_id method
    def get_runtime_label_by_id(self, technology_id: str, runtime_id: str) -> str:
        """Get the label of runtime

        Parameters
        ----------
        technology_id : str
            UUID of the technology
        runtime_id : str
            UUID of the runtime

        Returns
        -------
        str
            String of runtime label

        Examples
        --------
        >>> saagie_client.apps.get_runtime_label_by_id(
        ...     technology_id="11d63963-0a74-4821-b17b-8fcec1234567",
        ...     runtime_id="jupyter-spark-3.1"
        ... )
        'Jupyter Spark 3.1'
        """
        # Get all runtimes of the technology
        runtimes = self.saagie_api.get_runtimes(technology_id)["technology"]
        if not runtimes:  # If the technology doesn't exist, return an empty string
            logging.warning("❌ Technology [%s] not found", technology_id)
            return ""

        # Get the label of the runtime
        runtime_label = next(
            (runtime["label"] for runtime in runtimes.get("appContexts", {}) if runtime.get("id") == runtime_id), ""
        )

        # If the runtime was not found, return an empty string
        if not runtime_label:
            logging.warning("❌ Runtime [%s] not found in technology [%s]", runtime_id, technology_id)
            return ""

        return runtime_label

    def upgrade(
        self,
        app_id: str,
        release_note: str = "",
        exposed_ports: List[Dict] = None,
        storage_paths: List[Dict] = None,
        technology_context: str = None,
        image: str = None,
        docker_credentials_id: str = None,
    ) -> Dict:
        """Update the app

        Parameters
        ----------
        app_id : str
            App ID
        release_note : str, optional
            Release note for the app version
        exposed_ports: List[dict], optional
            List of dict of exposed ports
            If not filled, it takes exposed_ports of previous version
            Each dict should contains 'port' as key
            Ex: [{"basePathVariableName":"SAAGIE_BASE_PATH",
                "isRewriteUrl":True,
                "scope":"PROJECT",
                "number":5000,
                "name":"Test Port"}]
        storage_paths: List[Dict], optional
            List of dict indicating the volume path to the persistent storage
            and :
            - the id of the volume to be associated with the app.
                Ex: [{"path": "/home",
                    "volumeId": "cb70ad1d-7883-48ac-8740-2c8e5c5166ee"}]
        technology_context: str, optional
            Context version of the app
            Incompatible with parameters image & docker_credentials_id
            If not filled, it takes technology_context of previous version
        image: str, optional
            tag of the Docker Image
            Incompatible with parameter technology_context
            If not filled, it takes image of previous version
            ex: hello-world:nanoserver-ltc2022
        docker_credentials_id: str, optional
            Credentials's ID for the image if the image is not public
            Incompatible with parameter technology_context

        Returns
        -------
        dict
            Dict of app version information

        Examples
        --------
        >>> saagie_client.apps.upgrade(
        ...     app_id="97ec670f-8b11-479f-9cd2-c8904ef45b7f",
        ...     exposed_ports=[
        ...         {
        ...             "basePathVariableName": "SAAGIE_BASE_PATH",
        ...             "isRewriteUrl": True,
        ...             "scope": "PROJECT",
        ...             "number": 80,
        ...             "name": "Test Port"
        ...         }
        ...     ],
        ...     storage_paths=[
        ...         {
        ...             "path": "/home",
        ...             "volumeId": "00f5d5d4-1975-478b-81f3-2003b7cff4c2"
        ...         }
        ...     ]
        ... )
        {
            'addAppVersion': {
                'number': 2,
                'releaseNote': '',
                'dockerInfo': None,
                'ports': [
                    {
                        'number': 80,
                        'name': 'Test Port',
                        'basePathVariableName': 'SAAGIE_BASE_PATH',
                        'isRewriteUrl': True,
                        'scope': 'PROJECT'
                    }
                ],
                'volumesWithPath': [
                    {
                        'path': '/home',
                        'volume': {
                            'id': '62f5d5d4-9546-478b-81f3-1970b7cff4c2',
                            'name': 'storage 64MB',
                            'size': '64 MB',
                            'creator': 'titi.tata'
                        }
                    }
                ]
            }
        }
        """

        if technology_context is not None and (image is not None or docker_credentials_id is not None):
            raise ValueError(
                "❌ Incompatible parameters set up."
                "'technology_context' can't be associated to 'image' and/or 'docker_credentials_id'"
            )

        app_info = self.get_info(app_id)["app"]["currentVersion"]

        if exposed_ports is None:
            exposed_ports = app_info["ports"]
            [port.pop("internalUrl", None) for port in exposed_ports]

        params = {
            "appId": app_id,
            "appVersion": {
                "ports": exposed_ports,
                "releaseNote": release_note,
                "volumesWithPath": storage_paths,
                "dockerInfo": {},
            },
        }

        if technology_context is image is None:
            technology_context = app_info["runtimeContextId"]
            if app_info["dockerInfo"] is not None and "image" in app_info["dockerInfo"]:
                image = app_info["dockerInfo"]["image"]

        if image:
            params["appVersion"]["dockerInfo"]["image"] = image

        if docker_credentials_id:
            params["appVersion"]["dockerInfo"]["dockerCredentialsId"] = docker_credentials_id

        # in case of catalog app updated
        if technology_context:
            params["appVersion"]["runtimeContextId"] = technology_context
            params["appVersion"].pop("dockerInfo", None)

        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_APP), variable_values=params)
        logging.info("✅ App [%s] successfully updated", app_id)

        return result

    def rollback(self, app_id: str, version_number: str):
        """Rollback a given app to the given version

        Parameters
        ----------
        app_id : str
            UUID of your app (see README on how to find it)
        version_number : str
            Number of the version to rollback

        Returns
        -------
        dict
            Dict of rollback app

        Examples
        --------
        >>> saagie_api.apps.rollback(app_id="39c56012-0f59-4f51-9852-29a182eff13a", version_number=1)
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
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_ROLLBACK_APP_VERSION), variable_values={"appId": app_id, "versionNumber": version_number}
        )
        logging.info("✅ App [%s] successfully rollbacked to version [%s]", app_id, version_number)
        return result

    def export(
        self,
        app_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
        versions_only_current: bool = False,
    ) -> bool:
        """Export the app in a folder

        Parameters
        ----------
        app_id : str
            App ID
        output_folder : str
            Path to store the exported app
        error_folder : str
            Path to store the error
        error_folder : str, optional
            Path to store the app ID in case of error. If not set, app ID is not write
        versions_only_current : bool, optional
            Whether to only fetch the current version of each app

        Returns
        -------
        bool
            True if app is exported False otherwise

        Examples
        --------
        >>> saagieapi.apps.export(
        ...     app_id="befeacff-8b3b-4269-bf6d-73b5f369313a",
        ...     output_folder="./output/app/",
        ...     error_folder="./output/error/",
        ...     versions_only_current=True
        ... )
        True
        """
        app_info = None
        output_folder = Path(output_folder)

        try:
            app_info = self.get_info(app_id=app_id, versions_only_current=versions_only_current)["app"]
            app_techno_id = app_info["technology"]["id"]
            repo_name, techno_name = self.saagie_api.get_technology_name_by_id(app_techno_id)
            app_info["technology"].update({"name": techno_name, "technology_catalog": repo_name})

            if not versions_only_current:
                for version in app_info["versions"]:
                    version["runtimeContextLabel"] = self.get_runtime_label_by_id(
                        app_techno_id, version["runtimeContextId"]
                    )
            app_info["currentVersion"]["runtimeContextLabel"] = self.get_runtime_label_by_id(
                app_techno_id, app_info["currentVersion"]["runtimeContextId"]
            )
            create_folder(output_folder / app_id)

        except Exception as exception:
            logging.warning("Cannot get the information of the app [%s]", app_id)
            logging.error("Something went wrong %s", exception)
            logging.warning("❌ App [%s] has not been successfully exported", app_id)
            write_error(error_folder, "apps", app_id)
            return False

        write_to_json_file(output_folder / app_id / "app.json", app_info)
        logging.info("✅ App [%s] successfully exported", app_id)

        return True

    def import_from_json(
        self,
        json_file: str,
        project_id: str,
    ) -> bool:
        """Import an app from JSON format

        Parameters
        ----------
        json_file : str
            Path to the JSON file that contains app information
        project_id : str
            Project ID to import the app

        Returns
        -------
        bool
            True if app is imported False otherwise

        Examples
        --------
        >>> saagieapi.apps.import_from_json(
        ...     json_file="/path/to/the/json/file.json",
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        ... )
        True
        """
        json_file = Path(json_file)
        try:
            with json_file.open("r", encoding="utf-8") as file:
                app_info = json.load(file)
        except Exception as exception:
            return handle_error(f"Cannot open the JSON file {json_file}", exception)

        try:
            app_name = app_info["name"]
            app_technology_name = app_info["technology"]["name"]
            app_technology_catalog = app_info["technology"]["technology_catalog"]
            app_runtime_context = app_info["currentVersion"].get("runtimeContextLabel")

            # Remove internalUrl from ports
            app_ports = [
                {k: v for k, v in elem.items() if k != "internalUrl"} for elem in app_info["currentVersion"]["ports"]
            ]

            params = {"projectId": project_id}
            technology_id = context_app_info = None

            if app_runtime_context and app_info["currentVersion"]["runtimeContextId"]:
                techs_project = self.saagie_api.projects.get_apps_technologies(project_id)["appTechnologies"]
                params = self.saagie_api.check_technology(
                    params, app_technology_name, app_technology_catalog, [tech["id"] for tech in techs_project]
                )
                technology_id = params["technologyId"]

                runtimes = self.saagie_api.get_runtimes(technology_id)["technology"]["appContexts"]
                available_runtimes = [app for app in runtimes if app["available"]]
                context_app = next((app for app in available_runtimes if app["label"] == app_runtime_context), None)

                if not context_app:
                    available_contexts = [app["label"] for app in available_runtimes]
                    raise ValueError(
                        f"❌ Runtime '{app_runtime_context}' of the app '{technology_id}' doesn't exist "
                        f"or is not available in the project: '{project_id}'."
                        f"Available runtimes are: '{available_contexts}'"
                    )
                context_app_info = context_app["id"]

            curr_version = app_info["currentVersion"]

            self.create_from_scratch(
                project_id=project_id,
                app_name=app_name,
                image=(curr_version.get("dockerInfo") or {}).get("image", ""),
                description=app_info["description"],
                exposed_ports=app_ports,
                storage_paths=curr_version["volumesWithPath"],
                release_note=curr_version["releaseNote"],
                docker_credentials_id=(curr_version.get("dockerInfo") or {}).get("dockerCredentialsId"),
                emails=(app_info.get("alerting") or {}).get("emails", ""),
                status_list=(app_info.get("alerting") or {}).get("statusList", ""),
                resources=app_info["resources"],
                technology_id=technology_id,
                technology_context=context_app_info,
            )
            logging.info("✅ App [%s] successfully imported", app_name)
        except Exception as exception:
            return handle_error(f"❌ App [{app_name}] has not been successfully imported", exception)

        return True

    def get_id(self, app_name: str, project_name: str) -> str:
        """Get the app id with the app name and project name

        Parameters
        ----------
        app_name : str
            Name of your app
        project_name : str
            Name of your project

        Returns
        -------
        str
            App UUID

        Examples
        --------
        >>> saagieapi.apps.get_id(
        ...     app_name="my-app",
        ...     project_name="my-project"
        ... )
        "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        """
        project_id = self.saagie_api.projects.get_id(project_name)
        apps = self.list_for_project_minimal(project_id)["project"]["apps"]
        if app := next((app for app in apps if app["name"] == app_name), None):
            return app["id"]
        raise NameError(f"❌ App {app_name} does not exist.")

    def get_stats(self, history_id, version_number, start_time):
        """Get stats of the app

        Parameters
        ----------
        history_id : str
            UUID of your app history
        version_number : str
            Number of the version to get the stats
        start_time : str
            Date since to get the stats (format : "%Y-%m-%dT%H:%M:%S.%fZ")

        Returns
        -------
        dict
            Dict of app's stats

        Examples
        --------
        >>> saagieapi.apps.get_stats(
        ...     history_id="55943477-c41b-4dfe-a8ca-c110909d9204",
        ...     version_number=2,
        ...     start_time="2024-04-10T14:26:27.073Z"
        ... )
        {
            'appStats': {
                'uptimePercentage': 0.04,
                'downtimePercentage': 99.96,
                'recoveredCount': 0
            }
        }
        """
        params = {
            "appHistoryId": history_id,
            "versionNumber": version_number,
            "startTime": start_time,
        }

        return self.saagie_api.client.execute(query=gql(GQL_STATS_APP), variable_values=params)

    def get_history_statuses(self, history_id, version_number, start_time):
        """Get statuses history of the app

        Parameters
        ----------
        history_id : str
            UUID of your app history
        version_number : str
            Number of the version to get the statuses history
        start_time : str
            Date since to get the statuses history (format : "%Y-%m-%dT%H:%M:%S.%fZ")

        Returns
        -------
        dict
            Dict of app's statuses history

        Examples
        --------
        >>> saagieapi.apps.get_history_statuses(
        ...     history_id="55943477-c41b-4dfe-a8ca-c110909d9204",
        ...     version_number=2,
        ...     start_time="2023-07-31T14:26:27.073Z"
        ... )
        {
            'appHistoryStatuses': [
                {'status': 'STARTING', 'recordAt': '2023-08-01T08:38:34.859Z'},
                {'status': 'STARTED', 'recordAt': '2023-08-01T08:38:38.845Z'},
                {'status': 'FAILED', 'recordAt': '2023-08-01T08:38:39.875Z'},
                {'status': 'RECOVERING', 'recordAt': '2023-08-01T08:38:39.875Z'},
                {'status': 'STOPPING', 'recordAt': '2023-08-01T08:38:41.094Z'},
                {'status': 'STOPPED', 'recordAt': '2023-08-01T08:38:41.241Z'}
            ]
        }
        """
        params = {
            "appHistoryId": history_id,
            "versionNumber": version_number,
            "startTime": start_time,
        }

        return self.saagie_api.client.execute(query=gql(GQL_HISTORY_APP_STATUS), variable_values=params)

    def count_history_statuses(self, history_id, version_number, start_time):
        """Get count of statues history of the app

        Parameters
        ----------
        history_id : str
            UUID of your app history
        version_number : str
            Number of the version to get the count of statuses history
        start_time : str
            Date since to get the count of statuses history (format : "%Y-%m-%dT%H:%M:%S.%fZ")

        Returns
        -------
        dict
            count of statuses history

        Examples
        --------
        >>> saagieapi.apps.count_history_statuses(
        ...     history_id="55943477-c41b-4dfe-a8ca-c110909d9204",
        ...     version_number=2,
        ...     start_time="2024-04-10T14:26:27.073Z"
        ... )
        {
            'countAppHistoryStatuses': 6
        }
        """
        params = {
            "appHistoryId": history_id,
            "versionNumber": version_number,
            "startTime": start_time,
        }

        return self.saagie_api.client.execute(query=gql(GQL_COUNT_HISTORY_APP_STATUS), variable_values=params)

    def get_logs(
        self,
        app_id: str,
        app_execution_id: str,
        limit: int = None,
        skip: int = None,
        log_stream: str = None,
        start_at: str = None,
    ):
        """Get logs of the app

        Parameters
        ----------
        app_id : str
            UUID of your app
        app_execution_id : str
            UUID of the execution of your app
        limit : int, optional
            Number of log lines to retrieve
        skip : int, optional
            Number of log lines to skip
        log_stream: str, optional
            Stream of logs to follow. Values accepted :
            [ENVVARS_STDOUT, ENVVARS_STDERR, ORCHESTRATION_STDOUT, ORCHESTRATION_STDERR, STDERR, STDOUT]
            By default, all the streams are retrieved
        start_at: str, optional
            Get logs since a specific datetime.
            Following formats accepted : "2024-04-09 10:00:00" and "2024-04-09T10:00:00"

        Returns
        -------
        dict
            Logs of the app

        Examples
        --------
        >>> saagieapi.apps.get_logs(
        ...     app_id="70e85ade-d6cc-4a90-8d7d-639adbd25e5d",
        ...     app_execution_id="e3e31074-4a12-450e-96e4-0eae7801dfca",
        ...     limit=2,
        ...     skip=5,
        ...     start_at="2024-04-09 10:00:00"
        ... )
        {
            "appLogs": {
                "count": 25,
                "content": [
                    {
                        "index": 5,
                        "value": "[I 2024-04-09 13:38:36.982 ServerApp] jupyterlab_git | extension was successfully linked.",
                        "containerId": "d7104fa7371c5ed6ef540fa8b0620a654a0e02c57136e29f0fcc03d16e36d74f",
                        "stream": "STDERR",
                        "recordAt": "2024-04-09T13:38:36.982473892Z"
                    },
                    {
                        "index": 6,
                        "value": "[W 2024-04-09 13:38:36.987 NotebookApp] 'ip' has moved from NotebookApp to ServerApp. This config will be passed to ServerApp. Be sure to update your config before our next release.",
                        "containerId": "d7104fa7371c5ed6ef540fa8b0620a654a0e02c57136e29f0fcc03d16e36d74f",
                        "stream": "STDERR",
                        "recordAt": "2024-04-09T13:38:36.987400105Z"
                    }
                ]
            }
        }
        """
        params = {
            "appId": app_id,
            "appExecutionId": app_execution_id,
        }

        if limit:
            params["limit"] = limit

        if skip:
            params["skip"] = skip

        if log_stream:
            params["stream"] = log_stream

        if start_at:
            params["recordAt"] = start_at

        return self.saagie_api.client.execute(query=gql(GQL_GET_APP_LOG), variable_values=params)
