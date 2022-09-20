import logging
import re
from typing import Dict, List, Tuple

import pytz
from croniter import croniter
from gql import gql

from .apps import Apps
from .docker_credentials import DockerCredentials
from .env_vars import EnvVars
from .gql_queries import GQL_GET_CLUSTER_INFO, GQL_GET_REPOSITORIES_INFO, GQL_GET_RUNTIMES
from .jobs import Jobs
from .pipelines import Pipelines
from .projects import Projects
from .repositories import Repositories
from .storages import Storages
from .utils.bearer_auth import BearerAuth
from .utils.gql_client import GqlClient


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
        """
        if not url_saagie.endswith("/"):
            url_saagie += "/"

        self.url_saagie = url_saagie
        self.auth = BearerAuth(realm=realm, url=self.url_saagie, platform=id_platform, login=user, password=password)
        logging.info("✅ Successfully connected to your platform %s", self.url_saagie)
        url_api = f"{self.url_saagie}projects/api/platform/{str(id_platform)}/graphql"
        self.client = GqlClient(auth=self.auth, api_endpoint=url_api, retries=retries)

        url_gateway = self.url_saagie + "gateway/api/graphql"
        self.client_gateway = GqlClient(auth=self.auth, api_endpoint=url_gateway, retries=retries)

        self.projects = Projects(self)
        self.jobs = Jobs(self)
        self.pipelines = Pipelines(self)
        self.env_vars = EnvVars(self)
        self.apps = Apps(self)
        self.docker_credentials = DockerCredentials(self)
        self.repositories = Repositories(self)
        self.storages = Storages(self)
        self.pprint_global = pprint_global
        self.client.pprint_global = pprint_global
        self.client_gateway.pprint_global = pprint_global

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
        if bool(matches_url):
            url_saagie = matches_url.group(1)
            realm = matches_url.group(2)
            id_platform = matches_url.group(3)
        else:
            raise ValueError(
                "❌ Please use a correct URL (eg: https://saagie-workspace.prod.saagie.io/projects/platform/6/)"
            )
        return cls(url_saagie, id_platform, user, password, realm)

    @staticmethod
    def check_alerting(emails: List, params: Dict, status_list: List) -> Dict:
        """
        Check if the alerting is enabled for the given project and if so, check params and status_list.
        Parameters
        ----------
        emails : list
            List of emails to send the alert
        params : dict
            dict containing the params of the alert
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
        wrong_status_list = []
        for item in status_list:
            if item not in valid_status_list:
                wrong_status_list.append(item)
        if wrong_status_list:
            raise RuntimeError(
                f"❌ The following status are not valid: {wrong_status_list}. "
                f"Please make sure that each item of the parameter status_list should be "
                f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'"
            )

        params["alerting"] = {"emails": emails, "statusList": status_list}
        return params

    @staticmethod
    def check_scheduling(cron_scheduling: str, params: Dict, schedule_timezone: str) -> Dict:
        """
        Check if the cron_scheduling is valid and if it is, add it to the params.
        Parameters
        ----------
        cron_scheduling : str
            cronjob expression
        params : dict
            dict containing the params of the alert
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
        params["isScheduled"] = True
        if cron_scheduling and croniter.is_valid(cron_scheduling):
            params["cronScheduling"] = cron_scheduling
        else:
            raise RuntimeError(f"❌ {cron_scheduling} is not valid cron format")
        if schedule_timezone in list(pytz.all_timezones):
            params["scheduleTimezone"] = schedule_timezone
        else:
            raise RuntimeError("❌ Please specify a correct timezone")
        return params

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
        """
        query = gql(GQL_GET_CLUSTER_INFO)
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

        Returns
        -------
        dict
            Dict of technologies available
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

        """
        return self.client_gateway.execute(gql(GQL_GET_RUNTIMES), variable_values={"id": technology_id})

    def get_technology_name_by_id(self, technology_id: str) -> Tuple[str, str]:
        """
        Get the name and the repository of a specific technology
        Parameters
        ----------
        technology_id : str
            Technology ID

        Returns
        -------
        (str, str)
        Repository name and the label of the specific technology

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
        runtime_label = [
            runtime["label"] for runtime in runtimes["technology"]["appContexts"] if runtime["id"] == runtime_id
        ]

        return runtime_label
