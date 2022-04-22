import pytest
from gql import gql
from gql import Client
from graphql import build_ast_schema
from graphql.language.parser import parse
from saagieapi.gql_queries import *
from saagieapi import SaagieApi
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
        query = gql(GQL_GET_CLUSTER_INFO)
        self.client.validate(query)

    def test_check_scheduling(self):
        result = SaagieApi.check_scheduling(cron_scheduling='* * * * *', params={}, schedule_timezone="Pacific/Fakaofo")
        assert result["isScheduled"] is True
        assert result["cronScheduling"] == "* * * * *"

    def test_check_scheduling_bad_timezone(self):
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_scheduling(cron_scheduling='* * * * *', params={}, schedule_timezone="")
        assert str(rte.value) == "Please specify a correct timezone"

    def test_check_scheduling_bad_cronexpression(self):
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_scheduling(cron_scheduling='xx', params={}, schedule_timezone="Pacific/Fakaofo")
        assert str(rte.value) == "xx is not valid cron format"

    def test_check_alerting(self):
        result = SaagieApi.check_alerting(emails=["mail1", "mail2"], params={}, status_list=["FAILED"])
        assert result["alerting"]["emails"] == ["mail1", "mail2"]
        assert result["alerting"]["statusList"] == ["FAILED"]

    def test_check_alerting_bad_status_list(self):
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_alerting(emails=["mail1", "mail2"], params={}, status_list=["failure"])
        assert "The following status are not valid" in str(rte.value)
