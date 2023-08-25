import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from gql import gql

from ..utils.folder_functions import create_folder, write_error, write_to_json_file
from .gql_queries import *

LIST_EXPOSED_PORT_FIELD = ["basePathVariableName", "isRewriteUrl", "scope", "number", "name"]
LIST_EXPOSED_PORT_MANDATORY = ["isRewriteUrl", "scope", "number"]


def handle_error(msg, exception):
    logging.warning(msg)
    logging.error("Something went wrong %s", exception)
    return False


class Apps:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_for_project(
        self,
        project_id: str,
        minimal: Optional[bool] = False,
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
        minimal : bool, optional
            Whether to only return the app's name and id, default to False
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
            "minimal": minimal,
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

        params = {
            "id": project_id,
            "minimal": True,
            "versionsOnlyCurrent": True,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_APPS_FOR_PROJECT), variable_values=params, pprint_result=False
        )

    def get_info(
        self,
        app_id: str,
        versions_only_current: bool = True,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get app with given UUID.

        Parameters
        ----------
        app_id : str
            UUID of your app
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
            "id": app_id,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_APP_INFO), variable_values=params, pprint_result=pprint_result
        )

    def create_from_scratch(
        self,
        project_id: str,
        app_name: str,
        image: str = "",
        description: str = "",
        exposed_ports: List[Dict] = None,
        storage_paths: List[Dict] = None,
        release_note: str = "",
        docker_credentials_id: str = None,
        emails: List = None,
        logins: List = None,
        status_list: List = None,
        resources: Dict = None,
        technology_id: str = None,
        technology_context: str = None,
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
            Incompatible with parameters technology_id & technology_context
            ex: hello-world:nanoserver-ltc2022
        docker_credentials_id: str
            Credentials's ID for the image if the image is not public
            Incompatible with parameters technology_id & technology_context
        exposed_ports: List[dict]
            List of dict of exposed ports
            Each dict should contains 'port' as key
            Ex: [{"basePathVariableName":"SAAGIE_BASE_PATH",
                "isRewriteUrl":True,
                "scope":"PROJECT",
                "number":5000,
                "name":"Test Port"}]
        storage_paths: List[Dict], optional
            List of dictionnaries indicating the volume path to the persistent storage
            and :
            - the id of the volume to be associated with the app.
                Ex: [{"path": "/home",
                    "volumeId": "cb70ad1d-7883-48ac-8740-2c8e5c5166ee"}]
            - or the information needed to created the volume
                Ex: [{"path": "/home",
                    "volume": {
                            "name":"storage name",
                            "size":"64 MB",
                            "description":"storage description"
                        }
                    }]
        release_note: str,
            Release note for the app version
        emails: List[String], optional
            Emails to receive alerts for the app, each item should be a valid email
        logins: List[String], optional
            Logins to receive alerts for the app, each item should be a valid login
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "STARTING","STARTED",
            "ROLLING_BACK","UPGRADING","RECOVERING","RESTARTING","STOPPING","STOPPED","FAILED"
        resources: Dict, optional
            Resources CPU, RAM & GPU limited and guaranteed for the app
        technology_id: str, optional
            Technology id of the app
            Incompatible with parameters image & docker_credentials_id
        technology_context: str, optional
            Context version of the app
            Incompatible with parameters image & docker_credentials_id
        Returns
        -------
        dict
            Dict of app information
        """
        if storage_paths is None:
            storage_paths = []
        if exposed_ports is None:
            exposed_ports = []

        for storage in (s for s in storage_paths if "volume" in storage):
            result = self.saagie_api.storages.create(
                project_id,
                storage["volume"]["name"],
                storage["volume"]["size"],
                storage["volume"]["description"],
            )["createVolume"]
            storage["volumeId"] = result["id"]
            del storage["volume"]

        params = {
            "projectId": project_id,
            "name": app_name,
            "description": description,
            "version": {
                "dockerInfo": {
                    "image": image,
                },
                "ports": exposed_ports,
                "releaseNote": release_note,
                "volumesWithPath": storage_paths,
            },
        }
        # in case of catalog app imported
        if technology_id:
            techno_id = technology_id
            del params["version"]["dockerInfo"]
            params["version"]["runtimeContextId"] = technology_context
        else:
            repos = self.saagie_api.get_repositories_info()["repositories"]
            # Find Saagie repository
            repos = next(repo for repo in repos if repo["name"] == "Saagie")["technologies"]
            # Find docker technology id
            techno_id = next(techno["id"] for techno in repos if techno["label"] == "Docker image")
        params["technologyId"] = techno_id

        check_format_exposed_port = self.check_exposed_ports(exposed_ports)

        if not check_format_exposed_port:
            raise ValueError(
                "❌ The parameter 'exposed_ports' should be a list of dict. Each dict should contains the key 'number'."
                f"All accept key of each dict is: '{LIST_EXPOSED_PORT_FIELD}'"
            )

        if docker_credentials_id:
            params["version"]["dockerInfo"]["dockerCredentialsId"] = docker_credentials_id

        if emails or logins or status_list:
            params["alerting"] = self.check_alerting({}, emails, logins, status_list)

        if resources:
            params["resources"] = resources

        # Add the app layer in params object
        params = {"app": params}

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_APP_SCRATCH), variable_values=params)
        logging.info("✅ App [%s] successfully created", app_name)
        return result

    def create_from_catalog(
        self,
        project_id: str,
        context: str,
        technology_id: str = None,
        technology_catalog: str = "Saagie",
        technology_name: str = None,
    ) -> Dict:
        """Create an app in a specific project.
        If technology_id is provided, the catalog and name will be ignored.
        Parameters
        ----------
        project_id : str
            ID of the project
        context: str
            Name of the context
        technology_id: str, optional
            ID of the app technology
        technology_catalog: str, optional
            Name of the technology catalog
        technology_name: str, optional
            Name of the app technology
        Returns
        -------
        dict
            Dict of app information
        """
        # Initialize parameters to request GQL Graph
        params = {"projectId": project_id}

        # If the user has set a technology_id, we don't look at the name
        if technology_id:
            params["technologyId"] = technology_id
        else:
            # Get all id technologies in our project
            techs_project = [
                tech["id"] for tech in self.saagie_api.projects.get_apps_technologies(project_id)["appTechnologies"]
            ]

            # Check if the technology exist
            technology_id = self.saagie_api.check_technology(
                params, technology_name, technology_catalog, techs_project
            )["technologyId"]

            # Check if technology is is available in our project
            techno_app = self.saagie_api.projects.get_apps_technologies(project_id=project_id)
            app_is_available = [app["id"] for app in techno_app["appTechnologies"] if app["id"] == technology_id]
            if not app_is_available:
                raise ValueError(
                    f"❌ App '{technology_name}' is not available in the project: '{project_id}'. "
                    "Check your project settings"
                )

        # Get different runtimes of app
        runtimes = self.saagie_api.get_runtimes(technology_id)["technology"]["appContexts"]
        # Check if runtime is available
        available_runtimes = [app for app in runtimes if app["available"] is True]
        context_app = [app for app in available_runtimes if app["label"] == context]

        if not context_app:
            available_contexts = [app["label"] for app in available_runtimes]
            raise ValueError(
                f"❌ Runtime '{context}' of the app '{technology_id}' doesn't exist or is not available in the project: "
                f"'{project_id}'. Available runtimes are: '{available_contexts}'"
            )

        params["contextId"] = context_app[0]["id"]

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_APP_CATALOG), variable_values=params)
        label = technology_name or technology_id
        logging.info("✅ App [%s] successfully created", label)
        return result

    def edit(
        self,
        app_id: str,
        app_name: str = None,
        description: str = None,
        emails: List = None,
        logins: List = None,
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
        logins: List[String], optional
            Logins to receive alerts for the app, each item should be a valid login,
            If you want to remove alerting, please set logins to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the app status change to a specific status.
            Each item of the list should be one of these following values: "STARTING","STARTED",
            "ROLLING_BACK","UPGRADING","RECOVERING","RESTARTING","STOPPING","STOPPED","FAILED"
        Returns
        -------
        dict
            Dict of app information
        """
        params = {
            "id": app_id,
        }

        if app_name:
            params["name"] = app_name

        if description:
            params["description"] = description

        params["alerting"] = self.get_info(app_id)["app"]["alerting"]
        if emails or logins or status_list:
            params["alerting"] = self.check_alerting({}, emails, logins, status_list)

        params = {"app": params}
        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_APP), variable_values=params)
        logging.info("✅ App [%s] successfully edited", app_id)
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
        result = self.saagie_api.client.execute(query=gql(GQL_RUN_APP), variable_values={"id": app_id})
        logging.info("✅ App [%s] successfully started", app_id)
        return result

    def stop(self, app_id: str) -> Dict:
        """Stop a given job instance

        Parameters
        ----------
        app_id : str
            UUID of your app

        Returns
        -------
        dict
            app instance information
        """
        result = self.saagie_api.client.execute(query=gql(GQL_STOP_APP), variable_values={"id": app_id})
        logging.info("✅ App [%s] successfully stopped", app_id)
        return result

    @staticmethod
    def check_exposed_ports(exposed_ports: List[Dict]):
        """
        Check if exposed ports are valid
        Parameters
        ----------
        exposed_ports: List[Dict]
            List of exposed ports, each item of the list should be a dict and each dict must have
            'number' (int), 'scope' ('GLOBAL' or 'PROJECT'), and 'isRewriteUrl' (Boolean) as key,
            and only contain valid keys
        Returns
        -------
        bool
            True if all exposed port are in a valid format
            False otherwise
        """

        return bool(
            isinstance(exposed_ports, List)  # Exposed_ports is a list
            and exposed_ports  # Exposed_ports is not empty
            and all(isinstance(ep, Dict) for ep in exposed_ports)  # Exposed_ports is a list of dict
            # Mandatory keys are present in each dict
            and all((LIST_EXPOSED_PORT_MANDATORY - ep.keys()) == set() for ep in exposed_ports)
            # All keys are valid
            and all(set(ep.keys()).issubset(LIST_EXPOSED_PORT_FIELD) for ep in exposed_ports)
        )

    @staticmethod
    def check_alerting(
        alerting: Dict = None, emails: List = None, logins: List = None, status_list: List = None
    ) -> Dict:
        """
        Check if the alerting is enabled for the given app and if so, check alerting and status_list.
        If any parameter is missing, it will be set to the current value.
        Parameters
        ----------
        alerting : dict, optional
            dict containing the alerting informations
        emails : list, optional
            List of emails to send the alert
        logins : list, optional
            List of logins to send the alert
        status_list : list, optional
            Status list of the alert

        Returns
        -------
        dict
            Dict containing alert config

        Raises
        ------
        RunTimeError
            When the statut list is not valid
        """

        valid_status_list = [
            "STARTING",
            "STARTED",
            "ROLLING_BACK",
            "UPGRADING",
            "RECOVERING",
            "RESTARTING",
            "STOPPING",
            "STOPPED",
            "FAILED",
        ]

        if alerting is None:
            alerting = {}

        if "loginEmails" in alerting:
            del alerting["loginEmails"]

        if status_list:
            wrong_status_list = [item for item in status_list if item not in valid_status_list]
            alerting["statusList"] = status_list

            if wrong_status_list:
                raise RuntimeError(
                    f"❌ The following status are not valid: {wrong_status_list}. "
                    f"Please make sure that each item of the parameter status_list should be "
                    f"one of the following values: {valid_status_list}"
                )

        if emails:
            alerting["emails"] = emails

        if "emails" in alerting:
            alerting["emails"] = [item for item in alerting["emails"] if item]

        if logins:
            alerting["logins"] = logins

        # If alerting object doesn't contain both a status list and either an email or a login,
        # raise an error
        if "statusList" not in alerting or ("emails" not in alerting and "logins" not in alerting):
            raise RuntimeError("❌ You must provide a status list and either an email or a login to enable the alerting")

        return alerting

    def get_runtime_label_by_id(self, technology_id: str, runtime_id: str) -> str:
        """Get the label of runtime

        Parameters
        ----------
        technology_id : str
            UUID of the technology
        runtime_id : str
            UUID of the runtime

        Returns
        -------
        str
            String of runtime label

        """
        # Get all runtimes of the technology
        runtimes = self.saagie_api.get_runtimes(technology_id)["technology"]
        if not runtimes:  # If the technology doesn't exist, return an empty string
            logging.warning("❌ Technology [%s] not found", technology_id)
            return ""

        # Get the label of the runtime
        runtime_label = next(
            (runtime["label"] for runtime in runtimes.get("appContexts", {}) if runtime.get("id") == runtime_id), ""
        )

        # If the runtime was not found, return an empty string
        if not runtime_label:
            logging.warning("❌ Runtime [%s] not found in technology [%s]", runtime_id, technology_id)
            return ""

        return runtime_label

    def upgrade(
        self,
        app_id: str,
        release_note: str = "",
        exposed_ports: List[Dict] = None,
        storage_paths: List[Dict] = None,
        technology_context: str = None,
        image: str = None,
        docker_credentials_id: str = None,
    ) -> Dict:
        """Update the app

        Parameters
        ----------
        app_id : str
            App ID
        release_note : str, optional
            Release note for the app version
        exposed_ports: List[dict], optional
            List of dict of exposed ports
            If not filled, it takes exposed_ports of previous version
            Each dict should contains 'port' as key
            Ex: [{"basePathVariableName":"SAAGIE_BASE_PATH",
                "isRewriteUrl":True,
                "scope":"PROJECT",
                "number":5000,
                "name":"Test Port"}]
        storage_paths: List[Dict], optional
            List of dict indicating the volume path to the persistent storage
            and :
            - the id of the volume to be associated with the app.
                Ex: [{"path": "/home",
                    "volumeId": "cb70ad1d-7883-48ac-8740-2c8e5c5166ee"}]
        technology_context: str, optional
            Context version of the app
            Incompatible with parameters image & docker_credentials_id
            If not filled, it takes technology_context of previous version
        image: str, optional
            tag of the Docker Image
            Incompatible with parameter technology_context
            If not filled, it takes image of previous version
            ex: hello-world:nanoserver-ltc2022
        docker_credentials_id: str, optional
            Credentials's ID for the image if the image is not public
            Incompatible with parameter technology_context
        Returns
        -------
        dict
            Dict of app version information
        """

        if technology_context is not None and (image is not None or docker_credentials_id is not None):
            raise ValueError(
                "❌ Incompatible parameters set up."
                "'technology_context' can't be associated to 'image' and/or 'docker_credentials_id'"
            )

        app_info = self.get_info(app_id)["app"]["currentVersion"]
        exposed_ports = None

        if exposed_ports is None:
            exposed_ports = [port for port in app_info["ports"] if "internalUrl" not in port]

        params = {
            "appId": app_id,
            "appVersion": {
                "ports": exposed_ports,
                "releaseNote": release_note,
                "volumesWithPath": storage_paths,
                "dockerInfo": {},
            },
        }

        if technology_context is image is None:
            technology_context = app_info["runtimeContextId"]
            if app_info["dockerInfo"] is not None and "image" in app_info["dockerInfo"]:
                image = app_info["dockerInfo"]["image"]

        if image:
            params["appVersion"]["dockerInfo"]["image"] = image

        if docker_credentials_id:
            params["appVersion"]["dockerInfo"]["dockerCredentialsId"] = docker_credentials_id

        # in case of catalog app updated
        if technology_context and "dockerInfo" in params["appVersion"]:
            params["appVersion"]["runtimeContextId"] = technology_context
            params["appVersion"].pop("dockerInfo", None)

        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_APP), variable_values=params)
        logging.info("✅ App [%s] successfully updated", app_id)

        return result

    def rollback(self, app_id: str, version_number: str):
        """Rollback a given app to the given version

        Parameters
        ----------
        app_id : str
            UUID of your app (see README on how to find it)
        version_number : str
            Number of the version to rollback

        Returns
        -------
        dict
            Dict of rollback app

        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_ROLLBACK_APP_VERSION), variable_values={"appId": app_id, "versionNumber": version_number}
        )
        logging.info("✅ App [%s] successfully rollbacked to version [%s]", app_id, version_number)
        return result

    def export(
        self,
        app_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
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
        versions_only_current : bool, optional
            Whether to only fetch the current version of each app
        Returns
        -------
        bool
            True if app is exported False otherwise
        """
        app_info = None
        output_folder = Path(output_folder)

        try:
            app_info = self.get_info(app_id=app_id, versions_only_current=versions_only_current)["app"]
            app_techno_id = app_info["technology"]["id"]
            repo_name, techno_name = self.saagie_api.get_technology_name_by_id(app_techno_id)
            app_info["technology"].update({"name": techno_name, "technology_catalog": repo_name})

            if not versions_only_current:
                for version in app_info["versions"]:
                    version["runtimeContextLabel"] = self.get_runtime_label_by_id(
                        app_techno_id, version["runtimeContextId"]
                    )
            app_info["currentVersion"]["runtimeContextLabel"] = self.get_runtime_label_by_id(
                app_techno_id, app_info["currentVersion"]["runtimeContextId"]
            )
            create_folder(output_folder / app_id)

        except Exception as exception:
            logging.warning("Cannot get the information of the app [%s]", app_id)
            logging.error("Something went wrong %s", exception)
            logging.warning("❌ App [%s] has not been successfully exported", app_id)
            write_error(error_folder, "apps", app_id)
            return False

        write_to_json_file(output_folder / app_id / "app.json", app_info)
        logging.info("✅ App [%s] successfully exported", app_id)

        return True

    def import_from_json(
        self,
        json_file: str,
        project_id: str,
    ) -> bool:
        """Import an app from JSON format

        Parameters
        ----------
        json_file : str
            Path to the JSON file that contains app information
        project_id : str
            Project ID to import the app
        Returns
        -------
        bool
            True if app is imported False otherwise
        """
        json_file = Path(json_file)
        try:
            with json_file.open("r", encoding="utf-8") as file:
                app_info = json.load(file)
        except Exception as exception:
            return handle_error(f"Cannot open the JSON file {json_file}", exception)

        try:
            app_technology_name = app_info["technology"]["name"]
            app_technology_catalog = app_info["technology"]["technology_catalog"]
            app_runtime_context = app_info["currentVersion"].get("runtimeContextLabel")

            # Remove internalUrl from ports
            app_ports = [
                {k: v for k, v in elem.items() if k != "internalUrl"} for elem in app_info["currentVersion"]["ports"]
            ]

            params = {"projectId": project_id}
            technology_id = context_app_info = None

            if app_runtime_context and app_info["currentVersion"]["runtimeContextId"]:
                techs_project = self.saagie_api.projects.get_apps_technologies(project_id)["appTechnologies"]
                params = self.saagie_api.check_technology(
                    params, app_technology_name, app_technology_catalog, [tech["id"] for tech in techs_project]
                )
                technology_id = params["technologyId"]

                techno_app = self.saagie_api.projects.get_apps_technologies(project_id=project_id)
                if all(app["id"] != technology_id for app in techno_app["appTechnologies"]):
                    raise ValueError(
                        f"❌ App '{app_technology_name}' is not available in the project: '{project_id}'. "
                        "Check your project settings"
                    )

                runtimes = self.saagie_api.get_runtimes(technology_id)["technology"]["appContexts"]
                available_runtimes = [app for app in runtimes if app["available"]]
                context_app = next((app for app in available_runtimes if app["label"] == app_runtime_context), None)

                if not context_app:
                    available_contexts = [app["label"] for app in available_runtimes]
                    raise ValueError(
                        f"❌ Runtime '{app_runtime_context}' of the app '{technology_id}' doesn't exist "
                        f"or is not available in the project: '{project_id}'."
                        f"Available runtimes are: '{available_contexts}'"
                    )
                context_app_info = context_app["id"]

            app_name = app_info["name"]

            self.create_from_scratch(
                project_id=project_id,
                app_name=app_name,
                image=app_info["currentVersion"]["dockerInfo"].get("image", ""),
                description=app_info["description"],
                exposed_ports=app_ports,
                storage_paths=app_info["currentVersion"]["volumesWithPath"],
                release_note=app_info["currentVersion"]["releaseNote"],
                docker_credentials_id=app_info["currentVersion"]["dockerInfo"]["dockerCredentialsId"] or None,
                emails=app_info["alerting"]["emails"] or "",
                status_list=app_info["alerting"]["statusList"] or "",
                resources=app_info["resources"],
                technology_id=technology_id,
                technology_context=context_app_info,
            )
            logging.info("✅ App [%s] successfully imported", app_name)
        except Exception as exception:
            return handle_error(f"❌ App [{app_name}] has not been successfully imported", exception)

        return True

    def get_id(self, app_name: str, project_name: str) -> str:
        """Get the app id with the app name and project name
        Parameters
        ----------
        app_name : str
            Name of your app
        project_name : str
            Name of your project
        Returns
        -------
        str
            App UUID
        """
        project_id = self.saagie_api.projects.get_id(project_name)
        apps = self.saagie_api.apps.list_for_project_minimal(project_id)["project"]["apps"]
        if app := next((app for app in apps if app["name"] == app_name), None):
            return app["id"]
        raise NameError(f"❌ App {app_name} does not exist.")

    def get_stats(self, history_id, version_number, start_time):
        """Get stats of the app

        Parameters
        ----------
        history_id : str
            UUID of your app history
        version_number : str
            Number of the version to get the stats
        start_time : str
            Date since to get the stats (format : "%Y-%m-%dT%H:%M:%S.%fZ")

        Returns
        -------
        dict
            Dict of app's stats
        """
        params = {
            "appHistoryId": history_id,
            "versionNumber": version_number,
            "startTime": start_time,
        }

        return self.saagie_api.client.execute(query=gql(GQL_STATS_APP), variable_values=params)

    def get_history_statuses(self, history_id, version_number, start_time):
        """Get statuses history of the app

        Parameters
        ----------
        history_id : str
            UUID of your app history
        version_number : str
            Number of the version to get the statuses history
        start_time : str
            Date since to get the statuses history (format : "%Y-%m-%dT%H:%M:%S.%fZ")

        Returns
        -------
        dict
            Dict of app's statuses history
        """
        params = {
            "appHistoryId": history_id,
            "versionNumber": version_number,
            "startTime": start_time,
        }

        return self.saagie_api.client.execute(query=gql(GQL_HISTORY_APP_STATUS), variable_values=params)

    def count_history_statuses(self, history_id, version_number, start_time):
        """Get count of statues history of the app

        Parameters
        ----------
        history_id : str
            UUID of your app history
        version_number : str
            Number of the version to get the count of statuses history
        start_time : str
            Date since to get the count of statuses history (format : "%Y-%m-%dT%H:%M:%S.%fZ")

        Returns
        -------
        dict
            count of statuses history
        """
        params = {
            "appHistoryId": history_id,
            "versionNumber": version_number,
            "startTime": start_time,
        }

        return self.saagie_api.client.execute(query=gql(GQL_COUNT_HISTORY_APP_STATUS), variable_values=params)
