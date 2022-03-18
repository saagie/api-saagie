"""
Saagie API object to interact with Saagie API in Python (API for
Projects & Jobs - to interact with the manager API, see the manager subpackage)

"""
import logging
import time
import re
import pytz
from pathlib import Path
from croniter import croniter

from gql import gql
from gql import Client
from gql.transport.requests import RequestsHTTPTransport

from .auth import *
from .gql_template import *
from .graph_pipeline import *
import deprecation


class SaagieApi:
    """Define several methods to interact with Saagie API in Python (API for
    Projects & Jobs - to interact with the manager API, see the manager
    subpackage)
    """

    def __init__(self, url_saagie, id_platform, user, password, realm, retries=0):
        """
        Parameters
        ----------
        url_saagie : str
            platform base URL (eg: https://saagie-workspace.prod.saagie.io)
        id_platform : int or str
            Platform Id  (see README on how to find it)
        user : str
            username to log in with
        password : str
            password to log in with
        realm : str
            Saagie realm  (see README on how to find it)
        retries : int
            Pre-setup of the requests’ Session for performing retries
        """
        if not url_saagie.endswith('/'):
            url_saagie += '/'
        self.url_saagie = url_saagie
        self.id_platform = id_platform
        self.suffix_api = 'projects/api/'
        self.realm = realm
        self.login = user
        self.password = password
        self.retries = retries
        self.auth = BearerAuth(self.realm, self.url_saagie,
                               self.id_platform, self.login, self.password)
        url = self.url_saagie + self.suffix_api + 'platform/'
        url += str(self.id_platform) + '/graphql'
        self._url = url
        self._transport = RequestsHTTPTransport(
            url=self._url,
            auth=self.auth,
            use_json=True,
            verify=False,
            retries=self.retries
        )
        self.client = Client(
            transport=self._transport,
            fetch_schema_from_transport=True
        )

        # URL Gateway
        self.url_gateway = self.url_saagie + 'gateway/api/graphql'
        self._transport_gateway = RequestsHTTPTransport(
            url=self.url_gateway,
            auth=self.auth,
            use_json=True,
            verify=False
        )
        self.client_gateway = Client(
            transport=self._transport_gateway,
            fetch_schema_from_transport=True
        )

        # Valid status list of alerting
        self.valid_status_list = ["REQUESTED", "QUEUED", "RUNNING", "FAILED", "KILLED",
                                  "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"]

    @classmethod
    def easy_connect(cls, url_saagie_platform, user, password):
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
        url_regex = re.compile(
            r"(https://(\w+)-(?:\w|\.)+)/projects/platform/(\d+)")
        m = url_regex.match(url_saagie_platform)
        if bool(m):
            url_saagie = m.group(1)
            realm = m.group(2)
            id_platform = m.group(3)
        else:
            raise ValueError(
                "Please use a correct URL (eg: https://saagie-workspace.prod.saagie.io/projects/platform/6/)")
        return cls(url_saagie, id_platform, user, password, realm)

    # ######################################################
    # ###                    env vars                   ####
    # ######################################################

    def get_global_env_vars(self):
        """Get global environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the platform

        Returns
        -------
        dict
            Dict of global environment variable on the platform
        """
        query = gql(gql_get_global_env_vars)
        return self.client.execute(query)

    def create_global_env_var(self, name, value,
                              description='',
                              is_password=False):
        """Create a global environment variable

        Parameters
        ----------
        name : str
            Name of the environment variable to create
        value : str
            Value of the environment variable to create
        description : str, optional
            Description of the environment variable to create
        is_password : bool, optional
            Weather the environment variable to create is a password or not

        Returns
        -------
        dict
            Dict of created environment variable
        """
        query = gql(gql_create_global_env_var.format(name,
                                                     value,
                                                     description,
                                                     str(is_password).lower()))
        return self.client.execute(query)

    def delete_global_env_var(self, name):
        """Delete the given global environment variable

        Parameters
        ----------
        name : str
            Name of the environment variable to delete

        Returns
        -------
        dict
            Dict of deleted environment variable

        Raises
        ------
        ValueError
            When the given name doesn't correspond to an existing environment
            variable
        """
        global_envs = self.get_global_env_vars()['globalEnvironmentVariables']
        global_env = [env for env in global_envs if env['name'] == name]

        if len(global_env) == 0:
            raise ValueError("'name' must be the name of an existing global "
                             "environment variable")

        global_env_id = global_env[0]['id']

        query = gql(gql_delete_env_var.format(global_env_id))
        return self.client.execute(query)

    def get_project_env_vars(self, project_id):
        """Get project environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of project environment variables
        """
        query = gql(gql_get_project_env_vars.format(project_id))
        return self.client.execute(query)

    def create_project_env_var(self, project_id, name, value,
                               description='', is_password=False):
        """Create an environment variable in a given project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        name : str
            Name of the environment variable to create
        value : str
            Value of the environment variable to create
        description : str, optional
            Description of the environment variable to create
        is_password : bool, optional
            Weather the environment variable to create is a password or not

        Returns
        -------
        dict
            Dict of created environment variable
        """
        query = gql(gql_create_project_env_var.format(
            project_id,
            name,
            value,
            description,
            str(is_password).lower()
        ))
        return self.client.execute(query)

    def delete_project_env_var(self, project_id, name):
        """Delete a given environment variable inside a given project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        name : str
            Name of the environment variable to delete inside the given project

        Returns
        -------
        dict
            Dict of deleted environment variable

        Raises
        ------
        ValueError
            When the given name doesn't correspond to an existing environment
            variable inside the given project
        """
        project_envs = self.get_project_env_vars(project_id)
        project_env = [env for env
                       in project_envs['projectEnvironmentVariables']
                       if env['name'] == name]

        if len(project_env) == 0:
            raise ValueError("'name' must be the name of an existing "
                             "environment variable in the given project")

        project_env_id = project_env[0]['id']

        query = gql(gql_delete_env_var.format(project_env_id))
        return self.client.execute(query)

    # ##########################################################
    # ###                    cluster                        ####
    # ##########################################################

    def get_cluster_capacity(self):
        """Get information for cluster (cpu, gpu, memory)
        """
        query = gql(gql_get_cluster_info)
        return self.client_gateway.execute(query)

    # ##########################################################
    # ###                    repositories                   ####
    # ##########################################################

    def get_repositories_info(self):
        """Get information for all repositories (id, name, technologies)
        NB: You can only get repositories information if you have the right to
        access the technology catalog
        """
        query = gql(gql_get_repositories_info)
        return self.client_gateway.execute(query)

    # ##########################################################
    # ###                    technologies                   ####
    # ##########################################################

    def get_runtimes(self, technology_id):
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
        query = gql_get_runtimes.format(technology_id)
        return self.client_gateway.execute(gql(query))

    # ######################################################
    # ###                    projects                   ####
    # ######################################################
    def get_project_id(self, project_name):
        """Get the project id with the project name
        Parameters
        ----------
        project_name : str
            Name of your project
        Returns
        -------
        str
            Project UUID
        """
        projects = self.get_projects_info()["projects"]
        project = list(filter(lambda p: p["name"] == project_name, projects))
        if project:
            project_id = project[0]["id"]
            return project_id

        else:
            raise NameError(f"Project {project_name} does not exist or you don't have permission to see it.")

    def get_projects_info(self):
        """Get information for all projects (id, name, creator, description,
        jobCount and status)
        NB: You can only list projects you have rights on.

        Returns
        -------
        dict
            Dict of projects information
        """
        query = gql(gql_get_projects_info)
        return self.client.execute(query)

    def get_project_info(self, project_id):
        """Get information for a given project (id, name, creator, description,
        jobCount and status)
        NB: You can only get project information if you have at least the
        viewer role on this project or on all projects.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of project information
        """
        query = gql(gql_get_project_info.format(project_id))
        return self.client.execute(query)

    def get_project_technologies(self, project_id):
        """List available technologies (Id and label) for the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of available technologies
        """
        query = gql(gql_get_project_technologies.format(project_id))
        return self.client.execute(query)['project']

    def create_project(self, name, group=None, role="Manager", description=""):
        """Create a new project on the platform

        NOTE
        ----
        - Currently add all JobTechnologies of the main technology repository
          (the 'Saagie' technology repository)
          Future improvement: pass a dict of technologies as a parameter
        - Currently only take on group and one associated role to add to the
          project
          Future improvement: possibility to pass in argument several group
          names with several roles to add to the project

        Parameters
        ----------
        name : str
            Name of the project (must not already exist)
        group : None or str, optional
            Authorization management: name of the group to add the given role
            to
        role : str, optional
            Authorization management: role to give to the given group on the
            project
        description : str, optional
            Description of the project

        Returns
        -------
        dict
            Dict of created project

        Raises
        ------
        ValueError
            If given unknown role value
        """
        if role == 'Manager':
            role = 'ROLE_PROJECT_MANAGER'
        elif role == 'Editor':
            role = 'ROLE_PROJECT_EDITOR'
        elif role == 'Viewer':
            role = 'ROLE_PROJECT_VIEWER'
        else:
            raise ValueError("'role' takes value in ('Manager', 'Editor',"
                             " 'Viewer')")

        # Keep only JobTechnologies (discarding AppTechnologies) of main
        # technology repository (Saagie repository)
        repositories = self.get_repositories_info()['repositories']
        technologies = []
        for repo in repositories:
            if repo['name'] == 'Saagie':
                technologies = [techno for techno in repo['technologies']
                                if
                                techno['__typename'] == 'JobTechnology' or (techno['__typename'] == 'SparkTechnology')]

        # Generate the technology graphQL string only with technologies id
        technologies = [f'{{id: "{tech["id"]}"}}' for tech in technologies]

        group_block = ""
        if group is not None:
            group_block = group_block_template.format(group, role)

        query = gql(gql_create_project.format(name,
                                              description,
                                              group_block,
                                              ', '.join(technologies)))
        return self.client.execute(query)

    def delete_project(self, project_id):
        """Delete a given project
        NB: You can only delete projects where you have the manager role

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            dict of archived project
        """
        query = gql(gql_delete_project.format(project_id))
        return self.client.execute(query)

    # ######################################################
    # ###                      jobs                     ####
    # ######################################################

    def get_project_jobs(self, project_id, instances_limit=-1):
        """List jobs in the given project with their instances.
        NB: You can only list jobs if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest

        Returns
        -------
        dict
            Dict of jobs information
        """
        instances_limit_request = f" (limit: {str(instances_limit)})" if instances_limit != -1 else ""
        query = gql(gql_get_project_jobs.format(project_id, instances_limit_request))
        return self.client.execute(query)

    def get_project_job(self, job_id):
        """Get the given job information (return null if it doesn't exist).

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of job information
        """
        query = gql(gql_get_project_job.format(job_id))
        return self.client.execute(query)

    def get_job_instance(self, job_instance_id):
        """Get the given job instance

        Parameters
        ----------
        job_instance_id : str
            UUID of your job instance (see README on how to find it)

        Returns
        -------
        dict
            Dict of instance information
        """
        query = gql(gql_get_job_instance.format(job_instance_id))
        return self.client.execute(query)

    def run_job(self, job_id):
        """Run a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of the given job information
        """
        query = gql(gql_run_job.format(job_id))
        return self.client.execute(query)

    def run_job_callback(self, job_id, freq=10, timeout=-1):
        """Run a job and wait for the final status (KILLED, FAILED or SUCCESS).
        Regularly check (default to 10s) the job's status.

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        freq : int, optional
            Seconds to wait between two state checks
        timeout : int, optional
            Seconds before timeout for a status check call

        Returns
        -------
        str
            Final state of the job

        Raises
        ------
        TimeoutError
            When the status check is not responding
        """
        res = self.run_job(job_id)
        job_instance_id = res.get("runJob").get("id")
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED"]
        query = gql(gql_get_job_instance.format(job_instance_id))
        job_instance_info = self.client.execute(query)
        state = job_instance_info.get("jobInstance").get("status")
        sec = 0
        while state not in final_status_list:
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            job_instance_info = self.client.execute(query)
            state = job_instance_info.get("jobInstance").get("status")
            print('Current state : ' + state)
        return state

    def stop_job(self, job_instance_id):
        """Stop a given job instance

        Parameters
        ----------
        job_instance_id : str
            UUID of your job instance (see README on how to find it)

        Returns
        -------
        dict
            Job instance information
        """
        query = gql(gql_stop_job_instance.format(job_instance_id))
        return self.client.execute(query)

    def edit_job(self, job_id, job_name=None, description=None, is_scheduled=None,
                 cron_scheduling=None, schedule_timezone="UTC", resources=None,
                 emails=None, status_list=["FAILED"]):
        """Edit a job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        job_name : str, optional
            Job name
            If not filled, defaults to current value, else it will change the job's name
        description : str, optional
            Description of job
            if not filled, defaults to current value, else it will change the description of the pipeline
        is_scheduled : bool, optional
            True if the job is scheduled, else False
            if not filled, defaults to current value
        cron_scheduling : str, optional
            Scheduling CRON format
            When is_scheduled is set to True, it will be mandatory to fill this value
            if not filled, defaults to current value
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        resources : dict, optional
            CPU, memory limit and requests
            if not filled, defaults to current value
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"

        Returns
        -------
        dict
            Dict of job information
        """
        params = {"id": job_id}
        previous_job_version = self.get_job_info(job_id)["job"]

        if job_name:
            params["name"] = job_name
        else:
            params["name"] = previous_job_version["name"]

        if description:
            params["description"] = description
        else:
            params["description"] = previous_job_version["description"]

        if resources:
            params["resources"] = resources
        else:
            params["resources"] = previous_job_version["resources"]

        if is_scheduled:
            params["isScheduled"] = True

            if cron_scheduling and croniter.is_valid(cron_scheduling):
                params["cronScheduling"] = cron_scheduling
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                params["scheduleTimezone"] = schedule_timezone
            else:
                raise RuntimeError("Please specify a correct timezone")

        elif is_scheduled == False:
            params["isScheduled"] = False

        else:
            params["isScheduled"] = previous_job_version["isScheduled"]
            params["cronScheduling"] = previous_job_version["cronScheduling"]
            params["scheduleTimezone"] = previous_job_version["scheduleTimezone"]

        if emails:
            wrong_status_list = []

            for item in status_list:
                if item not in self.valid_status_list:
                    wrong_status_list.append(item)
            if wrong_status_list:
                raise RuntimeError(f"The following status are not valid: {wrong_status_list}. "
                                   f"Please make sure that each item of the parameter status_list should be "
                                   f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                                   f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'")

            else:
                params["alerting"] = {
                    "emails": emails,
                    "statusList": status_list
                }
        elif type(emails) == list:
            params["alerting"] = None
        else:
            previous_alerting = previous_job_version["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_alerting["emails"],
                    "statusList": previous_alerting["statusList"]
                }

        query = gql(gql_edit_job)
        return self.client.execute(query, variable_values=params)

    def create_job(self, job_name, project_id, file=None, description='',
                   category='Processing', technology='python',
                   technology_catalog='Saagie',
                   runtime_version='3.6',
                   command_line='python {file} arg1 arg2', release_note='',
                   extra_technology='', extra_technology_version='',
                   cron_scheduling=None, schedule_timezone="UTC", resources=None,
                   emails=None, status_list=["FAILED"]):
        """Create job in given project

        NOTE
        ----
        - Only work for gql>=3.0.0

        Parameters
        ----------
        job_name : str
            Name of the job. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        file : str, optional
            Local path of the file to upload
        description : str, optional
            Description of the job
        category : str, optional
            Category to create the job into. Must be 'Extraction', 'Processing'
            or 'Smart App'
        technology : str, optional
            Technology label of the job to create.
        technology_catalog : str, optional
            Technology catalog containing the technology to use for this job
        runtime_version : str, optional
            Technology version of the job
        command_line : str, optional
            Command line of the job
        release_note : str, optional
            Release note of the job
        extra_technology : str, optional
            Extra technology when needed (spark jobs). If not needed, leave to
            empty string or the request will not work
        extra_technology_version : str, optional
            Version of the extra technology. Leave to empty string when not
            needed
        cron_scheduling : str, optional
            Scheduling CRON format
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        resources : dict, optional
            CPU, memory limit and requests
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"

        Returns
        -------
        dict
            Dict of job information

        """
        params = {
            "projectId": project_id, "name": job_name, "description": description, "category": category,
            "releaseNote": release_note, "runtimeVersion": runtime_version, "commandLine": command_line}

        technologies_for_project = self.get_project_technologies(project_id)['technologiesByCategory']
        technologies_for_project_and_category = [
            tech['id'] for tech in
            [
                tech['technologies'] for tech in technologies_for_project
                if tech['jobCategory'] == category
            ][0]
        ]
        all_technologies_in_catalog = [
            catalog['technologies'] for catalog in self.get_repositories_info()['repositories']
            if catalog['name'] == technology_catalog
        ]
        if not all_technologies_in_catalog:
            raise RuntimeError(
                f"Catalog {technology_catalog} does not exist or does not contain technologies")

        technology_in_catalog = [tech['id'] for tech in
                                 all_technologies_in_catalog[0]
                                 if tech["label"].lower() == technology.lower()]

        if not technology_in_catalog:
            raise RuntimeError(
                f"Technology {technology} does not exist in the catalog {technology_catalog}")

        if technology_in_catalog[0] not in technologies_for_project_and_category:
            raise RuntimeError(
                f"Technology {technology} does not exist in the target project {project_id} "
                f"for the {category} category "
                f"and for the {technology_catalog} catalog")
        else:
            technology_id = technology_in_catalog[0]
            params["technologyId"] = technology_id

        if extra_technology != '':
            extra_tech = gql_extra_technology.format(extra_technology,
                                                     extra_technology_version)
        else:
            extra_tech = ''

        if emails:
            wrong_status_list = []

            for item in status_list:
                if item not in self.valid_status_list:
                    wrong_status_list.append(item)
            if wrong_status_list:
                raise RuntimeError(f"The following status are not valid: {wrong_status_list}. "
                                   f"Please make sure that each item of the parameter status_list should be "
                                   f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                                   f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'")

            else:
                params["alerting"] = {
                    "emails": emails,
                    "statusList": status_list
                }

        if cron_scheduling:
            params["isScheduled"] = True

            if croniter.is_valid(cron_scheduling):
                params["cronScheduling"] = cron_scheduling
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                params["scheduleTimezone"] = schedule_timezone
            else:
                raise RuntimeError("Please specify a correct timezone")

        else:
            params["isScheduled"] = False

        if resources:
            params["resources"] = resources

        payload_str = gql_create_job.format(extra_technology=extra_tech)
        return self.__launch_request(file, payload_str, params)

    def get_job_info(self, job_id):
        """Get job's info

        Parameters
        ----------
        job_id : str
            UUID of your job

        Returns
        -------
        dict
            Dict of job's info

        """
        query = gql_get_info_job.format(job_id)
        return self.client.execute(gql(query))

    def upgrade_job(self, job_id, file=None, use_previous_artifact=False, runtime_version='3.6',
                    command_line='python {file} arg1 arg2', release_note=None,
                    extra_technology='', extra_technology_version=''):
        """Upgrade a job

        Parameters
        ----------
        job_id : str
            UUID of your job
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        runtime_version: str (optional)
            Runtime version
        command_line: str (optional)
            Command line
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            empty string or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to empty string when not
            needed

        Returns
        -------
        dict
            Dict with version number
            Example: {'addJobVersion': {'number': 5, '__typename': 'JobVersion'}}

        """

        # Verify if specified runtime exists
        technology_id = self.get_job_info(job_id)["job"]["technology"]["id"]
        available_runtimes = [c["label"] for c in self.get_runtimes(technology_id)["technology"]["contexts"]]
        if runtime_version not in available_runtimes:
            raise RuntimeError(
                f"Specified runtime does not exist ({runtime_version}). "
                f"Available runtimes : {','.join(available_runtimes)}.")

        if file and use_previous_artifact:
            logging.warning(
                "You can not specify a file and use the previous artifact. "
                "By default, the specified file will be used.")

        if extra_technology != '':
            extra_tech = gql_extra_technology.format(extra_technology,
                                                     extra_technology_version)
        else:
            extra_tech = ''
        payload_str = gql_upgrade_job.format(extra_technology=extra_tech)
        params = {"jobId": job_id, "releaseNote": release_note, "runtimeVersion": runtime_version,
                  "commandLine": command_line, "usePreviousArtifact": use_previous_artifact}

        return self.__launch_request(file, payload_str, params)

    def __launch_request(self, file, payload_str, params):
        """Launch a GQL request with specified file, payload and params
        GQL3 needed to use this function
        Parameters
        ----------
        file : str
            Path to your file
        payload_str : str
            Payload to send
        params: dict
            variable values to pass to the GQL request
        Returns
        -------
        dict
            Dict of the request response
        """
        if file:
            file = Path(file)
            with file.open(mode='rb') as f:
                params["file"] = f
                try:
                    req = self.client.execute(gql(payload_str), variable_values=params, upload_files=True)
                    res = {"data": req}
                except Exception as e:
                    logging.error(f"Something went wrong: {e}")
                    raise e
                return res

        else:
            try:
                req = self.client.execute(gql(payload_str), variable_values=params)
                res = {"data": req}
            except Exception as e:
                logging.error(f"Something went wrong: {e}")
                raise e
            return res

    def get_job_id(self, job_name, project_name):
        """Get the job id with the job name and project name

        Parameters
        ----------
        job_name : str
            Name of your job
        project_name : str
            Name of your project

        Returns
        -------
        str
            Job UUID

        """
        project_id = self.get_project_id(project_name)
        jobs = self.get_project_jobs(project_id, instances_limit=1)["jobs"]
        job = list(filter(lambda j: j["name"] == job_name, jobs))
        if job:
            return job[0]["id"]
        else:
            raise NameError(f"Job {job_name} does not exist.")

    def upgrade_job_by_name(self, job_name, project_name, file=None, use_previous_artifact=False, runtime_version='3.6',
                            command_line='python {file} arg1 arg2', release_note=None,
                            extra_technology='', extra_technology_version=''
                            ):
        """Upgrade a job

        Parameters
        ----------
        job_name : str
            Name of your job
        project_name : str
            Name of your project
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        runtime_version: str (optional)
            Runtime version
        command_line: str (optional)
            Command line
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            empty string or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to empty string when not
            needed

        Returns
        -------
        dict
            Dict with version number
            Example: {'addJobVersion': {'number': 5, '__typename': 'JobVersion'}}

        """
        job_id = self.get_job_id(job_name, project_name)
        return self.upgrade_job(job_id, file, use_previous_artifact, runtime_version, command_line, release_note,
                                extra_technology, extra_technology_version)

    def delete_job(self, job_id):
        """Delete a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted job

        """
        query = gql(gql_delete_job.format(job_id))
        return self.client.execute(query)

    # ######################################################
    # ###                      apps                     ####
    # ######################################################

    # Difference between app and webapp in current graphQL API ?
    # Web App = Docker jobs ?
    def get_project_web_apps(self, project_id, instances_limit=-1):
        """List webApps of project with their instances.
        NB: You can only list webApps if you have at least the viewer role on
        the project.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per webapp. Fetch from most
            recent to oldest

        Returns
        -------
        dict
            Dict of webApp information
        """
        regex_error_missing_technology = r"io\.saagie\.projectsandjobs\.domain\.exception" \
                                         r"\.NonExistingTechnologyException: Technology \S{8}-\S{4}-\S{4}-\S{4}-\S{" \
                                         r"12} does not exist "
        instances_limit_request = f" (limit: {str(instances_limit)})" if instances_limit != -1 else ""

        query = gql(gql_get_project_web_apps.format(project_id,
                                                    instances_limit_request))
        result = self.client.execute(query)

        if result.errors:
            # Matching errors with error missing technology message
            errors_matching = [re.fullmatch(regex_error_missing_technology, e['message']) for e in result.errors]
            if None in errors_matching:
                raise Exception(str(result.errors[errors_matching.index(None)]))
            else:
                return result.data
        else:
            return result.data

    def get_project_web_app(self, web_app_id):
        """Get webApp with given UUID or null if it doesn't exist.

        Parameters
        ----------
        web_app_id : str
            Description

        Returns
        -------
        dict
            Dict of webApp information
        """
        query = gql(get_project_web_app.format(web_app_id))
        return self.client.execute(query)

    def get_project_app(self, app_id):
        """Get app with given UUID or null if it doesn't exist.

        Parameters
        ----------
        app_id : str
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of app information
        """
        query = gql(gql_get_project_app.format(app_id))
        return self.client.execute(query)

    # ######################################################
    # ###                   pipelines                   ####
    # ######################################################
    def get_project_pipelines(self, project_id, instances_limit=-1):
        """List pipelines of project with their instances.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per pipelines. Fetch from most
            recent to oldest

        Returns
        -------
        Dict
            Dict of pipelines information
        """
        instances_limit_request = f" (limit: {str(instances_limit)})" if instances_limit != -1 else ""
        query = gql(gql_get_pipelines.format(project_id, instances_limit_request))
        return self.client.execute(query)

    def get_project_pipeline(self, pipeline_id):
        """Get a given pipeline information

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline's information
        """
        query = gql(gql_get_pipeline.format(pipeline_id))
        return self.client.execute(query)

    def stop_pipeline(self, pipeline_instance_id):
        """Stop a given pipeline instance
        NB : You can only stop pipeline instance if you have at least the
        editor role on the project.

        Parameters
        ----------
        pipeline_instance_id : str
            UUID of your pipeline instance  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline's instance information
        """
        query = gql(gql_stop_pipeline_instance.format(pipeline_instance_id))
        return self.client.execute(query)

    def edit_pipeline(self, pipeline_id, name=None, description=None, emails=None,
                      status_list=["FAILED"], is_scheduled=None,
                      cron_scheduling=None, schedule_timezone="UTC"):
        """Edit a pipeline
        NB : You can only edit pipeline if you have at least the editor role on
        the project
        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        name : str, optional
            Pipeline name,
            if not filled, defaults to current value, else it will change the pipeline name
        description : str, optional
            Description of the pipeline
            if not filled, defaults to current value, else it will change the description of the pipeline
        is_scheduled : bool, optional
            True if the job is scheduled, else False
            if not filled, defaults to current value
        cron_scheduling : str, optional
            Scheduling CRON format
            When is_scheduled is set to True, it will be mandatory to fill this value
            if not filled, defaults to current value
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"

        Returns
        -------
        dict
            Dict of pipeline information
        """
        params = {"id": pipeline_id}
        previous_pipeline_info = self.get_project_pipeline(pipeline_id)["graphPipeline"]

        if name:
            params["name"] = name
        else:
            params["name"] = previous_pipeline_info["name"]

        if description:
            params["description"] = description
        else:
            params["description"] = previous_pipeline_info["description"]

        if is_scheduled:
            params["isScheduled"] = True

            if cron_scheduling and croniter.is_valid(cron_scheduling):
                params["cronScheduling"] = cron_scheduling
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                params["scheduleTimezone"] = schedule_timezone
            else:
                raise RuntimeError("Please specify a correct timezone")

        elif is_scheduled == False:
            params["isScheduled"] = False

        else:
            params["isScheduled"] = previous_pipeline_info["isScheduled"]
            params["cronScheduling"] = previous_pipeline_info["cronScheduling"]
            params["scheduleTimezone"] = previous_pipeline_info["scheduleTimezone"]

        if emails:
            wrong_status_list = []

            for item in status_list:
                if item not in self.valid_status_list:
                    wrong_status_list.append(item)
            if wrong_status_list:
                raise RuntimeError(f"The following status are not valid: {wrong_status_list}. "
                                   f"Please make sure that each item of the parameter status_list should be "
                                   f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                                   f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'")

            else:
                params["alerting"] = {
                    "emails": emails,
                    "statusList": status_list
                }
        elif type(emails) == list:
            params["alerting"] = None
        else:
            previous_alerting = previous_pipeline_info["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_pipeline_info["emails"],
                    "statusList": previous_pipeline_info["statusList"]
                }

        query = gql(gql_edit_pipeline)
        return self.client.execute(query, variable_values=params)

    def run_pipeline(self, pipeline_id):
        """Run a given pipeline
        NB : You can only run pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline instance's information
        """
        query = gql(gql_run_pipeline.format(pipeline_id))
        return self.client.execute(query)

    def run_pipeline_callback(self, pipeline_id, freq=10, timeout=-1):
        """Run a given pipeline and wait for its final status (KILLED, FAILED
        or SUCCESS).
        NB : You can only run pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)
        freq : int, optional
            Number of seconds between 2 state checks
        timeout : int, optional
            Number of seconds before timeout

        Returns
        -------
        str
            the final state of the pipeline
        Raises
        ------
        TimeoutError
            the last state known of the pipeline before timeout
        """
        res = self.run_pipeline(pipeline_id)
        pipeline_instance_id = res.get("runPipeline").get("id")
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED"]
        query = gql(gql_get_pipeline_instance.format(pipeline_instance_id))
        pipeline_instance_info = self.client.execute(query)
        state = pipeline_instance_info.get("pipelineInstance").get("status")
        sec = 0

        while state not in final_status_list:
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            pipeline_instance_info = self.client.execute(query)
            state = pipeline_instance_info.get("pipelineInstance") \
                .get("status")
            print('Current state : ' + state)
        return state

    @deprecation.deprecated(deprecated_in="Saagie 2.2.1",
                            details="This deprecated endpoint allows to create only linear pipeline. "
                                    "To create graph pipelines, use the endpoint `createGraphPipeline` instead.")
    def create_pipeline(self, name, project_id, jobs_id, description=""):
        """
        Create a pipeline in a given project

        Parameters
        ----------
        name : str
            Name of the pipeline. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        jobs_id : List
            Ordered list of job's id (example : ["id1", "id2", "id3"]
            will result in the following pipeline id1 -> id2 -> id3)
        description : str, optional
            Description of the pipeline

        Returns
        -------
        dict
            Dict of job information
        """
        query = gql(gql_create_pipeline.format(
            name,
            description,
            project_id,
            f"""["{'", "'.join(jobs_id)}"]"""
        ))
        return self.client.execute(query)

    def get_pipeline_instance(self, pipeline_instance_id):
        """
        Get the information of a given pipeline instance id

        Parameters
        ----------
        pipeline_instance_id : str
            Pipeline instance id

        Returns
        -------
        dict
            Dict of job information
        """
        query = gql(gql_get_pipeline_instance.format(pipeline_instance_id))
        return self.client.execute(query)

    def create_graph_pipeline(self, name, project_id, graph_pipeline, description="", release_note="",
                              cron_scheduling=None, schedule_timezone="UTC"):
        """
        Create a pipeline in a given project

        Parameters
        ----------
        name : str
            Name of the pipeline. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        graph_pipeline : GraphPipeline
            Example: If you want to create a simple pipeline with 2 jobs that started by job_node_1,
            you can use the following example
                job_node1 = JobNode(job_id_1)
                job_node2 = JobNode(job_id_2)
                job_node1.add_next_node(job_node2) # Indicates that the job_node_1 is followed by job_node_2
                graph_pipeline = GraphPipeline()
                graph_pipeline.add_root_node(job_node1) # Indicates the pipeline will started with job_node1
        description : str, optional
            Description of the pipeline
        release_note: str, optional
            Release note of the pipeline
        cron_scheduling : str, optional
            Scheduling CRON format
        schedule_timezone : str, optional
            Timezone of the scheduling

        Returns
        -------
        dict
            Dict of pipeline information
        """
        gql_scheduling_payload = []
        if not graph_pipeline.list_job_nodes:
            graph_pipeline.to_pipeline_graph_input()
        if cron_scheduling:
            gql_scheduling_payload.append('isScheduled: true')

            if croniter.is_valid(cron_scheduling):
                gql_scheduling_payload.append(f'cronScheduling: "{cron_scheduling}"')
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                gql_scheduling_payload.append(f'scheduleTimezone: "{schedule_timezone}"')
            else:
                raise RuntimeError("Please specify a correct timezone")

        else:
            gql_scheduling_payload.append('isScheduled: false')

        gql_scheduling_payload_str = ", ".join(gql_scheduling_payload)

        query_str = gql_create_graph_pipeline.format(
            name,
            description,
            project_id,
            release_note,
            gql_scheduling_payload_str
        )
        params = {'jobNodes': graph_pipeline.list_job_nodes, 'conditionNodes': graph_pipeline.list_conditions_nodes}

        query = gql(query_str)
        return self.client.execute(query, variable_values=params)

    def delete_pipeline(self, pipeline_id):
        """Delete a pipeline given pipeline id

        Parameters
        ----------
        pipeline_id : str
            Pipeline id

        Returns
        -------
        dict
            Dict containing status of deletion
        """
        query = gql(gql_delete_pipeline.format(pipeline_id))

        return self.client.execute(query)

    def upgrade_pipeline(self, pipeline_id, graph_pipeline, release_note=""):
        """
        Create a pipeline in a given project

        Parameters
        ----------
        pipeline_id: str, ID of pipeline
        graph_pipeline : GraphPipeline
        release_note: str, optional
            Release note of the pipeline

        Returns
        -------
        dict
            Dict of pipeline information
        """
        if not graph_pipeline.list_job_nodes:
            graph_pipeline.to_pipeline_graph_input()

        params = {'id': pipeline_id, 'jobNodes': graph_pipeline.list_job_nodes,
                  'conditionNodes': graph_pipeline.list_conditions_nodes, 'releaseNote': release_note}

        return self.client.execute(gql(gql_upgrade_pipeline), variable_values=params)

    def get_pipeline_id(self, pipeline_name, project_name):
        """Get the pipeline id with the pipeline name and project name
        Parameters
        ----------
        pipeline_name : str
            Name of your pipeline
        project_name : str
            Name of your project
        Returns
        -------
        str
            Pipeline UUID
        """
        project_id = self.get_project_id(project_name)
        pipelines = self.get_project_pipelines(project_id, instances_limit=1)["project"]["pipelines"]
        pipeline = list(filter(lambda j: j["name"] == pipeline_name, pipelines))
        if pipeline:
            return pipeline[0]["id"]
        else:
            raise NameError(f"pipeline {pipeline_name} does not exist.")

    # ######################################################
    # ###               Docker Credentials              ####
    # ######################################################

    def get_all_docker_credentials(self, project_id):
        """
        Get all saved docker credentials for a specific project
        Parameters
        ----------
        project_id : str
            ID of the project
        Returns
        -------
        dict

        """
        params = {"projectId": project_id}
        return self.client.execute(gql(gql_get_all_docker_credentials), variable_values=params)

    def get_docker_credentials(self, project_id, credential_id):
        """
        Get the info of a specific docker credentials in a specific project
        Parameters
        ----------
        project_id :
            ID of the project
        credential_id : str
            ID of the credentials of the container registry
        Returns
        -------
        dict

        """
        params = {"projectId": project_id, "id": credential_id}
        return self.client.execute(gql(gql_get_docker_credentials), variable_values=params)

    def get_docker_credentials_info_by_name(self, project_id, username, registry=None):
        """
        Get the info of a specific docker credentials in a specific project using the username
        and the registry
        Parameters
        ----------
        project_id :
            ID of the project
        username : str
            Login of the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
        Returns
        -------
        dict

        """
        all_docker_credentials = self.get_all_docker_credentials(project_id)["allDockerCredentials"]
        if len(all_docker_credentials):
            res = [credentials for credentials in all_docker_credentials if
                   credentials["username"] == username and credentials["registry"] == registry]
            if len(res):
                return res[0]
            else:
                raise RuntimeError(
                    f"There are no docker credentials in the project: '{project_id}' with the username: '{username}' "
                    f"and registry '{registry}'")
        else:
            raise RuntimeError(f"There are no docker credentials in the project: '{project_id}'")

    def create_docker_credentials(self, project_id, username, password, registry=None):
        """
        Create docker credentials for a specific project
        Parameters
        ----------
        project_id : str
            ID of the project
        username : str
            Login to the container registry
        password: str
            Password to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Else, you have to put the url of the container registry
        Returns
        -------
        dict

        """
        params = {"username": username, "password": password, "projectId": project_id}
        if registry:
            params["registry"] = registry
        return self.client.execute(gql(gql_create_docker_credentials), variable_values=params)

    def upgrade_docker_credentials_by_id(self, project_id, credential_id, password, registry=None,
                                         username=""):
        """
        Update docker credentials for a specific project
        Parameters
        ----------
        project_id : str
            ID of the project
        credential_id: str
            ID of the created docker credentials
        password: str
            Password to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Otherwise, you have to put the url of the container registry
        username : str, optional
            If you want to change the login of the container registry, you have to set it.
            Otherwise, you can let it to default value
        Returns
        -------
        dict

        """
        params = {"id": credential_id, "password": password, "projectId": project_id}
        if registry:
            params["registry"] = registry
        if username:
            params["username"] = username
        return self.client.execute(gql(gql_upgrade_docker_credentials), variable_values=params)

    def upgrade_docker_credentials_by_name(self, project_id, username, password, registry=None):
        """
        Update docker credentials for a specific project
        Parameters
        ----------
        project_id : str
            ID of the project
        username : str
            Login of the container registry
        password: str
            Password to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Otherwise, you have to put the url of the container registry
        Returns
        -------
        dict
        """
        credential_id = self.get_docker_credentials_info_by_name(project_id, username, registry)["id"]
        params = {"id": credential_id, "password": password, "projectId": project_id}

        if registry:
            params["registry"] = registry

        return self.client.execute(gql(gql_upgrade_docker_credentials), variable_values=params)

    def delete_docker_credentials_by_id(self, project_id, credential_id):
        """
        Delete a specific container registry credentials in a specific project
        Parameters
        ----------
        project_id :
            ID of the project
        credential_id : str
            ID of the credential
        Returns
        -------
        dict
        """
        params = {"id": credential_id, "projectId": project_id}
        return self.client.execute(gql(gql_delete_docker_credentials), variable_values=params)

    def delete_docker_credentials_by_name(self, project_id, username, registry=None):
        """
        Delete a specific container registry credentials in a specific project
        Parameters
        ----------
        project_id :
            ID of the project
        username : str
            Login to the container registry
        registry : str, optional
            If you do not set a registry, the registry will be Docker Hub.
            Otherwise, you have to put the url of the container registry
        Returns
        -------
        dict
        """
        credential_id = self.get_docker_credentials_info_by_name(project_id, username, registry)["id"]
        params = {"id": credential_id, "projectId": project_id}
        return self.client.execute(gql(gql_delete_docker_credentials), variable_values=params)
