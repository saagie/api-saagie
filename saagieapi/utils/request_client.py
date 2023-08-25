import logging
from typing import Optional

import requests
from requests import ConnectionError as requestsConnectionError
from requests import HTTPError, RequestException, Timeout

from .bearer_auth import BearerAuth


class RequestClient:
    def __init__(self, auth: BearerAuth, realm: str, verify_ssl: bool):
        self.auth = auth
        self.realm = realm
        self.verify_ssl = verify_ssl

    def send(
        self,
        method: str,
        url: str,
        raise_for_status: bool,
        json_data: Optional[dict] = None,
        stream: Optional[bool] = None,
        verify_ssl: Optional[bool] = None,
    ) -> requests.Response:
        """
        Construct and send a Request

        Parameters
        ----------
        method: str
            method for the new Request object: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.
        url: str
            URL for the new Request object
        raise_for_status: bool
            Whether you want to raise for status code of response object
        json_data: dict, optional
            A JSON serializable Python object to send in the body of the Request
        stream: bool, optional
            if False, the response content will be immediately downloaded.
        verify_ssl: bool, optional
            Enable or disable verification of SSL certification
            By default, refers to self.verify_ssl

        Returns
        -------
        requests.Response
            Response object

        Raises
        ------
        HTTPError, requestsConnectionError, Timeout, RequestException
        When raise_for_status is True

        """
        verify_ssl = verify_ssl if verify_ssl is not None else self.verify_ssl
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers={"Saagie-Realm": self.realm},
                verify=verify_ssl,
                json=json_data,
                stream=stream,
                timeout=60,
            )
            if raise_for_status:
                response.raise_for_status()
            return response
        except (HTTPError, requestsConnectionError, Timeout, RequestException) as err:
            logging.error(err)
            if raise_for_status:
                raise
            return requests.Response()
