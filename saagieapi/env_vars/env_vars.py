import json
import logging
from pathlib import Path
from typing import Dict, Optional

import deprecation
from gql import gql

from ..utils.folder_functions import create_folder, write_error, write_to_json_file
from .gql_queries import *


def handle_error(msg, project_id):
    logging.error("❌ Something went wrong %s", msg)
    logging.warning("❌ Environment variables of the project [%s] have not been successfully imported", project_id)
    return False


def check_scope(scope, project_id, pipeline_id, app_id):
    if scope not in ("GLOBAL", "PROJECT", "PIPELINE", "APP"):
        raise ValueError("❌ 'scope' must be one of GLOBAL, PROJECT, PIPELINE or APP")

    if scope == "PROJECT" and project_id is None:
        raise ValueError("❌ 'project_id' must be provided for scope PROJECT")

    if scope == "PIPELINE" and pipeline_id is None:
        raise ValueError("❌ 'pipeline_id' must be provided for scope PIPELINE")

    if scope == "APP" and app_id is None:
        raise ValueError("❌ 'app_id' must be provided for scope APP")


class EnvVars:
    # pylint: disable=singleton-comparison
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`list()` instead.",
        deprecated_in="2.8.0",
    )
    def list_globals(self, pprint_result: Optional[bool] = None) -> Dict:
        """Get global environment variables

        NB: You can only list environment variables if you have at least the
        viewer role on the platform

        Parameters
        ----------
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of global environment variable on the platform

        Examples
        --------
        >>> saagie_api.env_vars.list_globals()
        {
            "globalEnvironmentVariables": [
                {
                    "id": "334c2e0e-e8ea-4639-911e-757bf36bc91b",
                    "name": "TEST_PASSWORD",
                    "scope": "GLOBAL",
                    "value": None,
                    "description": "This is a password",
                    "isPassword": True,
                    "isValid": True,
                    "overriddenValues": [],
                    "invalidReasons": None
                },
                {
                    "id": "eb430066-551a-47f3-97c6-e56a9272fbd0",
                    "name": "PORT_WEBHDFS",
                    "scope": "GLOBAL",
                    "value": "50070",
                    "description": "",
                    "isPassword": False,
                    "isValid": True,
                    "overriddenValues": [],
                    "invalidReasons": None
                }
            ]
        }
        """
        return self.saagie_api.client.execute(query=gql(GQL_LIST_GLOBAL_ENV_VARS), pprint_result=pprint_result)

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`create()` instead.",
        deprecated_in="2.8.0",
    )
    def create_global(
        self, name: str, value: str = "DEFAULT_VALUE", description: str = "", is_password: bool = False
    ) -> Dict:
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

        Examples
        --------
        >>> saagieapi.env_vars.create_global(
        ...     name="TEST_PASSWORD",
        ...     value="test",
        ...     description="This is a password",
        ...     is_password=True
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "069f3bf2-da1a-4106-acb4-3c7cc37367a3"
            }
        }
        """
        params = {
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": "GLOBAL",
            }
        }

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully created", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`update()` instead.",
        deprecated_in="2.8.0",
    )
    def update_global(
        self, name: str, new_name: str = None, value: str = None, description: str = None, is_password: bool = None
    ) -> Dict:
        """
        Update environment variable with provided function variables if it exists

        Parameters
        ----------
        name : str
            Name of the environment variable to upgrade
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

        Examples
        --------
        >>> saagieapi.env_vars.update_global(
        ...     name="TEST_PASSWORD",
        ...     value="new value",
        ...     description="This is a new password",
        ...     is_password=True
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "069f3bf2-da1a-4106-acb4-3c7cc37367a3"
            }
        }
        """

        existing_env_var = self.list(scope="GLOBAL", pprint_result=False)["globalEnvironmentVariables"]

        if name not in [env_var["name"] for env_var in existing_env_var]:
            raise ValueError(f"❌ Environment variable {name} does not exists")

        params = {
            "envVar": [d for d in existing_env_var if d["name"] == name][0],
        }
        params["envVar"].pop("isValid")
        params["envVar"].pop("invalidReasons")
        if params["envVar"]["isPassword"] == True:
            params["envVar"].pop("value")
        if new_name is not None:
            params["envVar"]["name"] = new_name
        if value is not None:
            params["envVar"]["value"] = value
        if description is not None:
            params["envVar"]["description"] = description
        if is_password in {True, False}:
            params["envVar"]["isPassword"] = is_password
        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully updated", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`create_or_update()` instead.",
        deprecated_in="2.8.0",
    )
    def create_or_update_global(
        self, name: str, value: str = None, description: str = None, is_password: bool = None
    ) -> Dict:
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
            Weather the variable is a password or not (default: None)

        Returns
        -------
        dict
            Dict of created or updated environment variable

        Examples
        --------
        >>> saagieapi.env_vars.create_or_update_global(
        ...     name="TEST_PASSWORD",
        ...     value="new value",
        ...     description="This is a new password",
        ...     is_password=True
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "069f3bf2-da1a-4106-acb4-3c7cc37367a3"
            }
        }
        """

        existing_env_var = self.list_globals(pprint_result=False)["globalEnvironmentVariables"]
        present = name in [env["name"] for env in existing_env_var]

        # If variable not present, create it
        if not present:
            args = {
                "name": name,
                "value": value,
                "description": description,
                "is_password": is_password,
            }
            args2 = {k: v for k, v in args.items() if v is not None}
            return self.create_global(**args2)

        return self.update_global(
            name=name, new_name=None, value=value, description=description, is_password=is_password
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`delete()` instead.",
        deprecated_in="2.8.0",
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

        Examples
        --------
        >>> saagieapi.env_vars.delete_global(name="TEST_PASSWORD")
        {
            "deleteEnvironmentVariable": True
        }
        """
        global_envs = self.list_globals(pprint_result=False)["globalEnvironmentVariables"]
        global_env = [env for env in global_envs if env["name"] == name]

        if not global_env:
            raise ValueError("❌ 'name' must be the name of an existing global environment variable")

        global_env_id = global_env[0]["id"]

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_ENV_VAR), variable_values={"id": global_env_id})
        logging.info("✅ Environment variable [%s] successfully deleted", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`list()` instead.",
        deprecated_in="2.8.0",
    )
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

        Examples
        --------
        >>> saagieapi.env_vars.list_for_project(project_id="50033e21-83c2-4431-a723-d54c2693b964")
        {
            "projectEnvironmentVariables": [
                {
                    "id": "334c2e0e-e8ea-4639-911e-757bf36bc91b",
                    "name": "TEST_PASSWORD",
                    "scope": "GLOBAL",
                    "value": None,
                    "description": "This is a password",
                    "isPassword": True,
                    "isValid": True,
                    "overriddenValues": [],
                    "invalidReasons": None
                },
                {
                    "id": "eb430066-551a-47f3-97c6-e56a9272fbd0",
                    "name": "RSTUDIO_ADMIN_USER",
                    "scope": "PROJECT",
                    "value": "rstudio",
                    "description": "",
                    "isPassword": False
                    "isValid": True,
                    "overriddenValues": [],
                    "invalidReasons": None
                }
            ]
        }
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_PROJECT_ENV_VARS), variable_values={"projectId": project_id}, pprint_result=pprint_result
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`create()` instead.",
        deprecated_in="2.8.0",
    )
    def create_for_project(
        self, project_id: str, name: str, value: str = "DEFAULT_VALUE", description: str = "", is_password: bool = False
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

        Examples
        --------
        >>> saagieapi.env_vars.create_for_project(
        ...     name="TEST_PASSWORD",
        ...     value="test",
        ...     description="This is a password",
        ...     is_password=True,
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964"
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """
        params = {
            "entityId": project_id,
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": "PROJECT",
            },
        }

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully created", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`update()` instead.",
        deprecated_in="2.8.0",
    )
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
            Name of the environment variable to upgrade
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

        Examples
        --------
        >>> saagieapi.env_vars.update_for_project(
        ...     name="TEST_PASSWORD",
        ...     value="new value",
        ...     description="This is a new password",
        ...     is_password=True,
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964"
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """

        existing_env_var = self.list_for_project(project_id, pprint_result=False)["projectEnvironmentVariables"]

        if name not in [env_var["name"] for env_var in existing_env_var if env_var["scope"] == "PROJECT"]:
            raise ValueError(f"❌ Environment variable {name} does not exists")

        params = {
            "entityId": project_id,
            "envVar": [d for d in existing_env_var if d["name"] == name][0],
        }
        params["envVar"].pop("isValid")
        params["envVar"].pop("overriddenValues")
        params["envVar"].pop("invalidReasons")
        if params["envVar"]["isPassword"] == True:
            params["envVar"].pop("value")
        if new_name is not None:
            params["envVar"]["name"] = new_name
        if value is not None:
            params["envVar"]["value"] = value
        if description is not None:
            params["envVar"]["description"] = description
        if is_password in {True, False}:
            params["envVar"]["isPassword"] = is_password
        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully updated", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`create_or_update()` instead.",
        deprecated_in="2.8.0",
    )
    def create_or_update_for_project(
        self, project_id: str, name: str, value: str = None, description: str = None, is_password: bool = None
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

        Examples
        --------
        >>> saagieapi.env_vars.create_or_update_for_project(
        ...     name="TEST_PASSWORD",
        ...     value="new value",
        ...     description="This is a new password",
        ...     is_password=True,
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964"
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """

        existing_env_var = self.list_for_project(project_id, pprint_result=False)["projectEnvironmentVariables"]
        present = name in [env["name"] for env in existing_env_var if env["scope"] == "PROJECT"]

        # If variable not present, create it
        if not present:
            args = {
                k: v
                for k, v in {
                    "project_id": project_id,
                    "name": name,
                    "value": value,
                    "description": description,
                    "is_password": is_password,
                }.items()
                if v is not None
            }
            return self.create_for_project(**args)
        return self.update_for_project(
            project_id=project_id,
            name=name,
            new_name=None,
            value=value,
            description=description,
            is_password=is_password,
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`delete()` instead.",
        deprecated_in="2.8.0",
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

        Examples
        --------
        >>> saagieapi.env_vars.delete_for_project(
        ...     name="TEST_PASSWORD",
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964"
        ... )
        {
            "deleteEnvironmentVariable": True
        }
        """
        project_envs = self.list_for_project(project_id, pprint_result=False)
        project_env = [env for env in project_envs["projectEnvironmentVariables"] if env["name"] == name]

        if not project_env:
            raise ValueError("❌ 'name' must be the name of an existing environment variable in the given project")

        project_env_id = project_env[0]["id"]

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_ENV_VAR), variable_values={"id": project_env_id})
        logging.info("✅ Environment variable [%s] successfully deleted", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`list()` instead.",
        deprecated_in="2.8.0",
    )
    def list_for_pipeline(self, pipeline_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """Get pipeline environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of pipeline environment variables

        Examples
        --------
        >>> saagieapi.env_vars.list_for_pipeline(pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1")
        {
            "pipelineEnvironmentVariables": [
                {
                    "id": "40a7dd59-538f-4c55-a983-8a554525b060",
                    "scope": "GLOBAL",
                    "name": "TEST_GLOBAL",
                    "value": "TEST_GLOBAL",
                    "description": "",
                    "isPassword": False,
                    "isValid": True,
                    "overriddenValues": [],
                    "invalidReasons": None
                },
                {
                    "id": "3f4a8d8f-6f45-480f-8907-2f66ddf26e01",
                    "scope": "PROJECT",
                    "name": "TEST_PROJECT",
                    "value": "TEST_PROJECT",
                    "description": "",
                    "isPassword": False,
                    "isValid": True,
                    "overriddenValues": [],
                    "invalidReasons": None
                },
                {
                    "id": "750c5366-caea-4d1f-ad38-fa6089ea2015",
                    "scope": "PIPELINE",
                    "name": "BLK1",
                    "value": None,
                    "description": "This is a new password",
                    "isPassword": True,
                    "isValid": True,
                    "overriddenValues": [],
                    "invalidReasons": None
                }
            ]
        }
        """
        params = {
            "pipelineId": pipeline_id,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_PIPELINE_ENV_VARS), variable_values=params, pprint_result=pprint_result
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`create()` instead.",
        deprecated_in="2.8.0",
    )
    def create_for_pipeline(
        self,
        pipeline_id: str,
        name: str,
        value: str = "DEFAULT_VALUE",
        description: str = "",
        is_password: bool = False,
    ) -> Dict:
        """Create an environment variable in a given pipeline

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
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

        Examples
        --------
        >>> saagieapi.env_vars.create_for_pipeline(
        ...     pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
        ...     name="TEST_PASSWORD",
        ...     value="test",
        ...     description="This is a password",
        ...     is_password=True,
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """
        params = {
            "entityId": pipeline_id,
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": "PIPELINE",
            },
        }

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully created", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`update()` instead.",
        deprecated_in="2.8.0",
    )
    def update_for_pipeline(
        self,
        pipeline_id: str,
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
        pipeline_id : str
            ID of the project
        name : str
            Name of the environment variable to upgrade
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

        Examples
        --------
        >>> saagie_api.env_vars.update_for_pipeline(
        ...     pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
        ...     name="TEST_PASSWORD",
        ...     new_name="TEST_PWD",
        ...     value="new value",
        ...     description="This is a new password",
        ...     is_password=True,
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "750c5366-caea-4d1f-ad38-fa6089ea2015"
            }
        }
        """

        existing_env_var = self.list_for_pipeline(pipeline_id, pprint_result=False)["pipelineEnvironmentVariables"]

        if name not in [env_var["name"] for env_var in existing_env_var if env_var["scope"] == "PIPELINE"]:
            raise ValueError(f"❌ Environment variable {name} does not exists")

        params = {
            "entityId": pipeline_id,
            "envVar": [d for d in existing_env_var if d["name"] == name][0],
        }
        params["envVar"].pop("isValid")
        params["envVar"].pop("overriddenValues")
        params["envVar"].pop("invalidReasons")
        if params["envVar"]["isPassword"] == True:
            params["envVar"].pop("value")
        if new_name is not None:
            params["envVar"]["name"] = new_name
        if value is not None:
            params["envVar"]["value"] = value
        if description is not None:
            params["envVar"]["description"] = description
        if is_password in {True, False}:
            params["envVar"]["isPassword"] = is_password
        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully updated", name)
        return result

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`create_or_update()` instead.",
        deprecated_in="2.8.0",
    )
    def create_or_update_for_pipeline(
        self, pipeline_id: str, name: str, value: str = None, description: str = None, is_password: bool = None
    ) -> Dict:
        """
        Create a new pipeline environment variable or update it if it already exists

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
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

        Examples
        --------
        >>> saagieapi.env_vars.create_or_update_for_pipeline(
        ...     pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
        ...     name="TEST_PASSWORD",
        ...     value="test",
        ...     description="This is a password",
        ...     is_password=True,
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """

        existing_env_var = self.list_for_pipeline(pipeline_id, pprint_result=False)["pipelineEnvironmentVariables"]
        present = name in [env["name"] for env in existing_env_var if env["scope"] == "PIPELINE"]

        # If variable not present, create it
        if not present:
            args = {
                "pipeline_id": pipeline_id,
                "name": name,
                "value": value,
                "description": description,
                "is_password": is_password,
            }
            args2 = {k: v for k, v in args.items() if v is not None}
            return self.create_for_pipeline(**args2)
        return self.update_for_pipeline(
            pipeline_id=pipeline_id,
            name=name,
            new_name=None,
            value=value,
            description=description,
            is_password=is_password,
        )

    @deprecation.deprecated(
        details="This function is deprecated and will be removed in a future version. "
        "Please use :func:`delete()` instead.",
        deprecated_in="2.8.0",
    )
    def delete_for_pipeline(self, pipeline_id: str, name: str) -> Dict:
        """Delete a given environment variable inside a given pipeline

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        name : str
            Name of the environment variable to delete inside the given pipeline

        Returns
        -------
        dict
            Dict of deleted environment variable

        Raises
        ------
        ValueError
            When the given name doesn't correspond to an existing environment
            variable inside the given pipeline

        Examples
        --------
        >>> saagieapi.env_vars.delete_for_pipeline(
        ...     pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
        ...     name="TEST_PASSWORD",
        ... )
        {
            "deleteEnvironmentVariable": True
        }
        """
        pipeline_envs = self.list_for_pipeline(pipeline_id, pprint_result=False)
        pipeline_env = [env for env in pipeline_envs["pipelineEnvironmentVariables"] if env["name"] == name]

        if not pipeline_env:
            raise ValueError("❌ 'name' must be the name of an existing environment variable in the given pipeline")

        pipeline_env_id = pipeline_env[0]["id"]

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_ENV_VAR), variable_values={"id": pipeline_env_id})
        logging.info("✅ Environment variable [%s] successfully deleted", name)
        return result

    def list(
        self,
        scope: str,
        project_id: str = None,
        pipeline_id: str = None,
        app_id: str = None,
        scope_only: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get environment variables
        NB: You can only list environment variables if you have at least the
        viewer role on the project

        Parameters
        ----------
        scope : str
            Scope of the environment variable to list. Must be one of GLOBAL, PROJECT, PIPELINE or APP
        project_id : str, optional
            UUID of your project (see README on how to find it)
        pipeline_id : str, optional
            UUID of your pipeline (see README on how to find it)
        app_id : str, optional
            UUID of your app (see README on how to find it)
        scope_only : bool, optional
            Whether to return only the environment variables of the given scope
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of environment variables

        Examples
        --------
        >>> saagieapi.env_vars.list(scope="GLOBAL")
        [
            {
                "id": "334c2e0e-e8ea-4639-911e-757bf36bc91b",
                "name": "TEST_PASSWORD",
                "scope": "GLOBAL",
                "value": None,
                "description": "This is a password",
                "isPassword": True,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            },
            {
                "id": "eb430066-551a-47f3-97c6-e56a9272fbd0",
                "name": "PORT_WEBHDFS",
                "scope": "GLOBAL",
                "value": "50070",
                "description": "",
                "isPassword": False,
                "isValid": True,
                "overriddenValues": [],
                "invalidReasons": None
            }
        ]
        """
        check_scope(scope, project_id, pipeline_id, app_id)

        if scope == "GLOBAL":
            res = self.saagie_api.client.execute(query=gql(GQL_LIST_GLOBAL_ENV_VARS), pprint_result=pprint_result)[
                "globalEnvironmentVariables"
            ]
        elif scope == "PROJECT":
            res = self.saagie_api.client.execute(
                query=gql(GQL_LIST_PROJECT_ENV_VARS),
                variable_values={"projectId": project_id},
                pprint_result=pprint_result,
            )["projectEnvironmentVariables"]
        elif scope == "PIPELINE":
            res = self.saagie_api.client.execute(
                query=gql(GQL_LIST_PIPELINE_ENV_VARS),
                variable_values={"pipelineId": pipeline_id},
                pprint_result=pprint_result,
            )["pipelineEnvironmentVariables"]
        elif scope == "APP":
            res = self.saagie_api.client.execute(
                query=gql(GQL_LIST_APP_ENV_VARS),
                variable_values={"appId": app_id},
                pprint_result=pprint_result,
            )["appEnvironmentVariables"]

        return [env for env in res if env["scope"] == scope] if scope_only else res

    def get(
        self,
        scope: str,
        name: str,
        project_id: str = None,
        pipeline_id: str = None,
        app_id: str = None,
        scope_only: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """
        Get environment variable information
        NB: You can only get environment variable information if you have at least the
        viewer role on the project

        Parameters
        ----------
        scope : str
            Scope of the environment variable to get. Must be one of GLOBAL, PROJECT, PIPELINE or APP
        name : str
            Name of the environment variable to get
        project_id : str, optional
            UUID of your project (see README on how to find it)
        pipeline_id : str, optional
            UUID of your pipeline (see README on how to find it)
        app_id : str, optional
            UUID of your app (see README on how to find it)
        scope_only : bool, optional
            Whether to return only the environment variables of the given scope
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict (or None if not found)
            Dict of environment variable

        Examples
        --------
        >>> saagie_api.env_vars.get(scope="GLOBAL", name="TEST_GLOBAL_ENV_VARS")
        {
            'id': 'ef1aecd1-8cb0-4a09-8b1c-dff72ca97c1f',
            'name': 'TEST_GLOBAL_ENV_VARS',
            'scope': 'GLOBAL',
            'value': 'DEFAULT_VALUE',
            'description': '',
            'isPassword': False,
            'isValid': True,
            'invalidReasons': None
        }
        """
        check_scope(scope, project_id, pipeline_id, app_id)

        env_vars = self.list(scope, project_id, pipeline_id, app_id, scope_only, pprint_result)

        return next((d for d in env_vars if d["name"] == name), None)

    def create(
        self,
        scope: str,
        name: str,
        value: str = "DEFAULT_VALUE",
        description: str = "",
        is_password: bool = False,
        project_id: str = None,
        pipeline_id: str = None,
        app_id: str = None,
    ) -> Dict:
        """Create an environment variable in a given scope

        Parameters
        ----------
        scope : str
            Scope of the environment variable to create. Must be one of GLOBAL, PROJECT, PIPELINE or APP
        name : str
            Name of the environment variable to create
        value : str
            Value of the environment variable to create
        description : str, optional
            Description of the environment variable to create
        is_password : bool, optional
            Weather the environment variable to create is a password or not
        project_id : str, optional
            UUID of your project (see README on how to find it)
        pipeline_id : str, optional
            UUID of your pipeline (see README on how to find it)
        app_id : str, optional
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of created environment variable

        Examples
        --------
        >>> saagieapi.env_vars.create(
        ...     scope="PROJECT",
        ...     name="TEST_PASSWORD",
        ...     value="test",
        ...     description="This is a password",
        ...     is_password=True,
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964"
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """

        check_scope(scope, project_id, pipeline_id, app_id)

        params = {
            "envVar": {
                "name": name,
                "value": value,
                "description": description,
                "isPassword": is_password,
                "scope": scope,
            },
        }

        if scope == "PROJECT":
            params["entityId"] = project_id
        elif scope == "PIPELINE":
            params["entityId"] = pipeline_id
        elif scope == "APP":
            params["entityId"] = app_id

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully created", name)
        return result

    def update(
        self,
        scope: str,
        name: str,
        new_name: str = None,
        value: str = None,
        description: str = None,
        is_password: bool = None,
        project_id: str = None,
        pipeline_id: str = None,
        app_id: str = None,
    ) -> Dict:
        """
        Update environment variable with provided function variables if it exists

        Parameters
        ----------
        scope : str
            Scope of the environment variable to update. Must be one of GLOBAL, PROJECT, PIPELINE or APP
        name : str
            Name of the environment variable to upgrade
        new_name : str, optional
            New name of the environment variable. If none provided, keep the actual one
        value: str, optional
            New value of the environment variable. If none provided, keep the actual one
        description: str, optional
            New description of the environment variable. If none provided, keep the actual one
        is_password: boolean, optional
            New password boolean status. If none provided, keep the actual one
        project_id : str, optional
            UUID of your project (see README on how to find it)
        pipeline_id : str, optional
            UUID of your pipeline (see README on how to find it)
        app_id : str, optional
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict containing the id of the updated environment variable

        Raises
        ------
        ValueError
            When the variable doesn't already exist

        Examples
        --------
        >>> saagieapi.env_vars.update(
        ...     scope="PROJECT",
        ...     name="TEST_PASSWORD",
        ...     value="new value",
        ...     description="This is a new password",
        ...     is_password=True,
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964"
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """

        check_scope(scope, project_id, pipeline_id, app_id)

        existing_env_var = self.list(scope, project_id, pipeline_id, app_id, scope_only=True, pprint_result=False)

        var = next((d for d in existing_env_var if d["name"] == name), None)
        if var is None:
            raise ValueError(f"❌ Environment variable {name} does not exists")

        params = {
            "envVar": var,
        }

        if scope == "PROJECT":
            params["entityId"] = project_id
        elif scope == "PIPELINE":
            params["entityId"] = pipeline_id
        elif scope == "APP":
            params["entityId"] = app_id

        params["envVar"].pop("isValid", None)
        params["envVar"].pop("overriddenValues", None)
        params["envVar"].pop("invalidReasons", None)
        if params["envVar"]["isPassword"] == True:
            params["envVar"].pop("value")
        if new_name is not None:
            params["envVar"]["name"] = new_name
        if value is not None:
            params["envVar"]["value"] = value
        if description is not None:
            params["envVar"]["description"] = description
        if is_password in {True, False}:
            params["envVar"]["isPassword"] = is_password
        result = self.saagie_api.client.execute(query=gql(GQL_UPDATE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully updated", name)
        return result

    def create_or_update(
        self,
        scope: str,
        name: str,
        value: str = None,
        description: str = None,
        is_password: bool = None,
        project_id: str = None,
        pipeline_id: str = None,
        app_id: str = None,
    ) -> Dict:
        """
        Create a new environment variable or update it if it already exists

        Parameters
        ----------
        scope : str
            Scope of the environment variable to create. Must be one of GLOBAL, PROJECT, PIPELINE or APP
        name: str
            Unique name of the environment variable to create or modify
        value: str
            Value of the environment variable to create or modify
        description: str, optional
            Description of the variable
        is_password: boolean, optional
            Weather the variable is a password or not (default: False)
        project_id : str, optional
            UUID of your project (see README on how to find it)
        pipeline_id : str, optional
            UUID of your pipeline (see README on how to find it)
        app_id : str, optional
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of created or updated environment variable

        Examples
        --------
        >>> saagieapi.env_vars.create_or_update(
        ...     name="TEST_PASSWORD",
        ...     value="new value",
        ...     description="This is a new password",
        ...     is_password=True,
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964"
        ... )
        {
            "saveEnvironmentVariable": {
                "id": "8aaee333-a9f4-40f5-807a-44f8efa65a2f"
            }
        }
        """

        check_scope(scope, project_id, pipeline_id, app_id)

        existing_env_var = self.list(scope, project_id, pipeline_id, app_id, scope_only=True, pprint_result=False)

        var = next((d for d in existing_env_var if d["name"] == name), None)

        # If variable not present, create it
        if var is None:
            args = {
                "scope": scope,
                "name": name,
                "value": value,
                "description": description,
                "is_password": is_password,
                "project_id": project_id,
                "pipeline_id": pipeline_id,
                "app_id": app_id,
            }
            args2 = {k: v for k, v in args.items() if v is not None}
            return self.create(**args2)
        return self.update(
            scope=scope,
            name=name,
            new_name=None,
            value=value,
            description=description,
            is_password=is_password,
            project_id=project_id,
            pipeline_id=pipeline_id,
            app_id=app_id,
        )

    def delete(
        self,
        scope: str,
        name: str,
        project_id: str = None,
        pipeline_id: str = None,
        app_id: str = None,
    ) -> Dict:
        """Delete a given environment variable inside a given scope

        Parameters
        ----------
        scope : str
            Scope of the environment variable to delete. Must be one of GLOBAL, PROJECT, PIPELINE or APP
        name : str
            Name of the environment variable to delete inside the given scope
        project_id : str, optional
            UUID of your project (see README on how to find it)
        pipeline_id : str, optional
            UUID of your pipeline (see README on how to find it)
        app_id : str, optional
            UUID of your app (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted environment variable

        Raises
        ------
        ValueError
            When the given name doesn't correspond to an existing environment
            variable inside the given scope

        Examples
        --------
        >>>   saagieapi.env_vars.delete(scope="GLOBAL", name="TEST_PASSWORD")
        {
            "deleteEnvironmentVariable": True
        }
        """
        check_scope(scope, project_id, pipeline_id, app_id)

        existing_env_var = self.list(scope, project_id, pipeline_id, app_id, scope_only=True, pprint_result=False)

        var = next((d for d in existing_env_var if d["name"] == name), None)
        if var is None:
            raise ValueError(f"❌ Environment variable {name} does not exists")

        params = {
            "id": var["id"],
        }

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variable [%s] successfully deleted", name)
        return result

    def bulk_create_for_pipeline(self, pipeline_id: str, env_vars: Dict) -> Dict:
        """Delete all existing env vars and create new ones for the pipeline

        Parameters
        ----------
        pipeline_id : str
            Pipeline ID
        env_vars : Dict
            Dict that contains all the variables for the pipeline

        Returns
        -------
        dict
            Dict of created environment variables for pipeline

        Examples
        --------
        >>> saagie_api.env_vars.bulk_create_for_pipeline(
        ...     pipeline_id="5a064fe8-8de3-4dc7-9a69-40b079deaeb1",
        ...     env_vars={
        ...         "BULK1": "HELLO",
        ...         "BULK2": "WORLD"
        ...     }
        ... )
        {
            "replaceEnvironmentVariablesByRawForScope": [
                {
                    "id": "750c5366-caea-4d1f-ad38-fa6089ea2015",
                    "scope": "PIPELINE",
                    "name": "BULK1",
                    "value": "HELLO"
                },
                {
                    "id": "ce5f098e-4750-40b1-8c10-11b118ebc23a",
                    "scope": "PIPELINE",
                    "name": "BULK2",
                    "value": "WORLD"
                }
            ]
        }
        """

        # need to transform the dict in parameter to a string with the following format"var1=val1\nvar2=val2"
        var_str = "".join(f"{key}={env_vars[key]}\n" for key in env_vars)

        params = {
            "entityId": pipeline_id,
            "scope": "PIPELINE",
            "rawEnvironmentVariables": var_str,
        }

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_PIPELINE_ENV_VAR), variable_values=params)
        logging.info("✅ Environment variables for pipeline [%s] successfully created", pipeline_id)
        return result

    def export(
        self, project_id, output_folder: str, error_folder: Optional[str] = "", project_only: bool = False
    ) -> bool:
        """Export the environment variables of scope GLOBAL or PROJECT in a folder
        To export PIPELINE variables, use the pipelines.export function

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

        Examples
        --------
        >>> saagieapi.env_vars.export(
        ...     project_id="50033e21-83c2-4431-a723-d54c2693b964",
        ...     output_folder="./output/env_vars/",
        ...     error_folder="./output/error/",
        ...     project_only=True
        ... )
        True
        """

        output_folder = Path(output_folder)

        try:
            project_env_var = self.list(scope="PROJECT", project_id=project_id, scope_only=project_only)
        except Exception as exception:
            logging.warning("Cannot get the information of environment variable of the project [%s]", project_id)
            logging.error("Something went wrong %s", exception)
            return False

        if not project_env_var:
            logging.info("✅ The project [%s] doesn't have any environment variable", project_id)
            return True

        try:
            for env in project_env_var:
                create_folder(output_folder / env["name"])
                write_to_json_file(output_folder / env["name"] / "variable.json", env)

            logging.info("✅ Environment variables of the project [%s] have been successfully exported", project_id)
        except Exception as exception:
            logging.warning(
                "❌ Environment variables of the project [%s] have not been successfully exported", project_id
            )
            logging.error("Something went wrong %s", exception)
            write_error(error_folder, "env_vars", project_id)
            return False

        return True

    def import_from_json(self, json_file: str, project_id: str = None) -> bool:
        """Import environment variables from JSON format of scope GLOBAL or PROJECT
        To import PIPELINE variables, use the pipelines.import_from_json function

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

        Examples
        --------
        >>> saagieapi.env_vars.import_from_json(
        ...     json_file="/path/to/the/json/file.json",
        ...     project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        ... )
        True
        """
        json_file = Path(json_file)
        try:
            with json_file.open("r", encoding="utf-8") as file:
                env_var_info = json.load(file)
        except Exception as exception:
            return handle_error(f"{exception}\n Cannot open the JSON file {json_file}", project_id)

        try:
            res = self.create(
                scope=env_var_info["scope"],
                name=env_var_info["name"],
                value=env_var_info["value"] or "",
                description=env_var_info["description"],
                is_password=env_var_info["isPassword"],
                project_id=project_id,
            )
            if res["saveEnvironmentVariable"] is None:
                return handle_error(res, project_id)
        except Exception as exception:
            return handle_error(exception, project_id)

        logging.info("✅ Environment variables of the project [%s] have been successfully imported", project_id)

        return True
