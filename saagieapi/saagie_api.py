import logging
import re
from typing import Dict, List, Tuple

import pytz
from croniter import croniter
from gql import gql

from .apps import Apps
from .docker_credentials import DockerCredentials
from .env_vars import EnvVars
from .gql_queries import (
    GQL_CHECK_CUSTOM_EXPRESSION,
    GQL_COUNT_CONDITION_LOGS,
    GQL_GET_CLUSTER_INFO,
    GQL_GET_CONDITION_LOGS_BY_CONDITION,
    GQL_GET_CONDITION_LOGS_BY_INSTANCE,
    GQL_GET_PLATFORM_INFO,
    GQL_GET_REPOSITORIES_INFO,
    GQL_GET_RUNTIMES,
)
from .groups import Groups
from .jobs import Jobs
from .pipelines import Pipelines
from .profiles import Profiles
from .projects import Projects
from .repositories import Repositories
from .storages import Storages
from .users import Users
from .utils.bearer_auth import BearerAuth
from .utils.gql_client import GqlClient
from .utils.request_client import RequestClient


class SaagieApi:
    # pylint: disable=too-many-instance-attributes
    """Define several methods to interact with Saagie API in Python"""

    def __init__(
        self,
        url_saagie: str,
        id_platform: str,
        user: str,
        password: str,
        realm: str,
        retries: int = 0,
        pprint_global: bool = False,
        timeout: int = 10,
    ):
        """
        Parameters
        ----------
        url_saagie : str
            platform base URL (eg: https://saagie-workspace.prod.saagie.io)
        id_platform : int or str
            Platform id  (see README on how to find it)
        user : str
            username to log in with
        password : str
            password to log in with
        realm : str
            Saagie realm  (see README on how to find it)
        retries : int
            Pre-setup of the requests’ Session for performing retries
        pprint_global : bool
            Change the default pprint of all the requests made with this client
        timeout: int
            Pre-setup of the requests' Session Timeout, default to 10 seconds
        """
        if not url_saagie.endswith("/"):
            url_saagie += "/"

        self.url_saagie = url_saagie
        self.realm = realm
        self.auth = BearerAuth(
            realm=self.realm, url=self.url_saagie, platform=id_platform, login=user, password=password
        )
        logging.info("✅ Successfully connected to your platform %s", self.url_saagie)
        url_api = f"{self.url_saagie}projects/api/platform/{id_platform}/graphql"
        self.client = GqlClient(auth=self.auth, api_endpoint=url_api, timeout=timeout, retries=retries)

        url_gateway = f"{self.url_saagie}gateway/api/graphql"
        self.client_gateway = GqlClient(auth=self.auth, api_endpoint=url_gateway, timeout=timeout, retries=retries)

        self.projects = Projects(self)
        self.jobs = Jobs(self)
        self.pipelines = Pipelines(self)
        self.env_vars = EnvVars(self)
        self.apps = Apps(self)
        self.docker_credentials = DockerCredentials(self)
        self.repositories = Repositories(self)
        self.storages = Storages(self)
        self.users = Users(self)
        self.groups = Groups(self)
        self.profiles = Profiles(self)
        self.pprint_global = pprint_global
        self.client.pprint_global = pprint_global
        self.client_gateway.pprint_global = pprint_global
        self.verify_ssl = True
        self.request_client = RequestClient(auth=self.auth, realm=self.realm, verify_ssl=self.verify_ssl)

    @classmethod
    def easy_connect(cls, url_saagie_platform: str, user: str, password: str):
        """
        Alternative constructor which uses the complete URL (eg:
        https://saagie-workspace.prod.saagie.io/projects/platform/6/) and will
        parse it in order to retrieve the platform URL, platform id and the
        realm.

        Parameters
        ----------
        url_saagie_platform : str
            Complete platform URL (eg: https://saagie-workspace.prod.saagie.io/projects/platform/6/)
        user : str
            username to log in with
        password : str
            password to log in with
        """
        url_regex = re.compile(r"(https://(\w+)-(?:\w|\.)+)/projects/platform/(\d+)")
        matches_url = url_regex.match(url_saagie_platform)
        if not bool(matches_url):
            raise ValueError(
                "❌ Please use a correct URL (eg: https://saagie-workspace.prod.saagie.io/projects/platform/6/)"
            )
        url_saagie = matches_url[1]
        realm = matches_url[2]
        id_platform = matches_url[3]
        return cls(url_saagie, id_platform, user, password, realm)

    @staticmethod
    def check_alerting(emails: List, status_list: List) -> Dict:
        """
        Check if the alerting is enabled for the given project and if so, check params and status_list.
        Parameters
        ----------
        emails : list
            List of emails to send the alert
        status_list : list
            status list of the alert

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
            "REQUESTED",
            "QUEUED",
            "RUNNING",
            "FAILED",
            "KILLED",
            "KILLING",
            "SUCCEEDED",
            "UNKNOWN",
            "AWAITING",
            "SKIPPED",
        ]

        if not status_list:
            status_list = ["FAILED"]

        if wrong_status_list := [item for item in status_list if item not in valid_status_list]:
            raise RuntimeError(
                f"❌ The following status are not valid: {wrong_status_list}. "
                f"Please make sure that each item of the parameter status_list should be "
                f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'"
            )

        return {"alerting": {"emails": emails, "statusList": status_list}}

    @staticmethod
    def check_scheduling(cron_scheduling: str, schedule_timezone: str) -> Dict:
        """
        Check if the cron_scheduling is valid and if it is, add it to the params.
        Parameters
        ----------
        cron_scheduling : str
            cronjob expression
        schedule_timezone : str
            timezone of the schedule

        Returns
        -------
        dict
            Dict containing schedule config

        Raises
        ------
        RunTimeError
            When the cronjob expression is invalid of the timezone does not exist
        """
        schedule_dict = {"isScheduled": True}
        if cron_scheduling and croniter.is_valid(cron_scheduling):
            schedule_dict["cronScheduling"] = cron_scheduling
        else:
            raise RuntimeError(f"❌ {cron_scheduling} is not valid cron format")
        if schedule_timezone in list(pytz.all_timezones):
            schedule_dict["scheduleTimezone"] = schedule_timezone
        else:
            raise RuntimeError("❌ Please specify a correct timezone")
        return schedule_dict

    # ##########################################################
    # ###                    cluster                        ####
    # ##########################################################

    def get_cluster_capacity(self) -> Dict:
        """
        Get information for cluster (cpu, gpu, memory)

        Returns
        -------
        dict
            Dict of cluster resources

        Examples
        --------
        >>> saagie_api.get_cluster_capacity()
        {
            "getClusterCapacity":[
                {
                    "cpu":3.8,
                    "gpu":0.0,
                    "memory":16.083734528
                },
                {
                    "cpu":3.8,
                    "gpu":0.0,
                    "memory":16.083734528
                },
                {
                    "cpu":3.8,
                    "gpu":0.0,
                    "memory":16.08372224
                }
            ]
        }
        """
        query = gql(GQL_GET_CLUSTER_INFO)
        return self.client.execute(query)

    # ##########################################################
    # ###                    platform                       ####
    # ##########################################################

    def get_platform_info(self) -> Dict:
        """
        Get platform info (nb projects, jobs, apps, pipelines)

        Returns
        -------
        dict
            Dict of platform info

        Examples
        --------
        >>> saagie_api.get_platform_info()
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
        """
        query = gql(GQL_GET_PLATFORM_INFO)
        return self.client.execute(query)

    # ##########################################################
    # ###                    repositories                   ####
    # ##########################################################

    def get_repositories_info(self) -> Dict:
        """
        Get information for all repositories (id, name, technologies)
        NB: You can only get repositories information if you have the right to
        access the technology catalog

        Returns
        -------
        dict
            Dict of repositories

        Examples
        --------
        >>> saagie_api.get_repositories_info()
        {
            "repositories":[
                {
                    "id":"9fcbddfe-a7b7-4d25-807c-ad030782c923",
                    "name":"Saagie",
                    "technologies":[
                        {
                            "id":"5cbb55aa-8ce9-449b-b0b9-64cc6781ea89",
                            "label":"R",
                            "available":True,
                            "__typename":"JobTechnology"
                        },
                        {
                            "id":"36912c68-d084-43b9-9fda-b5ded8eb7b13",
                            "label":"Docker image",
                            "available":True,
                            "__typename":"AppTechnology"
                        },
                        {
                            "id":"1d117fb6-0697-438a-b419-a69e0e7406e8",
                            "label":"Spark",
                            "available":True,
                            "__typename":"SparkTechnology"
                        }
                    ]
                },
                {
                    "id":"fff42d30-2029-4f23-b326-d751f256f533",
                    "name":"Saagie Community",
                    "technologies":[
                        {
                            "id":"034c28d7-c21f-4d7c-8dd9-7d09bc02f33f",
                            "label":"ShinyProxy",
                            "available":True,
                            "__typename":"AppTechnology"
                        }
                    ]
                }
            ]
        }
        """
        query = gql(GQL_GET_REPOSITORIES_INFO)
        return self.client_gateway.execute(query)

    # ##########################################################
    # ###                    technologies                   ####
    # ##########################################################

    def check_technology(
        self, params: Dict, technology: str, technology_catalog: str, technologies_configured_for_project: List
    ):
        """
        Get all technlogies in the catalogs and calls the check_technology_valid method
        Parameters
        ----------
        params : dict
            dict containing the params of the technology
        technology : str
            technology to check
        technology_catalog : str
            timezone of the schedule
        technologies_configured_for_project : list
            list of technologies configured for the project (can be either jobs or apps)
        """
        all_technologies_in_catalog = self.get_available_technologies(technology_catalog)
        technology_id = self.check_technology_valid([technology], all_technologies_in_catalog, technology_catalog)[0]
        return self.check_technology_configured(params, technology, technology_id, technologies_configured_for_project)

    @staticmethod
    def check_technology_valid(
        technologies: List[str], all_technologies_in_catalog: List, technology_catalog: str
    ) -> List[str]:
        """
        Check if the technology is configured for the project
        Parameters
        ----------
        technologies : list
            technology labels to check
        all_technologies_in_catalog : list
            list of all technologies in the catalog
        technology_catalog : str
            catalog of the technology

        Returns
        -------
        list of technology ids

        Raises
        ------
        RunTimeError
            When :
            - the technology does not exist in the catalog
            - the catalog does not exist or does not contains technologies
        """
        if not all_technologies_in_catalog:
            raise RuntimeError(f"❌ Catalog {technology_catalog} does not exist or does not contain technologies")
        technology_ids_validated = [
            tech["id"]
            for tech in all_technologies_in_catalog
            if tech["label"].lower() in [t.lower() for t in technologies]
        ]
        if not technology_ids_validated:
            raise RuntimeError(f"❌ Technologies {technologies} do not exist in the catalog specified")
        if len(technology_ids_validated) != len(technologies):
            raise RuntimeError(f"❌ Some technologies among {technologies} do not exist in the catalog specified")

        return technology_ids_validated

    @staticmethod
    def check_technology_configured(
        params: Dict, technology: str, technology_id: str, technologies_configured_for_project: List
    ) -> Dict:
        """
        Check if the technology exists in the category specified
        Parameters
        ----------
        params : dict
            dict containing the params of the technology
        technology : str
            technology label to add
        technology_id : str
            technology id to add
        technologies_configured_for_project : list
            list of technologies configured for the project (can be either jobs or apps)

        Returns
        -------
        dict
            Dict containing technology id

        Raises
        ------
        RunTimeError
            When :
            - the technology is not configured in the project
        """
        if technology_id not in technologies_configured_for_project:
            raise RuntimeError(
                f"❌ Technology {technology} does not exist in the target project and for the catalog specified"
            )

        params["technologyId"] = technology_id
        return params

    def get_available_technologies(self, catalog: str) -> List:
        """Get the list of available jobs technologies for the specified catalog

        Parameters
        ----------
        catalog : str
            Catalog name

        Returns
        -------
        dict
            Dict of technologies available

        Examples
        --------
        >>> saagieapi.get_available_technologies(catalog="Saagie")
        [
            {
                'id': 'a3a5e5ea-7af1-47db-b9ca-fed722a123b1',
                'label': 'Apache Superset',
                'available': True,
                '__typename': 'AppTechnology'
            },
            {
                'id': '19d446bd-bf31-462b-9c0b-023123f5dc4a',
                'label': 'CloudBeaver',
                'available': True,
                '__typename': 'AppTechnology'
            },
            {
                'id': 'a55afd45-3938-4ee3-8d16-e93227c76b93',
                'label': 'Dash',
                'available': True,
                '__typename': 'AppTechnology'
            }
            ,
            {
                'id': '4adb934e-8ee7-4942-9951-fd461b6769b1',
                'label': 'Bash',
                'available': True,
                '__typename': 'JobTechnology'
            },
            {
                'id': '1669e3ca-9fcf-1234-be11-cc2f3afabb1d',
                'label': 'Generic',
                'available': True,
                '__typename': 'JobTechnology'
            },
            {
                'id': '7f7c5c02-e187-448c-8552-99eed6af2001',
                'label': 'Java/Scala',
                'available': True,
                '__typename': 'JobTechnology'
            },
            {
                'id': '9bb93cad-69a5-4a9d-b059-811c6cde589e',
                'label': 'Python',
                'available': True,
                '__typename': 'JobTechnology'
            }
        ]
        """
        all_technologies_in_catalog = [
            repository["technologies"]
            for repository in (self.get_repositories_info()["repositories"])
            if repository["name"].lower() == catalog.lower()
        ]
        return (
            [techno for techno in all_technologies_in_catalog[0] if techno["available"] is True]
            if all_technologies_in_catalog
            else []
        )

    def get_runtimes(self, technology_id) -> Dict:
        """Get the list of runtimes for a technology id

        Parameters
        ----------
        technology_id : str
            UUID of the technology

        Returns
        -------
        dict
            Dict of runtime labels

        Examples
        --------
        >>> saagieapi.get_runtimes(technology_id="11d63963-0a74-4821-b17b-8fcec4882863")
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
        """
        return self.client_gateway.execute(gql(GQL_GET_RUNTIMES), variable_values={"id": technology_id})

    def get_technology_name_by_id(self, technology_id: str) -> Tuple[str, str]:
        """Get the name and the repository of a specific technology

        Parameters
        ----------
        technology_id : str
            Technology ID

        Returns
        -------
        (str, str)
            Repository name and the label of the specific technology

        Examples
        --------
        >>> saagieapi.get_technology_name_by_id(technology_id="11d63963-0a74-4821-b17b-8fcec4882863")
        ('Saagie', 'Jupyter Notebook')
        """
        all_technologies = self.get_repositories_info()["repositories"]

        technology_label_with_repo_name = [
            (repo["name"], tech["label"])
            for repo in all_technologies
            for tech in repo["technologies"]
            if tech["id"] == technology_id
        ]
        if not technology_label_with_repo_name:
            return "", ""
        repo_name, tech_name = technology_label_with_repo_name[0]
        return repo_name, tech_name

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
        dict
            String of runtime label

        """
        runtimes = self.get_runtimes(technology_id)

        return [runtime["label"] for runtime in runtimes["technology"]["appContexts"] if runtime["id"] == runtime_id]

    # ##########################################################
    # ###                    Conditions                     ####
    # ##########################################################

    def check_condition_expression(self, expression: str, project_id: str, variables: Dict = None) -> Dict:
        """Test the condition expression

        Parameters
        ----------
        expression : str
            Expression to test
        project_id : str
            UUID of the project
        variables : Dict
            List of logs files name to see (example : STDERR, STDOUT)

        Returns
        -------
        Dict
            Dict of result of the condition expression

        Examples
        --------
        >>> saagieapi.check_condition_expression(
        ...     expression="double(rmse) > 500.0",
        ...     project_id="your_project_id",
        ...     variables={"key": "rmse", "value": 300}
        ... )
        {
            "data": {
                "evaluateConditionExpression": False
            }
        }
        """

        params = {
            "projectId": project_id,
            "expression": expression,
            "variables": variables or {"key": "", "value": ""},
        }
        return self.client.execute(query=gql(GQL_CHECK_CUSTOM_EXPRESSION), variable_values=params)

    def count_condition_logs(self, condition_instance_id: str, project_id: str, streams: List[str]) -> Dict:
        """Get number of logs line for an instance of a condition on Environment Variable

        Parameters
        ----------
        condition_instance_id : str
            UUID of the condition instance
        project_id : str
            UUID of the project
        streams : List[str]
            List of logs files name to see (example : STDERR, STDOUT)

        Returns
        -------
        Dic
            Dict of number of logs lines

        Examples
        --------
        >>> saagieapi.count_condition_logs(
        ...     condition_instance_id="your_condition_instance_id",
        ...     project_id="your_project_id",
        ...     streams=["STDOUT"]
        ... )
        {
            "data": {
                "conditionPipelineCountFilteredLogs": 4
            }
        }
        """

        params = {"conditionInstanceId": condition_instance_id, "projectID": project_id, "streams": streams}

        return self.client.execute(query=gql(GQL_COUNT_CONDITION_LOGS), variable_values=params)

    def get_condition_instance_logs_by_condition(
        self,
        condition_id: str,
        project_id: str,
        pipeline_instance_id: str,
        streams: List[str],
        limit: int = None,
        skip: int = None,
    ) -> Dict:
        """Get logs for a condition on Environment Variable of a pipeline instance

        Parameters
        ----------
        condition_id : str
            UUID of the condition
        project_id : str
            UUID of the project
        pipeline_instance_id ! str
            UUID of the pipeline instance
        streams : List[str]
            List of logs files name to see (example : STDERR, STDOUT)
        limit : int
            Number of logs lines to return from the beginning
        skip : int
            Number of logs lines to doesn't display from the beginning

        Returns
        -------
        dict
            Dict of logs lines

        Examples
        --------
        >>> saagieapi.get_condition_instance_logs_by_condition(
        ...     condition_id="condition_node_id",
        ...     project_id="project_id",
        ...     pipeline_instance_id="pipeline_instance_id",
        ...     streams=["STDOUT"]
        ... )
        {
            "data": {
                "conditionPipelineByNodeIdFilteredLogs": {
                    "count": 4,
                    "content": [
                        {
                            "index": 0,
                            "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Condition: 'tube_name.contains(\"Tube\") ||",
                            "stream": "STDOUT"
                        },
                        {
                            "index": 1,
                            "value": "double(diameter) > 1.0'",
                            "stream": "STDOUT"
                        },
                        {
                            "index": 2,
                            "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Condition evaluation took: 4.736725ms",
                            "stream": "STDOUT"
                        },
                        {
                            "index": 3,
                            "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Result: true",
                            "stream": "STDOUT"
                        }
                    ]
                }
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "conditionNodeID": condition_id,
            "projectID": project_id,
            "pipelineInstanceID": pipeline_instance_id,
            "streams": streams,
        }
        if limit:
            params["limit"] = limit

        if skip:
            params["skip"] = skip

        return self.client.execute(query=gql(GQL_GET_CONDITION_LOGS_BY_CONDITION), variable_values=params)

    def get_condition_instance_logs_by_instance(
        self,
        condition_instance_id: str,
        project_id: str,
        streams: List[str],
        limit: int = None,
        skip: int = None,
    ) -> Dict:
        """Get instance's logs of a condition on Environment Variable

        Parameters
        ----------
        condition_instance_id : str
            UUID of the condition instance
        project_id : str
            UUID of the project
        streams : List[str]
            List of logs files name to see (example : STDERR, STDOUT)
        limit : int
            Number of logs lines to return from the beginning
        skip : int
            Number of logs lines to doesn't display from the beginning

        Returns
        -------
        dict
            Dict of logs lines

        Examples
        --------
        >>> saagieapi.get_condition_instance_logs_by_instance(
        ...     condition_instance_id="condition_instance_id",
        ...     project_id="project_id"
        ... )
        {
            "data": {
                "conditionPipelineByNodeIdFilteredLogs": {
                    "count": 4,
                    "content": [
                        {
                            "index": 0,
                            "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Condition: 'tube_name.contains(\"Tube\") ||",
                            "stream": "STDOUT"
                        },
                        {
                            "index": 1,
                            "value": "double(diameter) > 1.0'",
                            "stream": "STDOUT"
                        },
                        {
                            "index": 2,
                            "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Condition evaluation took: 4.736725ms",
                            "stream": "STDOUT"
                        },
                        {
                            "index": 3,
                            "value": "2023/05/15 12:55:19 INFO [evaluate_condition] Result: true",
                            "stream": "STDOUT"
                        }
                    ]
                }
            }
        }
        """  # pylint: disable=line-too-long
        params = {
            "conditionInstanceId": condition_instance_id,
            "projectId": project_id,
            "streams": streams,
        }
        if limit:
            params["limit"] = limit

        if skip:
            params["skip"] = skip

        return self.client.execute(query=gql(GQL_GET_CONDITION_LOGS_BY_INSTANCE), variable_values=params)
