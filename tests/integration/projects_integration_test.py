# pylint: disable=attribute-defined-outside-init
import os
import time
from datetime import datetime
from typing import List

import pytest


class TestIntegrationProject:
    @staticmethod
    def test_get_project_id(create_global_project):
        conf = create_global_project
        expected_project_id = conf.project_id
        output_project_id = conf.saagie_api.projects.get_id(conf.project_name)
        assert expected_project_id == output_project_id

    @staticmethod
    def test_get_project_technologies(create_global_project):
        conf = create_global_project
        jobs_technologies = conf.saagie_api.projects.get_jobs_technologies(conf.project_id)
        apps_technologies = conf.saagie_api.projects.get_apps_technologies(conf.project_id)
        assert isinstance(jobs_technologies["technologiesByCategory"], List)
        assert len(jobs_technologies["technologiesByCategory"]) == 2  # Only python for Extraction and Processing
        assert isinstance(apps_technologies["appTechnologies"], List)
        assert len(apps_technologies["appTechnologies"]) > 2  # All Apps from saagie official catalog

    @staticmethod
    def test_get_project_rights(create_global_project):
        conf = create_global_project
        rights = conf.saagie_api.projects.get_rights(conf.project_id)
        expected_right_all_project = {"name": conf.group, "role": "ROLE_PROJECT_MANAGER", "isAllProjects": True}
        expected_right_project = {"name": conf.group, "role": "ROLE_PROJECT_MANAGER", "isAllProjects": False}
        assert isinstance(rights["rights"], list)
        assert expected_right_all_project in rights["rights"] or expected_right_project in rights["rights"]

    @staticmethod
    def test_edit_project(create_global_project):
        conf = create_global_project
        project_input = {
            "description": "new description",
            "jobs_technologies_allowed": {"saagie": ["python", "spark", "r", "bash"]},
        }

        conf.saagie_api.projects.edit(
            project_id=conf.project_id,
            description=project_input["description"],
            jobs_technologies_allowed=project_input["jobs_technologies_allowed"],
            groups_and_roles=[{conf.group: "Manager"}],
        )
        project_info = conf.saagie_api.projects.get_info(conf.project_id)
        technologies_allowed = conf.saagie_api.projects.get_jobs_technologies(conf.project_id)[
            "technologiesByCategory"
        ][0]

        to_validate = {
            "description": project_info["project"]["description"],
        }

        assert project_input["description"] == to_validate["description"]
        assert len(technologies_allowed["technologies"]) == 4  # R and Spark and Python and Bash for extraction

    @staticmethod
    def test_export_project(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.projects.export(conf.project_id, os.path.join(conf.output_dir, "projects"))
        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_import_project(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.projects.import_from_json(path_to_folder=os.path.join(conf.import_dir, "project"))

        conf.saagie_api.projects.delete(conf.saagie_api.projects.get_id("test import"))
        assert result is True

    @staticmethod
    def test_create_project_without_group_and_role(create_global_project):
        conf = create_global_project
        project_name = f"Integration_test_Saagie_API {datetime.timestamp(datetime.now())}"
        description = "For integration test - group and role"

        result = conf.saagie_api.projects.create(name=project_name, description=description)
        project_id = result["createProject"]["id"]

        # Waiting for the project to be ready
        project_status = conf.saagie_api.projects.get_info(project_id=project_id)["project"]["status"]
        waiting_time = 0

        # Safety: wait for 5min max for project initialisation
        project_creation_timeout = 400
        while project_status != "READY" and waiting_time <= project_creation_timeout:
            time.sleep(10)
            project_status = conf.saagie_api.projects.get_info(project_id)["project"]["status"]
            waiting_time += 10
        if project_status != "READY":
            raise TimeoutError(
                f"Project creation is taking longer than usual, "
                f"aborting integration tests after {project_creation_timeout} seconds"
            )

        conf.saagie_api.projects.delete(project_id)
        assert project_name == result["createProject"]["name"]

    @staticmethod
    def test_create_project_with_group_and_no_role(create_global_project):
        conf = create_global_project
        project_name = f"Integration_test_Saagie_API {datetime.timestamp(datetime.now())}"
        description = "For integration test - group and no role"

        with pytest.raises(RuntimeError) as rte:
            conf.saagie_api.projects.create(name=project_name, description=description, group=conf.group)
        assert (
            str(rte.value) == "❌ Too few arguments, specify either a group and role, "
            "or multiple groups and roles with groups_and_roles"
        )

    @staticmethod
    def test_get_project_info(create_global_project):
        conf = create_global_project
        expected_project = {
            "id": conf.project_id,
            "name": conf.project_name,
            "description": "For integration test",
        }
        output_project = conf.saagie_api.projects.get_info(conf.project_id)
        assert expected_project["name"] == output_project["project"]["name"]

    @staticmethod
    def test_get_project_info_by_name(create_global_project):
        conf = create_global_project
        expected_project = {
            "id": conf.project_id,
            "name": conf.project_name,
            "description": "For integration test",
        }
        output_project = conf.saagie_api.projects.get_info_by_name(conf.project_name)
        assert expected_project["id"] == output_project["projectByName"]["id"]
        assert expected_project["name"] == output_project["projectByName"]["name"]
