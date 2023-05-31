import json
import logging
from typing import Dict, List, Optional

import requests
from requests import ConnectionError as requestsConnectionError
from requests import HTTPError, RequestException, Timeout

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file


class Users:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(self, verify_ssl: bool = True) -> List[Dict]:
        """Get users
        NB: You can only list users if you have the admin role on the platform
        Params
        ------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

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
        try:
            response = requests.get(
                f"{self.saagie_api.url_saagie}auth/api/users",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info("✅ Successfully list users on the platform")
            return response.json()
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def get_info(self, user_name: str, verify_ssl: bool = True) -> Dict:
        """Get info of a specific user
        NB: You can only get user's information if you have the admin role on the platform
        Params
        ------
        user_name: str
            User's name
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

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
        try:
            response = requests.get(
                f"{self.saagie_api.url_saagie}auth/api/users/{user_name}",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
            )
            response.raise_for_status()
            return response.json()
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def export(self, output_folder: str, verify_ssl: bool = True) -> bool:
        """Export users in a file
        NB: You can only use this function if you have the admin role on the platform

        Parameters
        ----------
        output_folder : str, optional
            Path to store the exported users
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if users are exported False otherwise
        """
        users = None
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
        self, json_file: str, temp_pwd: str, error_folder: Optional[str] = "", verify_ssl: bool = True
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
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if users are all imported or already existed False otherwise

        """

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
                res = requests.get(
                    f"{self.saagie_api.url_saagie}auth/api/users/{user['login']}",
                    auth=self.saagie_api.auth,
                    headers={"Saagie-Realm": self.saagie_api.realm},
                    verify=verify_ssl,
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
        platforms: Optional[List[str]] = [],
        roles: Optional[List[str]] = ["ROLE_READER"],
        groups: Optional[List[str]] = [],
        verify_ssl: bool = True,
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
            By default, verification of SSL certification activated

        Returns
        -------
        bool
           True if user is created Error otherwise

        """
        try:
            response = requests.post(
                f"{self.saagie_api.url_saagie}auth/api/users",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                json={
                    "login": user_name,
                    "password": password,
                    "platforms": platforms,
                    "roles": roles,
                    "groups": groups,
                },
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info("✅ User [%s] successfully created", user_name)
            return True
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def delete(self, user_name, verify_ssl: bool = True) -> bool:
        """Delete a given user
        NB: You can only use this function if you have the admin role on the platform

        Parameters
        ----------
        user_name : str
            User name
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        bool
           True if user is deleted Error otherwise

        """

        try:
            response = requests.delete(
                f"{self.saagie_api.url_saagie}auth/api/users/{user_name}",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info("✅ User [%s] successfully deleted", user_name)
            return True
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def edit_password(self, user_name, previous_pwd, new_pwd, verify_ssl: bool = True):
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
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if user's password is successfully edited Error otherwise
        """
        try:
            response = requests.put(
                f"{self.saagie_api.url_saagie}authentication/api/open/password/change",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
                json={"login": user_name, "oldPassword": previous_pwd, "newPassword": new_pwd},
            )
            response.raise_for_status()
            logging.info("✅ Password of user [%s] successfully edited", user_name)
            return True
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise
