import time
import requests
from pathlib import Path
import json

from querySaagieApi.gql_template import *
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from querySaagieApi.utils import *


class QuerySaagieApiProject:
    def __init__(self, url_saagie, id_plateform, user, password, realm):
        """
        Initialize the class
        Doc Saagie URL example: https://saagie-manager.prod.saagie.io/api/doc
        :param url_saagie: platform URL (eg: https://saagie-workspace.prod.saagie.io)
        :param id_plateform: Platform Id (you can find in the URL when you are on your own
        platform (eg, the id of the platform is 6: https://saagie-workspace.prod.saagie.io/manager/platform/6/#/manager/6)
        :param user: username to login with
        :param password: password to login with
        :param realm: platform url prefix (eg: saagie)
        """
        if not url_saagie.endswith('/'):
            url_saagie += '/'
        self.url_saagie = url_saagie
        self.id_plateform = id_plateform
        self.suffix_api = 'api/v1/projects/'
        self.realm = realm
        self.login = user
        self.password = password
        self.auth = BearerAuth(self.realm, self.url_saagie, self.id_plateform, self.login, self.password)
        self._transport = RequestsHTTPTransport(
            url=self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + "/graphql",
            auth=self.auth,
            use_json=True,
            verify=False
        )
        self.client = Client(
            transport=self._transport,
            fetch_schema_from_transport=True
        )

    #######################################################
    ####                    env vars                   ####
    #######################################################

    def get_global_env_vars(self):
        """
        List global environment variables
        NB: You can only list environment variables if you have at least role viewer on the project or on all projects.
        dict: return: List of global environment variables
        """
        query = gql(gql_get_global_env_vars)
        return self.client.execute(query)

    def get_project_env_vars(self, project_id):
        """
        List environment variables of a specific project according to its projectId.
        NB: You can only list environment variables if you have at least role viewer on the project or on all projects.
        String :param project_id: Project ID
        dict: return: List of environment variables
        """
        query = gql(gql_get_project_env_vars.format(project_id))
        return self.client.execute(query)

    #######################################################
    ####                    projects                   ####
    #######################################################

    def get_projects_info(self):
        """
        Getting information on all projects (eg: id, name, creator, description, jobsCount and status)
        NB: You can only list projects you are rights on and projects you have created with less informations if you are project creator
        dict :return: the project's information
        """
        query = gql(gql_get_projects_info)
        return self.client.execute(query)

    def get_project_info(self, project_id):
        """
        Get project information (eg: name, creator, description, jobsCount and status) with given Id or null if it doesn't exist.
        string :param project_id: project ID
        NB: You can only get project if you have at least role viewer on this project or on all projects.
        dict :return: the project's information
        """
        query = gql(gql_get_project_info.format(project_id))
        return self.client.execute(query)

    def get_technologies(self):
        """
        List available technologies in plateform
        """
        query = gql(gql_get_technologies)
        return self.client.execute(query)

    def create_project(self, name, group=None, role="Manager", description=""):
        """
        Create a project with given name and description.
        :param name: str - name of the project (musn't be an existing project name)
        :param group: str - authorization management : group name to add role on the project to
        Must be an existing group in saagie.
        :param role: str - authorization management : role to give to group on the project
        :param description: str - description of the project

        NOTE:
        - Currently add all plateform technologies for Extraction and Processing
          Future improvement: pass a parameter dict of technologies
        - Currently only take on group and one associated role to add to the project
          Future improvement: possibility to pass in argument several group names with
          several roles to add to the project
        """
        if role == 'Manager':
            role = 'ROLE_PROJECT_MANAGER'
        elif role == 'Editor':
            role = 'ROLE_PROJECT_EDITOR'
        elif role == 'Viewer':
            role = 'ROLE_PROJECT_VIEWER'
        else:
            raise ValueError("'role' takes value in ('Manager', 'Editor', 'Viewer')")

        technologies = [f'{{id: "{tech["id"]}"}}' for tech in self.get_technologies()["technologies"]]
        
        group_block = ""
        if group is not None:
            group_block = group_block_template.format(group, role)

        query = gql(gql_create_project.format(name,
                                              description,
                                              group_block,
                                              ', '.join(technologies)))
        return self.client.execute(query)

    #######################################################
    ####                      jobs                     ####
    #######################################################

    def get_project_jobs(self, project_id, instances_limit):
        """
        List jobs of project get with project UUID
        string :param project_id: project ID
        int: param instances_limit: number of instances loaded from the newer to the olders
        NB: You can only list jobs if you have at least role viewer on the project or on all projects.
        dict :return: project's jobs information
        """
        query = gql(gql_get_project_jobs.format(project_id, instances_limit))
        return self.client.execute(query)

    def get_project_job(self, job_id):
        """
        Get job with given UUID or null if it doesn't exist.
        String :param job_id: Job ID
        dict :return: Job's information
        """
        query = gql(gql_get_project_job.format(job_id))
        return self.client.execute(query)

    def get_job_instance(self, job_instance_id):

        query = gql(gql_get_job_instance.format(job_instance_id))
        return self.client.execute(query)

    def run_job(self, job_id):
        """
        Run a specific job
        :param job_id: String, Job ID
        dict :return:
        """
        query = gql(gql_run_job.format(job_id))
        return self.client.execute(query)

    def run_job_callback(self, job_id, freq=10, timeout=-1):
        """
        Run a job and wait for the final status (KILLED, FAILED or SUCCESS)
        string:param job_id:
        int:param freq: Sec between two state ckecks
        int:param timeout: Sec before timeout
        string: return: the final state of this job
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
        """
        Stop a specific instance of job
        :param job_instance_id, String
        :dict: return:
        """
        query = gql(gql_stop_job_instance.format(job_instance_id))
        return self.client.execute(query)

    def edit_job(self, job):
        """
        Edit a job
        job:param job
        dict: return: job's information
        """
        query = gql(gql_edit_job.format(job))
        return self.client.execute(query)

    def create_job(self, job_name, project_id, file, description='', category='Processing',
                   technology='python', runtime_version='3.6', command_line='python {file} arg1 arg2',
                   release_note='', extra_technology='', extra_technology_version=''):
        """
        Create Job in given project
        :param job_name: job name - must not already exist in project
        :param project_id: id of the project in which one want to create the job
        :param file: local file path to upload
        :param description: description of the job
        :param category: category to create the job into. Must be 'Extraction',
        'Processing' or 'Smart App'
        :param technology: technology of the job to create. See self.get_technologies()
        for a list of available technologies
        :param runtime_version: technology version of the job
        :param command_line: command line of the job
        :param release_note: release note of the job
        :param extra_technology: extra technology when needed (spark jobs). If not
        needed, leave to empty string or the request will not work
        :param extra_technology_version: version of the extra technology. Leave to
        empty string when not needed

        NOTE:
        - Since gql does not support multipart graphQL requests, requests module is used for now.
          The create job graphQL API takes a multipart graphQL request to upload a file.
          See https://github.com/jaydenseric/graphql-multipart-request-spec for more details
        - 2020-06-08 : multipart graphQL support will probably be implemented in gql in the
          near future. See https://github.com/graphql-python/gql/issues/68 to follow this
          work.
        - Tested with python and spark jobs
        """
        file = Path(file)

        technology = technology.lower()
        technologies = self.get_technologies()['technologies']
        technology_id = [tech['id'] for tech in technologies if tech['label'].lower() == technology][0]

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

            response = requests.post(
                self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + "/graphql",
                files=files,
                auth=self.auth)

        if response:
            return json.loads(response.content)
        else:
            raise requests.exceptions.RequestException(f"Requests failed with status_code :'{response.status_code}'")

    #######################################################
    ####                      apps                     ####
    #######################################################

    def get_project_web_apps(self, project_id, instances_limit):
        """
        List webApps of project get with project UUID
        string :param project_id: project ID
        NB: You can only list webApps if you have at least role viewer on the project or on all projects.
        dict :return: webApp's information
        """
        query = gql(gql_get_project_web_apps.format(project_id, instances_limit))
        return self.client.execute(query)

    def get_project_web_app(self, web_app_id):
        """
        Get webApp with given UUID or null if it doesn't exist.
        String :param web_app_id: webApp ID
        dict :return: webApp's information
        """
        query = gql(get_project_web_app.format(web_app_id))
        return self.client.execute(query)

    def get_project_apps(self, project_id):
        """
        List apps of project get with project UUID
        string :param project_id: project ID
        NB: You can only list apps if you have at least role viewer on the project or on all projects.
        dict :return: webApp's information
        """
        query = gql(gql_get_project_apps.format(project_id))
        return self.client.execute(query)

    def get_project_app(self, app_id):
        """
        Get app with given UUID or null if it doesn't exist.
        String :param app_id: App ID
        dict :return: App's information
        """
        query = gql(gql_get_project_app.format(app_id))
        return self.client.execute(query)

    #######################################################
    ####                   pipelines                   ####
    #######################################################

    def get_project_pipelines(self, project_id, instances_limit):
        """
        List pipelines of project get with project UUID.
        String :param project_id: Project ID
        int: param instances_limit: number of instances loaded from the newer to the olders
        dict :return: all pipelines in the project
        """
        query = gql(gql_get_pipelines.format(project_id, instances_limit))
        return self.client.execute(query)

    def get_project_pipeline(self, pipeline_id):
        """
        Get pipeline with given UUID or null if it doesn't exist.
        String :param pipeline_id: Pipeline ID
        dict :return: pipeline's information
        """
        query = gql(gql_get_pipeline.format(pipeline_id))
        return self.client.execute(query)

    def stop_pipeline(self, pipeline_instance_id):
        """
        Stop a specific instance of pipeline
        :param pipeline_instance_id, String
        :dict: return:
        """
        query = gql(gql_stop_pipeline_instance.format(pipeline_instance_id))
        return self.client.execute(query)

    def edit_pipeline(self, pipeline):
        """
        Edit a pipeline
        pipeline:param pipeline
        dict: return: pipeline's information
        """
        query = gql(gql_edit_pipeline.format(pipeline))
        return self.client.execute(query)

    def run_pipeline(self, pipeline_id):
        """
        Run a specific pipeline
        :param pipeline_id: String, Pipeline ID
        dict :return:
        """
        query = gql(gql_run_pipeline.format(pipeline_id))
        return self.client.execute(query)

    def run_pipeline_callback(self, pipeline_id, freq=10, timeout=-1):
        """
        Run a pipeline and wait for the final status (KILLED, FAILED or SUCCESS)
        string:param pipeline_id:
        int:param freq: Sec between two state ckecks
        int:param timeout: Sec before timeout
        string: return: the final state of this pipeline
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
            state = pipeline_instance_info.get("pipelineInstance").get("status")
            print('Current state : ' + state)
        return state
