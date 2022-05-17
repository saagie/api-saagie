# pylint: disable=attribute-defined-outside-init
import pytest
from gql import gql

from saagieapi.projects.gql_queries import *
from saagieapi.projects.projects import *

from .saagie_api_unit_test import create_gql_client


class TestProjects:
    def setup_method(self):
        self.client = create_gql_client()

    def test_list_projects(self):
        query = gql(GQL_LIST_PROJECTS)
        self.client.validate(query)

    def test_get_project_jobs_technologies(self):
        query = gql(GQL_GET_PROJECT_JOBS_TECHNOLOGIES)
        self.client.validate(query)

    def test_get_project_apps_technologies(self):
        query = gql(GQL_GET_PROJECT_APPS_TECHNOLOGIES)
        self.client.validate(query)

    def test_get_project_info(self):
        query = gql(GQL_GET_PROJECT_INFO)
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
