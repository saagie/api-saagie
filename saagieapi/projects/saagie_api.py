"""
Saagie API object to interact with Saagie API in Python (API for
Projects & Jobs - to interact with the manager API, see the manager subpackage)

"""
import json
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


class SaagieApi:
    """Define several methods to interact with Saagie API in Python (API for
    Projects & Jobs - to interact with the manager API, see the manager
    subpackage)
    """

    def __init__(self, url_saagie, id_platform, user, password, realm):
        """
        Parameters
        ----------
        url_saagie : str
            platform base URL (eg: https://saagie-workspace.prod.saagie.io)
        id_platform : int or str
            Platform Id  (see README on how to find it)
        user : str
            username to login with
        password : str
            password to login with
        realm : str
            Saagie realm  (see README on how to find it)
        """
        if not url_saagie.endswith('/'):
            url_saagie += '/'
        self.url_saagie = url_saagie
        self.id_platform = id_platform
        self.suffix_api = 'projects/api/'
        self.realm = realm
        self.login = user
        self.password = password
        self.auth = BearerAuth(self.realm, self.url_saagie,
                               self.id_platform, self.login, self.password)
        url = self.url_saagie + self.suffix_api + 'platform/'
        url += str(self.id_platform) + '/graphql'
        self._transport = RequestsHTTPTransport(
            url=url,
            auth=self.auth,
            use_json=True,
            verify=False
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
            username to login with
        password : str
            password to login with
        """
        url_regex = re.compile(
            r"(https:\/\/(\w+)-(?:\w|\.)+)\/projects\/platform\/(\d+)")
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

    # ######################################################
    # ###                    projects                   ####
    # ######################################################

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
        return self.client.execute(query)

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

    def edit_job(self, job_id, job_name=None, description=None, is_scheduled=False,
                 cron_scheduling=None, schedule_timezone="UTC", resources=None):
        """Edit a job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        job_name : str, optional
            Seconds to wait between two state checks
        description : str, optional
            Description of job
        is_scheduled : bool, optional
            True if the job is scheduled, else False
        cron_scheduling : str, optional
            Scheduling cron format
        schedule_timezone : str, optional
            Timezone of the scheduling
        resources : dict, optional
            CPU, memory limit and requests
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}

        Returns
        -------
        dict
            Dict of job information
        """
        gql_payload = []
        if job_name:
            gql_payload.append(f'name: "{job_name}"')

        if description:
            gql_payload.append(f'description: "{description}"')

        if is_scheduled:
            gql_payload.append(f'isScheduled: true')

            if cron_scheduling and croniter.is_valid(cron_scheduling):
                gql_payload.append(f'cronScheduling: "{cron_scheduling}"')
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                gql_payload.append(f'scheduleTimezone: "{schedule_timezone}"')
            else:
                raise RuntimeError("Please specify a correct timezone")

        else:
            gql_payload.append(f'isScheduled: false')

        if resources:
            resources_str = json.dumps(resources).replace("\"", "")
            gql_payload.append(f'resources: {resources_str}')

        gql_payload_str = ", ".join(gql_payload)
        query = gql(gql_edit_job.format(job_id, gql_payload_str))
        return self.client.execute(query)

    def create_job(self, job_name, project_id, file=None, description='',
                   category='Processing', technology='python',
                   technology_catalog='Saagie',
                   runtime_version='3.6',
                   command_line='python {file} arg1 arg2', release_note='',
                   extra_technology='', extra_technology_version='',
                   cron_scheduling=None, schedule_timezone="UTC", resources=None):
        """Create job in given project

        NOTE
        ----
        - Since gql does not support multipart graphQL requests, requests
          package is used for now. The create job graphQL API takes a multipart
          graphQL request to upload a file.
          See https://github.com/jaydenseric/graphql-multipart-request-spec
          for more details
        - 2020-06-08 : multipart graphQL support will probably be implemented
          in gql in the near future.
          See https://github.com/graphql-python/gql/issues/68 to follow this
          work.
        - Tested with python and spark jobs

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
        schedule_timezone : str, optional
            Timezone of the scheduling
        resources : dict, optional
            CPU, memory limit and requests
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}

        Returns
        -------
        dict
            Dict of job information

        Raises
        ------
        requests.exceptions.RequestException
            When requests fails
        """

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

        if extra_technology != '':
            extra_tech = gql_extra_technology.format(extra_technology,
                                                     extra_technology_version)
        else:
            extra_tech = ''

        url = self.url_saagie + self.suffix_api + 'platform/'
        url += str(self.id_platform) + "/graphql"

        if resources is None:
            resources = {}
        gql_scheduling_payload = []

        if cron_scheduling:
            gql_scheduling_payload.append(f'"isScheduled": true')

            if croniter.is_valid(cron_scheduling):
                gql_scheduling_payload.append(f'"cronScheduling": "{cron_scheduling}"')
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                gql_scheduling_payload.append(f'"scheduleTimezone": "{schedule_timezone}"')
            else:
                raise RuntimeError("Please specify a correct timezone")

        else:
            gql_scheduling_payload.append(f'"isScheduled": false')

        gql_scheduling_payload_str = ", ".join(gql_scheduling_payload)
        resources_str = json.dumps(resources)
        payload_str = gql_create_job.format(job_name,
                                            project_id,
                                            description,
                                            category,
                                            technology_id,
                                            runtime_version,
                                            command_line,
                                            release_note,
                                            extra_tech,
                                            gql_scheduling_payload_str,
                                            resources_str)

        if file:
            file = Path(file)
            # logging.debug("Creating jobs with archive ...")
            with file.open(mode='rb') as f:
                files = {
                    '1': (file.name, f),
                    'operations': (None, payload_str),
                    'map': (None, '{ "1": ["variables.file"] }'),
                }
                response = requests.post(url,
                                         files=files,
                                         auth=self.auth,
                                         verify=False)
        else:

            payload = json.loads(payload_str)
            response = requests.post(url,
                                     json=payload,
                                     auth=self.auth,
                                     verify=False)

        if response:
            return json.loads(response.content)
        else:
            m = f"Requests failed with status_code :'{response.status_code}'"
            raise requests.exceptions.RequestException(m)

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
        regex_error_missing_technology = r"io\.saagie\.projectsandjobs\.domain\.exception\.NonExistingTechnologyException: Technology \S{8}-\S{4}-\S{4}-\S{4}-\S{12} does not exist"
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

    # TO DETAIL!
    # Detail pipeline dict parameters, or explode the number of parameters to
    # have a more comprehensible method
    def edit_pipeline(self, pipeline_id):
        """Edit a given pipeline
        NB : You can only edit pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline information
        """
        query = gql(gql_edit_pipeline.format(pipeline_id))
        return self.client.execute(query)

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
