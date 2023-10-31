import logging
from pathlib import Path
from typing import Dict, Optional

from ..utils.folder_functions import create_folder, write_to_json_file


class Profiles:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(self, verify_ssl: Optional[bool] = None) -> Dict:
        """Get profiles
        NB: You can only list profiles if you have the admin role on the platform

        Parameters
        ----------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        dict
            Dict of profiles on the platform

        Examples
        --------
        >>> saagieapi.profiles.list()
        [
            {
                "login": "test_user",
                "job": "DATA_ENGINEER",
                "email": "test_user@gmail.com"
            },
            {
                "login": "customer_admin",
                "job": None,
                "email": None
            }
        ]
        """

        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET", url=f"{self.saagie_api.url_saagie}profiles/api/", raise_for_status=True, verify_ssl=verify_ssl
        )
        logging.info("✅ Successfully list users on the platform")
        return response.json()

    def get_info(self, user_name: str, verify_ssl: Optional[bool] = None) -> Dict:
        """Get profile info of a specific user
        NB: You can only get user's profile information if you have the admin role on the platform

        Parameters
        ----------
        user_name: str
            User's name
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        Dict
            Dict of user's profile information on the platform

        Examples
        --------
        >>> saagieapi.profiles.get_info(user_name="test_user")
        {
            "login": "test_user",
            "job": "DATA_ENGINEER",
            "email": "test_user@gmail.com"
        }
        """

        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        response = self.saagie_api.request_client.send(
            method="GET",
            url=f"{self.saagie_api.url_saagie}profiles/api/{user_name}",
            raise_for_status=True,
            verify_ssl=verify_ssl,
        )
        return response.json()

    def export(self, output_folder: str, verify_ssl: Optional[bool] = None) -> bool:
        """Export profiles in a file
        NB: You can only export profiles if you have the admin role on the platform

        Parameters
        ----------
        output_folder : str
            Path to store the exported profiles
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if profiles are exported False otherwise

        Examples
        --------
        >>> saagieapi.profiles.export(output_folder="/tmp/")
        True
        """

        profiles = None
        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        try:
            profiles = self.list(verify_ssl=verify_ssl)
        except Exception as exception:
            logging.warning("❌ Cannot get the profile's information on the platform")
            logging.error("Something went wrong %s", exception)
        if profiles:
            output_folder = Path(output_folder)
            create_folder(output_folder)
            write_to_json_file(output_folder / "profiles.json", profiles)
            logging.info("✅ Profiles of the platform have been successfully exported")
            return True
        return False

    def edit(self, user_name: str, job_title: str = None, email: str = None, verify_ssl: Optional[bool] = None) -> bool:
        """Edit a profile
        NB: You can edit a user's profile if you have the admin role on the platform

        Parameters
        ----------
        user_name : str
            User name
        job_title : str
            Job title, for example: DATA_ENGINEER, PROJECT_MANAGER
            If not filled, defaults to current value, else it will change the job title
        email : str
            Email of the profile
            If not filled, defaults to current value, else it will change the user's email
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to saagie_api.verify_ssl

        Returns
        -------
        bool
            True if profile is successfully edited error otherwise

        Examples
        --------
        >>> saagieapi.profiles.edit(
        ...     user_name="test_user",
        ...     job_title="PROJECT_MANAGER",
        ...     email="test.user@gmail.com"
        ... )
        True
        """

        verify_ssl = verify_ssl if verify_ssl is not None else self.saagie_api.verify_ssl
        previous_profile = self.get_info(user_name, verify_ssl=verify_ssl)
        params = {
            "login": user_name,
            "job": job_title or previous_profile["job"],
            "email": email or previous_profile["email"],
        }

        self.saagie_api.request_client.send(
            method="PUT",
            url=f"{self.saagie_api.url_saagie}profiles/api/{user_name}",
            raise_for_status=True,
            json_data=params,
            verify_ssl=verify_ssl,
        )
        logging.info("✅ Profile [%s] successfully edited", user_name)
        return True
