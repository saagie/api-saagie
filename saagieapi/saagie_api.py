import logging
import re
from typing import Dict, List

import deprecation
import pytz
import requests
from croniter import croniter
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .apps import Apps
from .docker_credentials import DockerCredentials
from .env_vars import EnvVars
from .gql_queries import *
from .jobs import Jobs
from .pipelines import Pipelines
from .projects import Projects


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, realm: str, url: str, platform: str, login: str, password: str):
        self.token = self._authenticate(realm, url, login, password)
        self.platform = platform
        self.url = url

    def __call__(self, req):
        req.headers["authorization"] = "Bearer " + self.token
        return req

    @staticmethod
    def _authenticate(realm: str, url: str, login: str, password: str) -> str:
        """
        Retrieve a Bearer connection token
        :param realm: platform url prefix (eg: saagie)
        :param url: platform URL (eg: https://saagie-workspace.prod.saagie.io)
        :param login: username to log in with
        :param password: password to log in with
        :return: a token
        """
        session = requests.session()
        session.headers["Content-Type"] = "application/json"
        session.headers["Saagie-Realm"] = realm
        response = session.post(
            url + "/authentication/api/open/authenticate", json={"login": login, "password": password}, verify=False
        )
        return response.text


class SaagieApi:
    # pylint: disable=too-many-instance-attributes
    """Define several methods to interact with Saagie API in Python"""

    def __init__(self, url_saagie: str, id_platform: str, user: str, password: str, realm: str, retries: int = 0):
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
        """
        if not url_saagie.endswith("/"):
            url_saagie += "/"
        self.url_saagie = url_saagie
        self.id_platform = id_platform
        self.suffix_api = "projects/api/"
        self.realm = realm
        self.login = user
        self.password = password
        self.retries = retries
        self.auth = BearerAuth(self.realm, self.url_saagie, self.id_platform, self.login, self.password)
        url = self.url_saagie + self.suffix_api + "platform/"
        url += str(self.id_platform) + "/graphql"
        self._url = url
        self._transport = RequestsHTTPTransport(
            url=self._url, auth=self.auth, use_json=True, verify=False, retries=self.retries
        )
        self.client = Client(transport=self._transport, fetch_schema_from_transport=True)

        # URL Gateway
        self.url_gateway = self.url_saagie + "gateway/api/graphql"
        self._transport_gateway = RequestsHTTPTransport(
            url=self.url_gateway, auth=self.auth, use_json=True, verify=False
        )
        self.client_gateway = Client(transport=self._transport_gateway, fetch_schema_from_transport=True)

        # Valid status list of alerting
        self.projects = Projects(self)
        self.jobs = Jobs(self)
        self.pipelines = Pipelines(self)
        self.env_vars = EnvVars(self)
        self.apps = Apps(self)
        self.docker_credentials = DockerCredentials(self)

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
                "Please use a correct URL (eg: https://saagie-workspace.prod.saagie.io/projects/platform/6/)"
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
                f"The following status are not valid: {wrong_status_list}. "
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
            raise RuntimeError(f"{cron_scheduling} is not valid cron format")
        if schedule_timezone in list(pytz.all_timezones):
            params["scheduleTimezone"] = schedule_timezone
        else:
            raise RuntimeError("Please specify a correct timezone")
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
            timezone of the schedule
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
            raise RuntimeError(f"Catalog {technology_catalog} does not exist or does not contain technologies")
        technology_ids_validated = [
            tech["id"]
            for tech in all_technologies_in_catalog
            if tech["label"].lower() in [t.lower() for t in technologies]
        ]
        len(technologies)
        if not technology_ids_validated:
            raise RuntimeError(f"Technologies {technologies} do not exist in the catalog specified")
        if len(technology_ids_validated) != len(technologies):
            raise RuntimeError(f"Some technologies among {technologies} do not exist in the catalog specified")

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
                f"Technology {technology} does not exist in the target project  " f"and for the catalog specified"
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

    # ######################################################
    # ###                    jobs                   ####
    # ######################################################

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.list_for_project' instead."
    )
    def get_project_jobs(self, project_id, instances_limit=-1):
        return self.jobs.list_for_project(project_id, instances_limit)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.get_by_id' instead."
    )
    def get_project_job(self, job_id):
        return self.jobs.get_info(job_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.get_instance' instead."
    )
    def get_job_instance(self, job_instance_id):
        return self.jobs.get_instance(job_instance_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.run' instead."
    )
    def run_job(self, job_id):
        return self.jobs.run(job_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.run_with_callback' instead."
    )
    def run_job_callback(self, job_id, freq=10, timeout=-1):
        return self.jobs.run_with_callback(job_id, freq, timeout)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.stop' instead."
    )
    def stop_job(self, job_instance_id):
        return self.jobs.stop(job_instance_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.edit' instead."
    )
    def edit_job(
        self,
        job_id,
        job_name=None,
        description=None,
        is_scheduled=None,
        cron_scheduling=None,
        schedule_timezone="UTC",
        resources=None,
        emails=None,
        status_list=["FAILED"],
    ):
        return self.jobs.edit(
            job_id,
            job_name,
            description,
            is_scheduled,
            cron_scheduling,
            schedule_timezone,
            resources,
            emails,
            status_list,
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.create' instead."
    )
    def create_job(
        self,
        job_name,
        project_id,
        file=None,
        description="",
        category="Processing",
        technology="python",
        technology_catalog="Saagie",
        runtime_version="3.6",
        command_line="python {file} arg1 arg2",
        release_note="",
        extra_technology="",
        extra_technology_version="",
        cron_scheduling=None,
        schedule_timezone="UTC",
        resources=None,
        emails=None,
        status_list=["FAILED"],
    ):
        return self.jobs.create(
            job_name,
            project_id,
            file,
            description,
            category,
            technology,
            technology_catalog,
            runtime_version,
            command_line,
            release_note,
            extra_technology,
            extra_technology_version,
            cron_scheduling,
            schedule_timezone,
            resources,
            emails,
            status_list,
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.get_info' instead."
    )
    def get_job_info(self, job_id):
        return self.jobs.get_info(job_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.upgrade' instead."
    )
    def upgrade_job(
        self,
        job_id,
        file=None,
        use_previous_artifact=False,
        runtime_version="3.6",
        command_line="python {file} arg1 arg2",
        release_note=None,
        extra_technology="",
        extra_technology_version="",
    ):
        return self.jobs.upgrade(
            job_id,
            file,
            use_previous_artifact,
            runtime_version,
            command_line,
            release_note,
            extra_technology,
            extra_technology_version,
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.get_id' instead."
    )
    def get_job_id(self, job_name, project_name):
        return self.jobs.get_id(job_name, project_name)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.upgrade_by_name' instead."
    )
    def upgrade_job_by_name(
        self,
        job_name,
        project_name,
        file=None,
        use_previous_artifact=False,
        runtime_version="3.6",
        command_line="python {file} arg1 arg2",
        release_note=None,
        extra_technology="",
        extra_technology_version="",
    ):
        return self.jobs.upgrade_by_name(
            job_name,
            project_name,
            file,
            use_previous_artifact,
            runtime_version,
            command_line,
            release_note,
            extra_technology,
            extra_technology_version,
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.jobs.delete' instead."
    )
    def delete_job(self, job_id):
        return self.jobs.delete(job_id)

    # ######################################################
    # ###                    pipelines                  ####
    # ######################################################

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.list_for_project' instead."
    )
    def get_project_pipelines(self, project_id, instances_limit=-1):
        return self.pipelines.list_for_project(project_id, instances_limit)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.get_info' instead."
    )
    def get_project_pipeline(self, pipeline_id):
        return self.pipelines.get_info(pipeline_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.stop' instead."
    )
    def stop_pipeline(self, pipeline_instance_id):
        return self.pipelines.stop(pipeline_instance_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.edit' instead."
    )
    def edit_pipeline(
        self,
        pipeline_id,
        name=None,
        description=None,
        emails=None,
        status_list=["FAILED"],
        is_scheduled=None,
        cron_scheduling=None,
        schedule_timezone="UTC",
    ):
        return self.pipelines.edit(
            pipeline_id, name, description, emails, status_list, is_scheduled, cron_scheduling, schedule_timezone
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.run' instead."
    )
    def run_pipeline(self, pipeline_id):
        return self.pipelines.run(pipeline_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.run_with_callback' instead."
    )
    def run_pipeline_callback(self, pipeline_id, freq=10, timeout=-1):
        return self.pipelines.run_with_callback(pipeline_id, freq, timeout)

    @deprecation.deprecated(
        deprecated_in="Saagie 2.2.1",
        details="This deprecated endpoint allows to create only linear pipeline. "
        "To create graph pipelines, use `saagieapi.pipelines.create_graph` instead.",
    )
    def create_pipeline(self, name, project_id, jobs_id, description=""):
        return self.pipelines.create(name, project_id, jobs_id, description)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.get_instance' instead."
    )
    def get_pipeline_instance(self, pipeline_instance_id):
        return self.pipelines.get_instance(pipeline_instance_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.create_graph' instead."
    )
    def create_graph_pipeline(
        self,
        name,
        project_id,
        graph_pipeline,
        description="",
        release_note="",
        cron_scheduling=None,
        schedule_timezone="UTC",
    ):
        return self.pipelines.create_graph(
            name, project_id, graph_pipeline, description, release_note, cron_scheduling, schedule_timezone
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.delete' instead."
    )
    def delete_pipeline(self, pipeline_id):
        return self.pipelines.delete(pipeline_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.upgrade' instead."
    )
    def upgrade_pipeline(self, pipeline_id, graph_pipeline, release_note=""):
        return self.pipelines.upgrade(pipeline_id, graph_pipeline, release_note)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.pipelines.get_id' instead."
    )
    def get_pipeline_id(self, pipeline_name, project_name):
        return self.pipelines.get_id(pipeline_name, project_name)

    # ######################################################
    # ###                    projects                   ####
    # ######################################################
    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.projects.get_id' instead."
    )
    def get_project_id(self, project_name):
        return self.projects.get_id(project_name)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.projects.list' instead."
    )
    def get_projects_info(self):
        return self.projects.list()

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.projects.get_info' instead."
    )
    def get_project_info(self, project_id):
        return self.projects.get_info(project_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.projects.get_jobs_technologies' instead."
    )
    def get_project_technologies(self, project_id):
        return self.projects.get_jobs_technologies(project_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.projects.create' instead."
    )
    def create_project(self, name, group=None, role="Manager", description=""):
        return self.projects.create(name, group, role, description)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.projects.delete' instead."
    )
    def delete_project(self, project_id):
        return self.projects.delete(project_id)

    # ######################################################
    # ###                    env vars                   ####
    # ######################################################

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.env_vars.list_globals' instead."
    )
    def get_global_env_vars(self):
        return self.env_vars.list_globals()

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.env_vars.create_global' instead."
    )
    def create_global_env_var(self, name, value, description="", is_password=False):
        return self.env_vars.create_global(name, value, description, is_password)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.env_vars.delete_global' instead."
    )
    def delete_global_env_var(self, name):
        return self.env_vars.delete_global(name)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.env_vars.list_for_project' instead."
    )
    def get_project_env_vars(self, project_id):
        return self.env_vars.list_for_project(project_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.env_vars.create_for_project' instead."
    )
    def create_project_env_var(self, project_id, name, value, description="", is_password=False):
        return self.env_vars.create_for_project(project_id, name, value, description, is_password)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.env_vars.delete_for_project' instead."
    )
    def delete_project_env_var(self, project_id, name):
        return self.env_vars.delete_for_project(project_id, name)

    # ######################################################
    # ###                      apps                     ####
    # ######################################################

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.apps.list_for_project' instead."
    )
    def get_project_web_apps(self, project_id, instances_limit=-1):
        logging.warning(
            f"parameter 'instances_limit' {instances_limit} is not used anymore, keeping it only to keep "
            f"the function signature unchanged"
        )
        return self.apps.list_for_project(project_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.apps.get_info' instead."
    )
    def get_project_web_app(self, web_app_id):
        return self.apps.get_info(web_app_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.apps.get_info' instead."
    )
    def get_project_app(self, app_id):
        return self.apps.get_info(app_id)

    # ######################################################
    # ###               Docker Credentials              ####
    # ######################################################

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.list_for_project' instead."
    )
    def get_all_docker_credentials(self, project_id):
        return self.docker_credentials.list_for_project(project_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.get_info' instead."
    )
    def get_docker_credentials(self, project_id, credential_id):
        return self.docker_credentials.get_info(project_id, credential_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.get_info_for_username' instead."
    )
    def get_docker_credentials_info_by_name(self, project_id, username, registry=None):
        return self.docker_credentials.get_info_for_username(project_id, username, registry)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.create' instead."
    )
    def create_docker_credentials(self, project_id, username, password, registry=None):
        return self.docker_credentials.create(project_id, username, password, registry)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.upgrade' instead."
    )
    def upgrade_docker_credentials_by_id(self, project_id, credential_id, password, registry=None, username=""):
        return self.docker_credentials.upgrade(project_id, credential_id, password, registry, username)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.upgrade_for_username' instead."
    )
    def upgrade_docker_credentials_by_name(self, project_id, username, password, registry=None):
        return self.docker_credentials.upgrade_for_username(project_id, username, password, registry)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.delete' instead."
    )
    def delete_docker_credentials_by_id(self, project_id, credential_id):
        return self.docker_credentials.delete(project_id, credential_id)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use 'saagieapi.docker_credentials.delete_for_username' instead."
    )
    def delete_docker_credentials_by_name(self, project_id, username, registry=None):
        return self.docker_credentials.delete_for_username(project_id, username, registry)
