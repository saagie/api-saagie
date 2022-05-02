# pylint: disable=attribute-defined-outside-init
import os

import pytest
from gql import Client, gql
from graphql import build_ast_schema
from graphql.language.parser import parse

from saagieapi import SaagieApi
from saagieapi.gql_queries import GQL_GET_CLUSTER_INFO


def create_gql_client():
    """
    Return a GQL Client with a defined schema
    :return: GQL Client
    """
    with open(
        file=os.path.dirname(os.path.abspath(__file__)) + "/resources/schema.graphqls", encoding="utf-8"
    ) as source:
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

    @staticmethod
    def test_check_scheduling():
        result = SaagieApi.check_scheduling(cron_scheduling="* * * * *", params={}, schedule_timezone="Pacific/Fakaofo")
        assert result["isScheduled"] is True
        assert result["cronScheduling"] == "* * * * *"

    @staticmethod
    def test_check_scheduling_bad_timezone():
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_scheduling(cron_scheduling="* * * * *", params={}, schedule_timezone="")
        assert str(rte.value) == "Please specify a correct timezone"

    @staticmethod
    def test_check_scheduling_bad_cronexpression():
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_scheduling(cron_scheduling="xx", params={}, schedule_timezone="Pacific/Fakaofo")
        assert str(rte.value) == "xx is not valid cron format"

    @staticmethod
    def test_check_alerting():
        result = SaagieApi.check_alerting(emails=["mail1", "mail2"], params={}, status_list=["FAILED"])
        assert result["alerting"]["emails"] == ["mail1", "mail2"]
        assert result["alerting"]["statusList"] == ["FAILED"]

    @staticmethod
    def test_check_alerting_bad_status_list():
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_alerting(emails=["mail1", "mail2"], params={}, status_list=["failure"])
        assert "The following status are not valid" in str(rte.value)

    @staticmethod
    def test_check_technology_valid():
        result = SaagieApi.check_technology_valid(
            technologies=["python"],
            all_technologies_in_catalog=[{"label": "python", "id": "123"}, {"label": "java", "id": "456"}],
            technology_catalog="catalog",
        )
        assert result == ["123"]

    @staticmethod
    def test_check_technology_valid_empty_catalog():
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_technology_valid(
                technologies=["python"], all_technologies_in_catalog=[], technology_catalog="catalog"
            )
        assert str(rte.value) == "Catalog catalog does not exist or does not contain technologies"

    @staticmethod
    def test_check_technology_valid_no_technologies_exists():
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_technology_valid(
                technologies=["r"],
                all_technologies_in_catalog=[{"label": "python", "id": "123"}, {"label": "java", "id": "456"}],
                technology_catalog="catalog",
            )
        assert str(rte.value) == "Technologies ['r'] do not exist in the catalog specified"

    @staticmethod
    def test_check_technology_valid_some_technology_not_exist():
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_technology_valid(
                technologies=["r", "python"],
                all_technologies_in_catalog=[{"label": "python", "id": "123"}, {"label": "java", "id": "456"}],
                technology_catalog="catalog",
            )
        assert str(rte.value) == "Some technologies among ['r', 'python'] do not exist in the catalog specified"

    @staticmethod
    def test_check_technology_configured():
        result = SaagieApi.check_technology_configured(
            params={}, technology="python", technology_id="123", technologies_configured_for_project=["123", "456"]
        )
        assert result["technologyId"] == "123"

    @staticmethod
    def test_check_technology_configured_technology_not_configured():
        with pytest.raises(RuntimeError) as rte:
            SaagieApi.check_technology_configured(
                params={}, technology="python", technology_id="123", technologies_configured_for_project=["456"]
            )
        assert "Technology python does not exist in the target project  and for the catalog specified" == str(rte.value)
