from gql import gql
from saagieapi.pipelines.gql_queries import *
from .saagie_api_unit_test import create_gql_client


class TestPipelines:

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_pipelines(self):
        project_id = "1234"
        instances_limit = " (limit: 1)"
        query = gql(gql_list_pipelines_for_project.format(project_id, instances_limit))
        self.client.validate(query)

    def test_get_pipeline(self):
        pipeline_id = 1
        query = gql(gql_get_pipeline.format(pipeline_id))
        self.client.validate(query)

    def test_stop_pipeline_instance(self):
        pipeline_instance_id = "1"
        query = gql(gql_stop_pipeline_instance.format(pipeline_instance_id))
        self.client.validate(query)

    def test_gql_edit_pipeline(self):
        query = gql(gql_edit_pipeline)
        self.client.validate(query)

    def test_run_pipeline(self):
        pipeline_id = "1"
        query = gql(gql_run_pipeline.format(pipeline_id))
        self.client.validate(query)

    def test_create_pipeline(self):
        project_id = "1"
        pipeline_name = "test"
        job_id_list = "[id1, id2, id3]"
        query = gql(gql_create_pipeline.format(pipeline_name, "", project_id, job_id_list))
        self.client.validate(query)

    def test_get_pipeline_instance(self):
        pipeline_instance_id = "1"
        query = gql(gql_get_pipeline_instance.format(pipeline_instance_id))
        self.client.validate(query)

    def test_create_graph_pipeline(self):
        pipeline_name = "test"
        project_id = "1"
        description = "test"
        release_note = "test"
        schedule_string = 'isScheduled: true, cronScheduling: "0 0 * * *", scheduleTimezone: "Pacific/Fakaofo"'
        query = gql(
            gql_create_graph_pipeline.format(pipeline_name, description, project_id, release_note, schedule_string))
        self.client.validate(query)

    def test_delete_pipeline(self):
        pipeline_id = "1"
        query = gql(gql_delete_pipeline.format(pipeline_id))
        self.client.validate(query)

    def test_upgrade_pipeline(self):
        query = gql(gql_upgrade_pipeline)
        self.client.validate(query)
