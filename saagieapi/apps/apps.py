import logging
from typing import Dict, List, Optional

from gql import gql

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file
from .gql_queries import *

LIST_EXPOSED_PORT_FIELD = ["basePathVariableName", "isRewriteUrl", "isAuthenticationRequired", "port", "name"]


class Apps:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_for_project(
        self,
        project_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """List apps of project.
        NB: You can only list apps if you have at least the viewer role on
        the project.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit: int, optional
            limit the number of instances to return, default to no limit
        versions_limit : int, optional
            Maximum limit of versions to fetch per app. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each app
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of app information
        """
        params = {
            "id": project_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_APPS_FOR_PROJECT), variable_values=params, pprint_result=pprint_result
        )

    def list_for_project_minimal(self, project_id: str) -> Dict:
        """List only app names and ids in the given project .
        NB: You can only list apps if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of apps ids and names
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_APPS_FOR_PROJECT_MINIMAL), variable_values={"projectId": project_id}
        )

    def get_info(
        self,
        app_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get app with given UUID.

        Parameters
        ----------
        app_id : str
            UUID of your app
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global
        instances_limit: int, optional
            limit the number of instances to return, default to no limit
        versions_limit : int, optional
            Maximum limit of versions to fetch per app. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each app

        Returns
        -------
        dict
            Dict of app information
        """
        params = {
            "id": app_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_APP_INFO), variable_values=params, pprint_result=pprint_result
        )

    def create_from_scratch(
        self,
        project_id: str,
        app_name: str,
        image: str,
        description: str = "",
        exposed_ports: List[Dict] = None,
        storage_paths: List = None,
        storage_size_in_mb: int = 128,
        release_note: str = "",
        docker_credentials_id: str = None,
        emails: List = None,
        status_list: List = None,
    ) -> Dict:
        """Create an app in a specific project
        Parameters
        ----------
        project_id : str
            ID of the project
        app_name: str
            Name of the app
        description: str
            Description of the app
        image: str
            tag of the Docker Image
            ex: hello-world:nanoserver-ltc2022
        docker_credentials_id: str
            Credentials's ID for the image if the image is not public
        exposed_ports: List[dict]
            List of dict of exposed ports
            Each dict should contains 'port' as key
            Ex: [{"basePathVariableName":"SAAGIE_BASE_PATH",
                "isRewriteUrl":True,
                "isAuthenticationRequired":True,
                "port":5000,
                "name":"Test Port"}]
        storage_paths: List[String], optional
            List of strings indicating the volume path to the persistent storage
        storage_size_in_mb: int, optional
            Storage size in mb for the volume path
        release_note: str,
            Release note for the app version
        emails: List[String], optional
            Emails to receive alerts for the app, each item should be a valid email
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        Returns
        -------
        dict
            Dict of app information
        """
        if storage_paths is None:
            storage_paths = []
        if exposed_ports is None:
            exposed_ports = []

        params = {
            "projectId": project_id,
            "name": app_name,
            "description": description,
            "releaseNote": release_note,
            "storageSizeInMB": storage_size_in_mb,
            "image": image,
            "exposedPorts": exposed_ports,
            "storagePaths": storage_paths,
        }

        check_format_exposed_port = self.check_exposed_ports(exposed_ports)
        if not check_format_exposed_port:
            raise ValueError(
                "❌ The parameter 'exposed_ports' should be a list of dict. Each dict should contains the key 'port'."
                f"All accept key of each dict is: '{LIST_EXPOSED_PORT_FIELD}'"
            )

        technology = "Docker image"
        technology_catalog = "Saagie"
        technologies_for_project = self.saagie_api.projects.get_apps_technologies(project_id)["appTechnologies"]
        technologies_for_project = [tech["id"] for tech in technologies_for_project]
        # For apps, docker technology is always available
        repositories = self.saagie_api.get_repositories_info()["repositories"]
        # Filter saagie repo
        saagie_repo = [repo for repo in repositories if repo["name"] == technology_catalog][0]["technologies"]
        # Get id of docker technology
        docker_id = [repo["id"] for repo in saagie_repo if repo["label"] == technology][0]
        # Add docker technology to the list of technologies for the project
        technologies_for_project.append(docker_id)
        params = self.saagie_api.check_technology(params, technology, technology_catalog, technologies_for_project)

        if docker_credentials_id:
            params["dockerCredentialsId"] = docker_credentials_id

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)
        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_APP), variable_values=params)
        logging.info("✅ App [%s] successfully created", app_name)
        return result

    def create_from_catalog(
        self,
        project_id: str,
        app_name: str,
        technology: str,
        context: str,
        technology_catalog: str = "Saagie",
        description: str = "",
        storage_size_in_mb: int = 128,
        release_note: str = "",
        emails: List = None,
        status_list: List = None,
    ) -> Dict:
        """Create an app in a specific project
        Parameters
        ----------
        project_id : str
            ID of the project
        app_name: str
            Name of the app
        technology: str
            Label of the technology
        context: str
            The runtimes context to use for the chosen technology
        technology_catalog: str
            Name of the technology catalog
        description: str
            Description of the app
        storage_size_in_mb: int, optional
            Storage size in mb for the volume path
        release_note: str,
            Release note for the app version
        emails: List[String], optional
            Emails to receive alerts for the app, each item should be a valid email
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        Returns
        -------
        dict
            Dict of app information
        """
        # Initialize parameters to request GQL Graph
        params = {
            "projectId": project_id,
            "name": app_name,
            "description": description,
            "releaseNote": release_note,
            "storageSizeInMB": storage_size_in_mb,
        }

        # Get all id technologies in our project
        technologies_for_project = self.saagie_api.projects.get_apps_technologies(project_id)["appTechnologies"]
        technologies_for_project = [tech["id"] for tech in technologies_for_project]

        # Check if the technology exist
        params = self.saagie_api.check_technology(params, technology, technology_catalog, technologies_for_project)
        app_id = params["technologyId"]

        # Check if app_is is available in our project
        techno_app = self.saagie_api.projects.get_apps_technologies(project_id=project_id)
        app_is_available = [app["id"] for app in techno_app["appTechnologies"] if app["id"] == app_id]
        if not app_is_available:
            raise ValueError(
                f"❌ App '{technology}' is not available in the project: '{project_id}'. Check your project settings"
            )

        # Get different runtimes of app
        runtimes = self.saagie_api.get_runtimes(app_id)["technology"]["appContexts"]
        # Check if runtime is available
        available_runtimes = [app for app in runtimes if app["available"] is True]
        context_app = [app for app in available_runtimes if app["label"] == context]

        if not context_app:
            available_contexts = [app["label"] for app in available_runtimes]
            raise ValueError(
                f"❌ Runtime '{context}' of the app '{technology}' doesn't exist or is not available in the project: "
                f"'{project_id}'. Available runtimes are: '{available_contexts}'"
            )
        context_app_info = context_app[0]

        exposed_ports = context_app_info["ports"]
        # change key names in the list of dict exposed_ports
        exposed_ports = [
            {
                "basePathVariableName": port["basePath"],
                "isRewriteUrl": port["rewriteUrl"],
                "isAuthenticationRequired": True,
                "port": port["port"],
                "name": port["name"],
            }
            if port["scope"] == "PROJECT"
            else {
                "basePathVariableName": port["basePath"],
                "isRewriteUrl": port["rewriteUrl"],
                "isAuthenticationRequired": False,
                "port": port["port"],
                "name": port["name"],
            }
            for port in exposed_ports
        ]

        # Get image_name with concatenated image name with tag (version)
        image_app = f"{context_app_info['dockerInfo']['image']}:{context_app_info['dockerInfo']['version']}"

        check_format_exposed_port = self.check_exposed_ports(exposed_ports)
        if not check_format_exposed_port:
            raise ValueError(
                "❌ The parameter 'exposed_ports' should be a list of dict. Each dict should contains the key 'port'."
                f"All accept key of each dict is: '{LIST_EXPOSED_PORT_FIELD}'"
            )

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)

        # Add collected information (Docker image, ports exposed, path for the storage) to the list of parameters
        params.update({"image": image_app, "exposedPorts": exposed_ports, "storagePaths": context_app_info["volumes"]})

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_APP), variable_values=params)
        logging.info("✅ App [%s] successfully created", app_name)
        return result

    def edit(
        self,
        app_id: str,
        app_name: str = None,
        description: str = None,
        emails: List = None,
        status_list: List = None,
    ) -> Dict:
        """Edit an app
        Each optional parameter can be set to change the value of the corresponding field.
        Parameters
        ----------
        app_id : str
            UUID of your app
        app_name : str, optional
            App name
            If not filled, defaults to current value, else it will change the app's name
        description : str, optional
            Description of app
            if not filled, defaults to current value, else it will change the description of the app
        emails: List[String], optional
            Emails to receive alerts for the app, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the app status change to a specific status.
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
            You cannot change only the status_lit, you must set both emails and status_list.
        Returns
        -------
        dict
            Dict of app information
        """
        params = {"id": app_id}
        previous_app_version = self.get_info(
            app_id, instances_limit=1, versions_limit=1, versions_only_current=True, pprint_result=False
        )["labWebApp"]

        if app_name:
            params["name"] = app_name
        else:
            params["name"] = previous_app_version["name"]

        if description:
            params["description"] = description
        else:
            params["description"] = previous_app_version["description"]

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)
        elif isinstance(emails, List):
            params["alerting"] = None
        else:
            previous_alerting = previous_app_version["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_alerting["emails"],
                    "statusList": previous_alerting["statusList"],
                }

        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_APP), variable_values=params)
        logging.info("✅ App [%s] successfully edited", app_name)
        return result

    def delete(self, app_id: str) -> Dict:
        """Delete a given app

        Parameters
        ----------
        app_id : str
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted app

        """
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_APP), variable_values={"appId": app_id})
        logging.info("✅ App [%s] successfully deleted", app_id)
        return result

    def run(self, app_id: str) -> Dict:
        """Run a given app

        Parameters
        ----------
        app_id : str
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of the given app information
        """
        result = self.saagie_api.client.execute(query=gql(GQL_RUN_APP), variable_values={"appId": app_id})
        logging.info("✅ App [%s] successfully started", app_id)
        return result

    def stop(self, app_instance_id: str) -> Dict:
        """Stop a given job instance

        Parameters
        ----------
        app_instance_id : str
            UUID of your application instance (see README on how to find it)

        Returns
        -------
        dict
            app instance information
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_STOP_APP_INSTANCE), variable_values={"appInstanceId": app_instance_id}
        )
        logging.info("✅ App instance [%s] successfully stopped", app_instance_id)
        return result

    @staticmethod
    def check_exposed_ports(exposed_ports: List):
        """
        Check
        Parameters
        ----------
        exposed_ports : list
            List of exposed ports, each item of the list should be a dict
            and each dict should have 'port' as key
        Returns
        -------
        bool
            True if all exposed port is in the validate format
            Otherwise False
        """

        if not isinstance(exposed_ports, List):
            return False

        if len(exposed_ports):
            check_type = all(isinstance(ep, Dict) for ep in exposed_ports)
            if check_type:
                check_port = all("port" in ep.keys() for ep in exposed_ports)
                if check_port:
                    check_every_key = all(
                        all(elem in LIST_EXPOSED_PORT_FIELD for elem in ep.keys()) for ep in exposed_ports
                    )
                    if check_every_key:
                        return True
                    return False
                return False
            return False
        return True

    def export(
        self,
        app_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
    ) -> bool:
        """Export the app in a folder

        Parameters
        ----------
        app_id : str
            App ID
        output_folder : str
            Path to store the exported app
        error_folder : str
            Path to store the error
        error_folder : str, optional
            Path to store the app ID in case of error. If not set, app ID is not write
        versions_limit : int, optional
            Maximum limit of versions to fetch per app. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each app
        Returns
        -------
        bool
            True if app is exported False otherwise
        """
        result = True
        output_folder = check_folder_path(output_folder)
        app_info = None

        try:
            app_info = self.get_info(
                app_id, instances_limit=1, versions_limit=versions_limit, versions_only_current=versions_only_current
            )["labWebApp"]
            create_folder(output_folder + app_id)
        except Exception as e:
            logging.warning("Cannot get the information of the app [%s]", app_id)
            logging.error("Something went wrong %s", e)

        if app_info:
            write_to_json_file(output_folder + app_id + "/app.json", app_info)
            logging.info("✅ App [%s] successfully exported", app_id)
        else:
            logging.warning("❌ App [%s] has not been successfully exported", app_id)
            write_error(error_folder, "apps", app_id)
            result = False
        return result
