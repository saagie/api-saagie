from gql import gql

from .gql_queries import *


class Apps:

    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client
        self.valid_status_list = saagie_api.valid_status_list
        self.list_exposed_ports_field = ["basePathVariableName", "isRewriteUrl",
                                         "isAuthenticationRequired", "port", "name"]

    def list_for_project(self, project_id):
        """List apps of project.
        NB: You can only list apps if you have at least the viewer role on
        the project.
        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        Returns
        -------
        dict
            Dict of app information
        """
        query = gql(gql_get_project_apps)
        return self.client.execute(query, variable_values={"id": project_id})

    def get_info(self, app_id):
        """Get app with given UUID.
        Parameters
        ----------
        app_id : str
            UUID of your app
        Returns
        -------
        dict
            Dict of app information
        """
        query = gql(gql_get_project_app)
        return self.client.execute(query, variable_values={"id": app_id})

    def create(self, project_id, app_name, image, description='', technology_catalog='Saagie',
               technology="Docker image", docker_credentials_id=None, exposed_ports=[], storage_paths=[],
               storage_size_in_mb=128, release_note='', emails=None, status_list=["FAILED"]):
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
            tag of the image
            ex: hello-world:nanoserver-ltsc2022
        technology_catalog: str
            Name of the technology catalog
        technology: str
            Name of the technology
            If you are creating a custom app, do not update this value
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
        check_fomat_exposed_port = self.__check_exposed_ports(exposed_ports, self.list_exposed_ports_field)
        if not check_fomat_exposed_port:
            raise ValueError(
                f"The parameter 'exposed_ports' should be a list of dict. Each dict should contains the key 'port'."
                "All accept key of each dict is: '{list_exposed_port_field}'")

        all_technologies_in_catalog = [
            catalog['technologies'] for catalog in self.saagie_api.get_repositories_info()['repositories']
            if catalog['name'] == technology_catalog
        ]
        if not all_technologies_in_catalog:
            raise RuntimeError(
                f"Catalog {technology_catalog} does not exist or does not contain technologies")
        technology_in_catalog = [tech['id'] for tech in
                                 all_technologies_in_catalog[0]
                                 if
                                 tech["label"].lower() == technology.lower() and tech["__typename"] == "AppTechnology"]

        if not technology_in_catalog:
            raise RuntimeError(
                f"Technology {technology} does not exist in the catalog {technology_catalog}")
        technology_id = technology_in_catalog[0]
        params["technologyId"] = technology_id

        if docker_credentials_id:
            params["dockerCredentialsId"] = docker_credentials_id

        if emails:
            wrong_status_list = []

            for item in status_list:
                if item not in self.valid_status_list:
                    wrong_status_list.append(item)
            if wrong_status_list:
                raise RuntimeError(f"The following status are not valid: {wrong_status_list}. "
                                   f"Please make sure that each item of the parameter status_list should be "
                                   f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                                   f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'")

            else:
                params["alerting"] = {
                    "emails": emails,
                    "statusList": status_list
                }
        query = gql(gql_create_app)
        return self.client.execute(query, variable_values=params)

    def edit(self, app_id, app_name=None, description=None, emails=None, status_list=["FAILED"]):
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
        previous_app_version = self.get_project_app(app_id)["labWebApp"]

        if app_name:
            params["name"] = app_name
        else:
            params["name"] = previous_app_version["name"]

        if description:
            params["description"] = description
        else:
            params["description"] = previous_app_version["description"]

        if emails:
            wrong_status_list = []

            for item in status_list:
                if item not in self.valid_status_list:
                    wrong_status_list.append(item)
            if wrong_status_list:
                raise RuntimeError(f"The following status are not valid: {wrong_status_list}. "
                                   f"Please make sure that each item of the parameter status_list should be "
                                   f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                                   f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'")

            else:
                params["alerting"] = {
                    "emails": emails,
                    "statusList": status_list
                }
        elif type(emails) == list:
            params["alerting"] = None
        else:
            previous_alerting = previous_app_version["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_alerting["emails"],
                    "statusList": previous_alerting["statusList"]
                }

        query = gql(gql_edit_app)
        return self.client.execute(query, variable_values=params)

    @staticmethod
    def __check_exposed_ports(exposed_ports, list_exposed_port_field):
        """
        Check
        Parameters
        ----------
        exposed_ports : list
            List of exposed ports, each item of the list should be a dict
            and each dict should have 'port' as key
        list_exposed_port_field : list
            List of valid field of each exposed port
        Returns
        -------
        bool
            True if all exposed port is in the validate format
            Otherwise False
        """
        if type(exposed_ports) != list:
            return False
        else:
            if len(exposed_ports):
                check_type = all([type(ep) == dict for ep in exposed_ports])
                if check_type:
                    check_port = all(["port" in ep.keys() for ep in exposed_ports])
                    if check_port:
                        check_every_key = all(
                            [all(elem in list_exposed_port_field for elem in ep.keys()) for ep in exposed_ports])
                        if check_every_key:
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return True
