# pylint: disable=attribute-defined-outside-init
from gql import gql

from saagieapi.pipelines.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestPipelines:
    def setup_method(self):
        self.client = create_gql_client()

    def test_list_pipelines_minimal(self):
        query = gql(GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL)
        self.client.validate(query)

    def test_list_pipelines(self):
        query = gql(GQL_LIST_PIPELINES_FOR_PROJECT)
        self.client.validate(query)

    def test_get_pipeline(self):
        query = gql(GQL_GET_PIPELINE)
        self.client.validate(query)

    def test_get_pipeline_by_name(self):
        query = gql(GQL_GET_PIPELINE_BY_NAME)
        self.client.validate(query)

    def test_stop_pipeline_instance(self):
        query = gql(GQL_STOP_PIPELINE_INSTANCE)
        self.client.validate(query)

    def test_gql_edit_pipeline(self):
        query = gql(GQL_EDIT_PIPELINE)
        self.client.validate(query)

    def test_run_pipeline(self):
        query = gql(GQL_RUN_PIPELINE)
        self.client.validate(query)

    def test_get_pipeline_instance(self):
        query = gql(GQL_GET_PIPELINE_INSTANCE)
        self.client.validate(query)

    def test_create_graph_pipeline(self):
        query = gql(GQL_CREATE_GRAPH_PIPELINE)
        self.client.validate(query)

    def test_delete_pipeline(self):
        query = gql(GQL_DELETE_PIPELINE)
        self.client.validate(query)

    def test_upgrade_pipeline(self):
        query = gql(GQL_UPGRADE_PIPELINE)
        self.client.validate(query)

    def test_rollback_pipeline(self):
        query = gql(GQL_ROLLBACK_PIPELINE_VERSION)
        self.client.validate(query)

    def test_delete_versions(self):
        query = gql(GQL_DELETE_PIPELINE_VERSION)
        self.client.validate(query)

    def test_delete_instances(self):
        query = gql(GQL_DELETE_PIPELINE_INSTANCE)
        self.client.validate(query)

    def test_delete_instances_by_selector(self):
        query = gql(GQL_DELETE_PIPELINE_INSTANCE_BY_SELECTOR)
        self.client.validate(query)

    def test_delete_instances_by_date(self):
        query = gql(GQL_DELETE_PIPELINE_INSTANCE_BY_DATE)
        self.client.validate(query)

    def test_count_deletable_instances_by_status(self):
        query = gql(GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_STATUS)
        self.client.validate(query)

    def test_count_deletable_instances_by_date(self):
        query = gql(GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_DATE)
        self.client.validate(query)

    def test_duplicate_pipeline(self):
        query = gql(GQL_DUPLICATE_PIPELINE)
        self.client.validate(query)
