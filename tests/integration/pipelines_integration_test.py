import json
import os
from pathlib import Path

import pytest

from saagieapi.pipelines.graph_pipeline import ConditionExpressionNode, ConditionStatusNode, GraphPipeline, JobNode


class TestIntegrationPipelines:
    @pytest.fixture
    @staticmethod
    def create_then_delete_graph_pipeline(create_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, job_id = create_graph_pipeline

        yield pipeline_id, job_id

        conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

    @pytest.fixture
    @staticmethod
    def delete_pipeline(create_global_project):
        conf = create_global_project
        pipeline_name = "pipeline_upgrade_test"

        yield pipeline_name

        pipeline_id = conf.saagie_api.pipelines.get_id(pipeline_name, conf.project_name)
        job_id = conf.saagie_api.jobs.get_id("python_test", conf.project_name)

        conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

    @staticmethod
    def test_create_graph_pipeline(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline
        list_pipelines = conf.saagie_api.pipelines.list_for_project(conf.project_id)
        list_pipelines_id = [pipeline["id"] for pipeline in list_pipelines["project"]["pipelines"]]

        assert pipeline_id in list_pipelines_id

    @staticmethod
    def test_get_graph_pipeline_id(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline
        pipeline_name = "TEST_VIA_API"
        output_pipeline_id = conf.saagie_api.pipelines.get_id(pipeline_name, conf.project_name)
        assert pipeline_id == output_pipeline_id

    @staticmethod
    def test_run_graph_pipeline(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline
        output_pipeline_run_status = conf.saagie_api.pipelines.run(pipeline_id)["runPipeline"]["status"]
        assert output_pipeline_run_status == "REQUESTED"

    @staticmethod
    def test_stop_graph_pipeline(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline
        output_pipeline_run_id = conf.saagie_api.pipelines.run(pipeline_id)["runPipeline"]["id"]
        output_pipeline_stop_status = conf.saagie_api.pipelines.stop(output_pipeline_run_id)["stopPipelineInstance"][
            "status"
        ]
        assert output_pipeline_stop_status == "KILLING"

    @staticmethod
    def test_delete_graph_pipeline(create_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, job_id = create_graph_pipeline

        result = conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

        assert result == {"deletePipeline": True}

    @staticmethod
    def test_edit_graph_pipeline(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline
        pipeline_input = {
            "name": "test_edit_graph_pipeline",
            "alias": "test_edit_alias_graph_pipeline",
            "description": "test_edit_graph_pipeline",
            "is_scheduled": True,
            "cron_scheduling": "0 0 * * *",
            "schedule_timezone": "UTC",
            "alerting": None,
            "hasExecutionVariablesEnabled": True,
        }
        conf.saagie_api.pipelines.edit(
            pipeline_id,
            name=pipeline_input["name"],
            alias=pipeline_input["alias"],
            description=pipeline_input["description"],
            is_scheduled=pipeline_input["is_scheduled"],
            cron_scheduling=pipeline_input["cron_scheduling"],
            schedule_timezone=pipeline_input["schedule_timezone"],
            has_execution_variables_enabled=pipeline_input["hasExecutionVariablesEnabled"],
        )
        pipeline_info = conf.saagie_api.pipelines.get_info(pipeline_id)
        to_validate = {
            "name": pipeline_info["graphPipeline"]["name"],
            "alias": pipeline_info["graphPipeline"]["alias"],
            "description": pipeline_info["graphPipeline"]["description"],
            "alerting": None,
            "is_scheduled": pipeline_info["graphPipeline"]["isScheduled"],
            "cron_scheduling": pipeline_info["graphPipeline"]["cronScheduling"],
            "schedule_timezone": pipeline_info["graphPipeline"]["scheduleTimezone"],
            "hasExecutionVariablesEnabled": pipeline_info["graphPipeline"]["hasExecutionVariablesEnabled"],
        }

        assert pipeline_input == to_validate

    @staticmethod
    def test_export_pipeline(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline
        result = conf.saagie_api.pipelines.export(pipeline_id, os.path.join(conf.output_dir, "pipelines"))
        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_import_pipeline_from_json_with_non_existing_jobs(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.pipelines.import_from_json(
            os.path.join(conf.import_dir, "pipelines", "without-existing-jobs", "pipeline.json"),
            conf.project_id,
        )
        assert not result

    @staticmethod
    def test_import_pipeline_from_json_with_existing_jobs(create_global_project):
        conf = create_global_project
        job_json_path = conf.import_dir / "project" / "jobs" / "job"
        with Path(job_json_path / "job.json").open("r", encoding="utf-8") as file:
            job_info = json.load(file)
        job_name = job_info["name"]

        jobs = conf.saagie_api.jobs.list_for_project_minimal(conf.project_id)["jobs"]
        job = list(filter(lambda j: j["name"] == job_name, jobs))
        if not job:
            conf.saagie_api.jobs.import_from_json(
                project_id=conf.project_id,
                path_to_folder=job_json_path,
            )

        pipeline_json_path = conf.import_dir / "project" / "pipelines" / "with-existing-jobs" / "pipeline.json"

        result = conf.saagie_api.pipelines.import_from_json(
            json_file=pipeline_json_path,
            project_id=conf.project_id,
        )

        with Path(pipeline_json_path).open("r", encoding="utf-8") as file:
            pipeline_info = json.load(file)

        conf.saagie_api.pipelines.delete(
            pipeline_id=conf.saagie_api.pipelines.get_id(pipeline_info["name"], conf.project_name)
        )
        conf.saagie_api.jobs.delete(job_id=conf.saagie_api.jobs.get_id(job_name, conf.project_name))

        assert result

    @staticmethod
    def test_import_pipeline_from_json_without_alerting(create_global_project):
        conf = create_global_project
        job_json_path = conf.import_dir / "project" / "jobs" / "job"
        with Path(job_json_path / "job.json").open("r", encoding="utf-8") as file:
            job_info = json.load(file)
        job_name = job_info["name"]
        jobs = conf.saagie_api.jobs.list_for_project_minimal(conf.project_id)["jobs"]
        job = list(filter(lambda j: j["name"] == job_name, jobs))
        if not job:
            conf.saagie_api.jobs.import_from_json(
                project_id=conf.project_id,
                path_to_folder=job_json_path,
            )

        json_path = conf.import_dir / "project" / "pipelines" / "without-alerting" / "pipeline.json"

        result = conf.saagie_api.pipelines.import_from_json(
            json_file=json_path,
            project_id=conf.project_id,
        )

        with Path(json_path).open("r", encoding="utf-8") as file:
            pipeline_info = json.load(file)

        conf.saagie_api.pipelines.delete(
            pipeline_id=conf.saagie_api.pipelines.get_id(pipeline_info["name"], conf.project_name)
        )
        conf.saagie_api.jobs.delete(job_id=conf.saagie_api.jobs.get_id(job_name, conf.project_name))

        assert result

    @staticmethod
    def test_upgrade_graph_pipeline(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, job_id = create_then_delete_graph_pipeline

        job_node1 = JobNode(job_id)
        job_node2 = JobNode(job_id)
        job_node3 = JobNode(job_id)
        job_node4 = JobNode(job_id)
        condition_node_1 = ConditionStatusNode()
        condition_node_1.put_at_least_one_success()
        job_node1.add_next_node(condition_node_1)
        condition_node_1.add_success_node(job_node2)
        condition_node_1.add_failure_node(job_node3)

        condition_node_2 = ConditionExpressionNode()
        condition_node_2.set_expression("1 + 1 == 2")
        condition_node_2.add_success_node(job_node4)

        job_node2.add_next_node(condition_node_2)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        release_note = "amazing new version !"

        pipeline_version_info = conf.saagie_api.pipelines.upgrade(pipeline_id, graph_pipeline, release_note)

        job_nodes_id = [
            job_node["id"] for job_node in pipeline_version_info["addGraphPipelineVersion"]["graph"]["jobNodes"]
        ]

        result = (str(job_node3.uid) in job_nodes_id) and (
            pipeline_version_info["addGraphPipelineVersion"]["releaseNote"] == release_note
        )

        assert result

    @staticmethod
    def test_rollback_pipeline_version(create_then_delete_graph_pipeline, create_global_project):
        conf = create_global_project
        pipeline_id, job_id = create_then_delete_graph_pipeline

        job_node1 = JobNode(job_id)
        job_node2 = JobNode(job_id)
        job_node3 = JobNode(job_id)
        job_node4 = JobNode(job_id)
        condition_node_1 = ConditionStatusNode()
        condition_node_1.put_at_least_one_success()
        job_node1.add_next_node(condition_node_1)
        condition_node_1.add_success_node(job_node2)
        condition_node_1.add_failure_node(job_node3)

        condition_node_2 = ConditionExpressionNode()
        condition_node_2.set_expression("1 + 1 == 2")
        condition_node_2.add_success_node(job_node4)

        job_node2.add_next_node(condition_node_2)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        conf.saagie_api.pipelines.upgrade(pipeline_id=pipeline_id, graph_pipeline=graph_pipeline, release_note="")

        pipeline_rollback = conf.saagie_api.pipelines.rollback(pipeline_id=pipeline_id, version_number="1")
        pipeline_rollback_current_version = [
            version
            for version in pipeline_rollback["rollbackPipelineVersion"]["versions"]
            if version["isCurrent"] is True
        ]

        assert pipeline_rollback_current_version[0]["number"] == 1

    @staticmethod
    def test_create_or_upgrade_pipeline(delete_pipeline, create_job, create_global_project):
        conf = create_global_project
        pipeline_name = delete_pipeline
        pipeline_alias = pipeline_name.replace(" ", "_")

        job_id = create_job
        job_node1 = JobNode(job_id)
        job_node2 = JobNode(job_id)
        job_node3 = JobNode(job_id)
        job_node4 = JobNode(job_id)
        condition_node_1 = ConditionStatusNode()
        condition_node_1.put_at_least_one_success()
        job_node1.add_next_node(condition_node_1)
        condition_node_1.add_success_node(job_node2)
        condition_node_1.add_failure_node(job_node3)

        condition_node_2 = ConditionExpressionNode()
        condition_node_2.set_expression("1 + 1 == 2")
        condition_node_2.add_success_node(job_node4)

        job_node2.add_next_node(condition_node_2)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        pipeline_create = conf.saagie_api.pipelines.create_or_upgrade(
            name=pipeline_name,
            alias=pipeline_alias,
            project_id=conf.project_id,
            description="Description pipeline dev test",
            release_note="First release",
            emails=["example@test.com"],
            status_list=["FAILED"],
            is_scheduled=True,
            cron_scheduling="5 12 5 * *",
            schedule_timezone="Europe/Paris",
            graph_pipeline=graph_pipeline,
        )

        pipeline_id = pipeline_create["createGraphPipeline"]["id"]

        assert pipeline_id is not None

        pipeline_upgrade = conf.saagie_api.pipelines.create_or_upgrade(
            name=pipeline_name,
            alias=pipeline_alias,
            project_id=conf.project_id,
            description="Description pipeline dev test",
            release_note="Second release",
            emails=["example@test.com"],
            status_list=["FAILED"],
            is_scheduled=True,
            cron_scheduling="5 12 5 * *",
            schedule_timezone="Europe/Paris",
            graph_pipeline=graph_pipeline,
        )

        assert "editPipeline" in pipeline_upgrade
        assert "addGraphPipelineVersion" in pipeline_upgrade

    @staticmethod
    def test_delete_versions(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, job_id = create_then_delete_graph_pipeline

        job_node1 = JobNode(job_id)
        job_node2 = JobNode(job_id)
        job_node3 = JobNode(job_id)
        job_node4 = JobNode(job_id)
        condition_node_1 = ConditionStatusNode()
        condition_node_1.put_at_least_one_success()
        job_node1.add_next_node(condition_node_1)
        condition_node_1.add_success_node(job_node2)
        condition_node_1.add_failure_node(job_node3)

        condition_node_2 = ConditionExpressionNode()
        condition_node_2.set_expression("1 + 1 == 2")
        condition_node_2.add_success_node(job_node4)

        job_node2.add_next_node(condition_node_2)

        graph_pipeline = GraphPipeline()
        graph_pipeline.add_root_node(job_node1)

        release_note = "amazing new version !"

        _ = conf.saagie_api.pipelines.upgrade(pipeline_id, graph_pipeline, release_note)

        result = conf.saagie_api.pipelines.delete_versions(pipeline_id=pipeline_id, versions=[1])

        assert result["deletePipelineVersions"][0]["success"] is True

    @staticmethod
    def test_delete_instances(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        _, instance_id = conf.saagie_api.pipelines.run_with_callback(pipeline_id)

        res = conf.saagie_api.pipelines.delete_instances(pipeline_id=pipeline_id, pipeline_instances_id=[instance_id])

        # test only the presence of the field, deletion can't be made because instances are still in the orchestrator
        # and system can't delete them
        assert "deletePipelineInstances" in res

    @staticmethod
    def test_delete_instances_by_status(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        _, instance_id = conf.saagie_api.pipelines.run_with_callback(pipeline_id=pipeline_id)
        _, instance_id2 = conf.saagie_api.pipelines.run_with_callback(pipeline_id=pipeline_id)

        res = conf.saagie_api.pipelines.delete_instances_by_selector(
            pipeline_id=pipeline_id,
            selector="ALL",
            exclude_instances_id=[instance_id],
            include_instances_id=[instance_id2],
        )

        # test only the presence of the field, deletion can't be made because instances are still in the orchestrator
        # and system can't delete them
        assert "deletePipelineInstancesByStatusSelector" in res

    @staticmethod
    def test_delete_instances_by_date(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        _, instance_id = conf.saagie_api.pipelines.run_with_callback(pipeline_id=pipeline_id)
        _, instance_id2 = conf.saagie_api.pipelines.run_with_callback(pipeline_id=pipeline_id)

        res = conf.saagie_api.pipelines.delete_instances_by_date(
            pipeline_id=pipeline_id,
            date_before="2023-10-01T00:00:00+01:00",
            exclude_instances_id=[instance_id],
            include_instances_id=[instance_id2],
        )

        # test only the presence of the field, deletion can't be made because instances are still in the orchestrator
        # and system can't delete them
        assert "deletePipelineInstancesByDateSelector" in res

    @staticmethod
    def test_count_deletable_instances_by_status(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        result = conf.saagie_api.pipelines.count_deletable_instances_by_status(pipeline_id=pipeline_id)

        assert len(result["countDeletablePipelineInstancesByStatus"]) == 5
        assert "ALL" in [select["selector"] for select in result["countDeletablePipelineInstancesByStatus"]]

    @staticmethod
    def test_count_deletable_instances_by_date(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        result = conf.saagie_api.pipelines.count_deletable_instances_by_date(
            pipeline_id=pipeline_id, date_before="2023-10-01T00:00:00+01:00"
        )

        assert "countDeletablePipelineInstancesByDate" in result

    @staticmethod
    def test_get_info_by_name(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        result = conf.saagie_api.pipelines.get_info_by_name(pipeline_name="TEST_VIA_API", project_id=conf.project_id)

        assert result["graphPipelineByName"]["id"] == pipeline_id

    @staticmethod
    def test_duplicate_pipeline(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        result = conf.saagie_api.pipelines.duplicate(pipeline_id=pipeline_id)

        conf.saagie_api.pipelines.delete(pipeline_id=result["duplicatePipeline"]["id"])

        assert "duplicatePipeline" in result

    @staticmethod
    def test_get_info_by_alias(create_global_project, create_then_delete_graph_pipeline):
        conf = create_global_project
        pipeline_id, _ = create_then_delete_graph_pipeline

        result = conf.saagie_api.pipelines.get_info_by_alias(
            pipeline_alias="ALIAS_TEST_VIA_API", project_id=conf.project_id
        )

        assert result["graphPipelineByAlias"]["id"] == pipeline_id
