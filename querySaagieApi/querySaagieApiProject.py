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
            use_json=True
        )
        self.client = Client(
            transport=self._transport,
            fetch_schema_from_transport=True
        )

    def get_projects_info(self):
        """
        Getting information on all projects (eg: id, name, creator, description, jobsCount and status)
        NB: You can only list projects you are rights on and projects you have created with less informations if you are project creator
        dict :return: the project's information
        """
        query = gql_get_projects_info
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

    def get_project_jobs(self, project_id):
        """
        List jobs of project get with project UUID
        string :param project_id: project ID
        NB: You can only list jobs if you have at least role viewer on the project or on all projects.
        dict :return: project's jobs information
        """
        query = gql(gql_get_project_jobs.format(project_id))
        return self.client.execute(query)

    def get_project_job(self, job_id):
        """
        Get job with given UUID or null if it doesn't exist.
        String :param job_id: Job ID
        dict :return: Job's information
        """
        query = gql(gql_get_project_job.format(job_id))
        return self.client.execute(query)

    def get_project_web_apps(self, project_id):
        """
        List webApps of project get with project UUID
        string :param project_id: project ID
        NB: You can only list webApps if you have at least role viewer on the project or on all projects.
        dict :return: webApp's information
        """
        query = gql(gql_get_project_web_apps.format(project_id))
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

    def get_project_env_vars(self, project_id):
        """
        List environment variables of a specific project according to its projectId.
        NB: You can only list environment variables if you have at least role viewer on the project or on all projects.
        String :param project_id: Project ID
        dict: return: List of environment variables
        """
        query = gql(gql_get_project_env_vars.format(project_id))
        return self.client.execute(query)

    def get_global_env_vars(self):
        """
        List global environment variables
        NB: You can only list environment variables if you have at least role viewer on the project or on all projects.
        dict: return: List of global environment variables
        """
        query = gql(gql_get_global_env_vars)
        return self.client.execute(query)