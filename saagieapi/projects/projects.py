import json
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from gql import gql

from ..utils.folder_functions import create_folder, write_to_json_file
from .gql_queries import *


class Projects:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    @staticmethod
    def __map_role(role: str) -> str:
        """
        Map role with valid Saagie Role

        Parameters
        ----------
        role : str
            Role as simple string

        Returns
        -------
        str
            Valid Saagie role
        """

        if role.lower() in {"manager", "editor", "viewer"}:
            return f"ROLE_PROJECT_{role.upper()}"
        raise ValueError("❌ 'role' takes value in ('Manager', 'Editor', 'Viewer')")

    @staticmethod
    def _create_groupe_role(
        group: Optional[str],
        role: Optional[str],
        groups_and_roles: Optional[List[Dict]],
    ) -> Dict:
        if groups_and_roles and (group or role):
            raise RuntimeError(
                "❌ Too many arguments, specify either a group and role, "
                "or multiple groups and roles with groups_and_roles"
            )

        if (group and role is None) or (group is None and role):
            raise RuntimeError(
                "❌ Too few arguments, specify either a group and role, "
                "or multiple groups and roles with groups_and_roles"
            )

        if groups_and_roles:
            group_block = [
                {"name": g, "role": Projects.__map_role(r)} for mydict in groups_and_roles for g, r in mydict.items()
            ]

            return {"authorizedGroups": group_block}

        if group and role:
            saagie_role = Projects.__map_role(role)
            group_block = [{"name": group, "role": saagie_role}]
            return {"authorizedGroups": group_block}
        return {}

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

        Examples
        --------
        >>> saagieapi.projects.list()
        {
            "projects":[
                {
                    "id":"8321e13c-892a-4481-8552-5be4d6cc5df4",
                    "name":"Project A",
                    "creator":"john.doe",
                    "description":"My project A",
                    "jobsCount":49,
                    "status":"READY"
                },
                {
                    "id":"33b70e1b-3111-4376-a839-12d2f93c323b",
                    "name":"Project B",
                    "creator":"john.doe",
                    "description":"My project B",
                    "jobsCount":1,
                    "status":"READY"
                }
            ]
        }
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

        Examples
        --------
        >>> saagieapi.projects.get_id("Project A")
        "8321e13c-892a-4481-8552-5be4d6cc5df4"
        """

        projects = self.list()["projects"]
        if project := list(filter(lambda p: p["name"] == project_name, projects)):
            return project[0]["id"]
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

        Examples
        --------
        >>> saagieapi.projects.get_info(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")
        {
            "project": {
                "name":"Project A",
                "creator":"john.doe",
                "description":"My project A",
                "jobsCount":49,
                "status":"READY"
            }
        }
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PROJECT_INFO), variable_values={"id": project_id}, pprint_result=pprint_result
        )

    def get_info_by_name(self, project_name: str, pprint_result: Optional[bool] = None) -> Dict:
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

        Examples
        --------
        >>> saagieapi.projects.get_info_by_name(project_name="Project A")
        {
            "projectByName": {
                "id": "8321e13c-892a-4481-8552-5be4d6cc5df4",
                "name":"Project A",
                "creator":"john.doe",
                "description":"My project A",
                "jobsCount":49,
                "status":"READY"
            }
        }
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PROJECT_INFO_BY_NAME), variable_values={"name": project_name}, pprint_result=pprint_result
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

        Examples
        --------
        >>> saagieapi.projects.get_jobs_technologies(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")
        {
            'technologiesByCategory': [
                {
                    'jobCategory': 'Extraction',
                    'technologies': [
                        {
                            'id': '9bb75cad-69a5-4a9d-b059-811c6cde589e',
                            '__typename': 'Technology'
                        },
                        {
                            'id': 'f267085d-cc52-4ae8-ad9e-af8721c81127',
                            '__typename': 'Technology'
                        }
                    ]
                },
                {
                    'jobCategory': 'Processing',
                    'technologies': [
                        {
                            'id': '9bb75cad-69a5-4a9d-b059-811c6cde589e',
                            '__typename': 'Technology'
                        }
                    ]
                },
                {
                    'jobCategory': 'Smart App',
                    'technologies': []
                }
            ]
        }
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

        Examples
        --------
        >>> saagieapi.projects.get_apps_technologies(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")
        {
            'appTechnologies': [
                {
                    'id': '11d63963-0a74-4821-b17b-8fcec4882863'
                },
                {
                    'id': '56ad4996-7285-49a6-aece-b9525c57c619'
                },
                {
                    'id': 'd0b55623-9dc0-4e03-89c7-6a2494387a4f'
                }
            ]
        }
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

        Examples
        --------
        >>> saagie_client.projects.create(
        ...     name="Project_A",
        ...     groups_and_roles=[{"my_group": "Manager"}],
        ...     jobs_technologies_allowed={"saagie": ["python", "spark"]},
        ...     apps_technologies_allowed={"saagie": ["Jupyter Notebook"]}
        ... )
        {
            'createProject': {
                'id': '09515109-e8d3-4ed0-9ab7-5370efcb6cb5',
                'name': 'Project_A',
                'creator': 'toto.tata'
            }
        }
        """

        # Create the params of the query
        params = {"name": name}
        params.update(self._create_groupe_role(group, role, groups_and_roles))
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
                if techno["__typename"] in ("JobTechnology", "SparkTechnology")
            ]
        tech_ids = []
        for catalog, technos in jobs_technologies_allowed.items():
            tech_ids.extend(
                self.saagie_api.check_technology_valid(
                    technos,
                    [
                        techno
                        for techno in self.saagie_api.get_available_technologies(catalog)
                        if techno["__typename"] in ("JobTechnology", "SparkTechnology")
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

        Examples
        --------
        >>> saagieapi.projects.get_rights(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")
        {
            'rights': [
                {
                    'name': 'manager_group',
                    'role': 'ROLE_PROJECT_MANAGER',
                    'isAllProjects': True
                },
                {
                    'name': 'my_group',
                    'role': 'ROLE_PROJECT_MANAGER',
                    'isAllProjects': False
                }
            ]
        }
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

        Examples
        --------
        >>> saagie_client.projects.edit(
        ...     project_id="9a261ae0-fd73-400c-b9b6-b4b63ac113eb",
        ...     name="PROJECT B",
        ...     groups_and_roles=[{"my_group": "Viewer"}],
        ...     description="new desc",
        ...     jobs_technologies_allowed={"saagie": ["r"]},
        ...     apps_technologies_allowed={"saagie": ["Dash"]}
        ... )
        {
            'editProject': {
                'id': '9a261ae0-fd73-400c-b9b6-b4b63ac113eb',
                'name': 'PROJECT B',
                'creator': 'toto.tata'
            }
        }
        """

        params = {"projectId": project_id}
        previous_project_version = self.get_info(project_id)["project"]
        params.update(self._create_groupe_role(group, role, groups_and_roles))

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

        Examples
        --------
        >>> saagieapi.projects.delete(project_id="8321e13c-892a-4481-8552-5be4d6cc5df4")
        {
            "deleteProject": True
        }
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

        Examples
        --------
        >>> saagieapi.projects.export(
        ...     project_id="8321e13c-892a-4481-8552-5be4d6cc5df4",
        ...     output_folder="./output/",
        ...     error_folder= "./error/",
        ...     versions_only_current = True,
        ...     project_only_env_vars = True
        ... )
        True
        """

        output_folder = Path(output_folder) / project_id
        create_folder(output_folder)

        project_info = self.get_info(project_id)["project"]

        job_tech_dict = defaultdict(list)
        for category in self.get_jobs_technologies(project_id=project_id)["technologiesByCategory"]:
            for tech in category["technologies"]:
                catalog, techno = self.saagie_api.get_technology_name_by_id(tech["id"])
                if catalog != "" and techno != "" and techno not in job_tech_dict[catalog]:
                    job_tech_dict[catalog].append(techno)

        project_info["jobs_technologies"] = job_tech_dict or None

        app_tech_dict = defaultdict(list)
        for tech in self.get_apps_technologies(project_id=project_id)["appTechnologies"]:
            catalog, techno = self.saagie_api.get_technology_name_by_id(tech["id"])
            if catalog != "" and techno != "" and techno not in app_tech_dict[catalog]:
                app_tech_dict[catalog].append(techno)

        project_info["apps_technologies"] = app_tech_dict or None

        rights = [{right["name"]: right["role"].split("_")[-1]} for right in self.get_rights(project_id)["rights"]]

        project_info["rights"] = rights

        write_to_json_file(output_folder / "project.json", project_info)

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
            project_id=project_id,
            output_folder=output_folder / "env_vars",
            error_folder=error_folder,
            project_only=project_only_env_vars,
        )
        if not env_vars_export:
            env_var_failed.append(project_id)

        for id_job in id_jobs:
            job_export = self.saagie_api.jobs.export(
                job_id=id_job,
                output_folder=output_folder / "jobs",
                error_folder=error_folder,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )
            if not job_export:
                job_failed.append(id_job)

        for id_pipeline in id_pipelines:
            pipeline_export = self.saagie_api.pipelines.export(
                pipeline_id=id_pipeline,
                output_folder=output_folder / "pipelines",
                error_folder=error_folder,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )
            if not pipeline_export:
                pipeline_failed.append(id_pipeline)

        for id_app in id_apps:
            app_export = self.saagie_api.apps.export(
                app_id=id_app,
                output_folder=output_folder / "apps",
                error_folder=error_folder,
                versions_only_current=versions_only_current,
            )
            if not app_export:
                app_failed.append(id_app)

        if job_failed or pipeline_failed or app_failed or env_var_failed:
            logging.warning("❌ Project [%s] has not been successfully exported", project_id)
            return False

        logging.info("✅ Project [%s] successfully exported", project_id)
        return True

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

        Examples
        --------
        >>> saagieapi.projects.import_from_json(path_to_folder="./output/")
        True
        """

        try:
            path_to_folder = Path(path_to_folder)
            json_file = path_to_folder / "project.json"
            with json_file.open("r", encoding="utf-8") as file:
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

            # # Safety: wait for 5min max for project initialisation
            timeout = 400
            project_status = self.get_status_with_callback(project_id=new_project_id, freq=10, timeout=timeout)
            if project_status != "READY":
                raise TimeoutError(
                    f"Project creation is taking longer than usual, " f"Aborting project import after {timeout} seconds"
                )
        except Exception as exception:
            logging.warning("❌ Project [%s] has not been successfully imported", project_name)
            logging.error("Something went wrong %s", exception)
            return False

        status = True
        list_failed = {"jobs": [], "pipelines": [], "apps": [], "env_vars": []}

        for filename in (path_to_folder / "jobs").rglob("job.json"):
            job_status = self.saagie_api.jobs.import_from_json(
                project_id=new_project_id, path_to_folder=filename.parent
            )
            if not job_status:
                list_failed["jobs"].append(filename.parent.name)
                status = False

        # Import pipelines
        for filename in (path_to_folder / "pipelines").rglob("pipeline.json"):
            pipeline_status = self.saagie_api.pipelines.import_from_json(json_file=filename, project_id=new_project_id)
            if not pipeline_status:
                list_failed["pipelines"].append(filename.parent.name)
                status = False

        # Import apps
        for filename in (path_to_folder / "apps").rglob("app.json"):
            app_status = self.saagie_api.apps.import_from_json(json_file=filename, project_id=new_project_id)
            if not app_status:
                list_failed["apps"].append(filename.parent.name)
                status = False

        # Import env vars
        for filename in (path_to_folder / "env_vars").rglob("env_var.json"):
            env_var_status = self.saagie_api.env_vars.import_from_json(json_file=filename, project_id=new_project_id)
            if not env_var_status:
                list_failed["env_vars"].append(filename.parent.name)
                status = False

        if not status:
            logging.error("Something went wrong during project import %s", list_failed)
        return status

    def get_status_with_callback(self, project_id: str, freq: int = 10, timeout: int = -1):
        project_status = self.get_info(project_id=project_id)["project"]["status"]
        waiting_time = 0

        while project_status != "READY" and waiting_time <= timeout:
            time.sleep(freq)
            project_status = self.get_info(project_id)["project"]["status"]
            waiting_time += freq
        return project_status
