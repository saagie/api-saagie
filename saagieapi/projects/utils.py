import importlib.metadata
import json
import logging
from json import JSONDecodeError
from packaging import version

import requests


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, realm, url, platform, login, password):
        self.token = self._authenticate(realm, url, login, password)
        self.platform = platform
        self.url = url

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

    @staticmethod
    def _authenticate(realm, url, login, password):
        """
        Retrieve a Bearer connection token
        :param realm: platform url prefix (eg: saagie)
        :param url: platform URL (eg: https://saagie-workspace.prod.saagie.io)
        :param login: username to login with
        :param password: password to login with
        :return: a token
        """
        s = requests.session()
        s.headers["Content-Type"] = "application/json"
        s.headers["Saagie-Realm"] = realm
        r = s.post(url + '/authentication/api/open/authenticate',
                   json={'login': login, 'password': password},
                   verify=False)
        return r.text


def get_saagie_version(auth: BearerAuth, url_saagie: str):
    s = auth(requests.session())
    saagie_compatibility_matrix = json.load(open("saagieapi/compatibility_matrix.json"))
    saagie_api_current_version = importlib.metadata.version("saagieapi")
    logging.debug(f"Compatibility matrix : {saagie_compatibility_matrix}")
    logging.debug(f"Current api-saagie version : {saagie_api_current_version}")

    try:
        saagie_versions = json.loads(s.get(f"{url_saagie}version.json").text)
        saagie_current_version = saagie_versions['major']
        compatible_versions = saagie_compatibility_matrix[saagie_current_version]
        minimal_version = compatible_versions["min_api_saagie_version"]
        maximal_version = compatible_versions["max_api_saagie_version"]
        if version.parse(saagie_api_current_version) < version.parse(minimal_version):
            print("babla")
            logging.warning(
                f"You are using a saagiepi version ({saagie_api_current_version}) "
                f"not compatible with your Saagie platform (Saagie v.{saagie_current_version})")
            logging.warning(
                f"Your Saagie platform requires at least the version {minimal_version} "
                f"of saagieapi. Please consider upgrading.")
        if version.parse(saagie_api_current_version) > version.parse(maximal_version):
            logging.warning(
                f"You are using a saagiepi version ({saagie_api_current_version}) "
                f"not compatible with your Saagie platform (Saagie v.{saagie_current_version})")
            logging.warning(
                f"Your Saagie platform is not compatible with versions > {maximal_version} "
                f"of saagieapi. Please consider downgrading.")

    except JSONDecodeError:
        logging.warning("Could not get Saagie version")
