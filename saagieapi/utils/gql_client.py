import logging
from typing import Dict, Optional

import requests
from gql import Client
from gql.transport.exceptions import TransportQueryError, TransportServerError
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode

from .bearer_auth import BearerAuth
from .rich_console import console


class GqlClient:
    def __init__(self, api_endpoint: str, auth: BearerAuth, retries: int = 0):
        self.auth = auth
        self._transport = RequestsHTTPTransport(
            url=api_endpoint, auth=auth, use_json=True, verify=False, retries=retries, timeout=10
        )
        self.client: Client = Client(transport=self._transport, fetch_schema_from_transport=True)

    def execute(
        self,
        query: DocumentNode,
        variable_values: Optional[Dict] = None,
        upload_files: Optional[bool] = False,
        is_retry: Optional[bool] = False,
        pprint_result: Optional[bool] = None,
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
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict containing the query result
        """
        pprint_result = pprint_result if pprint_result is not None else self.pprint_global
        try:
            result = self.client.execute(document=query, variable_values=variable_values, upload_files=upload_files)
            if pprint_result:
                console.print(result)
            return result
        except TransportQueryError as transport_error:
            logging.warning("❗Unexpected error, printing result anyway")
            console.print_exception(show_locals=False, max_frames=2)
            if pprint_result:
                console.print(transport_error.data)
            return transport_error.data
        except TransportServerError as transport_error:
            if transport_error.code == 401 and not is_retry:
                logging.warning("❗Authentication error, error 401 received, trying to refresh token")
                try:
                    self.auth.refresh_token()
                    logging.warning("🔁 Token successfully refreshed")
                except requests.exceptions.HTTPError as errh:
                    raise RuntimeError(f"❌ Http Error: {errh}") from transport_error
                return self.execute(
                    query=query, variable_values=variable_values, upload_files=upload_files, is_retry=True
                )
            raise transport_error
        except Exception as exception:
            console.print_exception(show_locals=False, max_frames=2)
            raise exception
