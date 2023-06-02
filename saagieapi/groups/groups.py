import json
import logging
from typing import Dict, List, Optional

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file


class Groups:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(self, verify_ssl: Optional[bool] = None) -> List[Dict]:
        """Get groups
        NB: You can only list users if you have the admin role on the platform
        Params
        ------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        dict
            Dict of groups on the platform
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET",
            url=f"{self.saagie_api.url_saagie}auth/api/groups",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        logging.info("✅ Successfully list groups on the platform")
        return response.json()

    def get_permission(self, group_name: str, verify_ssl: Optional[bool] = None) -> Dict:
        """Get group's permissions
        NB: You can only list group's permission if you have the admin role on the platform
        Params
        ------
        group_name: str
            Name of the group
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        dict
            Dict of group's permissions
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET",
            url=f"{self.saagie_api.url_saagie}security/api/groups/{group_name}",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        logging.info(f"✅  Successfully list permissions of the group [{group_name}]")
        return response.json()

    def get_users(self, group_name, verify_ssl: Optional[bool] = None) -> Dict:
        """Get group's users
        NB: You can only list group's users if you have the admin role on the platform
        Params
        ------
        group_name: str
            Name of the group
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        dict
            Dict of group's users
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET",
            url=f"{self.saagie_api.url_saagie}auth/api/groups/{group_name}",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        logging.info("✅ Successfully list group's users on the platform")
        return response.json()

    def export(self, output_folder: str, error_folder: Optional[str] = "", verify_ssl: Optional[bool] = None) -> bool:
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
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if group is exported False otherwise
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
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
                group_user_list = self.get_users(group_name, verify_ssl=verify_ssl)
                if group_user_list:
                    write_to_json_file(output_folder + f"user_{group_name}.json", group_user_list)

                permission_list = self.get_permission(group_name, verify_ssl=verify_ssl)
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

    def create(self, group_name: str, users: List[str], verify_ssl: Optional[bool] = None) -> bool:
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
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if group is exported False otherwise
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        self.saagie_api.request_client.send(
            method="POST",
            url=f"{self.saagie_api.url_saagie}auth/api/groups",
            raise_for_status=True,
            json_data={"name": group_name, "users": users},
            verify_ssl=verify_ssl,
        )
        logging.info(f"✅ Successfully create group [{group_name}] on the platform")
        return True

    def edit_permission(
        self,
        group_name: str,
        authorizations: Optional[List[Dict]] = None,
        realm_authorization: Optional[Dict] = None,
        verify_ssl: Optional[bool] = None,
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
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if group's permission successfully edited False otherwise
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        previous_group_permission = self.get_permission(group_name, verify_ssl)
        params = {
            "role": previous_group_permission["role"],
            "authorizations": authorizations if authorizations else previous_group_permission["authorizations"],
            "realmAuthorization": realm_authorization
            if realm_authorization
            else previous_group_permission["realmAuthorization"],
        }

        self.saagie_api.request_client.send(
            method="PUT",
            url=f"{self.saagie_api.url_saagie}security/api/groups/{group_name}",
            raise_for_status=True,
            json_data=params,
            verify_ssl=verify_ssl,
        )
        logging.info(f"✅ Successfully edit group permission [{group_name}] on the platform")
        return True

    def delete(self, group_name: str, verify_ssl: Optional[bool] = None) -> bool:
        """Delete a given group

        Parameters
        ----------
        group_name : str
            Group name
        verify_ssl: bool, optional
           Enable or disable verification of SSL certification
           By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
           True if group is deleted Error otherwise

        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        self.saagie_api.request_client.send(
            method="DELETE",
            url=f"{self.saagie_api.url_saagie}auth/api/groups/{group_name}",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        logging.info("✅ Group [%s] successfully deleted", group_name)
        return True

    def import_from_json(
        self, path_to_folder: str, error_folder: Optional[str] = "", verify_ssl: Optional[bool] = None
    ) -> bool:
        """Import groups from JSON format
        NB: You can only use this function if you have the admin role on the platform
            All protected groups (created at platform installation) will not be imported.
            For the moment, authorizations of groups are not imported, so if you want the same authorization,
            you have to set up manually.

        Parameters
        ----------
        path_to_folder : str
            Path to the folder of the groups to import
        error_folder : str
            Path to store the failed imported groups in case of error.
            If not set, failed imported users not write
        verify_ssl: bool, optional
           Enable or disable verification of SSL certification
           By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if groups are imported False otherwise
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
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
                res = self.saagie_api.request_client.send(
                    method="GET",
                    url=f"{self.saagie_api.url_saagie}auth/api/groups/{group_name}",
                    raise_for_status=False,
                    verify_ssl=verify_ssl,
                )
                if res.status_code == 500:
                    groups_user_json_path = path_to_folder + f"groups/user_{group_name}.json"
                    group_permission_json_path = path_to_folder + f"groups/perm_{group_name}.json"
                    try:
                        with open(groups_user_json_path, "r", encoding="utf-8") as file:
                            group_user = json.load(file)
                        if group_user:
                            self.create(group_name=group_name, users=group_user["users"], verify_ssl=verify_ssl)

                        with open(group_permission_json_path, "r", encoding="utf-8") as file:
                            group_permission = json.load(file)
                        if group_permission:
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
