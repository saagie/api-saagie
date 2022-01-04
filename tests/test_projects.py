from gql import gql
from gql import Client
from graphql import build_ast_schema
from graphql.language.parser import parse
from saagieapi.projects.gql_template import *

import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(dir_path + '/..')


def create_gql_client(schema_file):
    """
    Return a GQL Client with a defined schema
    :param schema_file: String, File path of schema
    :return: GQL Client
    """
    with open(schema_file) as source:
        document = parse(source.read())
    schema = build_ast_schema(document)
    client = Client(schema=schema)
    return client


class TestGQLTemplate:

    def setup_method(self):
        self.client = create_gql_client(dir_path + '/schema.graphqls')

    # ######################################################
    # ###                    env vars                   ####
    # ######################################################

    def test_get_global_env_vars(self):
        query = gql(gql_get_global_env_vars)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_global_env_var(self):
        name = 'test'
        value = 'test'
        description = ''
        is_password = False
        query = gql(gql_create_global_env_var.format(name, value, description,
                                                     str(is_password).lower()))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_env_var(self):
        env_var_id = '1234'
        query = gql(gql_delete_env_var.format(env_var_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_env_vars(self):
        project_id = "1234"
        query = gql(gql_get_project_env_vars.format(project_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_project_env_var(self):
        project_id = '1234'
        name = 'test'
        value = 'test'
        description = ''
        is_password = False
        query = gql(gql_create_project_env_var.format(
            project_id,
            name,
            value, description,
            str(is_password).lower()
        ))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    # ##########################################################
    # ###                    cluster                        ####
    # ##########################################################

    def test_get_cluster_capacity(self):
        query = gql(gql_get_cluster_info)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    # ######################################################
    # ###                    projects                   ####
    # ######################################################

    def test_get_projects_info(self):
        query = gql(gql_get_projects_info)
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_info(self):
        project_id = "1234"
        query = gql(gql_get_project_info.format(project_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_gql_create_project_without_group_block(self):
        name = "test_project"
        description = ""
        technologies = ['{id: "{1234}"}']
        group_block = ""
        query = gql(gql_create_project.format(name,
                                              description,
                                              group_block,
                                              ', '.join(technologies)))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_project_with_group_block(self):
        name = "test_project"
        description = ""
        technologies = ['{id: "{1234}"}']
        group = "test_group"
        role = "ROLE_PROJECT_VIEWER"
        group_block = group_block_template.format(group, role)
        query = gql(gql_create_project.format(name,
                                              description,
                                              group_block,
                                              ', '.join(technologies)))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_project(self):
        job_id = "1234"
        query = gql(gql_delete_project.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    # ######################################################
    # ###                      jobs                     ####
    # ######################################################

    def test_get_project_jobs(self):
        project_id = "1234"
        instances_limit = " (limit: 3)"
        query = gql(gql_get_project_jobs.format(project_id, instances_limit))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_job(self):
        job_id = "1234"
        query = gql(gql_get_project_job.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_job_instance(self):
        job_instance_id = "job_instance_1234"
        query = gql(gql_get_job_instance.format(job_instance_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_run_job(self):
        job_id = "job_1234"
        query = gql(gql_run_job.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_stop_job(self):
        job_id = "job_1234"
        query = gql(gql_stop_job_instance.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_edit_job(self):
        job_id = "job_1234"

        query = gql(gql_edit_job.format(job_id, ""))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_delete_job(self):
        job_id = "1234"
        query = gql(gql_delete_job.format(job_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    # ######################################################
    # ###                      apps                     ####
    # ######################################################

    def test_get_project_web_apps(self):
        project_id = "1234"
        instances_limit = " (limit: 1)"
        query = gql(gql_get_project_web_apps.format(project_id,
                                                    instances_limit))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_web_app(self):
        web_app_id = "1"
        query = gql(get_project_web_app.format(web_app_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_project_app(self):
        app_id = "1"
        query = gql(gql_get_project_app.format(app_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    # ######################################################
    # ###                   pipelines                   ####
    # ######################################################

    def test_get_pipelines(self):
        project_id = "1234"
        instances_limit = " (limit: 1)"
        query = gql(gql_get_pipelines.format(project_id, instances_limit))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_pipeline(self):
        pipeline_id = 1
        query = gql(gql_get_pipeline.format(pipeline_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_stop_pipeline_instance(self):
        pipeline_instance_id = "1"
        query = gql(gql_stop_pipeline_instance.format(pipeline_instance_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_gql_edit_pipeline(self):
        pipeline = """
        {
            id: "1234",
            name: "new_name"
        }"""
        query = gql(gql_edit_pipeline.format(pipeline))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_run_pipeline(self):
        pipeline_id = "1"
        query = gql(gql_run_pipeline.format(pipeline_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_create_pipeline(self):
        project_id = "1"
        pipeline_name = "test"
        job_id_list = "[id1, id2, id3]"
        query = gql(gql_create_pipeline.format(pipeline_name, "", project_id, job_id_list))
        result = self.client.validate(query)
        expected = None
        assert result == expected

    def test_get_pipeline_instance(self):
        pipeline_instance_id = "1"
        query = gql(gql_get_pipeline_instance.format(pipeline_instance_id))
        result = self.client.validate(query)
        expected = None
        assert result == expected
