import json
import logging
import os
import time
from collections import defaultdict
from typing import Dict, List, Optional

from gql import gql

from ..utils.folder_functions import check_folder_path, create_folder, write_to_json_file
from .gql_queries import *


class Projects:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    @staticmethod
    def __map_role(role: str) -> str:
        """
        Map role with valid Saagie Role
        ----------
        params:role:str
            Role as simple string
        Returns
        -------
        str
            Valid Saagie role
        """
        if role.lower() in ("manager", "editor", "viewer"):
            return f"ROLE_PROJECT_{role.upper()}"
        raise ValueError("❌ 'role' takes value in ('Manager', 'Editor'," " 'Viewer')")

    @staticmethod
    def _create_groupe_role(
        params: Dict,
        group: Optional[str],
        role: Optional[str],
        groups_and_roles: Optional[List[Dict]],
    ) -> Dict:

        if groups_and_roles and (group or role):
            raise RuntimeError(
                "❌ Too many arguments, specify either a group and role, "
                "or multiple groups and roles with groups_and_roles"
            )

        if groups_and_roles:
            group_block = [
                {"name": g, "role": Projects.__map_role(r)} for mydict in groups_and_roles for g, r in mydict.items()
            ]

            params["authorizedGroups"] = group_block
            return params

        if group and role:
            saagie_role = Projects.__map_role(role)
            group_block = [{"name": group, "role": saagie_role}]
            params["authorizedGroups"] = group_block
            return params

        if (group and role is None) or (group is None and role):
            raise RuntimeError(
                "❌ Too few arguments, specify either a group and role, "
                "or multiple groups and roles with groups_and_roles"
            )

        return params

    def list(self, pprint_result: Optional[bool] = None) -> Dict:
        """Get information for all projects (id, name, creator, description,
        jobCount and status)
        NB: You can only list projects you have rights on.

        Parameters
        ----------
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of projects information
        """
        return self.saagie_api.client.execute(query=gql(GQL_LIST_PROJECTS), pprint_result=pprint_result)

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
        raise NameError(f"❌ Project {project_name} does not exist or you don't have permission to see it.")

    def get_info(self, project_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """Get information for a given project (id, name, creator, description,
        jobCount and status)
        NB: You can only get project information if you have at least the
        viewer role on this project or on all projects.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of project information
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PROJECT_INFO), variable_values={"id": project_id}, pprint_result=pprint_result
        )

    def get_jobs_technologies(self, project_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """List available jobs technologies id for the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of available jobs technology ids
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PROJECT_JOBS_TECHNOLOGIES),
            variable_values={"id": project_id},
            pprint_result=pprint_result,
        )["project"]

    def get_apps_technologies(self, project_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """List available apps technology ids for the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global
        Returns
        -------
        dict
            Dict of available apps technology ids
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PROJECT_APPS_TECHNOLOGIES),
            variable_values={"id": project_id},
            pprint_result=pprint_result,
        )["project"]

    def create(
        self,
        name: str,
        group: str = None,
        role: str = None,
        groups_and_roles: Optional[List[Dict]] = None,
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
        groups_and_roles:list[dict], optional
            dict of groups and their respective roles on the project
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
        params = self._create_groupe_role(params, group, role, groups_and_roles)
        if description:
            params["description"] = description

        params["technologies"] = self.__get_jobs_for_project(jobs_technologies_allowed)
        params["appTechnologies"] = self.__get_apps_for_projects(apps_technologies_allowed)

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_PROJECT), variable_values=params)
        logging.info("✅ Project [%s] successfully created", name)
        return result

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
        return self.saagie_api.client.execute(query=gql(GQL_GET_PROJECT_RIGHTS), variable_values={"id": project_id})

    def edit(
        self,
        project_id: str,
        name: str = None,
        group: str = None,
        role: str = None,
        groups_and_roles: Optional[List[Dict]] = None,
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
            Authorization management: name of the group to add the given role to,
            cannot be set if groups_and_roles is already set
        role : str, optional
            Authorization management: role to give to the given group on the project
            cannot be set if groups_and_roles is already set
        groups_and_roles:list[dict], optional
            dict of groups and their respective roles on the project, cannot be set if group or role are already set
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
        params = self._create_groupe_role(params, group, role, groups_and_roles)

        if not group and not role and not groups_and_roles:
            params["authorizedGroups"] = [
                {"name": group_role["name"], "role": group_role["role"]}
                for group_role in self.get_rights(project_id)["rights"]
            ]

        params["name"] = name or previous_project_version["name"]
        params["description"] = description or previous_project_version["description"]

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

        return self.saagie_api.client.execute(query=gql(GQL_EDIT_PROJECT), variable_values=params)

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
        result = self.saagie_api.client.execute(
            query=gql(GQL_DELETE_PROJECT), variable_values={"projectId": project_id}
        )
        logging.info("✅ Project [%s] successfully deleted", project_id)
        return result

    def export(
        self,
        project_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        project_only_env_vars: bool = False,
    ) -> bool:
        """Export the project in a folder

        Parameters
        ----------
        project_id : str
            Project ID
        output_folder : str
            Path to store the exported project
        error_folder : str, optional
            Path to store the non exported job/app/pipeline ID in case of error. If not set, error is not write
        versions_limit : int, optional
            Maximum limit of versions to fetch per job/app/pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job/app/pipeline
        project_only_env_vars : bool, optional
            True if only project environment variable should be exported False otherwise
        Returns
        -------
        bool
            True if project is successfully exported False otherwise
        """

        result = True
        output_folder = check_folder_path(output_folder)
        output_folder += project_id + "/"
        create_folder(output_folder)
        output_folder_job = output_folder + "jobs/"
        output_folder_pipeline = output_folder + "pipelines/"
        output_folder_app = output_folder + "apps/"
        output_folder_env_vars = output_folder + "env_vars/"

        project_info = self.saagie_api.projects.get_info(project_id)["project"]

        job_tech_dict = {}
        job_tech_dict = defaultdict(list)
        for category in self.saagie_api.projects.get_jobs_technologies(project_id=project_id)["technologiesByCategory"]:
            for tech in category["technologies"]:
                catalog, techno = self.saagie_api.get_technology_name_by_id(tech["id"])
                if catalog != "" and techno != "":
                    if techno not in job_tech_dict[catalog]:
                        job_tech_dict[catalog].append(techno)

        project_info["jobs_technologies"] = job_tech_dict if job_tech_dict else None

        app_tech_dict = {}
        app_tech_dict = defaultdict(list)
        for tech in self.saagie_api.projects.get_apps_technologies(project_id=project_id)["appTechnologies"]:
            catalog, techno = self.saagie_api.get_technology_name_by_id(tech["id"])
            if catalog != "" and techno != "":
                if techno not in app_tech_dict[catalog]:
                    app_tech_dict[catalog].append(techno)

        project_info["apps_technologies"] = app_tech_dict if app_tech_dict else None

        rights = []
        for right in self.saagie_api.projects.get_rights(project_id)["rights"]:
            rights.append({right["name"]: right["role"].split("_")[-1]})

        project_info["rights"] = rights

        write_to_json_file(output_folder + "project.json", project_info)

        list_jobs = self.saagie_api.jobs.list_for_project_minimal(project_id)
        id_jobs = [job["id"] for job in list_jobs["jobs"]]

        list_pipelines = self.saagie_api.pipelines.list_for_project_minimal(project_id)["project"]
        id_pipelines = [pipeline["id"] for pipeline in list_pipelines["pipelines"]]

        list_apps = self.saagie_api.apps.list_for_project_minimal(project_id)
        id_apps = [app["id"] for app in list_apps["project"]["apps"]]

        job_failed = []
        pipeline_failed = []
        app_failed = []
        env_var_failed = []

        env_vars_export = self.saagie_api.env_vars.export(
            project_id, output_folder_env_vars, error_folder=error_folder, project_only=project_only_env_vars
        )
        if not env_vars_export:
            env_var_failed.append(project_id)

        for id_job in id_jobs:
            job_export = self.saagie_api.jobs.export(
                id_job,
                output_folder_job,
                error_folder=error_folder,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )
            if not job_export:
                job_failed.append(id_job)

        for id_pipeline in id_pipelines:
            pipeline_export = self.saagie_api.pipelines.export(
                id_pipeline,
                output_folder_pipeline,
                error_folder=error_folder,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )
            if not pipeline_export:
                pipeline_failed.append(id_pipeline)

        for id_app in id_apps:
            app_export = self.saagie_api.apps.export(
                id_app,
                output_folder_app,
                error_folder=error_folder,
                versions_only_current=versions_only_current,
            )
            if not app_export:
                app_failed.append(id_app)
        if job_failed or pipeline_failed or app_failed or env_var_failed:
            result = False
            logging.warning("❌ Project [%s] has not been successfully exported", project_id)
        else:
            logging.info("✅ Project [%s] successfully exported", project_id)
        return result

    def import_from_json(
        self,
        path_to_folder: str = None,
    ) -> bool:
        """Import a project from a folder

        Parameters
        ----------
        path_to_folder : str, optional
            Path to the folder of the project to import
        Returns
        -------
        bool
            True if project is imported False otherwise
        """
        try:
            path_to_folder = os.path.abspath(path_to_folder)
            json_file = os.path.join(path_to_folder, "project.json")
            with open(json_file, "r") as file:
                config_dict = json.load(file)
        except Exception as exception:
            logging.warning("Cannot open the JSON file %s", json_file)
            logging.error("Something went wrong %s", exception)
            return False

        try:
            project_name = config_dict["name"]
            new_project_id = self.create(
                name=project_name,
                groups_and_roles=config_dict["rights"],
                apps_technologies_allowed=config_dict["apps_technologies"],
                jobs_technologies_allowed=config_dict["jobs_technologies"],
                description=config_dict["description"],
            )["createProject"]["id"]

            # Waiting for the project to be ready
            project_status = self.saagie_api.projects.get_info(project_id=new_project_id)["project"]["status"]
            waiting_time = 0

            # Safety: wait for 5min max for project initialisation
            project_creation_timeout = 400
            while project_status != "READY" and waiting_time <= project_creation_timeout:
                time.sleep(10)
                project_status = self.saagie_api.projects.get_info(new_project_id)["project"]["status"]
                waiting_time += 10
            if project_status != "READY":
                raise TimeoutError(
                    f"Project creation is taking longer than usual, "
                    f"Aborting project import after {project_creation_timeout} seconds"
                )
        except Exception as exception:
            logging.warning("❌ Project [%s] has not been successfully imported", project_name)
            logging.error("Something went wrong %s", exception)
            return False

        status = True
        list_failed = {"jobs": [], "pipelines": [], "apps": [], "env_vars": []}

        jobs_list = list(os.listdir(os.path.join(path_to_folder, "jobs")))
        for job in jobs_list:
            # TODO if conversion of path_to_folder to absolute path is not efficient
            # os.chdir(os.path.abspath(path_to_folder))
            job_status = self.saagie_api.jobs.import_from_json(
                project_id=new_project_id, path_to_folder=os.path.join(path_to_folder, "jobs", job)
            )
            if not job_status:
                list_failed["jobs"].append(job)
                status = False

        # Import pipelines
        for (dirpath, _, filenames) in os.walk(os.path.join(path_to_folder, "pipelines")):
            for filename in filenames:
                json_file = os.path.join(dirpath, filename)
                pipeline_status = self.saagie_api.pipelines.import_from_json(
                    json_file=json_file, project_id=new_project_id
                )
                if not pipeline_status:
                    list_failed["pipelines"].append(dirpath.split(os.sep)[-1])
                    status = False

        # Import apps
        for (dirpath, _, filenames) in os.walk(os.path.join(path_to_folder, "apps")):
            for filename in filenames:
                json_file = os.path.join(dirpath, filename)
                app_status = self.saagie_api.apps.import_from_json(json_file=json_file, project_id=new_project_id)
                if not app_status:
                    list_failed["apps"].append(dirpath.split(os.sep)[-1])
                    status = False

        # Import env vars
        for (dirpath, _, filenames) in os.walk(os.path.join(path_to_folder, "env_vars")):
            for filename in filenames:
                json_file = os.path.join(dirpath, filename)
                env_var_status = self.saagie_api.env_vars.import_from_json(
                    json_file=json_file, project_id=new_project_id
                )
                if not env_var_status:
                    list_failed["env_vars"].append(dirpath.split(os.sep)[-1])
                    status = False

        if not status:
            logging.error("Something went wrong during project import %s", list_failed)
        return status
