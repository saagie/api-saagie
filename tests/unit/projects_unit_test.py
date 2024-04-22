# pylint: disable=attribute-defined-outside-init,protected-access
import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.projects import Projects
from saagieapi.projects.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestProjects:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()

        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_projects_gql(self):
        query = gql(GQL_LIST_PROJECTS)
        self.client.validate(query)

    def test_list_projects(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        expected_query = gql(GQL_LIST_PROJECTS)

        project.list()

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, pprint_result=None)

    def test_get_project_id(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_name = "Project A"

        with patch.object(project, "list") as list_proj:
            list_proj.return_value = {
                "projects": [
                    {
                        "id": "8321e13c-892a-4481-8552-5be4d6cc5df4",
                        "name": "Project A",
                        "creator": "john.doe",
                        "description": "My project A",
                        "jobsCount": 49,
                        "status": "READY",
                    },
                    {
                        "id": "33b70e1b-3111-4376-a839-12d2f93c323b",
                        "name": "Project B",
                        "creator": "john.doe",
                        "description": "My project B",
                        "jobsCount": 1,
                        "status": "READY",
                    },
                ]
            }
            project.get_id(project_name=project_name)

    def test_get_project_id_error(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_name = "Project C"

        with patch.object(project, "list") as list_proj, pytest.raises(NameError):
            list_proj.return_value = {
                "projects": [
                    {
                        "id": "8321e13c-892a-4481-8552-5be4d6cc5df4",
                        "name": "Project A",
                        "creator": "john.doe",
                        "description": "My project A",
                        "jobsCount": 49,
                        "status": "READY",
                    },
                    {
                        "id": "33b70e1b-3111-4376-a839-12d2f93c323b",
                        "name": "Project B",
                        "creator": "john.doe",
                        "description": "My project B",
                        "jobsCount": 1,
                        "status": "READY",
                    },
                ]
            }
            project.get_id(project_name=project_name)

    def test_get_project_info_gql(self):
        query = gql(GQL_GET_PROJECT_INFO)
        self.client.validate(query)

    def test_get_project_info(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"

        params = {"id": project_id}

        expected_query = gql(GQL_GET_PROJECT_INFO)

        project.get_info(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_project_info_by_name_gql(self):
        query = gql(GQL_GET_PROJECT_INFO_BY_NAME)
        self.client.validate(query)

    def test_get_project_info_by_name(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_name = "project_name"

        params = {"name": project_name}

        expected_query = gql(GQL_GET_PROJECT_INFO_BY_NAME)

        project.get_info_by_name(project_name=project_name)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_project_jobs_technologies_gql(self):
        query = gql(GQL_GET_PROJECT_JOBS_TECHNOLOGIES)
        self.client.validate(query)

    def test_get_project_jobs_technologies(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"

        params = {"id": project_id}

        expected_query = gql(GQL_GET_PROJECT_JOBS_TECHNOLOGIES)

        project.get_jobs_technologies(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_get_project_apps_technologies_gql(self):
        query = gql(GQL_GET_PROJECT_APPS_TECHNOLOGIES)
        self.client.validate(query)

    def test_get_project_apps_technologies(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"

        params = {"id": project_id}

        expected_query = gql(GQL_GET_PROJECT_APPS_TECHNOLOGIES)

        project.get_apps_technologies(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_create_project_gql(self):
        query = gql(GQL_CREATE_PROJECT)
        self.client.validate(query)

    def test_create_project(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_name = "project_name"
        desc = "description"
        rights = [{"name": "group1", "role": "ROLE_PROJECT_MANAGER"}]

        params = {
            "name": project_name,
            "description": desc,
            "authorizedGroups": rights,
            "technologies": [],
            "appTechnologies": [],
        }

        expected_query = gql(GQL_CREATE_PROJECT)

        with patch.object(project, "_create_groupe_role") as cgr, patch.object(
            project, "_Projects__get_jobs_for_project"
        ) as jobs, patch.object(project, "_Projects__get_apps_for_projects") as apps:
            jobs.return_value = []
            apps.return_value = []
            cgr.return_value = {"authorizedGroups": rights}
            project.create(name=project_name, group="group1", role="MANAGER", description=desc)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_project_rights_gql(self):
        query = gql(GQL_GET_PROJECT_RIGHTS)
        self.client.validate(query)

    def test_project_rights(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"

        params = {"id": project_id}

        expected_query = gql(GQL_GET_PROJECT_RIGHTS)

        project.get_rights(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_edit_project_gql(self):
        query = gql(GQL_EDIT_PROJECT)
        self.client.validate(query)

    def test_edit_project(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"
        project_name = "project_name"
        desc = "description"
        rights = [{"name": "group1", "role": "ROLE_PROJECT_MANAGER"}]
        jobs_value = [{"id": "9bb75cad-69a5-4a9d-b059-811c6cde589e"}, {"id": "f267085d-cc52-4ae8-ad9e-af8721c81127"}]
        apps_value = [{"id": "11d63963-0a74-4821-b17b-8fcec4882863"}, {"id": "56ad4996-7285-49a6-aece-b9525c57c619"}]

        params = {
            "projectId": project_id,
            "name": project_name,
            "description": desc,
            "authorizedGroups": rights,
            "technologies": jobs_value,
            "appTechnologies": apps_value,
        }

        expected_query = gql(GQL_EDIT_PROJECT)

        with patch.object(project, "get_info") as info, patch.object(
            project, "_create_groupe_role"
        ) as cgr, patch.object(project, "_Projects__get_jobs_for_project") as jobs, patch.object(
            project, "_Projects__get_apps_for_projects"
        ) as apps:
            jobs.return_value = jobs_value
            apps.return_value = apps_value
            cgr.return_value = {"authorizedGroups": rights}
            info.return_value = {"project": None}
            project.edit(
                project_id=project_id,
                name=project_name,
                group="group1",
                role="MANAGER",
                description=desc,
                jobs_technologies_allowed={"saagie": ["python", "spark"]},
                apps_technologies_allowed={"saagie": ["Jupyter Notebook", "RStudio"]},
            )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_edit_project2(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"
        project_name = "project_name"
        desc = "description"
        rights = [{"name": "group1", "role": "ROLE_PROJECT_MANAGER"}]
        jobs_value = [{"id": "9bb75cad-69a5-4a9d-b059-811c6cde589e"}, {"id": "f267085d-cc52-4ae8-ad9e-af8721c81127"}]
        apps_value = [{"id": "11d63963-0a74-4821-b17b-8fcec4882863"}, {"id": "56ad4996-7285-49a6-aece-b9525c57c619"}]

        params = {
            "projectId": project_id,
            "name": project_name,
            "description": desc,
            "authorizedGroups": rights,
            "technologies": jobs_value,
            "appTechnologies": apps_value,
        }

        expected_query = gql(GQL_EDIT_PROJECT)

        with patch.object(project, "get_info") as info, patch.object(
            project, "_create_groupe_role"
        ) as cgr, patch.object(project, "get_jobs_technologies") as jobs, patch.object(
            project, "get_apps_technologies"
        ) as apps, patch.object(
            project, "get_rights"
        ) as g_rights:
            jobs.return_value = {
                "technologiesByCategory": [
                    {
                        "jobCategory": "Extraction",
                        "technologies": [
                            {"id": "9bb75cad-69a5-4a9d-b059-811c6cde589e"},
                            {"id": "f267085d-cc52-4ae8-ad9e-af8721c81127"},
                        ],
                    }
                ]
            }
            apps.return_value = {
                "appTechnologies": [
                    {"id": "11d63963-0a74-4821-b17b-8fcec4882863"},
                    {"id": "56ad4996-7285-49a6-aece-b9525c57c619"},
                ]
            }
            cgr.return_value = {}
            g_rights.return_value = {
                "rights": [
                    {"name": "group1", "role": "ROLE_PROJECT_MANAGER", "isAllProjects": True},
                ]
            }
            info.return_value = {"project": None}
            project.edit(project_id=project_id, name=project_name, description=desc)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_delete_project_gql(self):
        query = gql(GQL_DELETE_PROJECT)
        self.client.validate(query)

    def test_delete_project(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"

        params = {"projectId": project_id}

        expected_query = gql(GQL_DELETE_PROJECT)

        project.delete(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_export_project(self, saagie_api_mock, tmp_path):
        saagie_api_mock.get_technology_name_by_id.side_effect = [
            {"Saagie", "python"},
            {"Saagie", "spark"},
            {"Saagie", "Jupyter Notebook"},
            {"Saagie", "RStudio"},
        ]
        saagie_api_mock.env_vars.export.side_effect = [True]
        saagie_api_mock.jobs.list_for_project_minimal.return_value = {
            "jobs": [
                {
                    "id": "fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10",
                    "name": "Python test job 1",
                    "alias": "Python_test_job_1",
                },
                {
                    "id": "e92ed170-50d6-4041-bba9-098a8e16f444",
                    "name": "Python test job 2",
                    "alias": "Python_test_job_2",
                },
            ]
        }
        saagie_api_mock.jobs.export.side_effect = [True, True]
        saagie_api_mock.pipelines.list_for_project_minimal.return_value = {
            "project": {
                "pipelines": [
                    {"id": "5d1999f5-fa70-47d9-9f41-55ad48333629", "name": "Pipeline A"},
                    {"id": "9a2642df-550c-4c69-814f-1008f177b0e1", "name": "Pipeline B"},
                ]
            }
        }
        saagie_api_mock.pipelines.export.side_effect = [True, True]
        saagie_api_mock.apps.list_for_project_minimal.return_value = {
            "project": {"apps": [{"id": "d0d6a466-10d9-4120-8101-56e46563e05a", "name": "Jupyter Notebook"}]}
        }
        saagie_api_mock.apps.export.side_effect = [True]

        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"

        project_params = {
            "project_id": project_id,
            "output_folder": tmp_path,
        }

        with patch("saagieapi.utils.folder_functions.create_folder") as create_folder, patch.object(
            project, "get_info"
        ) as info, patch.object(project, "get_jobs_technologies") as jobs, patch.object(
            project, "get_apps_technologies"
        ) as apps, patch.object(
            project, "get_rights"
        ) as rights:
            create_folder.side_effect = [
                Path(tmp_path / project_id).mkdir(),
            ]
            info.return_value = {
                "project": {
                    "name": "Project A",
                    "creator": "john.doe",
                    "description": "My project A",
                    "jobsCount": 49,
                    "status": "READY",
                }
            }
            jobs.return_value = {
                "technologiesByCategory": [
                    {
                        "jobCategory": "Extraction",
                        "technologies": [
                            {"id": "9bb75cad-69a5-4a9d-b059-811c6cde589e"},
                            {"id": "f267085d-cc52-4ae8-ad9e-af8721c81127"},
                        ],
                    }
                ]
            }
            apps.return_value = {
                "appTechnologies": [
                    {"id": "11d63963-0a74-4821-b17b-8fcec4882863"},
                    {"id": "56ad4996-7285-49a6-aece-b9525c57c619"},
                ]
            }
            rights.return_value = {
                "rights": [
                    {"name": "group1", "role": "ROLE_PROJECT_MANAGER", "isAllProjects": True},
                ]
            }

            project_result = project.export(**project_params)

        assert project_result is True

    def test_export_project_error(self, saagie_api_mock, tmp_path):
        saagie_api_mock.get_technology_name_by_id.side_effect = [
            {"Saagie", "python"},
            {"Saagie", "spark"},
            {"Saagie", "Jupyter Notebook"},
            {"Saagie", "RStudio"},
        ]
        saagie_api_mock.env_vars.export.side_effect = [False]
        saagie_api_mock.jobs.list_for_project_minimal.return_value = {
            "jobs": [
                {
                    "id": "fc7b6f52-5c3e-45bb-9a5f-a34bcea0fc10",
                    "name": "Python test job 1",
                    "alias": "Python_test_job_1",
                },
                {
                    "id": "e92ed170-50d6-4041-bba9-098a8e16f444",
                    "name": "Python test job 2",
                    "alias": "Python_test_job_2",
                },
            ]
        }
        saagie_api_mock.jobs.export.side_effect = [True, False]
        saagie_api_mock.pipelines.list_for_project_minimal.return_value = {
            "project": {
                "pipelines": [
                    {"id": "5d1999f5-fa70-47d9-9f41-55ad48333629", "name": "Pipeline A"},
                    {"id": "9a2642df-550c-4c69-814f-1008f177b0e1", "name": "Pipeline B"},
                ]
            }
        }
        saagie_api_mock.pipelines.export.side_effect = [True, False]
        saagie_api_mock.apps.list_for_project_minimal.return_value = {
            "project": {"apps": [{"id": "d0d6a466-10d9-4120-8101-56e46563e05a", "name": "Jupyter Notebook"}]}
        }
        saagie_api_mock.apps.export.side_effect = [False]

        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"

        project_params = {
            "project_id": project_id,
            "output_folder": tmp_path,
        }

        with patch("saagieapi.utils.folder_functions.create_folder") as create_folder, patch.object(
            project, "get_info"
        ) as info, patch.object(project, "get_jobs_technologies") as jobs, patch.object(
            project, "get_apps_technologies"
        ) as apps, patch.object(
            project, "get_rights"
        ) as rights:
            create_folder.side_effect = [
                Path(tmp_path / project_id).mkdir(),
            ]
            info.return_value = {
                "project": {
                    "name": "Project A",
                    "creator": "john.doe",
                    "description": "My project A",
                    "jobsCount": 49,
                    "status": "READY",
                }
            }
            jobs.return_value = {
                "technologiesByCategory": [
                    {
                        "jobCategory": "Extraction",
                        "technologies": [
                            {"id": "9bb75cad-69a5-4a9d-b059-811c6cde589e"},
                            {"id": "f267085d-cc52-4ae8-ad9e-af8721c81127"},
                        ],
                    }
                ]
            }
            apps.return_value = {
                "appTechnologies": [
                    {"id": "11d63963-0a74-4821-b17b-8fcec4882863"},
                    {"id": "56ad4996-7285-49a6-aece-b9525c57c619"},
                ]
            }
            rights.return_value = {
                "rights": [
                    {"name": "group1", "role": "ROLE_PROJECT_MANAGER", "isAllProjects": True},
                ]
            }

            project_result = project.export(**project_params)

        assert project_result is False

    def test_import_project_success(self, saagie_api_mock, tmp_path):
        saagie_api_mock.jobs.import_from_json.return_value = True
        saagie_api_mock.pipelines.import_from_json.return_value = True
        saagie_api_mock.apps.import_from_json.return_value = True
        saagie_api_mock.env_vars.import_from_json.return_value = True
        project = Projects(saagie_api_mock)

        cur_path = Path(__file__).parent
        cur_path = cur_path.parent / "integration" / "resources" / "import" / "project"
        origin_path = cur_path / "project.json"
        with origin_path.open("r", encoding="utf-8") as file:
            project_info = json.load(file)

        tmp_file = Path(tmp_path / "project.json")
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(project_info, file, indent=4)

        origin_path = cur_path / "jobs" / "job" / "job.json"
        with origin_path.open("r", encoding="utf-8") as file:
            job_info = json.load(file)

        tmp_file = Path(tmp_path / "jobs" / "job" / "job.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(job_info, file, indent=4)

        origin_path = cur_path / "pipelines" / "with-existing-jobs" / "pipeline.json"
        with origin_path.open("r", encoding="utf-8") as file:
            pipeline_info = json.load(file)

        tmp_file = Path(tmp_path / "pipelines" / "pipeline" / "pipeline.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(pipeline_info, file, indent=4)

        origin_path = cur_path / "apps" / "from-catalog" / "app.json"
        with origin_path.open("r", encoding="utf-8") as file:
            job_info = json.load(file)

        tmp_file = Path(tmp_path / "apps" / "app" / "app.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(job_info, file, indent=4)

        origin_path = cur_path / "env_vars" / "PROJECT" / "variable.json"
        with origin_path.open("r", encoding="utf-8") as file:
            env_var_info = json.load(file)

        tmp_file = Path(tmp_path / "env_vars" / "PROJECT" / "env_var.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(env_var_info, file, indent=4)

        with patch.object(project, "create") as create, patch.object(project, "get_status_with_callback") as info:
            create.return_value = {"createProject": {"id": "8321e13c-892a-4481-8552-5be4d6cc5df4"}}
            info.return_value = "READY"
            project_result = project.import_from_json(path_to_folder=tmp_path)

        assert project_result is True

    def test_import_project_error_reading_project_json(self, saagie_api_mock, tmp_path):
        project = Projects(saagie_api_mock)

        tmp_file = Path(tmp_path / "project.json")
        tmp_file.write_text("This is not a json format.", encoding="utf-8")

        project_result = project.import_from_json(path_to_folder=tmp_path)

        assert project_result is False

    def test_import_project_error_creating_project(self, saagie_api_mock, tmp_path):
        project = Projects(saagie_api_mock)

        cur_path = Path(__file__).parent
        cur_path = cur_path.parent / "integration" / "resources" / "import" / "project"
        origin_path = cur_path / "project.json"
        with origin_path.open("r", encoding="utf-8") as file:
            project_info = json.load(file)

        tmp_file = Path(tmp_path / "project.json")
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(project_info, file, indent=4)

        with patch.object(project, "create") as create:
            create.return_value = {"createProjects": {"id": "8321e13c-892a-4481-8552-5be4d6cc5df4"}}

            project_result = project.import_from_json(path_to_folder=tmp_path)

        assert project_result is False

    def test_import_project_error_getting_project_ready(self, saagie_api_mock, tmp_path):
        project = Projects(saagie_api_mock)

        cur_path = Path(__file__).parent
        cur_path = cur_path.parent / "integration" / "resources" / "import" / "project"
        origin_path = cur_path / "project.json"
        with origin_path.open("r", encoding="utf-8") as file:
            project_info = json.load(file)

        tmp_file = Path(tmp_path / "project.json")
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(project_info, file, indent=4)

        with patch.object(project, "create") as create, patch.object(project, "get_status_with_callback") as info:
            create.return_value = {"createProject": {"id": "8321e13c-892a-4481-8552-5be4d6cc5df4"}}
            info.return_value = "CREATING"

            project_result = project.import_from_json(path_to_folder=tmp_path)

        assert project_result is False

    def test_import_project_error_importing_subelements(self, saagie_api_mock, tmp_path):
        saagie_api_mock.jobs.import_from_json.return_value = False
        saagie_api_mock.pipelines.import_from_json.return_value = False
        saagie_api_mock.apps.import_from_json.return_value = False
        saagie_api_mock.env_vars.import_from_json.return_value = False
        project = Projects(saagie_api_mock)

        cur_path = Path(__file__).parent
        cur_path = cur_path.parent / "integration" / "resources" / "import" / "project"
        origin_path = cur_path / "project.json"
        with origin_path.open("r", encoding="utf-8") as file:
            project_info = json.load(file)

        tmp_file = Path(tmp_path / "project.json")
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(project_info, file, indent=4)

        origin_path = cur_path / "jobs" / "job" / "job.json"
        with origin_path.open("r", encoding="utf-8") as file:
            job_info = json.load(file)

        tmp_file = Path(tmp_path / "jobs" / "job" / "job.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(job_info, file, indent=4)

        origin_path = cur_path / "pipelines" / "with-existing-jobs" / "pipeline.json"
        with origin_path.open("r", encoding="utf-8") as file:
            pipeline_info = json.load(file)

        tmp_file = Path(tmp_path / "pipelines" / "pipeline" / "pipeline.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(pipeline_info, file, indent=4)

        origin_path = cur_path / "apps" / "from-catalog" / "app.json"
        with origin_path.open("r", encoding="utf-8") as file:
            job_info = json.load(file)

        tmp_file = Path(tmp_path / "apps" / "app" / "app.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(job_info, file, indent=4)

        origin_path = cur_path / "env_vars" / "PROJECT" / "variable.json"
        with origin_path.open("r", encoding="utf-8") as file:
            env_var_info = json.load(file)

        tmp_file = Path(tmp_path / "env_vars" / "PROJECT" / "env_var.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(env_var_info, file, indent=4)

        with patch.object(project, "create") as create, patch.object(project, "get_status_with_callback") as info:
            create.return_value = {"createProject": {"id": "8321e13c-892a-4481-8552-5be4d6cc5df4"}}
            info.return_value = "READY"
            project_result = project.import_from_json(path_to_folder=tmp_path)

        assert project_result is False

    @staticmethod
    def test_create_groupe_role_one_group():
        result = Projects._create_groupe_role(group="group1", role="Manager", groups_and_roles=None)
        assert result == {"authorizedGroups": [{"name": "group1", "role": "ROLE_PROJECT_MANAGER"}]}

    @staticmethod
    def test_create_groupe_role_multiple_groups():
        result = Projects._create_groupe_role(
            group=None, role=None, groups_and_roles=[{"group1": "Editor"}, {"group2": "Manager"}]
        )
        assert result == {
            "authorizedGroups": [
                {"name": "group1", "role": "ROLE_PROJECT_EDITOR"},
                {"name": "group2", "role": "ROLE_PROJECT_MANAGER"},
            ]
        }

    @staticmethod
    def test_create_groupe_role_incorrect_role():
        with pytest.raises(ValueError) as rte:
            Projects._create_groupe_role(group="group1", role="Incorrect_role", groups_and_roles=None)

        assert str(rte.value) == "❌ 'role' takes value in ('Manager', 'Editor', 'Viewer')"

    @staticmethod
    def test_create_groupe_role_too_many_arguments1():
        with pytest.raises(RuntimeError) as rte:
            Projects._create_groupe_role(
                group="group1",
                role="manager",
                groups_and_roles=[{"group1": "Editor"}, {"group2": "Manager"}],
            )

        assert (
            str(rte.value) == "❌ Too many arguments, specify either a group and role, "
            "or multiple groups and roles with groups_and_roles"
        )

    @staticmethod
    def test_create_groupe_role_too_many_arguments2():
        with pytest.raises(RuntimeError) as rte:
            Projects._create_groupe_role(
                group=None, role="Manager", groups_and_roles=[{"group1": "Editor"}, {"group2": "Manager"}]
            )

        assert (
            str(rte.value) == "❌ Too many arguments, specify either a group and role, "
            "or multiple groups and roles with groups_and_roles"
        )

    @staticmethod
    def test_create_groupe_role_not_enough_arguments1():
        with pytest.raises(RuntimeError) as rte:
            Projects._create_groupe_role(group="group1", role=None, groups_and_roles=None)

        assert (
            str(rte.value) == "❌ Too few arguments, specify either a group and role, "
            "or multiple groups and roles with groups_and_roles"
        )

    def test_get_status_with_callback(self, saagie_api_mock):
        project = Projects(saagie_api_mock)

        project_id = "8321e13c-892a-4481-8552-5be4d6cc5df4"
        with patch.object(project, "get_info") as get_info:
            get_info.side_effect = [
                {"project": {"status": "CREATING"}},
                {"project": {"status": "READY"}},
            ]
            status = project.get_status_with_callback(project_id=project_id, freq=1, timeout=2)

        assert status == "READY"
