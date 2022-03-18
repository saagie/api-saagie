from gql import gql

from .gql_queries import *


class Projects:

    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list(self):
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

    def get_id(self, project_name):
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
        projects = self.list()["projects"]
        project = list(filter(lambda p: p["name"] == project_name, projects))
        if project:
            project_id = project[0]["id"]
            return project_id

        else:
            raise NameError(f"Project {project_name} does not exist or you don't have permission to see it.")

    def get_info(self, project_id):
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

    def get_technologies(self, project_id):
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

    def create(self, name, group=None, role="Manager", description=""):
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
        repositories = self.saagie_api.get_repositories_info()['repositories']
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

    def delete(self, project_id):
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
