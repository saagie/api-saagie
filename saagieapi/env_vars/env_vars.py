from gql import gql

from .gql_queries import *


class EnvVars:

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
        query = gql(gql_get_global_env_vars)
        return self.client.execute(query)

    def create_global(self, name, value,
                      description='',
                      is_password=False):
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
        query = gql(gql_create_global_env_var.format(name,
                                                     value,
                                                     description,
                                                     str(is_password).lower()))
        return self.client.execute(query)

    def update_global(self, name, new_name=None, value=None, description=None, is_password=None):
        """
        Update environment variable with provided function vairables if it exists
        Parameters
        ----------
        name : str
            Name of the environment to upgrade
        new_name : str, optional
            New name of the environment variable. If none provided, keep the actual one
        value: str, optional
            New value of the environment variable. If none provided, keep the actual one
        description; str, optional
            New description of the environment variable. If none provided, keep the actual one
        is_password: boolean, optional
            New password boolean status. If none provided, keep the actual one
        Returns
        -------
        Dict containing the id of the updated environment variable
        """

        existing_env_var = self.list_globals()['globalEnvironmentVariables']

        if name not in [env_var['name'] for env_var in existing_env_var]:
            raise ValueError("Environment variable does not exists")

        params = [d for d in existing_env_var if d['name'] == name][0]

        if params['isPassword'] == True:
            params.pop('value')
        if new_name:
            params['name'] = new_name
        if value:
            params['value'] = value
        if description:
            params['description'] = description
        if is_password == True:
            params['isPassword'] = is_password
        elif is_password == False:
            params['isPassword'] = is_password

        query = gql(gql_update_env_var)

        return self.client.execute(query, variable_values=params)

    def delete_global(self, name):
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
        global_envs = self.list_globals()['globalEnvironmentVariables']
        global_env = [env for env in global_envs if env['name'] == name]

        if len(global_env) == 0:
            raise ValueError("'name' must be the name of an existing global "
                             "environment variable")

        global_env_id = global_env[0]['id']

        query = gql(gql_delete_env_var.format(global_env_id))
        return self.client.execute(query)

    def list_for_project(self, project_id):
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
        query = gql(gql_get_project_env_vars.format(project_id))
        return self.client.execute(query)

    def create_for_project(self, project_id, name, value,
                           description='', is_password=False):
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
        query = gql(gql_create_project_env_var.format(
            project_id,
            name,
            value,
            description,
            str(is_password).lower()
        ))
        return self.client.execute(query)

    def update_for_project(self, project_id, name, new_name=None, value=None, description=None, is_password=None):
        """
        Update environment variable with provided function vairables if it exists
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
        description; str, optional
            New description of the environment variable. If none provided, keep the actual one
        is_password: boolean, optional
            New password boolean status. If none provided, keep the actual one
        Returns
        -------
        Dict containing the id of the updated environment variable
        """

        existing_env_var = self.list_for_project(project_id)['projectEnvironmentVariables']

        if name not in [env_var['name'] for env_var in existing_env_var]:
            raise ValueError("Environment variable does not exists")

        params = [d for d in existing_env_var if d['name'] == name][0]
        params["entityId"] = project_id
        if params['isPassword'] == True:
            params.pop('value')
        if new_name:
            params['name'] = new_name
        if value:
            params['value'] = value
        if description:
            params['description'] = description
        if is_password == True:
            params['isPassword'] = is_password
        elif is_password == False:
            params['isPassword'] = is_password

        query = gql(gql_update_env_var)

        return self.client.execute(query, variable_values=params)

    def delete_for_project(self, project_id, name):
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
        project_env = [env for env
                       in project_envs['projectEnvironmentVariables']
                       if env['name'] == name]

        if len(project_env) == 0:
            raise ValueError("'name' must be the name of an existing "
                             "environment variable in the given project")

        project_env_id = project_env[0]['id']

        query = gql(gql_delete_env_var.format(project_env_id))
        return self.client.execute(query)
