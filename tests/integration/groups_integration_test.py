import os
import shutil

import pytest


class TestIntegrationGroups:
    @staticmethod
    def test_list_groups(create_global_project):
        conf = create_global_project
        list_groups = conf.saagie_api.groups.list()
        group_names = [group["name"] for group in list_groups]
        assert conf.group in group_names

    @staticmethod
    def test_list_users_in_group(create_global_project):
        conf = create_global_project
        list_group_users = conf.saagie_api.groups.get_users(conf.group)
        users = list(list_group_users["users"])
        assert conf.user in users

    @staticmethod
    def test_list_permissions_in_group(create_global_project):
        conf = create_global_project
        list_group_permissions = conf.saagie_api.groups.get_permission(conf.group)
        assert "authorizations" in list_group_permissions.keys()

    @staticmethod
    def test_export_groups(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.groups.export(output_folder=os.path.join(conf.output_dir, "groups"))
        to_validate = True
        assert result == to_validate
        shutil.rmtree(os.path.join(conf.output_dir, "groups"))

    @pytest.fixture
    @staticmethod
    def create_group(create_global_project):
        conf = create_global_project
        group_name = "test_api_group_to_delete"
        conf.saagie_api.groups.create(group_name=group_name, users=[conf.user])
        return group_name

    @pytest.fixture
    @staticmethod
    def create_then_delete_group(create_group, create_global_project):
        conf = create_global_project
        group_name = create_group

        yield group_name

        conf.saagie_api.groups.delete(group_name=group_name)

    @staticmethod
    def test_create_group(create_then_delete_group, create_global_project):
        conf = create_global_project
        group_name = create_then_delete_group
        group_user = conf.saagie_api.groups.get_users(group_name)

        assert group_user["name"] == group_name

    @staticmethod
    def test_delete_group(create_group, create_global_project):
        conf = create_global_project
        group_name = create_group

        result = conf.saagie_api.groups.delete(group_name)
        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_edit_group_permission(create_then_delete_group, create_global_project):
        conf = create_global_project
        group_name = create_then_delete_group
        new_realm_authorization = {"permissions": [{"artifact": {"type": "TECHNOLOGY_CATALOG"}, "role": "ROLE_ACCESS"}]}

        conf.saagie_api.groups.edit_permission(group_name=group_name, realm_authorization=new_realm_authorization)
        group_permission = conf.saagie_api.groups.get_permission(group_name=group_name)

        assert group_permission["realmAuthorization"] == new_realm_authorization
