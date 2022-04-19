from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.docker_credentials.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(dir_path + '/..')


class TestDockerCredentials:

    def setup_method(self):
        self.client = create_gql_client()

    def test_get_all_docker_credentials(self):
        query = gql(gql_get_all_docker_credentials)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_docker_credentials(self):
        query = gql(gql_get_docker_credentials)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_docker_credentials(self):
        query = gql(gql_create_docker_credentials)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_upgrade_docker_credentials(self):
        query = gql(gql_upgrade_docker_credentials)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_docker_credentials(self):
        query = gql(gql_delete_docker_credentials)
        result = self.client.validate(query)
        expected = None
        assert result == expected
