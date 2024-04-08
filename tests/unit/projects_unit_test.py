# pylint: disable=attribute-defined-outside-init,unused-wildcard-import,protected-access
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.projects.gql_queries import *
from saagieapi.projects.projects import *

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

    def test_get_project_jobs_technologies(self):
        query = gql(GQL_GET_PROJECT_JOBS_TECHNOLOGIES)
        self.client.validate(query)

    def test_get_project_apps_technologies(self):
        query = gql(GQL_GET_PROJECT_APPS_TECHNOLOGIES)
        self.client.validate(query)

    def test_get_project_info_by_name(self):
        query = gql(GQL_GET_PROJECT_INFO_BY_NAME)
        self.client.validate(query)

    def test_gql_create_project(self):
        query = gql(GQL_CREATE_PROJECT)
        self.client.validate(query)

    def test_edit_project(self):
        query = gql(GQL_EDIT_PROJECT)
        self.client.validate(query)

    def get_project_rights(self):
        query = gql(GQL_GET_PROJECT_RIGHTS)
        self.client.validate(query)

    def test_delete_project(self):
        query = gql(GQL_DELETE_PROJECT)
        self.client.validate(query)

    @staticmethod
    def test_create_groupe_role_one_group():
        result = Projects._create_groupe_role(params={}, group="group1", role="Manager", groups_and_roles=None)
        assert result == {"authorizedGroups": [{"name": "group1", "role": "ROLE_PROJECT_MANAGER"}]}

    @staticmethod
    def test_create_groupe_role_multiple_groups():
        result = Projects._create_groupe_role(
            params={}, group=None, role=None, groups_and_roles=[{"group1": "Editor"}, {"group2": "Manager"}]
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
            Projects._create_groupe_role(params={}, group="group1", role="Incorrect_role", groups_and_roles=None)

        assert str(rte.value) == "❌ 'role' takes value in ('Manager', 'Editor', 'Viewer')"

    @staticmethod
    def test_create_groupe_role_too_many_arguments1():
        with pytest.raises(RuntimeError) as rte:
            Projects._create_groupe_role(
                params={},
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
                params={}, group=None, role="Manager", groups_and_roles=[{"group1": "Editor"}, {"group2": "Manager"}]
            )

        assert (
            str(rte.value) == "❌ Too many arguments, specify either a group and role, "
            "or multiple groups and roles with groups_and_roles"
        )

    @staticmethod
    def test_create_groupe_role_not_enough_arguments1():
        with pytest.raises(RuntimeError) as rte:
            Projects._create_groupe_role(params={}, group="group1", role=None, groups_and_roles=None)

        assert (
            str(rte.value) == "❌ Too few arguments, specify either a group and role, "
            "or multiple groups and roles with groups_and_roles"
        )
