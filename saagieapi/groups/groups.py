import json
import logging
from typing import Dict, List, Optional

import requests
from requests import ConnectionError as requestsConnectionError
from requests import HTTPError, RequestException, Timeout

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file


class Groups:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(self, verify_ssl: bool = True) -> List[Dict]:
        """Get groups
        NB: You can only list users if you have the admin role on the platform
        Params
        ------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        dict
            Dict of groups on the platform
        """
        try:
            response = requests.get(
                f"{self.saagie_api.url_saagie}auth/api/groups",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info("✅ Successfully list groups on the platform")
            return response.json()
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def get_permission(self, group_name: str, verify_ssl: bool = True) -> Dict:
        """Get group's permissions
        NB: You can only list group's permission if you have the admin role on the platform
        Params
        ------
        group_name: str
            Name of the group
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        dict
            Dict of group's permissions
        """
        try:
            response = requests.get(
                f"{self.saagie_api.url_saagie}security/api/groups/{group_name}",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info(f"✅  Successfully list permissions of the group [{group_name}]")
            return response.json()
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def get_users(self, group_name, verify_ssl: bool = True) -> Dict:
        """Get group's users
        NB: You can only list group's users if you have the admin role on the platform
        Params
        ------
        group_name: str
            Name of the group
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        dict
            Dict of group's users
        """

        try:
            response = requests.get(
                f"{self.saagie_api.url_saagie}auth/api/groups/{group_name}",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info("✅ Successfully list group's users on the platform")
            return response.json()
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def export(self, output_folder: str, error_folder: Optional[str] = "", verify_ssl: bool = True) -> bool:
        """Export groups
        NB: You can only export group's information if you have the admin role on the platform
        Params
        ------
        output_folder: str
            Folder to store the exported groups
        error_folder: str
            Path to store the not correctly exported group in case of error.
            If not set, not correctly exported group is not write
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if group is exported False otherwise
        """
        output_folder = check_folder_path(output_folder)
        groups = self.list(verify_ssl)
        list_failed = []

        if groups:
            create_folder(output_folder)
            write_to_json_file(output_folder + "groups.json", groups)
            group_names = [group["name"] for group in groups]
            output_folder = check_folder_path(output_folder + "groups/")
            create_folder(output_folder)
        else:
            logging.info("No group(s) to export")
            return True

        for group_name in group_names:
            try:
                group_user_list = self.get_users(group_name)
                if group_user_list:
                    write_to_json_file(output_folder + f"user_{group_name}.json", group_user_list)

                permission_list = self.get_permission(group_name)
                if permission_list:
                    write_to_json_file(output_folder + f"perm_{group_name}.json", permission_list)

            except Exception as exception:
                logging.error("Something went wrong when getting group's users or group's permissions: %s", exception)
                list_failed.append(group_name)
        if list_failed:
            logging.warning(f"❌ The following groups are failed to export: {list_failed}")
            write_error(error_folder, "groups", str(list_failed))
            return False
        else:
            logging.info("✅ Groups have been successfully exported")
            return True

    def create(self, group_name: str, users: List[str], verify_ssl: bool = True) -> bool:
        """Create a group
        NB: You can only create group if you have the admin role on the platform
        Params
        ------
        group_name: str
            Name of the group
        users: List[str]
            Group's users
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if group is exported False otherwise
        """
        try:
            response_group_user = requests.post(
                f"{self.saagie_api.url_saagie}auth/api/groups",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                json={"name": group_name, "users": users},
                verify=verify_ssl,
            )
            response_group_user.raise_for_status()

            logging.info(f"✅ Successfully create group [{group_name}] on the platform")
            return True
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def edit_permission(
        self,
        group_name: str,
        authorizations: Optional[List[Dict]] = None,
        realm_authorization: Optional[Dict] = None,
        verify_ssl: bool = True,
    ) -> bool:
        """Create a group
        NB: You can only create group if you have the admin role on the platform
        Params
        ------
        group_name: str
            Name of the group
        authorizations: Optional[List[Dict]]
            Group's authorization on the platform
            if not filled, defaults to current value
            For example:
            [
               {
                 "platformId": 1,
                 "platformName": "Dev",
                 "permissions": [
                   {
                     "artifact": {
                       "id": "project_id",
                       "type": "PROJECT"
                     },
                     "role": "ROLE_PROJECT_VIEWER"
                   }
                 ]
               }
             ]
        realm_authorization: Optional[Dict]
             Dict of authorization to technology catalog and cluster overview
             if not filled, defaults to current value
             For example:
             {
               "permissions": [
                 {
                   "artifact": {
                     "type": "TECHNOLOGY_CATALOG"
                   },
                   "role": "ROLE_ACCESS"
                 },
                 {
                   "artifact": {
                     "type": "OPERATIONS"
                   },
                   "role": "ROLE_ACCESS"
                 },
               ]
             }
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if group's permission successfully edited False otherwise
        """
        previous_group_permission = self.get_permission(group_name, verify_ssl)
        params = {
            "role": previous_group_permission["role"],
            "authorizations": authorizations if authorizations else previous_group_permission["authorizations"],
            "realmAuthorization": realm_authorization
            if realm_authorization
            else previous_group_permission["realmAuthorization"],
        }

        try:
            response_group_permission = requests.put(
                f"{self.saagie_api.url_saagie}security/api/groups/{group_name}",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                json=params,
                verify=verify_ssl,
            )
            response_group_permission.raise_for_status()

            logging.info(f"✅ Successfully edit group permission [{group_name}] on the platform")
            return True
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def delete(self, group_name: str, verify_ssl: bool = True) -> bool:
        """Delete a given group

        Parameters
        ----------
        group_name : str
            Group name
        verify_ssl: bool, optional
           Enable or disable verification of SSL certification
           By default, verification of SSL certification activated

        Returns
        -------
        bool
           True if group is deleted Error otherwise

        """

        try:
            response = requests.delete(
                f"{self.saagie_api.url_saagie}auth/api/groups/{group_name}",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info("✅ Group [%s] successfully deleted", group_name)
            return True
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise

    def import_from_json(self, path_to_folder: str, error_folder: str, verify_ssl: bool = True):
        """Import groups from JSON format
        NB: You can only use this function if you have the admin role on the platform
            All protected groups (created at platform installation) will not be imported.

        Parameters
        ----------
        path_to_folder : str
            Path to the folder of the groups to import
        error_folder : str
            Path to the folder of the groups to import
        verify_ssl: bool, optional
           Enable or disable verification of SSL certification
           By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if groups are imported False otherwise
        """

        path_to_folder = check_folder_path(path_to_folder)
        groups_json_path = path_to_folder + "groups.json"
        bypassed_list = []
        failed_list = []
        already_exist_list = []
        imported_list = []
        try:
            with open(groups_json_path, "r", encoding="utf-8") as file:
                groups_list = json.load(file)
        except Exception as exception:
            logging.warning("Cannot open the JSON file %s", groups_json_path)
            logging.error("Something went wrong %s", exception)
            return False
        total_group = len(groups_list)

        for group in groups_list:
            if group["protected"]:
                bypassed_list.append(group["name"])
            else:
                group_name = group["name"]
                res = requests.get(
                    f"{self.saagie_api.url_saagie}auth/api/groups/{group_name}",
                    auth=self.saagie_api.auth,
                    headers={"Saagie-Realm": self.saagie_api.realm},
                    verify=verify_ssl,
                )
                if res.status_code == 500:
                    groups_user_json_path = path_to_folder + f"groups/user_{group_name}.json"
                    group_permission_json_path = path_to_folder + f"groups/perm_{group_name}.json"
                    try:
                        with open(groups_user_json_path, "r", encoding="utf-8") as file:
                            group_user = json.load(file)
                        if group_user:
                            self.create(group_name=group_name, users=group_user["users"])

                        with open(group_permission_json_path, "r", encoding="utf-8") as file:
                            group_permission = json.load(file)
                        if group_permission:
                            # TODO: for authorizations, ID needed, not import ?
                            self.edit_permission(
                                group_name=group_name,
                                authorizations=[],
                                realm_authorization=group_permission["realmAuthorization"],
                                verify_ssl=verify_ssl,
                            )
                        imported_list.append(group_name)
                    except Exception as err:
                        logging.error(f"Something went wrong when importing group [{group_name}]: %s", err)
                        failed_list.append(group_name)

                else:
                    already_exist_list.append(group["name"])
        if failed_list:
            logging.info(f"{len(failed_list)}/{total_group} are failed to import")
            logging.warning(f"❌ The following groups are failed to import: {failed_list}")
            write_error(error_folder, "groups", str(failed_list))
            return False
        else:
            logging.info(f"{len(imported_list)}/{total_group} are successfully imported")
            logging.info(f"{len(already_exist_list)}/{total_group} are already exist")
            logging.info("✅ Groups have been successfully imported")
            return True
