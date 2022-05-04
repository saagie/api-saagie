from typing import Dict, List

from gql import gql

from .gql_queries import *


class Projects:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    @staticmethod
    def __create_groupe_role(params: Dict, group: str, role: str) -> Dict:
        """
        Create a dict with the group and role to add to the project
        Parameters
        ----------
        params:Dict
            Dict of parameters to create the role
        group : str
            Authorization management: name of the group to add the given role to
        role : str
            Authorization management: role to give to the given group on the project
        Returns
        -------
        Dict
            Dict that contains the authorized group and role
        """
        if role:
            if role == "Manager":
                role = "ROLE_PROJECT_MANAGER"
            elif role == "Editor":
                role = "ROLE_PROJECT_EDITOR"
            elif role == "Viewer":
                role = "ROLE_PROJECT_VIEWER"
            else:
                raise ValueError("'role' takes value in ('Manager', 'Editor'," " 'Viewer')")

        # Set group permission
        if group is not None:
            group_block = [{"name": group, "role": role}]
            params["authorizedGroups"] = group_block

        return params

    def list(self) -> Dict:
        """Get information for all projects (id, name, creator, description,
        jobCount and status)
        NB: You can only list projects you have rights on.

        Returns
        -------
        dict
            Dict of projects information
        """
        query = gql(GQL_LIST_PROJECTS)
        return self.client.execute(query)

    def get_id(self, project_name: str) -> Dict:
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
        raise NameError(f"Project {project_name} does not exist or you don't have permission to see it.")

    def get_info(self, project_id: str) -> Dict:
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
        query = gql(GQL_GET_PROJECT_INFO)
        return self.client.execute(query, variable_values={"id": project_id})

    def get_jobs_technologies(self, project_id: str) -> Dict:
        """List available jobs technologies id for the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of available jobs technology ids
        """
        query = gql(GQL_GET_PROJECT_JOBS_TECHNOLOGIES)
        return self.client.execute(query, variable_values={"id": project_id})["project"]

    def get_apps_technologies(self, project_id: str) -> Dict:
        """List available apps technology ids for the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of available apps technology ids
        """
        query = gql(GQL_GET_PROJECT_APPS_TECHNOLOGIES)
        return self.client.execute(query, variable_values={"id": project_id})["project"]

    def create(
        self,
        name: str,
        group: str = None,
        role: str = "Manager",
        description: str = "",
        jobs_technologies_allowed: Dict = None,
        apps_technologies_allowed: Dict = None,
    ) -> Dict:
        """Create a new project on the platform with all the job technologies and the app technologies
        of the official Saagie catalog if no technologies are specified.

        Parameters
        ----------
        name : str
            Name of the project (must not already exist)
        group : None or str, optional
            Authorization management: name of the group to add the given role to
        role : str, optional
            Authorization management: role to give to the given group on the project
        description : str, optional
            Description of the project
        jobs_technologies_allowed:list, optional
            Dict of catalog and jobs technologies allowed for the project
        apps_technologies_allowed:list, optional
            Dict of catalog and apps technologies allowed for the project

        Returns
        -------
        dict
            Dict of created project

        Raises
        ------
        ValueError
            If given unknown role value
        """
        # Create the params of the query
        params = {"name": name}
        params = self.__create_groupe_role(params, group, role)
        if description:
            params["description"] = description

        params["technologies"] = self.__get_jobs_for_project(jobs_technologies_allowed)
        params["appTechnologies"] = self.__get_apps_for_projects(apps_technologies_allowed)

        query = gql(GQL_CREATE_PROJECT)
        return self.client.execute(query, variable_values=params)

    def __get_apps_for_projects(self, apps_technologies_allowed) -> List:
        """
        Get technology ids for the apps configured in parameters
        If param is empty, get all apps technology ids from the official saagie catalog
        Parameters
        ----------
        apps_technologies_allowed:list, optional
            Dict of catalog and apps technologies allowed for the project

        Returns
        -------
        list
            List of dict of apps technologies
        """
        if not apps_technologies_allowed:
            return [
                {"id": techno["id"]}
                for techno in self.saagie_api.get_available_technologies("saagie")
                if techno["__typename"] == "AppTechnology"
            ]
        tech_ids = []
        for catalog, technos in apps_technologies_allowed.items():
            tech_ids.extend(
                self.saagie_api.check_technology_valid(
                    technos,
                    [
                        techno
                        for techno in self.saagie_api.get_available_technologies(catalog)
                        if techno["__typename"] == "AppTechnology"
                    ],
                    catalog,
                )
            )
        return [{"id": t} for t in tech_ids]

    def __get_jobs_for_project(self, jobs_technologies_allowed) -> List:
        """
        Get technology ids for the jobs configured in parameters
        If param is empty, get all jobs technology ids from the official saagie catalog
        Parameters
        ----------
        jobs_technologies_allowed:list, optional
            Dict of catalog and jobs technologies allowed for the project

        Returns
        -------
        list
            List of dict of jobs technologies
        """
        if not jobs_technologies_allowed:
            return [
                {"id": techno["id"]}
                for techno in self.saagie_api.get_available_technologies("saagie")
                if techno["__typename"] == "JobTechnology" or (techno["__typename"] == "SparkTechnology")
            ]
        tech_ids = []
        for catalog, technos in jobs_technologies_allowed.items():
            tech_ids.extend(
                self.saagie_api.check_technology_valid(
                    technos,
                    [
                        techno
                        for techno in self.saagie_api.get_available_technologies(catalog)
                        if techno["__typename"] == "JobTechnology" or techno["__typename"] == "SparkTechnology"
                    ],
                    catalog,
                )
            )
        return [{"id": t} for t in tech_ids]

    def get_rights(self, project_id: str) -> Dict:
        """List rights associated for the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of rights associated for the project
        """
        query = gql(GQL_GET_PROJECT_RIGHTS)
        return self.client.execute(query, variable_values={"id": project_id})

    def edit(
        self,
        project_id: str,
        name: str = None,
        group: str = None,
        role: str = None,
        description: str = None,
        jobs_technologies_allowed: Dict = None,
        apps_technologies_allowed: Dict = None,
    ) -> Dict:
        """Edit a project


        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        name : str, optional
            Name of the project
            If not filled, defaults to current value, else it will change the job's name
        group : None or str, optional
            Authorization management: name of the group to add the given role to
            If not filled, defaults to current value, else it will change the group
        role : str, optional
            Authorization management: role to give to the given group on the project
            If not filled, defaults to current value, else it will change the role
        description : str, optional
            Description of the project
            If not filled, defaults to current value, else it will change the job's description
        jobs_technologies_allowed:list, optional
            Dict of catalog and jobs technologies allowed for the project
            If not filled, defaults to current value, else it will change the jobs technologies allowed
        apps_technologies_allowed:list, optional
            Dict of catalog and apps technologies allowed for the project
            If not filled, defaults to current value, else it will change the apps technologies allowed

        Returns
        -------
        dict
            Dict of created project

        Raises
        ------
        ValueError
            If given unknown role value
        """
        params = {"projectId": project_id}
        previous_project_version = self.get_info(project_id)["project"]
        params = self.__create_groupe_role(params, group, role)

        if not group and not role:
            params["authorizedGroups"] = [
                {"name": group_role["name"], "role": group_role["role"]}
                for group_role in self.get_rights(project_id)["rights"]
            ]

        if name:
            params["name"] = name
        else:
            params["name"] = previous_project_version["name"]

        if description:
            params["description"] = description
        else:
            params["description"] = previous_project_version["description"]

        if jobs_technologies_allowed:
            params["technologies"] = self.__get_jobs_for_project(jobs_technologies_allowed)
        else:
            previous_project_technologies = [
                {"id": techno["id"]}
                for techno in self.get_jobs_technologies(project_id)["technologiesByCategory"][0]["technologies"]
            ]
            params["technologies"] = previous_project_technologies

        if apps_technologies_allowed:
            params["appTechnologies"] = self.__get_apps_for_projects(apps_technologies_allowed)
        else:
            params["appTechnologies"] = self.get_apps_technologies(project_id)["appTechnologies"]

        query = gql(GQL_EDIT_PROJECT)
        return self.client.execute(query, variable_values=params)

    def delete(self, project_id: str) -> Dict:
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
        query = gql(GQL_DELETE_PROJECT)
        return self.client.execute(query, variable_values={"projectId": project_id})
