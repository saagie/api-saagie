import unittest

from gql import Client
from graphql import build_ast_schema
from graphql.language.parser import parse

import sys
sys.path.append("..")

from saagieapi.projects.gql_template import *


def create_gql_client(schema_file="./schema.graphqls"):
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


class GQLTemplateTest(unittest.TestCase):

    #######################################################
    ####                    env vars                   ####
    #######################################################

    def test_get_global_env_vars(self):
        client = create_gql_client()
        query = gql(gql_get_global_env_vars)
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_global_env_vars")

    def test_get_project_env_vars(self):
        client = create_gql_client()
        project_id = "1234"
        query = gql(gql_get_project_env_vars.format(project_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_project_env_vars")

    #######################################################
    ####                    projects                   ####
    #######################################################
    def test_get_projects_info(self):
        client = create_gql_client()
        query = gql(gql_get_projects_info)
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_projects_info")

    def test_get_project_info(self):
        client = create_gql_client()
        project_id = "1234"
        query = gql(gql_get_project_info.format(project_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_project_info")

    def test_gql_get_technologies(self):
        client = create_gql_client()
        query = gql(gql_get_technologies)
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_technologies")

    def test_gql_create_project_without_group_block(self):
        client = create_gql_client()
        name = "test_project"
        description = ""
        technologies = ['{id: "{1234}"}']
        group_block = ""
        query = gql(gql_create_project.format(name,
                                              description,
                                              group_block,
                                              ', '.join(technologies)))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for create_project without group_block")

    def test_create_project_with_group_block(self):
        client = create_gql_client()
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
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for create_project with group_block")

    #######################################################
    ####                      jobs                     ####
    #######################################################

    def test_get_project_jobs(self):
        client = create_gql_client()
        project_id = "1234"
        instances_limit = 3
        query = gql(gql_get_project_jobs.format(project_id, instances_limit))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_project_jobs")

    def test_get_project_job(self):
        client = create_gql_client()
        job_id = "1234"
        query = gql(gql_get_project_job.format(job_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_project_job")

    def test_get_job_instance(self):
        client = create_gql_client()
        job_instance_id = "job_instance_1234"
        query = gql(gql_get_job_instance.format(job_instance_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_job_instance")

    def test_run_job(self):
        client = create_gql_client()
        job_id = "job_1234"
        query = gql(gql_run_job.format(job_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_run_job")

    def test_stop_job(self):
        client = create_gql_client()
        job_id = "job_1234"
        query = gql(gql_stop_job_instance.format(job_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_stop_job_instance")

    def test_edit_job(self):
        client = create_gql_client()
        job_update = """
        {
            id: "1234",
            storageSizeInMB: 1579
        }"""

        query = gql(gql_edit_job.format(job_update))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_edit_job")

    #######################################################
    ####                      apps                     ####
    #######################################################
    def test_get_project_web_apps(self):
        client = create_gql_client()
        project_id = "1234"
        instances_limit = 1
        query = gql(gql_get_project_web_apps.format(project_id, instances_limit))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_project_web_apps")

    def test_get_project_web_app(self):
        client = create_gql_client()
        web_app_id = "1"
        query = gql(get_project_web_app.format(web_app_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for get_project_web_app")

    def test_get_project_app(self):
        client = create_gql_client()
        app_id = "1"
        query = gql(gql_get_project_app.format(app_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_project_app")

    #######################################################
    ####                   pipelines                   ####
    #######################################################

    def test_get_pipelines(self):
        client = create_gql_client()
        project_id = "1234"
        instances_limit = 1
        query = gql(gql_get_pipelines.format(project_id, instances_limit))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_pipelines")

    def test_get_pipeline(self):
        client = create_gql_client()
        pipeline_id = 1
        query = gql(gql_get_pipeline.format(pipeline_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_get_pipeline")

    def test_stop_pipeline_instance(self):
        client = create_gql_client()
        pipeline_instance_id = "1"
        query = gql(gql_stop_pipeline_instance.format(pipeline_instance_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_stop_pipeline_instance")

    def test_gql_edit_pipeline(self):
        client = create_gql_client()
        pipeline = """
        {
            id: "1234",
            name: "new_name"
        }"""
        query = gql(gql_edit_pipeline.format(pipeline))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_edit_pipeline")

    def test_run_pipeline(self):
        client = create_gql_client()
        pipeline_id = "1"
        query = gql(gql_run_pipeline.format(pipeline_id))
        result = client.validate(query)
        expected = None
        self.assertEqual(result, expected, "should validate the template for gql_run_pipeline")


if __name__ == '__main__':
    unittest.main()



















