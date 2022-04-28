from gql import gql

from saagieapi.docker_credentials.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestDockerCredentials:

    def setup_method(self):
        self.client = create_gql_client()

    def test_get_all_docker_credentials(self):
        query = gql(GQL_GET_ALL_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_get_docker_credentials(self):
        query = gql(GQL_GET_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_create_docker_credentials(self):
        query = gql(GQL_CREATE_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_upgrade_docker_credentials(self):
        query = gql(GQL_UPGRADE_DOCKER_CREDENTIALS)
        self.client.validate(query)

    def test_delete_docker_credentials(self):
        query = gql(GQL_DELETE_DOCKER_CREDENTIALS)
        self.client.validate(query)
