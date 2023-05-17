import logging
from typing import Dict

import requests
from requests import ConnectionError as requestsConnectionError
from requests import HTTPError, RequestException, Timeout

from ..utils.folder_functions import check_folder_path, create_folder, write_to_json_file


class Profiles:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(self, verify_ssl: bool = True) -> Dict:
        """Get profiles
        NB: You can only list profiles if you have the admin role on the platform
        Params
        ------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        dict
            Dict of profiles on the platform
        """
        try:
            response = requests.get(
                f"{self.saagie_api.url_saagie}profiles/api/",
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
        """Get profile info of a specific user
        NB: You can only get user's profile information if you have the admin role on the platform
        Params
        ------
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        Dict
            Dict of user's profile information on the platform
        """
        try:
            response = requests.get(
                f"{self.saagie_api.url_saagie}profiles/api/{user_name}",
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
        """Export profiles in a file
        NB: You can only export profiles if you have the admin role on the platform

        Parameters
        ----------
        output_folder : str
            Path to store the exported profiles
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if profiles are exported False otherwise
        """
        profiles = None
        try:
            profiles = self.list(verify_ssl=verify_ssl)
        except Exception as exception:
            logging.warning("❌ Cannot get the profile's information on the platform")
            logging.error("Something went wrong %s", exception)
        if profiles:
            output_folder = check_folder_path(output_folder)
            create_folder(output_folder)
            write_to_json_file(output_folder + "profiles.json", profiles)
            logging.info("✅ Profiles of the platform have been successfully exported")
            return True
        else:
            return False

    def edit(self, user_name, job_title: str = None, email: str = None, verify_ssl: bool = True) -> bool:
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
            By default, verification of SSL certification activated

        Returns
        -------
        bool
            True if profile is successfully edited error otherwise
        """
        params = {"login": user_name}
        previous_profile = self.get_info(user_name)
        if job_title:
            params["job"] = job_title
        else:
            params["job"] = previous_profile["job"]

        if email:
            params["email"] = email
        else:
            params["email"] = previous_profile["email"]

        try:
            response = requests.put(
                f"{self.saagie_api.url_saagie}profiles/api/{user_name}",
                auth=self.saagie_api.auth,
                headers={"Saagie-Realm": self.saagie_api.realm},
                json=params,
                verify=verify_ssl,
            )
            response.raise_for_status()
            logging.info("✅ Profile [%s] successfully edited", user_name)
            return True
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            raise
