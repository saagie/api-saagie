"""
Saagie API object to interact with Saagie API in Python (API for
Projects & Jobs - to interact with the manager API, see the manager subpackage)

"""
import time
import requests
from pathlib import Path
import json

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from .gql_template import *
from .auth import *


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
            Platform Id (you can find it in the URL after the '/platform/' when
            you are on your own platform (eg, the platform'id is 6 in
            https://saagie-workspace.prod.saagie.io/manager/platform/6/#/manager/6))
        user : str
            username to login with
        password : str
            password to login with
        realm : str
            Saagie realm, which is the prefix that was determined during Saagie
            installation. One can find it in the base url before the first '-'
            (eg, the platform's realm is 'saagie' in
            https://saagie-workspace.prod.saagie.io)
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

    # ######################################################
    # ###                    env vars                   ####
    # ######################################################

    def get_global_env_vars(self):
        """Get global environmnet variables
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
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)

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
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)
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
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)
        name : str
            Name of the environment variable to delete inside the given project

        Returns
        -------
        dict
            Dict of deleted environment variable

        Raises
        ------
        ValueError
            When the given name doesn't correspond to an existing environmnent
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
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)

        Returns
        -------
        dict
            Dict of project information
        """
        query = gql(gql_get_project_info.format(project_id))
        return self.client.execute(query)

    def get_technologies(self):
        """List available technologies in the platform (Id and label)

        Returns
        -------
        dict
            Dict of available technologies
        """
        query = gql(gql_get_technologies)
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

        # technologies = [f'{{id: "{tech["id"]}"}}'
        #                 for tech in self.get_technologies()["technologies"]]

        # Keep only JobTechnologies (discarding AppTechnologies) of main
        # technology repository (Saagie repository)
        repositories = self.get_repositories_info()['repositories']
        for repo in repositories:
            if repo['name'] == 'Saagie':
                technologies = [techno for techno in repo['technologies']
                                if techno['__typename'] == 'JobTechnology']

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
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)

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

    def get_project_jobs(self, project_id, instances_limit):
        """List jobs in the given project with their instances.
        NB: You can only list jobs if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project. Can be found in the project URL after the
            '/project/' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)
        instances_limit : int
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest

        Returns
        -------
        dict
            Dict of jobs information
        """
        instances_limit = str(instances_limit)
        query = gql(gql_get_project_jobs.format(project_id, instances_limit))
        return self.client.execute(query)

    def get_project_job(self, job_id):
        """Get the given job information (return null if it doesn't exist).

        Parameters
        ----------
        job_id : str
            UUID of your job. Can be found in the project URL after the '/job/'
            (eg: the job UUID is 'a85ac3db-bca1-4f15-b8f7-44731fba874b' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b)

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
            UUID of your job instance. Can be found in the job instance URL
            after the '/instances/' (eg: the job instance UUID is
            '6ff448ae-3770-4639-b0f8-079e5c614ab6' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b/instances/6ff448ae-3770-4639-b0f8-079e5c614ab6)

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
            UUID of your job. Can be found in the project URL after the '/job/'
            (eg: the job UUID is 'a85ac3db-bca1-4f15-b8f7-44731fba874b' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b)

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
            UUID of your job. Can be found in the project URL after the '/job/'
            (eg: the job UUID is 'a85ac3db-bca1-4f15-b8f7-44731fba874b' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b)
        freq : int, optional
            Seconds to wait between two state checks
        timeout : int, optional
            Seconds before timeout for a status'check call

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
        to = False
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
            UUID of your job instance. Can be found in the job instance URL
            after the '/instances/' (eg: the job instance UUID is
            '6ff448ae-3770-4639-b0f8-079e5c614ab6' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b/instances/6ff448ae-3770-4639-b0f8-079e5c614ab6)

        Returns
        -------
        dict
            Job instance information
        """
        query = gql(gql_stop_job_instance.format(job_instance_id))
        return self.client.execute(query)

    # TO DETAIL!
    # Detail job dict parameter, or explode the number of parameters to have
    # a more comprehensible method
    def edit_job(self, job):
        """Edit a job

        Parameters
        ----------
        job : TYPE
            Job

        Returns
        -------
        dict
            Dict of job information
        """
        query = gql(gql_edit_job.format(job))
        return self.client.execute(query)

    def create_job(self, job_name, project_id, file, description='',
                   category='Processing', technology='python',
                   runtime_version='3.6',
                   command_line='python {file} arg1 arg2', release_note='',
                   extra_technology='', extra_technology_version=''):
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
        - The technology parameter must have issues now that the SDK is out and
          that a platform can have multiple technology repositories (there
          might be some overlap between the labels)

        Parameters
        ----------
        job_name : str
            Name of the job. Must not already exist in the project
        project_id : str
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)
        file : str
            Local path of the file to upload
        description : str, optional
            Description of the job
        category : str, optional
            Category to create the job into. Must be 'Extraction', 'Processing'
            or 'Smart App'
        technology : str, optional
            Technology label of the job to create. See self.get_technologies()
            for a list of available technologies
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

        Returns
        -------
        dict
            Dict of job information

        Raises
        ------
        requests.exceptions.RequestException
            When requests fails
        """
        file = Path(file)

        technology = technology.lower()
        technologies = self.get_technologies()['technologies']
        technology_id = [tech['id'] for tech in technologies
                         if tech['label'].lower() == technology][0]

        if extra_technology != '':
            extra_technology = extra_technology.capitalize()
            extra_tech = gql_extra_technology.format(extra_technology,
                                                     extra_technology_version)
        else:
            extra_tech = ''

        with file.open(mode='rb') as f:
            files = {
                '1': (file.name, f),
                'operations': (None, gql_create_job.format(job_name,
                                                           project_id,
                                                           description,
                                                           category,
                                                           technology_id,
                                                           runtime_version,
                                                           command_line,
                                                           release_note,
                                                           extra_tech)),
                'map': (None, '{ "1": ["variables.file"] }'),
            }

            url = self.url_saagie + self.suffix_api + 'platform/'
            url += str(self.id_platform) + "/graphql"
            response = requests.post(url,
                                     files=files,
                                     auth=self.auth)

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
            UUID of your job. Can be found in the project URL after the '/job/'
            (eg: the job UUID is 'a85ac3db-bca1-4f15-b8f7-44731fba874b' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b)

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
    def get_project_web_apps(self, project_id, instances_limit):
        """List webApps of project with their instances.
        NB: You can only list webApps if you have at least the viewer role on
        the project.

        Parameters
        ----------
        project_id : str
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)
        instances_limit : int
            Maximum limit of instances to fetch per webapp. Fetch from most
            recent to oldest

        Returns
        -------
        dict
            Dict of webApp information
        """
        query = gql(gql_get_project_web_apps.format(project_id,
                                                    instances_limit))
        return self.client.execute(query)

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
            UUID of your app. Can be found in the project URL after the '/app/'
            (eg: the app UUID is '02c01d47-8a29-47d0-a53c-235add43c885' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/app/02c01d47-8a29-47d0-a53c-235add43c885)

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
    def get_project_pipelines(self, project_id, instances_limit):
        """List pipelines of project with their instances.

        Parameters
        ----------
        project_id : str
            UUID of your project. Can be found in the project URL after the
            '/project' (eg: the project UUID is
            '8321e13c-892a-4481-8552-5be4b6cc5df4' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs)
        instances_limit : int
            Maximum limit of instances to fetch per pipelines. Fetch from most
            recent to oldest

        Returns
        -------
        Dict
            Dict of pipelines information
        """
        query = gql(gql_get_pipelines.format(project_id, instances_limit))
        return self.client.execute(query)

    def get_project_pipeline(self, pipeline_id):
        """Get a given pipeline information

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline. Can be found in the URL after the
            '/pipeline' (eg: the pipeline UUID is
            '4da29f25-e7c9-4410-869e-40b9ba0074d1' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/pipeline/4da29f25-e7c9-4410-869e-40b9ba0074d1)

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
            UUID of your pipeline instance. Can be found in the URL after the
            '/pipeline' (eg: the pipeline UUID is
            'b26bebf1-46fe-481e-8fb7-ddd4d8cdd798' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/pipeline/4da29f25-e7c9-4410-869e-40b9ba0074d1/instances/b26bebf1-46fe-481e-8fb7-ddd4d8cdd798)

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
    def edit_pipeline(self, pipeline):
        """Edit a given pipeline
        NB : You can only edit pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline. Can be found in the URL after the
            '/pipeline' (eg: the pipeline UUID is
            '4da29f25-e7c9-4410-869e-40b9ba0074d1' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/pipeline/4da29f25-e7c9-4410-869e-40b9ba0074d1)

        Returns
        -------
        dict
            Dict of pipeline information
        """
        query = gql(gql_edit_pipeline.format(pipeline))
        return self.client.execute(query)

    def run_pipeline(self, pipeline_id):
        """Run a given pipeline
        NB : You can only run pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline. Can be found in the URL after the
            '/pipeline' (eg: the pipeline UUID is
            '4da29f25-e7c9-4410-869e-40b9ba0074d1' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/pipeline/4da29f25-e7c9-4410-869e-40b9ba0074d1)

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
            UUID of your pipeline. Can be found in the URL after the
            '/pipeline' (eg: the pipeline UUID is
            '4da29f25-e7c9-4410-869e-40b9ba0074d1' in
            https://saagie-workspace.prod.saagie.io/projects/platform/6/project/8321e13c-892a-4481-8552-5be4b6cc5df4/pipeline/4da29f25-e7c9-4410-869e-40b9ba0074d1)
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
        to = False
        while state not in final_status_list:
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            pipeline_instance_info = self.client.execute(query)
            state = pipeline_instance_info.get("pipelineInstance")\
                .get("status")
            print('Current state : ' + state)
        return state
