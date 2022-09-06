# pylint: disable=attribute-defined-outside-init
import os

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
            file=os.path.join(conf.dir_path, "resources", "hello_world.py"),
            description="",
            category="Extraction",
            technology_catalog="Saagie",
            technology="spark",
            runtime_version="2.4",
            command_line="spark-submit",
            release_note="release_note",
            extra_technology="Python",
            extra_technology_version="3.7",
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

        assert job_instance_status in ["KILLED", "KILLING"]

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
        result = conf.saagie_api.jobs.export(job_id, os.path.join(conf.output_dir, "jobs"))
        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_import_job_from_json(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.jobs.import_from_json(
            os.path.join(conf.import_dir, "job", "job.json"),
            conf.project_id,
            os.path.join(conf.import_dir, "job", "hello_world.py"),
        )

        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_import_job_spark_from_json(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.jobs.import_from_json(
            os.path.join(conf.import_dir, "job_spark", "job.json"),
            conf.project_id,
            os.path.join(conf.import_dir, "job_spark", "Documents_empty.txt"),
        )

        to_validate = True
        assert result == to_validate

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
        file = os.path.join(conf.dir_path, "resources", "hello_world.py")

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
