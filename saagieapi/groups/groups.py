import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file


class Groups:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(self, verify_ssl: Optional[bool] = None) -> List[Dict]:
        """Get groups
        NB: You can only list users if you have the admin role on the platform

        Parameters
        ----------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        dict
            Dict of groups on the platform

        Examples
        --------
        >>> saagieapi.groups.list()
        [
            {
                "name": "administrators",
                "protected": True
            },
            {
                "name": "test_group",
                "protected": False
            }
        ]
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

        Parameters
        ----------
        group_name: str
            Name of the group
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        dict
            Dict of group's permissions

        Examples
        --------
        >>> saagieapi.groups.get_permission(group_name="test_group")
        {
            "name": "test_group",
            "role": "ROLE_READER",
            "authorizations": [
                {
                    "platformId": 1,
                    "platformName": "Dev",
                    "permissions": [
                        {
                            "artifact": {
                                "type": "PROJECTS_ENVVAR_EDITOR"
                            },
                            "role": "ROLE_PROJECT_ENVVAR_EDITOR"
                        },
                        {
                            "artifact": {
                                "id": "87ad5abb-5ee9-4e7d-8c82-5b40378ad931",
                                "type": "PROJECT"
                            },
                            "role": "ROLE_PROJECT_MANAGER"
                        }
                    ]
                }
            ],
            "protected": False,
            "realmAuthorization": {
                "permissions": [
                    {
                        "artifact": {
                            "type": "TECHNOLOGY_CATALOG"
                        },
                        "role": "ROLE_ACCESS"
                    }
                ]
            }
        }
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET",
            url=f"{self.saagie_api.url_saagie}security/api/groups/{group_name}",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        logging.info("✅  Successfully list permissions of the group [{%s}]", group_name)
        return response.json()

    def get_users(self, group_name, verify_ssl: Optional[bool] = None) -> Dict:
        """Get group's users
        NB: You can only list group's users if you have the admin role on the platform

        Parameters
        ----------
        group_name: str
            Name of the group
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        dict
            Dict of group's users

        Examples
        --------
        >>> saagieapi.groups.get_users(group_name="test_group")
        {
            "name": "test_group",
            "users": ["test_user"],
            "protected": False
        }
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

        Parameters
        ----------
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

        Examples
        --------
        >>> saagieapi.groups.export(
        ...     output_folder="./output/groups/",
        ...     error_folder=""./output/error_folder/"
        ... )
        True
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        output_folder = check_folder_path(output_folder)
        if groups := self.list(verify_ssl):
            create_folder(output_folder)
            write_to_json_file(f"{output_folder}groups.json", groups)
            group_names = [group["name"] for group in groups]
            output_folder = check_folder_path(f"{output_folder}groups/")
            create_folder(output_folder)
        else:
            logging.info("No group(s) to export")
            return True

        list_failed = []
        for group_name in group_names:
            try:
                if group_user_list := self.get_users(group_name, verify_ssl=verify_ssl):
                    write_to_json_file(f"{output_folder}user_{group_name}.json", group_user_list)

                if permission_list := self.get_permission(group_name, verify_ssl=verify_ssl):
                    write_to_json_file(f"{output_folder}perm_{group_name}.json", permission_list)

            except Exception as exception:
                logging.error("Something went wrong when getting group's users or group's permissions: %s", exception)
                list_failed.append(group_name)
        if list_failed:
            logging.warning("❌ The following groups are failed to export: %s", list_failed)
            write_error(error_folder, "groups", str(list_failed))
            return False

        logging.info("✅ Groups have been successfully exported")
        return True

    def create(self, group_name: str, users: List[str], verify_ssl: Optional[bool] = None) -> bool:
        """Create a group
        NB: You can only create group if you have the admin role on the platform

        Parameters
        ----------
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

        Examples
        --------
        >>> saagieapi.groups.create(
        ...     group_name="group_reader",
        ...     users=["user1", "user2"]
        ... )
        True
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        self.saagie_api.request_client.send(
            method="POST",
            url=f"{self.saagie_api.url_saagie}auth/api/groups",
            raise_for_status=True,
            json_data={"name": group_name, "users": users},
            verify_ssl=verify_ssl,
        )
        logging.info("✅ Successfully create group [%s] on the platform", group_name)
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

        Parameters
        ----------
        group_name: str
            Name of the group
        authorizations: Optional[List[Dict]]
            Group's authorization on the platform
            if not filled, defaults to current value
        realm_authorization: Optional[Dict]
            Dict of authorization to technology catalog and cluster overview
            if not filled, defaults to current value
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if group's permission successfully edited False otherwise

        Examples
        --------
        >>> saagieapi.groups.edit_permission(
        ...     group_name="group_reader",
        ...     authorizations=[
        ...         {
        ...             "platformId": 1,
        ...             "platformName": "Dev",
        ...             "permissions": [
        ...                 {
        ...                     "artifact": {
        ...                         "id": "project_id",
        ...                         "type": "PROJECT"
        ...                     },
        ...                     "role": "ROLE_PROJECT_VIEWER"
        ...                 }
        ...             ]
        ...         }
        ...     ],
        ...     realm_authorization={
        ...         "permissions": [
        ...             {
        ...                 "artifact": {
        ...                     "type": "TECHNOLOGY_CATALOG"
        ...                 },
        ...                 "role": "ROLE_ACCESS"
        ...             }
        ...         ]
        ...     }
        ... )
        True
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        previous_group_permission = self.get_permission(group_name, verify_ssl)
        params = {
            "role": previous_group_permission["role"],
            "authorizations": authorizations or previous_group_permission["authorizations"],
            "realmAuthorization": realm_authorization or previous_group_permission["realmAuthorization"],
        }

        self.saagie_api.request_client.send(
            method="PUT",
            url=f"{self.saagie_api.url_saagie}security/api/groups/{group_name}",
            raise_for_status=True,
            json_data=params,
            verify_ssl=verify_ssl,
        )
        logging.info("✅ Successfully edit group permission [%s] on the platform", group_name)
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

        Examples
        --------
        >>> saagieapi.groups.delete(group_name="test_user")
        True
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

        Examples
        --------
        >>> saagieapi.groups.import_from_json(
        ...     path_to_folder="/path/to/the/group/folder",
        ...     error_folder="/path/to/the/error/folder"
        ... )
        True
        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        path_to_folder = Path(path_to_folder)
        groups_json_path = path_to_folder / "groups.json"
        bypassed_list = []
        failed_list = []
        already_exist_list = []
        imported_list = []
        try:
            with groups_json_path.open("r", encoding="utf-8") as file:
                groups_list = json.load(file)
        except Exception as exception:
            logging.warning("Cannot open the JSON file %s", groups_json_path)
            logging.error("Something went wrong %s", exception)
            return False
        total_group = len(groups_list)

        for group in groups_list:
            if group["protected"]:
                bypassed_list.append(group["name"])
                continue

            group_name = group["name"]
            res = self.saagie_api.request_client.send(
                method="GET",
                url=f"{self.saagie_api.url_saagie}auth/api/groups/{group_name}",
                raise_for_status=False,
                verify_ssl=verify_ssl,
            )
            if res.status_code != 500:
                already_exist_list.append(group["name"])
                continue

            groups_user_json_path = path_to_folder / "groups" / f"user_{group_name}.json"
            group_permission_json_path = path_to_folder / "groups" / f"perm_{group_name}.json"
            try:
                with groups_user_json_path.open("r", encoding="utf-8") as file:
                    group_user = json.load(file)
                if group_user:
                    self.create(group_name=group_name, users=group_user["users"], verify_ssl=verify_ssl)

                with group_permission_json_path.open("r", encoding="utf-8") as file:
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
                logging.error("Something went wrong when importing group [%s]: %s", group_name, err)
                failed_list.append(group_name)
        if failed_list:
            logging.info("%s/%s are failed to import", len(failed_list), total_group)
            logging.warning("❌ The following groups are failed to import: %s", failed_list)
            write_error(error_folder, "groups", str(failed_list))
            return False

        logging.info("%s/%s are successfully imported", len(imported_list), total_group)
        logging.info("%s/%s are already exist", len(already_exist_list), total_group)
        logging.info("✅ Groups have been successfully imported")
        return True
