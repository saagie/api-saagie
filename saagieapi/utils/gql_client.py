import logging
from typing import Dict, Optional

import requests
from gql import Client
from gql.transport.exceptions import TransportServerError
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode

from .bearer_auth import BearerAuth


class GqlClient:
    def __init__(self, api_endpoint: str, auth: BearerAuth, retries: int = 0):
        self.auth = auth
        self._transport = RequestsHTTPTransport(
            url=api_endpoint, auth=auth, use_json=True, verify=False, retries=retries
        )
        self.client: Client = Client(transport=self._transport, fetch_schema_from_transport=True)

    def execute(
        self,
        query: DocumentNode,
        variable_values: Optional[Dict] = None,
        upload_files: Optional[bool] = False,
        is_retry: bool = False,
    ) -> Dict:
        """
        Execute a GraphQL query and returns the result
        Parameters
        ----------
        query : DocumentNode
            dict containing the params of the technology
        variable_values : Optional[Dict]
            dict containing the params of the query
        upload_files : bool
            whether to upload files
        is_retry : bool
            whether this execution is a retry

        Returns
        -------
        dict
            Dict containing the query result
        """
        try:
            return self.client.execute(document=query, variable_values=variable_values, upload_files=upload_files)
        except TransportServerError as transport_error:
            if transport_error.code == 401 and not is_retry:
                logging.warning("Authentication error, error 401 received, trying to refresh token")
                try:
                    self.auth.refresh_token()
                    logging.warning("Token successfully refreshed")
                except requests.exceptions.HTTPError as errh:
                    raise RuntimeError(f"Http Error: {errh}") from transport_error
                return self.execute(
                    query=query, variable_values=variable_values, upload_files=upload_files, is_retry=True
                )

            raise transport_error
