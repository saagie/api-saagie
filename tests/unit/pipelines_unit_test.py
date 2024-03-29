# pylint: disable=attribute-defined-outside-init
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.pipelines.gql_queries import *
from saagieapi.pipelines.graph_pipeline import ConditionExpressionNode, ConditionStatusNode, GraphPipeline, JobNode
from saagieapi.pipelines.pipelines import Pipelines

from .saagie_api_unit_test import create_gql_client


class TestPipelines:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()

        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_pipelines_minimal_gql(self):
        query = gql(GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL)
        self.client.validate(query)

    def test_list_pipelines_minimal(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        # Define the expected query
        expected_query = gql(GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL)

        # Call the function under test
        pipeline.list_for_project_minimal(project_id=project_id)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values={"projectId": project_id}
        )

    def test_list_pipelines_gql(self):
        query = gql(GQL_LIST_PIPELINES_FOR_PROJECT)
        self.client.validate(query)

    def test_list_pipelines(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "projectId": project_id,
            "instancesLimit": None,
            "versionsLimit": None,
            "versionsOnlyCurrent": False,
        }

        # Define the expected query
        expected_query = gql(GQL_LIST_PIPELINES_FOR_PROJECT)

        # Call the function under test
        pipeline.list_for_project(project_id=project_id)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_pipeline_id(self, saagie_api_mock):
        saagie_api_mock.projects.get_id.return_value = "project_id"
        pipeline = Pipelines(saagie_api_mock)

        list_project = {
            "project": {
                "pipelines": [
                    {
                        "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                        "name": "Pipeline A",
                    },
                    {
                        "id": "9a2642df-550c-4c69-814f-1008f177b0e1",
                        "name": "Pipeline B",
                    },
                ]
            }
        }

        with patch.object(pipeline, "list_for_project") as l_proj:
            l_proj.return_value = list_project
            pipeline_id = pipeline.get_id(pipeline_name="Pipeline B", project_name="name")

        assert pipeline_id == "9a2642df-550c-4c69-814f-1008f177b0e1"

    def test_get_pipeline_id_not_found(self, saagie_api_mock):
        saagie_api_mock.projects.get_id.return_value = "project_id"
        pipeline = Pipelines(saagie_api_mock)

        list_project = {
            "project": {
                "pipelines": [
                    {
                        "id": "5d1999f5-fa70-47d9-9f41-55ad48333629",
                        "name": "Pipeline A",
                    },
                    {
                        "id": "9a2642df-550c-4c69-814f-1008f177b0e1",
                        "name": "Pipeline B",
                    },
                ]
            }
        }

        with patch.object(pipeline, "list_for_project") as l_proj, pytest.raises(NameError):
            l_proj.return_value = list_project
            pipeline_id = pipeline.get_id(pipeline_name="Pipeline C", project_name="name")

    def test_get_pipeline_gql(self):
        query = gql(GQL_GET_PIPELINE)
        self.client.validate(query)

    def test_get_pipeline(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": pipeline_id,
            "instancesLimit": None,
            "versionsLimit": None,
            "versionsOnlyCurrent": False,
        }

        # Define the expected query
        expected_query = gql(GQL_GET_PIPELINE)

        # Call the function under test
        pipeline.get_info(pipeline_id=pipeline_id)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_pipeline_by_name_gql(self):
        query = gql(GQL_GET_PIPELINE_BY_NAME)
        self.client.validate(query)

    def test_get_pipeline_by_name(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        pipeline_name = "pipeline_name"

        params = {
            "projectId": project_id,
            "pipelineName": pipeline_name,
            "instancesLimit": None,
            "versionsLimit": None,
            "versionsOnlyCurrent": False,
        }

        # Define the expected query
        expected_query = gql(GQL_GET_PIPELINE_BY_NAME)

        # Call the function under test
        pipeline.get_info_by_name(project_id=project_id, pipeline_name=pipeline_name)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_pipeline_instance_gql(self):
        query = gql(GQL_GET_PIPELINE_INSTANCE)
        self.client.validate(query)

    def test_get_pipeline_instance(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        pipeline_instance_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        # Define the expected query
        expected_query = gql(GQL_GET_PIPELINE_INSTANCE)

        # Call the function under test
        pipeline.get_instance(pipeline_instance_id=pipeline_instance_id)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values={"id": pipeline_instance_id}, pprint_result=None
        )

    def test_create_graph_pipeline_gql(self):
        query = gql(GQL_CREATE_GRAPH_PIPELINE)
        self.client.validate(query)

    def test_create_graph_pipeline(self, saagie_api_mock):
        pipeline = Pipelines(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "Amazing Pipeline"
        alias = "amazing_pipeline"
        desc = "new pipeline"

        job_node1 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node2 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node3 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        condition_status_node = ConditionStatusNode()
        condition_status_node.put_at_least_one_success()
        condition_status_node.add_success_node(job_node2)
        condition_status_node.add_failure_node(job_node3)
        job_node1.add_next_node(condition_status_node)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        pipeline_id = pipeline.create_graph(
            project_id=project_id,
            graph_pipeline=graph_pipeline,
            name=name,
            alias=alias,
            description=desc,
        )

        expected_query = gql(GQL_CREATE_GRAPH_PIPELINE)

        graph_pipeline.to_pipeline_graph_input()

        params = {
            "name": name,
            "description": desc,
            "projectId": project_id,
            "releaseNote": "",
            "jobNodes": graph_pipeline.list_job_nodes,
            "conditionNodes": graph_pipeline.list_conditions_nodes,
            "alias": alias,
            "isScheduled": False,
        }

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_graph_pipeline_with_scheduling_and_alerting(self, saagie_api_mock):
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "Amazing Pipeline"
        alias = "amazing_pipeline"
        desc = "new pipeline"
        cron = "0 0 * * *"
        timezone = "Pacific/Fakaofo"
        emails = ["hello.world@gmail.com"]
        status = ["FAILED"]

        job_node1 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node2 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node3 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        condition_status_node = ConditionStatusNode()
        condition_status_node.put_at_least_one_success()
        condition_status_node.add_success_node(job_node2)
        condition_status_node.add_failure_node(job_node3)
        job_node1.add_next_node(condition_status_node)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        saagie_api_mock.check_scheduling.return_value = {
            "isScheduled": True,
            "cronScheduling": cron,
            "scheduleTimezone": timezone,
        }
        saagie_api_mock.check_alerting.return_value = {"alerting": {"emails": emails, "statusList": status}}

        pipeline = Pipelines(saagie_api_mock)

        pipeline.create_graph(
            project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
            graph_pipeline=graph_pipeline,
            name=name,
            alias=alias,
            description=desc,
            cron_scheduling=cron,
            schedule_timezone=timezone,
            emails=emails,
            status_list=status,
            has_execution_variables_enabled=True,
        )

        expected_query = gql(GQL_CREATE_GRAPH_PIPELINE)

        graph_pipeline.to_pipeline_graph_input()

        params = {
            "name": name,
            "description": desc,
            "projectId": project_id,
            "releaseNote": "",
            "jobNodes": graph_pipeline.list_job_nodes,
            "conditionNodes": graph_pipeline.list_conditions_nodes,
            "alias": alias,
            "isScheduled": True,
            "cronScheduling": "0 0 * * *",
            "scheduleTimezone": timezone,
            "alerting": {
                "emails": emails,
                "statusList": status,
            },
            "hasExecutionVariablesEnabled": True,
        }

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_delete_pipeline_gql(self):
        query = gql(GQL_DELETE_PIPELINE)
        self.client.validate(query)

    def test_delete_pipeline(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        # Define the expected query
        expected_query = gql(GQL_DELETE_PIPELINE)

        # Call the function under test
        pipeline.delete(pipeline_id=pipeline_id)

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values={"id": pipeline_id})

    def test_upgrade_pipeline_gql(self):
        query = gql(GQL_UPGRADE_PIPELINE)
        self.client.validate(query)

    def test_upgrade_pipeline(self, saagie_api_mock):
        pipeline = Pipelines(saagie_api_mock)

        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        job_node1 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node2 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node3 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        condition_status_node = ConditionStatusNode()
        condition_status_node.put_at_least_one_success()
        condition_status_node.add_success_node(job_node2)
        condition_status_node.add_failure_node(job_node3)
        job_node1.add_next_node(condition_status_node)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        pipeline.upgrade(
            pipeline_id=pipeline_id,
            graph_pipeline=graph_pipeline,
        )

        expected_query = gql(GQL_UPGRADE_PIPELINE)

        graph_pipeline.to_pipeline_graph_input()

        params = {
            "id": pipeline_id,
            "jobNodes": graph_pipeline.list_job_nodes,
            "conditionNodes": graph_pipeline.list_conditions_nodes,
            "releaseNote": "",
        }

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_edit_pipeline_gql(self):
        query = gql(GQL_EDIT_PIPELINE)
        self.client.validate(query)

    def test_edit_pipeline(self, saagie_api_mock):
        # Set up the expected parameters
        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "new name"
        alias = "new_alias"
        description = "new description"
        is_scheduled = True
        cron = "0 0 * * *"
        timezone = "Pacific/Fakaofo"
        emails = ["hello.world@gmail.com"]
        status = ["FAILED"]
        has_execution_variables_enabled = True

        saagie_api_mock.check_scheduling.return_value = {
            "isScheduled": True,
            "cronScheduling": cron,
            "scheduleTimezone": timezone,
        }
        saagie_api_mock.check_alerting.return_value = {"alerting": {"emails": emails, "statusList": status}}
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Define the expected query
        expected_query = gql(GQL_EDIT_PIPELINE)

        get_info = {
            "graphPipeline": {
                "id": "860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                "name": "Pipeline A",
                "alias": "Pipeline_A",
                "description": "My Pipeline A",
                "alerting": "NULL",
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isLegacyPipeline": False,
            }
        }

        # Call the function under test
        with patch.object(pipeline, "get_info") as l_proj:
            l_proj.return_value = get_info
            pipeline.edit(
                pipeline_id=pipeline_id,
                name=name,
                alias=alias,
                description=description,
                is_scheduled=is_scheduled,
                cron_scheduling=cron,
                schedule_timezone=timezone,
                emails=emails,
                status_list=status,
                has_execution_variables_enabled=has_execution_variables_enabled,
            )

        params = {
            "id": pipeline_id,
            "name": name,
            "alias": alias,
            "description": description,
            "isScheduled": is_scheduled,
            "cronScheduling": cron,
            "scheduleTimezone": timezone,
            "alerting": {
                "emails": emails,
                "statusList": status,
            },
            "hasExecutionVariablesEnabled": has_execution_variables_enabled,
        }

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_edit_pipeline_no_schedule_and_alerting(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "new name"
        alias = "new_alias"
        description = "new description"
        is_scheduled = False
        emails = []
        has_execution_variables_enabled = False

        # Define the expected query
        expected_query = gql(GQL_EDIT_PIPELINE)

        get_info = {
            "graphPipeline": {
                "id": "860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                "name": "Pipeline A",
                "alias": "Pipeline_A",
                "description": "My Pipeline A",
                "alerting": "NULL",
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isLegacyPipeline": False,
            }
        }

        # Call the function under test
        with patch.object(pipeline, "get_info") as l_proj:
            l_proj.return_value = get_info
            pipeline.edit(
                pipeline_id=pipeline_id,
                name=name,
                alias=alias,
                description=description,
                is_scheduled=is_scheduled,
                emails=emails,
                has_execution_variables_enabled=has_execution_variables_enabled,
            )

        params = {
            "id": pipeline_id,
            "name": name,
            "alias": alias,
            "description": description,
            "isScheduled": is_scheduled,
            "alerting": None,
            "hasExecutionVariablesEnabled": has_execution_variables_enabled,
        }

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_edit_pipeline_previous_schedule_and_alerting(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "new name"
        alias = "new_alias"
        description = "new description"
        emails = ["email.test@saagie.com"]
        status = ["FAILED"]

        # Define the expected query
        expected_query = gql(GQL_EDIT_PIPELINE)

        get_info = {
            "graphPipeline": {
                "id": "860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                "name": "Pipeline A",
                "alias": "Pipeline_A",
                "description": "My Pipeline A",
                "alerting": {
                    "emails": emails,
                    "statusList": status,
                },
                "isScheduled": False,
                "cronScheduling": None,
                "scheduleStatus": None,
                "scheduleTimezone": "UTC",
                "isLegacyPipeline": False,
                "hasExecutionVariablesEnabled": False,
            }
        }

        # Call the function under test
        with patch.object(pipeline, "get_info") as l_proj:
            l_proj.return_value = get_info
            pipeline.edit(
                pipeline_id=pipeline_id,
                name=name,
                alias=alias,
                description=description,
            )

        params = {
            "id": pipeline_id,
            "name": name,
            "alias": alias,
            "description": description,
            "isScheduled": False,
            "cronScheduling": None,
            "scheduleTimezone": "UTC",
            "alerting": {
                "emails": emails,
                "statusList": status,
            },
            "hasExecutionVariablesEnabled": False,
        }

        # Assert that the query was executed with the expected parameters
        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_or_upgrade_create(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "name"
        alias = "alias"

        job_node1 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node2 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node3 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        condition_status_node = ConditionStatusNode()
        condition_status_node.put_at_least_one_success()
        condition_status_node.add_success_node(job_node2)
        condition_status_node.add_failure_node(job_node3)
        job_node1.add_next_node(condition_status_node)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        l_proj_min = {
            "project": {
                "pipelines": [
                    {"id": "5d1999f5-fa70-47d9-9f41-55ad48333629", "name": "Pipeline A"},
                    {"id": "9a2642df-550c-4c69-814f-1008f177b0e1", "name": "Pipeline B"},
                ]
            }
        }

        create_graph = {"createGraphPipeline": {"id": "ca79c5c8-2e57-4a35-bcfc-5065f0ee901c"}}

        # Call the function under test
        with patch.object(pipeline, "list_for_project_minimal") as l_proj, patch.object(
            pipeline, "create_graph"
        ) as c_graph:
            l_proj.return_value = l_proj_min
            c_graph.return_value = create_graph
            res = pipeline.create_or_upgrade(
                name=name,
                alias=alias,
                project_id=project_id,
                graph_pipeline=graph_pipeline,
            )

        assert res == create_graph

    def test_create_or_upgrade_upgrade(self, saagie_api_mock):
        # Create an instance of EnvVars with the mock saagie_api
        pipeline = Pipelines(saagie_api_mock)

        # Set up the expected parameters
        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "Pipeline A"
        alias = "alias"

        job_node1 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node2 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        job_node3 = JobNode("5d1999f5-fa70-47d9-9f41-55ad48333629")
        condition_status_node = ConditionStatusNode()
        condition_status_node.put_at_least_one_success()
        condition_status_node.add_success_node(job_node2)
        condition_status_node.add_failure_node(job_node3)
        job_node1.add_next_node(condition_status_node)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        l_proj_min = {
            "project": {
                "pipelines": [
                    {"id": "860b8dc8-e634-4c98-b2e7-f9ec32ab4771", "name": "Pipeline A"},
                    {"id": "9a2642df-550c-4c69-814f-1008f177b0e1", "name": "Pipeline B"},
                ]
            }
        }

        edit_graph = {
            "editPipeline": {
                "id": "860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                "name": "Amazing Pipeline 2",
                "alias": "Amazing_Pipeline_2",
                "description": "",
                "alerting": None,
                "isScheduled": True,
                "cronScheduling": "0 0 1 * *",
                "scheduleTimezone": "UTC",
                "hasExecutionVariablesEnabled": False,
            }
        }

        upgrade_graph = {
            "addGraphPipelineVersion": {
                "number": 4,
                "releaseNote": "",
                "graph": {
                    "jobNodes": [
                        {
                            "id": "82383907-bdd9-4d66-bc00-a84ff3a9caee",
                            "job": {"id": "7a706539-69dd-4f5d-bba3-4eac6be74d8d"},
                        },
                        {
                            "id": "5501eea2-e7af-4b44-a784-387f133b28c6",
                            "job": {"id": "3dbbb785-a7f4-4840-9f98-814b105a1a31"},
                        },
                        {
                            "id": "560d99bb-4e7b-4ab4-a5df-d879d31b4c0a",
                            "job": {"id": "e5e9fa38-1af8-42e7-95df-8d983eb78387"},
                        },
                    ],
                    "conditionNodes": [{"id": "9d0e886c-7771-4aa7-8321-cbccfaf4d3bb"}],
                },
                "creationDate": "2022-04-28T15:35:32.381215Z[UTC]",
                "creator": "john.doe",
                "isCurrent": True,
                "isMajor": False,
            }
        }

        # Call the function under test
        with patch.object(pipeline, "list_for_project_minimal") as l_proj, patch.object(
            pipeline, "edit"
        ) as edit, patch.object(pipeline, "upgrade") as upgrade:
            l_proj.return_value = l_proj_min
            edit.return_value = edit_graph
            upgrade.return_value = upgrade_graph
            res = pipeline.create_or_upgrade(
                name=name,
                alias=alias,
                project_id=project_id,
                graph_pipeline=graph_pipeline,
            )

        assert res == {
            "editPipeline": edit_graph["editPipeline"],
            "addGraphPipelineVersion": upgrade_graph["addGraphPipelineVersion"],
        }

    def test_rollback_pipeline_gql(self):
        query = gql(GQL_ROLLBACK_PIPELINE_VERSION)
        self.client.validate(query)

    def test_rollback_pipeline(self, saagie_api_mock):
        pipeline = Pipelines(saagie_api_mock)

        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        pipeline.rollback(
            pipeline_id=pipeline_id,
            version_number=1,
        )

        expected_query = gql(GQL_ROLLBACK_PIPELINE_VERSION)

        params = {
            "pipelineId": pipeline_id,
            "versionNumber": 1,
        }

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_run_pipeline_gql(self):
        query = gql(GQL_RUN_PIPELINE)
        self.client.validate(query)

    def test_run_pipeline(self, saagie_api_mock):
        pipeline = Pipelines(saagie_api_mock)

        pipeline_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        pipeline.run(pipeline_id=pipeline_id)

        expected_query = gql(GQL_RUN_PIPELINE)

        params = {"pipelineId": pipeline_id}

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_stop_pipeline_instance_gql(self):
        query = gql(GQL_STOP_PIPELINE_INSTANCE)
        self.client.validate(query)

    def test_count_deletable_instances_by_status_gql(self):
        query = gql(GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_STATUS)
        self.client.validate(query)

    def test_count_deletable_instances_by_date_gql(self):
        query = gql(GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_DATE)
        self.client.validate(query)

    def test_delete_versions_gql(self):
        query = gql(GQL_DELETE_PIPELINE_VERSION)
        self.client.validate(query)

    def test_delete_instances_gql(self):
        query = gql(GQL_DELETE_PIPELINE_INSTANCE)
        self.client.validate(query)

    def test_delete_instances_by_selector_gql(self):
        query = gql(GQL_DELETE_PIPELINE_INSTANCE_BY_SELECTOR)
        self.client.validate(query)

    def test_delete_instances_by_date_gql(self):
        query = gql(GQL_DELETE_PIPELINE_INSTANCE_BY_DATE)
        self.client.validate(query)

    def test_duplicate_pipeline_gql(self):
        query = gql(GQL_DUPLICATE_PIPELINE)
        self.client.validate(query)
