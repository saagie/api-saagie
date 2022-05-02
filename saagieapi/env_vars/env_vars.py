from typing import Dict

from gql import gql

from .gql_queries import *


class EnvVars:
    # pylint: disable=singleton-comparison
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_globals(self):
        """Get global environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the platform

        Returns
        -------
        dict
            Dict of global environment variable on the platform
        """
        query = gql(GQL_LIST_GLOBAL_ENV_VARS)
        return self.client.execute(query)

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
        query = gql(GQL_CREATE_ENV_VAR)
        return self.client.execute(query, variable_values=params)

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

        existing_env_var = self.list_globals()["globalEnvironmentVariables"]

        if name not in [env_var["name"] for env_var in existing_env_var]:
            raise ValueError("Environment variable does not exists")

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

        query = gql(GQL_UPDATE_ENV_VAR)

        return self.client.execute(query, variable_values=params)

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

        existing_env_var = self.list_globals()["globalEnvironmentVariables"]
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
        global_envs = self.list_globals()["globalEnvironmentVariables"]
        global_env = [env for env in global_envs if env["name"] == name]

        if len(global_env) == 0:
            raise ValueError("'name' must be the name of an existing global " "environment variable")

        global_env_id = global_env[0]["id"]

        query = gql(GQL_DELETE_ENV_VAR)
        return self.client.execute(query, variable_values={"id": global_env_id})

    def list_for_project(self, project_id: str) -> Dict:
        """Get project environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of project environment variables
        """
        query = gql(GQL_LIST_PROJECT_ENV_VARS)
        return self.client.execute(query, variable_values={"projectId": project_id})

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
        query = gql(GQL_CREATE_ENV_VAR)
        return self.client.execute(query, variable_values=params)

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

        existing_env_var = self.list_for_project(project_id)["projectEnvironmentVariables"]

        if name not in [env_var["name"] for env_var in existing_env_var]:
            raise ValueError("Environment variable does not exists")

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

        query = gql(GQL_UPDATE_ENV_VAR)

        return self.client.execute(query, variable_values=params)

    def create_or_update_for_project(
        self, project_id: str, name: str, value: str, description: str = "", is_password: bool = False
    ) -> Dict:
        """
        Create a new project environnement variable or update it if it already exists

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
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

        existing_env_var = self.list_for_project(project_id)["projectEnvironmentVariables"]
        present = name in [env["name"] for env in existing_env_var]

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
        project_envs = self.list_for_project(project_id)
        project_env = [env for env in project_envs["projectEnvironmentVariables"] if env["name"] == name]

        if len(project_env) == 0:
            raise ValueError("'name' must be the name of an existing " "environment variable in the given project")

        project_env_id = project_env[0]["id"]

        query = gql(GQL_DELETE_ENV_VAR)
        return self.client.execute(query, variable_values={"id": project_env_id})
