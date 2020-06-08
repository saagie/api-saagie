import time

from querySaagieApi.gql_template import *
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


class QuerySaagieApiProject:
    def __init__(self, url_saagie, id_plateform, user, password):
        """
        Initialize the class
        Doc Saagie URL example: https://saagie-manager.prod.saagie.io/api/doc
        :param url_saagie: platform URL (eg: https://saagie-manager.prod.saagie.io)
        :param id_plateform: Platform Id (you can find in the URL when you are on your own
        platform (eg, the id of the platform is 6: https://saagie-beta.prod.saagie.io/manager/platform/6/#/manager/6))
        :param user: username to login with
        :param password: password to login with
        """
        if not url_saagie.endswith('/'):
            url_saagie += '/'
        self.url_saagie = url_saagie
        self.id_plateform = id_plateform
        self.suffix_api = 'api/v1/projects/'
        self.auth = (user, password)
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

    def create_project(self, name, group, role="Manager", description=""):
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

        query = gql(gql_create_project.format(name,
                                              description,
                                              group,
                                              role,
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
