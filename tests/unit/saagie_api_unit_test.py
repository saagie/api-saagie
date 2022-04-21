from gql import gql
from gql import Client
from graphql import build_ast_schema
from graphql.language.parser import parse
from saagieapi.gql_queries import *
import os


def create_gql_client():
    """
    Return a GQL Client with a defined schema
    :return: GQL Client
    """
    with open(os.path.dirname(os.path.abspath(__file__)) + '/resources/schema.graphqls') as source:
        document = parse(source.read())
    schema = build_ast_schema(document)
    client = Client(schema=schema)
    return client


class TestGQLTemplate:

    def setup_method(self):
        self.client = create_gql_client()

    def test_get_cluster_capacity(self):
        query = gql(gql_get_cluster_info)
        self.client.validate(query)

    # Schema is included in gateway schema
    # def test_get_runtimes(self):
    #     technology_id = "techno_id"
    #     query = gql(gql_get_runtimes.format(technology_id))
    #     self.client.validate(query)
    #     expected = None
    #     assert result == expected
