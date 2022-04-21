from gql import gql
from .saagie_api_unit_test import create_gql_client
from saagieapi.docker_credentials.gql_queries import *


class TestDockerCredentials:

    def setup_method(self):
        self.client = create_gql_client()

    def test_get_all_docker_credentials(self):
        query = gql(gql_get_all_docker_credentials)
        self.client.validate(query)

    def test_get_docker_credentials(self):
        query = gql(gql_get_docker_credentials)
        self.client.validate(query)

    def test_create_docker_credentials(self):
        query = gql(gql_create_docker_credentials)
        self.client.validate(query)

    def test_upgrade_docker_credentials(self):
        query = gql(gql_upgrade_docker_credentials)
        self.client.validate(query)

    def test_delete_docker_credentials(self):
        query = gql(gql_delete_docker_credentials)
        self.client.validate(query)
