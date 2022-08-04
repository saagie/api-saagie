import logging
import sys

import requests
from requests import ConnectionError as requestsConnectionError
from requests import HTTPError, RequestException, Timeout


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, realm: str, url: str, platform: str, login: str, password: str):
        self._realm = realm
        self._url = url
        self._platform = platform
        self._login = login
        self._password = password
        self.token = self._authenticate(realm, url, login, password)

    def refresh_token(self):
        self.token = self._authenticate(self._realm, self._url, self._login, self._password)

    def __call__(self, req):
        req.headers["authorization"] = "Bearer " + self.token
        return req

    @staticmethod
    def _authenticate(realm: str, url: str, login: str, password: str) -> str:
        """
        Retrieve a Bearer connection token
        :param realm: platform url prefix (eg: saagie)
        :param url: platform URL (eg: https://saagie-workspace.prod.saagie.io)
        :param login: username to log in with
        :param password: password to log in with
        :return: a token
        """
        try:
            session = requests.session()
            session.headers["Content-Type"] = "application/json"
            session.headers["Saagie-Realm"] = realm
            response = session.post(
                url + "/authentication/api/open/authenticate", json={"login": login, "password": password}, verify=False
            )
            response.raise_for_status()
            return response.text
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            sys.exit(1)
