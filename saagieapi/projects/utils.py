import importlib.metadata
import json
import logging
from pathlib import Path
from json import JSONDecodeError
from packaging import version

import requests
from packaging.version import Version

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARN)
logging.getLogger("gql").setLevel(logging.WARN)

dir_path = Path(__file__).resolve().parent


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


def __get_saagie_current_version(auth: BearerAuth, url_saagie: str) -> str:
    """
    Retrieve the current Saagie version on the target platform
    :param auth: BearerAuth object
    :param url_saagie: Saagie URL
    :return: Saagie major version
    """
    try:
        saagie_versions = auth(requests.session()).get(f"{url_saagie}version.json").json()
        return saagie_versions['major']
    except (JSONDecodeError, KeyError):
        logging.warning("Could not get Saagie version")
        return "unknown-version "


def __get_min_max_saagie_versions(saagie_current_version: str) -> (Version, Version):
    """
    Retrieve the minimum and maximum Saagie version supported by the Saagie API
    based on the compatibility matrix
    :param saagie_current_version: Saagie platform current version
    :return: (min_version, max_version)
    """
    saagie_compatibility_matrix = json.load(open(dir_path.joinpath('compatibility_matrix.json')))
    logging.debug(f"Compatibility matrix : {saagie_compatibility_matrix}")
    try:
        compatible_versions = saagie_compatibility_matrix[saagie_current_version]
        minimal_version = version.parse(compatible_versions.get("min_api_saagie_version", "0"))
        maximal_version = version.parse(compatible_versions.get("max_api_saagie_version", "9.9"))
        return minimal_version, maximal_version
    except KeyError:
        logging.warning(f"Could not find your Saagie version ({saagie_current_version}) in the compatibility matrix")
        return version.parse("0"), version.parse("9.9")


def check_saagie_version_compatibility(auth: BearerAuth, url_saagie: str):
    """
    Check if the Saagie version is compatible with the Saagie API version and display warnings if not
    :param auth: BearerAuth object
    :param url_saagie: Saagie URL
    """
    saagie_current_version = __get_saagie_current_version(auth, url_saagie)
    saagie_api_current_version = version.parse(importlib.metadata.version("saagieapi"))

    logging.info(f"Current saagie version : {saagie_current_version}")
    logging.info(f"Current api-saagie version : {saagie_api_current_version}")
    min_version, max_version = __get_min_max_saagie_versions(saagie_current_version)
    if saagie_api_current_version < min_version:
        logging.warning(
            f"You are using a saagie-api version ({saagie_api_current_version}) "
            f"not compatible with your Saagie platform (Saagie v.{saagie_current_version})")
        logging.warning(
            f"Your Saagie platform requires at least the version {min_version} "
            f"of saagieapi. Please consider upgrading.")
    if saagie_api_current_version > max_version:
        logging.warning(
            f"You are using a saagie-api version ({saagie_api_current_version}) "
            f"not compatible with your Saagie platform (Saagie v.{saagie_current_version})")
        logging.warning(
            f"Your Saagie platform is not compatible with versions > {max_version} "
            f"of saagieapi. Please consider downgrading.")
