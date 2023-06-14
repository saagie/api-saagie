import json
import logging
from typing import Dict, List, Optional

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file


class Users:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(self, verify_ssl: Optional[bool] = None) -> List[Dict]:
        """Get users
        NB: You can only list users if you have the admin role on the platform
        Params
        ------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        List[Dict]
            List of users on the platform, each dict have the following struct:
            {'login': 'str',
              'roles': ['str'],
              'platforms': [],
              'groups': ['str'],
              'protected': bool
            }
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET",
            url=f"{self.saagie_api.url_saagie}auth/api/users",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        return response.json()

    def get_info(self, user_name: str, verify_ssl: Optional[bool] = None) -> Dict:
        """Get info of a specific user
        NB: You can only get user's information if you have the admin role on the platform
        Params
        ------
        user_name: str
            User's name
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        Dict
            Dict of user's information on the platform,
            {'login': 'str',
              'roles': ['str'],
              'platforms': [],
              'groups': ['str'],
              'protected': bool
            }
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET",
            url=f"{self.saagie_api.url_saagie}auth/api/users/{user_name}",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        return response.json()

    def export(self, output_folder: str, verify_ssl: Optional[bool] = None) -> bool:
        """Export users in a file
        NB: You can only use this function if you have the admin role on the platform

        Parameters
        ----------
        output_folder : str, optional
            Path to store the exported users
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if users are exported False otherwise
        """
        users = None
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        try:
            users = self.list(verify_ssl=verify_ssl)
        except Exception as exception:
            logging.warning("❌ Cannot get the user's information on the platform")
            logging.error("Something went wrong %s", exception)
        if users:
            output_folder = check_folder_path(output_folder)
            create_folder(output_folder)
            write_to_json_file(output_folder + "users.json", users)
            logging.info("✅ Users of the platform have been successfully exported")
            return True
        else:
            return False

    def import_from_json(
        self, json_file: str, temp_pwd: str, error_folder: Optional[str] = "", verify_ssl: Optional[bool] = None
    ) -> bool:
        """Import users from JSON format file
        NB: You can only use this function if you have the admin role on the platform
            All protected (created at platform installation) users will not be imported.

        Parameters
        ----------
        json_file : str
            Path to json file that contains users
        temp_pwd : str
            Password to all user that you want to import.
            At the first connection, each user has to change the password
        error_folder : str, optional
            Path to store the failed imported user in case of error.
            If not set, failed imported users not write
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if users are all imported or already existed False otherwise

        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl

        bypassed_list = []
        failed_list = []
        already_exist_list = []
        imported_list = []

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                users_list = json.load(file)
        except Exception as exception:
            logging.warning("Cannot open the JSON file %s", json_file)
            logging.error("Something went wrong %s", exception)
            return False

        total_user = len(users_list)

        for user in users_list:
            if user["protected"]:
                bypassed_list.append(user["login"])
            else:
                res = self.saagie_api.request_client.send(
                    method="GET",
                    url=f"{self.saagie_api.url_saagie}auth/api/users/{user['login']}",
                    verify_ssl=verify_ssl,
                )
                if res.status_code == 404:
                    try:
                        self.create(
                            user_name=user["login"],
                            password=temp_pwd,
                            platforms=user["platforms"],
                            roles=user["roles"],
                            verify_ssl=verify_ssl,
                        )
                        imported_list.append(user["login"])
                    except Exception as err:
                        logging.error(err)
                        failed_list.append(user["login"])

                else:
                    already_exist_list.append(user["login"])

        if failed_list:
            logging.info(f"{len(failed_list)}/{total_user} are failed to import")
            logging.warning(f"❌ The following users are failed to import: {failed_list}")
            write_error(error_folder, "users", str(failed_list))
            return False
        else:
            logging.info(f"{len(imported_list)}/{total_user} are successfully imported")
            logging.info(f"{len(already_exist_list)}/{total_user} are already exist")
            logging.info("✅ Users have been successfully imported")
            return True

    def create(
        self,
        user_name: str,
        password: str,
        platforms: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        verify_ssl: Optional[bool] = None,
    ) -> bool:
        """Create a given user
        NB: You can only use this function if you have the admin role on the platform

        Parameters
        ----------
        user_name : str
            User name
        password: str
            User password
        platforms: List[str], optional
            List of platforms
        roles: List[str], optional
            List of roles
            By default, using ROLE_READER to have read access on the platform
        groups: List[str], optional
            List of groups
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
           True if user is created Error otherwise

        """
        if platforms is None:
            platforms = []
        if roles is None:
            roles = ["ROLE_READER"]
        if groups is None:
            groups = []
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        self.saagie_api.request_client.send(
            method="POST",
            url=f"{self.saagie_api.url_saagie}auth/api/users",
            raise_for_status=True,
            json_data={
                "login": user_name,
                "password": password,
                "platforms": platforms,
                "roles": roles,
                "groups": groups,
            },
            verify_ssl=verify_ssl,
        )
        logging.info("✅ User [%s] successfully created", user_name)
        return True

    def delete(self, user_name, verify_ssl: Optional[bool] = None) -> bool:
        """Delete a given user
        NB: You can only use this function if you have the admin role on the platform

        Parameters
        ----------
        user_name : str
            User name
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
           True if user is deleted Error otherwise

        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        self.saagie_api.request_client.send(
            method="DELETE",
            url=f"{self.saagie_api.url_saagie}auth/api/users/{user_name}",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        logging.info("✅ User [%s] successfully deleted", user_name)
        return True

    def edit_password(self, user_name, previous_pwd, new_pwd, verify_ssl: Optional[bool] = None):
        """Edit a given user's password
        NB: You can only use this function if you have the admin role on the platform

        Parameters
        ----------
        user_name : str
            User name
        previous_pwd: str
            Previous user password
        new_pwd: str
            New user password
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if user's password is successfully edited Error otherwise
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        self.saagie_api.request_client.send(
            method="PUT",
            url=f"{self.saagie_api.url_saagie}authentication/api/open/password/change",
            raise_for_status=True,
            json_data={"login": user_name, "oldPassword": previous_pwd, "newPassword": new_pwd},
            verify_ssl=verify_ssl,
        )
        logging.info("✅ Password of user [%s] successfully edited", user_name)
        return True
