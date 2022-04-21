from gql import gql
from saagie_api_unit_test import create_gql_client
from saagieapi.pipelines.gql_queries import *
from .saagie_api_unit_test import create_gql_client


class TestPipelines:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_pipelines(self):
        query = gql(gql_list_pipelines_for_project)
        self.client.validate(query)

    def test_get_pipeline(self):
        query = gql(gql_get_pipeline)
        self.client.validate(query)

    def test_stop_pipeline_instance(self):
        query = gql(gql_stop_pipeline_instance)
        self.client.validate(query)

    def test_gql_edit_pipeline(self):
        query = gql(gql_edit_pipeline)
        self.client.validate(query)

    def test_run_pipeline(self):
        query = gql(gql_run_pipeline)
        self.client.validate(query)

    def test_create_pipeline(self):
        query = gql(gql_create_pipeline)
        self.client.validate(query)

    def test_get_pipeline_instance(self):
        query = gql(gql_get_pipeline_instance)
        self.client.validate(query)

    def test_create_graph_pipeline(self):
        query = gql(gql_create_graph_pipeline)
        self.client.validate(query)

    def test_delete_pipeline(self):
        query = gql(gql_delete_pipeline)
        self.client.validate(query)

    def test_upgrade_pipeline(self):
        query = gql(gql_upgrade_pipeline)
        self.client.validate(query)
