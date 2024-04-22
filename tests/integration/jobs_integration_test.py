# pylint: disable=attribute-defined-outside-init
import json
import time
from pathlib import Path

import pytest


class TestIntegrationJobs:
    @pytest.fixture
    @staticmethod
    def create_then_delete_job(create_job, create_global_project):
        conf = create_global_project
        job_id = create_job

        yield job_id

        conf.saagie_api.jobs.delete(job_id)

    @pytest.fixture
    @staticmethod
    def delete_job(create_global_project):
        conf = create_global_project
        job_name = "python_test_upgrade"

        yield job_name

        job_id = conf.saagie_api.jobs.get_id(job_name, conf.project_name)

        conf.saagie_api.jobs.delete(job_id)

    @staticmethod
    def test_create_python_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        project_jobs = conf.saagie_api.jobs.list_for_project(project_id=conf.project_id, instances_limit=0)

        project_jobs_ids = [job["id"] for job in project_jobs["jobs"]]

        assert job_id in project_jobs_ids

    @staticmethod
    def test_create_spark_job(create_global_project):
        conf = create_global_project
        job = conf.saagie_api.jobs.create(
            job_name="job_name",
            project_id=conf.project_id,
            file=conf.dir_path / "resources" / "hello_world.py",
            description="",
            category="Extraction",
            technology_catalog="Saagie",
            technology="spark",
            runtime_version="3.1",
            command_line="spark-submit",
            release_note="release_note",
            extra_technology="Python",
            extra_technology_version="3.9",
        )
        job_id = job["data"]["createJob"]["id"]
        project_jobs = conf.saagie_api.jobs.list_for_project(project_id=conf.project_id, instances_limit=0)

        project_jobs_ids = [job["id"] for job in project_jobs["jobs"]]

        assert job_id in project_jobs_ids
        conf.saagie_api.jobs.delete(job_id)

    @staticmethod
    def test_get_job_id(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        job_name = "python_test"
        output_job_id = conf.saagie_api.jobs.get_id(job_name, conf.project_name)
        assert job_id == output_job_id

    @staticmethod
    def test_delete_job(create_job, create_global_project):
        conf = create_global_project
        job_id = create_job

        result = conf.saagie_api.jobs.delete(job_id)

        assert result == {"deleteJob": True}

    @staticmethod
    def test_run_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        job_before_run = conf.saagie_api.jobs.get_info(job_id=job_id)
        num_instances_before_run = job_before_run["job"]["countJobInstance"]

        conf.saagie_api.jobs.run_with_callback(job_id=job_id, freq=10, timeout=-1)

        job_after_run = conf.saagie_api.jobs.get_info(job_id=job_id)
        num_instances_after_run = job_after_run["job"]["countJobInstance"]

        assert num_instances_after_run == (num_instances_before_run + 1)

    @staticmethod
    def test_stop_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        runjob = conf.saagie_api.jobs.run(job_id)
        job_instance_id = runjob["runJob"]["id"]

        conf.saagie_api.jobs.stop(job_instance_id)

        job_instance_status = conf.saagie_api.jobs.get_instance(job_instance_id)["jobInstance"]["status"]

        assert job_instance_status in ("KILLED", "KILLING")

    @staticmethod
    def test_edit_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job
        job_input = {
            "name": "new_name",
            "description": "new description",
            "is_scheduled": True,
            "cron_scheduling": "0 0 * * *",
            "schedule_timezone": "UTC",
            "alerting": None,
        }
        conf.saagie_api.jobs.edit(
            job_id,
            job_name=job_input["name"],
            description=job_input["description"],
            is_scheduled=job_input["is_scheduled"],
            cron_scheduling=job_input["cron_scheduling"],
            schedule_timezone=job_input["schedule_timezone"],
        )
        job_info = conf.saagie_api.jobs.get_info(job_id)
        to_validate = {
            "name": job_info["job"]["name"],
            "description": job_info["job"]["description"],
            "alerting": None,
            "is_scheduled": job_info["job"]["isScheduled"],
            "cron_scheduling": job_info["job"]["cronScheduling"],
            "schedule_timezone": job_info["job"]["scheduleTimezone"],
        }

        assert job_input == to_validate

    @staticmethod
    def test_export_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job
        result = conf.saagie_api.jobs.export(job_id, conf.output_dir / "jobs")
        assert result

    @staticmethod
    def test_import_job_from_json(create_global_project):
        conf = create_global_project

        path_to_json = conf.import_dir / "project" / "jobs" / "job"

        result = conf.saagie_api.jobs.import_from_json(
            project_id=conf.project_id,
            path_to_folder=path_to_json,
        )

        json_file = Path(path_to_json / "job.json")

        with json_file.open("r", encoding="utf-8") as file:
            job_info = json.load(file)

        conf.saagie_api.jobs.delete(
            job_id=conf.saagie_api.jobs.get_id(job_name=job_info["name"], project_name=conf.project_name)
        )

        assert result

    @staticmethod
    def test_import_job_spark_from_json(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.jobs.import_from_json(
            project_id=conf.project_id,
            path_to_folder=conf.import_dir / "project" / "jobs" / "job_spark",
        )

        json_file = Path(conf.import_dir / "project" / "jobs" / "job_spark" / "job.json")

        with json_file.open("r", encoding="utf-8") as file:
            job_info = json.load(file)

        conf.saagie_api.jobs.delete(
            job_id=conf.saagie_api.jobs.get_id(job_name=job_info["name"], project_name=conf.project_name)
        )

        assert result

    @staticmethod
    def test_upgrade_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job
        job_input = {"command_line": "python {file}", "release_note": "hello_world", "runtime_version": "3.9"}
        conf.saagie_api.jobs.upgrade(
            job_id,
            use_previous_artifact=True,
            runtime_version=job_input["runtime_version"],
            command_line=job_input["command_line"],
            release_note=job_input["release_note"],
        )
        job_info = conf.saagie_api.jobs.get_info(job_id)
        version = job_info["job"]["versions"][0]
        to_validate = {
            "command_line": version["commandLine"],
            "release_note": version["releaseNote"],
            "runtime_version": version["runtimeVersion"],
        }

        assert job_input == to_validate

    @staticmethod
    def test_create_or_upgrade_job(delete_job, create_global_project):
        conf = create_global_project
        job_name = delete_job
        file = conf.dir_path / "resources" / "hello_world.py"

        job_create = conf.saagie_api.jobs.create_or_upgrade(
            job_name=job_name,
            project_id=conf.project_id,
            file=file,
            description="",
            category="Processing",
            technology="python",
            technology_catalog="Saagie",
            runtime_version="3.9",
            command_line="python {file} arg1 arg2",
            release_note="",
            extra_technology="",
            extra_technology_version="",
        )

        job_id = job_create["data"]["createJob"]["id"]

        assert job_id is not None

        job_upgrade = conf.saagie_api.jobs.create_or_upgrade(
            job_name=job_name,
            project_id=conf.project_id,
            file=file,
            description="",
            category="Processing",
            technology="python",
            technology_catalog="Saagie",
            runtime_version="3.9",
            command_line="python {file} arg1 arg2",
            release_note="",
            extra_technology="",
            extra_technology_version="",
        )

        assert "addJobVersion" in job_upgrade
        assert "editJob" in job_upgrade

    @staticmethod
    def test_rollback_job_version(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job
        conf.saagie_api.jobs.upgrade(
            job_id=job_id,
            file=None,
            use_previous_artifact=True,
            runtime_version="3.9",
            command_line="python {file} arg1 arg2",
            release_note=None,
            extra_technology="",
            extra_technology_version="",
        )

        job_rollback = conf.saagie_api.jobs.rollback(job_id=job_id, version_number="1")
        job_rollback_current_version = [
            version for version in job_rollback["rollbackJobVersion"]["versions"] if version["isCurrent"] is True
        ]

        assert job_rollback_current_version[0]["number"] == 1

    @staticmethod
    def test_create_or_upgrade_bash_job(create_global_project):
        conf = create_global_project
        job_name = "bash job"

        job_create = conf.saagie_api.jobs.create_or_upgrade(
            job_name=job_name,
            project_id=conf.project_id,
            file=None,
            use_previous_artifact=None,
            description="",
            category="Processing",
            technology="bash",
            technology_catalog="Saagie",
            runtime_version="debian11-bullseye",
            command_line="echo Hello",
            release_note="",
            extra_technology="",
            extra_technology_version="",
        )

        job_id = job_create["data"]["createJob"]["id"]

        assert job_id is not None

        job_upgrade = conf.saagie_api.jobs.create_or_upgrade(
            job_name=job_name,
            project_id=conf.project_id,
            file=None,
            use_previous_artifact=None,
            description="",
            category="Processing",
            technology="bash",
            technology_catalog="Saagie",
            runtime_version="debian11-bullseye",
            command_line="echo World",
            release_note="",
            extra_technology="",
            extra_technology_version="",
        )

        assert "addJobVersion" in job_upgrade
        assert "editJob" in job_upgrade
        conf.saagie_api.jobs.delete(job_id)

    @staticmethod
    def test_delete_instances(create_global_project, create_then_delete_job):
        conf = create_global_project
        job_id = create_then_delete_job
        _, instance_id = conf.saagie_api.jobs.run_with_callback(job_id)

        res = conf.saagie_api.jobs.delete_instances(job_id=job_id, job_instances_id=[instance_id])

        # test only the presence of the field, deletion can't be made because instances are still in the orchestrator
        # and system can't delete them
        assert "deleteJobInstances" in res

    @staticmethod
    def test_delete_instances_by_selector(create_global_project, create_then_delete_job):
        conf = create_global_project
        job_id = create_then_delete_job

        _, instance_id = conf.saagie_api.jobs.run_with_callback(job_id=job_id)
        _, instance_id2 = conf.saagie_api.jobs.run_with_callback(job_id=job_id)

        res = conf.saagie_api.jobs.delete_instances_by_selector(
            job_id=job_id, selector="ALL", exclude_instances_id=[instance_id], include_instances_id=[instance_id2]
        )

        # test only the presence of the field, deletion can't be made because instances are still in the orchestrator
        # and system can't delete them
        assert "deleteJobInstancesBySelector" in res

    @staticmethod
    def test_delete_instances_by_date(create_global_project, create_then_delete_job):
        conf = create_global_project
        job_id = create_then_delete_job

        _, instance_id = conf.saagie_api.jobs.run_with_callback(job_id=job_id)
        _, instance_id2 = conf.saagie_api.jobs.run_with_callback(job_id=job_id)

        res = conf.saagie_api.jobs.delete_instances_by_date(
            job_id=job_id,
            date_before="2023-10-01T00:00:00+01:00",
            exclude_instances_id=[instance_id],
            include_instances_id=[instance_id2],
        )

        # test only the presence of the field, deletion can't be made because instances are still in the orchestrator
        # and system can't delete them
        assert "deleteJobInstancesByDate" in res

    @staticmethod
    def test_delete_job_versions(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job
        conf.saagie_api.jobs.upgrade(
            job_id=job_id,
            file=None,
            use_previous_artifact=True,
            runtime_version="3.9",
            command_line="python {file} arg1 arg2",
            release_note=None,
            extra_technology="",
            extra_technology_version="",
        )

        res = conf.saagie_api.jobs.delete_versions(job_id=job_id, versions=["1"])

        assert res["deleteJobVersions"][0]["success"]

    @staticmethod
    def test_duplicate_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        result = conf.saagie_api.jobs.duplicate(job_id=job_id)

        jobs_list = conf.saagie_api.jobs.list_for_project_minimal(project_id=conf.project_id)

        conf.saagie_api.jobs.delete(job_id=result["duplicateJob"]["id"])

        assert result["duplicateJob"]["id"] in [job["id"] for job in jobs_list["jobs"]]

    @staticmethod
    def test_count_deletable_instances_by_status(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        result = conf.saagie_api.jobs.count_deletable_instances_by_status(job_id=job_id)

        assert len(result["countJobInstancesBySelector"]) == 5
        assert "ALL" in [select["selector"] for select in result["countJobInstancesBySelector"]]

    @staticmethod
    def test_count_deletable_instances_by_date(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        result = conf.saagie_api.jobs.count_deletable_instances_by_date(
            job_id=job_id, date_before="2023-10-01T00:00:00+01:00"
        )

        assert "countJobInstancesByDate" in result
        assert result["countJobInstancesByDate"] == 0

    @staticmethod
    def test_move_job(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        job_init = conf.saagie_api.jobs.get_info(job_id=job_id)

        res = conf.saagie_api.projects.create(
            name="test_project_move_job",
            group=conf.group,
            role="Manager",
            description="For integration test move job",
            jobs_technologies_allowed={"saagie": ["python", "spark", "bash"]},
        )
        new_project_id = res["createProject"]["id"]

        # Waiting for the project to be ready
        project_status = conf.saagie_api.projects.get_info(project_id=new_project_id)["project"]["status"]
        waiting_time = 0

        # Safety: wait for 5min max for project initialisation
        project_creation_timeout = 400
        while project_status != "READY" and waiting_time <= project_creation_timeout:
            time.sleep(10)
            project_status = conf.saagie_api.projects.get_info(new_project_id)["project"]["status"]
            waiting_time += 10
        if project_status != "READY":
            raise TimeoutError(
                f"Project creation is taking longer than usual, "
                f"aborting integration tests after {project_creation_timeout} seconds"
            )

        result = conf.saagie_api.jobs.move_job(
            job_id=job_id, target_platform_id=conf.id_platform, target_project_id=new_project_id
        )

        job_after = conf.saagie_api.jobs.get_info(job_id=result["moveJob"])

        conf.saagie_api.projects.delete(project_id=new_project_id)

        assert job_init["job"]["name"] == job_after["job"]["name"]

    @staticmethod
    def test_generate_description_by_ai(create_then_delete_job, create_global_project):
        conf = create_global_project
        job_id = create_then_delete_job

        result = conf.saagie_api.jobs.generate_description_by_ai(job_id=job_id)

        assert "editJobWithAiGeneratedDescription" in result
        assert result["editJobWithAiGeneratedDescription"]["id"] == job_id

    @staticmethod
    def test_get_info_by_alias(create_global_project, create_then_delete_job):
        conf = create_global_project
        job_id = create_then_delete_job

        result = conf.saagie_api.jobs.get_info_by_alias(project_id=conf.project_id, job_alias="python_test")

        assert result["jobByAlias"]["id"] == job_id
