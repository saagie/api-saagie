from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.pipelines.gql_queries import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("../..")
sys.path.append(dir_path + '/..')


class TestPipelines:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_pipelines(self):
        query = gql(gql_list_pipelines_for_project)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_pipeline(self):
        query = gql(gql_get_pipeline)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_stop_pipeline_instance(self):
        query = gql(gql_stop_pipeline_instance)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_gql_edit_pipeline(self):
        query = gql(gql_edit_pipeline)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_run_pipeline(self):
        query = gql(gql_run_pipeline)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_pipeline(self):
        query = gql(gql_create_pipeline)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_pipeline_instance(self):
        query = gql(gql_get_pipeline_instance)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_graph_pipeline(self):
        query = gql(gql_create_graph_pipeline)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_pipeline(self):
        query = gql(gql_delete_pipeline)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_upgrade_pipeline(self):
        query = gql(gql_upgrade_pipeline)
        result = self.client.validate(query)
        expected = None
        assert result == expected
