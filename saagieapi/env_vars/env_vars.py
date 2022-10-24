import json
import logging
from typing import Dict, Optional

from gql import gql

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file
from .gql_queries import *


class EnvVars:
    # pylint: disable=singleton-comparison
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_globals(self, pprint_result: Optional[bool] = None):
        """Get global environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the platform
        Params
        ------
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global
        Returns
        -------
        dict
            Dict of global environment variable on the platform
        """
        return self.saagie_api.client.execute(query=gql(GQL_LIST_GLOBAL_ENV_VARS), pprint_result=pprint_result)

    def create_global(self, name: str, value: str, description: str = "", is_password: bool = False) -> Dict:
        """Create a global environment variable

        Parameters
        ----------
        name : str
            Name of the environment variable to create
        value : str
            Value of the environment variable to create
        description : str, optional
            Description of the environment variable to create
        is_password : bool, optional
            Weather the environment variable to create is a password or not

        Returns
        -------
        dict
            Dict of created environment variable
        """
        params = {
            "name": name,
            "value": value,
            "description": description,
            "isPassword": is_password,
            "scope": "GLOBAL",
        }

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully created", name)
        return result

    def update_global(
        self, name: str, new_name: str = None, value: str = None, description: str = None, is_password: bool = None
    ) -> Dict:
        """
        Update environment variable with provided function variables if it exists
        Parameters
        ----------
        name : str
            Name of the environment to upgrade
        new_name : str, optional
            New name of the environment variable. If none provided, keep the actual one
        value: str, optional
            New value of the environment variable. If none provided, keep the actual one
        description: str, optional
            New description of the environment variable. If none provided, keep the actual one
        is_password: boolean, optional
            New password boolean status. If none provided, keep the actual one

        Returns
        -------
        dict
            Dict containing the id of the updated environment variable

        Raises
        ------
        ValueError
            When the variable doesn't already exist
        """

        existing_env_var = self.list_globals(pprint_result=False)["globalEnvironmentVariables"]

        if name not in [env_var["name"] for env_var in existing_env_var]:
            raise ValueError(f"❌ Environment variable {name} does not exists")

        params = [d for d in existing_env_var if d["name"] == name][0]

        if params["isPassword"] == True:
            params.pop("value")
        if new_name:
            params["name"] = new_name
        if value:
            params["value"] = value
        if description:
            params["description"] = description
        if is_password == True:
            params["isPassword"] = is_password
        elif is_password == False:
            params["isPassword"] = is_password

        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully updated", name)
        return result

    def create_or_update_global(self, name: str, value: str, description: str = "", is_password: bool = False) -> Dict:
        """
        Create a new global environnement variable or update it if it already exists

        Parameters
        ----------
        name: str
            Unique name of the environnement variable to create or modify
        value: str
            Value of the environnement variable to create or modify
        description: str, optional
            Description of the variable
        is_password: boolean, optional
            Weather the variable is a password or not (default: False)

        Returns
        -------
        dict
            Dict of created or updated environment variable
        """

        existing_env_var = self.list_globals(pprint_result=False)["globalEnvironmentVariables"]
        present = name in [env["name"] for env in existing_env_var]

        # If variable not present, create it
        if not present:
            return self.create_global(name=name, value=value, description=description, is_password=is_password)

        return self.update_global(
            name=name, new_name=None, value=value, description=description, is_password=is_password
        )

    def delete_global(self, name: str) -> Dict:
        """Delete the given global environment variable

        Parameters
        ----------
        name : str
            Name of the environment variable to delete

        Returns
        -------
        dict
            Dict of deleted environment variable

        Raises
        ------
        ValueError
            When the given name doesn't correspond to an existing environment
            variable
        """
        global_envs = self.list_globals(pprint_result=False)["globalEnvironmentVariables"]
        global_env = [env for env in global_envs if env["name"] == name]

        if len(global_env) == 0:
            raise ValueError("❌ 'name' must be the name of an existing global " "environment variable")

        global_env_id = global_env[0]["id"]

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_ENV_VAR), variable_values={"id": global_env_id})
        logging.info("✅ Environment variable [%s] successfully deleted", name)
        return result

    def list_for_project(self, project_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """Get project environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the project

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
            Dict of project environment variables
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_PROJECT_ENV_VARS), variable_values={"projectId": project_id}, pprint_result=pprint_result
        )

    def create_for_project(
        self, project_id: str, name: str, value: str, description: str = "", is_password: bool = False
    ) -> Dict:
        """Create an environment variable in a given project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        name : str
            Name of the environment variable to create
        value : str
            Value of the environment variable to create
        description : str, optional
            Description of the environment variable to create
        is_password : bool, optional
            Weather the environment variable to create is a password or not

        Returns
        -------
        dict
            Dict of created environment variable
        """
        params = {
            "projectId": project_id,
            "name": name,
            "value": value,
            "description": description,
            "isPassword": is_password,
            "scope": "PROJECT",
        }

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully created", name)
        return result

    def update_for_project(
        self,
        project_id: str,
        name: str,
        new_name: str = None,
        value: str = None,
        description: str = None,
        is_password: bool = None,
    ) -> Dict:
        """
        Update environment variable with provided function variables if it exists

        Parameters
        ----------
        project_id : str
            ID of the project
        name : str
            Name of the environment to upgrade
        new_name : str, optional
            New name of the environment variable. If none provided, keep the actual one
        value: str, optional
            New value of the environment variable. If none provided, keep the actual one
        description: str, optional
            New description of the environment variable. If none provided, keep the actual one
        is_password: boolean, optional
            New password boolean status. If none provided, keep the actual one

        Returns
        -------
        dict
            Dict containing the id of the updated environment variable

        Raises
        ------
        ValueError
            When the variable doesn't already exist
        """

        existing_env_var = self.list_for_project(project_id, pprint_result=False)["projectEnvironmentVariables"]

        if name not in [env_var["name"] for env_var in existing_env_var if env_var["scope"] == "PROJECT"]:
            raise ValueError(f"❌ Environment variable {name} does not exists")

        params = [d for d in existing_env_var if d["name"] == name][0]
        params["projectId"] = project_id
        if params["isPassword"] == True:
            params.pop("value")
        if new_name:
            params["name"] = new_name
        if value:
            params["value"] = value
        if description:
            params["description"] = description
        if is_password == True:
            params["isPassword"] = is_password
        elif is_password == False:
            params["isPassword"] = is_password

        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully updated", name)
        return result

    def create_or_update_for_project(
        self, project_id: str, name: str, value: str, description: str = "", is_password: bool = False
    ) -> Dict:
        """
        Create a new project environment variable or update it if it already exists

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        name: str
            Unique name of the environment variable to create or modify
        value: str
            Value of the environment variable to create or modify
        description: str, optional
            Description of the variable
        is_password: boolean, optional
            Weather the variable is a password or not (default: False)

        Returns
        -------
        dict
            Dict of created or updated environment variable
        """

        existing_env_var = self.list_for_project(project_id, pprint_result=False)["projectEnvironmentVariables"]
        present = name in [env["name"] for env in existing_env_var if env["scope"] == "PROJECT"]

        # If variable not present, create it
        if not present:
            return self.create_for_project(
                project_id=project_id, name=name, value=value, description=description, is_password=is_password
            )
        return self.update_for_project(
            project_id=project_id,
            name=name,
            new_name=None,
            value=value,
            description=description,
            is_password=is_password,
        )

    def delete_for_project(self, project_id: str, name: str) -> Dict:
        """Delete a given environment variable inside a given project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        name : str
            Name of the environment variable to delete inside the given project

        Returns
        -------
        dict
            Dict of deleted environment variable

        Raises
        ------
        ValueError
            When the given name doesn't correspond to an existing environment
            variable inside the given project
        """
        project_envs = self.list_for_project(project_id, pprint_result=False)
        project_env = [env for env in project_envs["projectEnvironmentVariables"] if env["name"] == name]

        if len(project_env) == 0:
            raise ValueError("❌ 'name' must be the name of an existing " "environment variable in the given project")

        project_env_id = project_env[0]["id"]

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_ENV_VAR), variable_values={"id": project_env_id})
        logging.info("✅ Environment variable [%s] successfully deleted", name)
        return result

    def export(self, project_id, output_folder: str, error_folder: Optional[str] = "", project_only: bool = False):
        """Export the environment variables in a folder

        Parameters
        ----------
        project_id : str
            Project ID
        output_folder : str
            Path to store the exported environment variables
        project_only : boolean, optional
            True if only project environment variable should be exported False otherwise
        error_folder : str, optional
            Path to store the project ID in case of error. If not set, project ID is not write

        Returns
        -------
        bool
            True if environment variables are exported False otherwise
        """
        result = True
        output_folder = check_folder_path(output_folder)
        project_env_var = None

        try:
            project_env_var = self.list_for_project(project_id)["projectEnvironmentVariables"]
            if project_only:
                project_env_var = [env for env in project_env_var if env["scope"] == "PROJECT"]
        except Exception as exception:
            logging.warning("Cannot get the information of environment variable of the project [%s]", project_id)
            logging.error("Something went wrong %s", exception)
        if project_env_var:
            try:
                for env in project_env_var:
                    env_var_name = env["name"]
                    create_folder(output_folder + env_var_name)
                    write_to_json_file(output_folder + env_var_name + "/variable.json", env)

                logging.info("✅ Environment variables of the project [%s] have been successfully exported", project_id)
            except Exception as exception:
                logging.warning(
                    "❌ Environment variables of the project [%s] have not been successfully exported", project_id
                )
                logging.error("Something went wrong %s", exception)
                write_error(error_folder, "env_vars", project_id)
                result = False
                return result
        else:
            logging.info("✅ The project [%s] doesn't have any environment variable", project_id)

        return result

    def import_from_json(self, json_file: str, project_id: str = None) -> bool:
        """Import environment variables from JSON format
        Parameters
        ----------
        json_file : str
            Path to the JSON file that contains env var information
        project_id : str, optional
            Project ID
        Returns
        -------
        bool
            True if environment variables are imported False otherwise
        """
        result = True

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                env_var_info = json.load(file)
        except Exception as exception:
            logging.warning("Cannot open the JSON file %s", json_file)
            logging.error("Something went wrong %s", exception)
            return False

        try:
            env_var_name = env_var_info["name"]
            env_var_scope = env_var_info["scope"]
            env_var_value = env_var_info["value"] if env_var_info["value"] is not None else ""
            env_var_description = env_var_info["description"]
            env_var_is_password = env_var_info["isPassword"]

            if env_var_scope == "PROJECT":
                res = self.create_for_project(
                    project_id=project_id,
                    name=env_var_name,
                    value=env_var_value,
                    description=env_var_description,
                    is_password=env_var_is_password,
                )
                if res["saveEnvironmentVariable"] is not None:
                    result = True
                else:
                    result = False
                    logging.error("❌ Something went wrong %s", res)
            elif env_var_scope == "GLOBAL":
                res = self.create_global(
                    name=env_var_name,
                    value=env_var_value,
                    description=env_var_description,
                    is_password=env_var_is_password,
                )
                if res["saveEnvironmentVariable"] is not None:
                    result = True
                else:
                    result = False
                    logging.error("❌ Something went wrong %s", res)
            else:
                result = False
        except Exception as exception:
            result = False
            logging.error("Something went wrong %s", exception)

        if result:
            logging.info("✅ Environment variables of the project [%s] have been successfully imported", project_id)
        else:
            logging.warning(
                "❌ Environment variables of the project [%s] have not been successfully imported", project_id
            )

        return result
