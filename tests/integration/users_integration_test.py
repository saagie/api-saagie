import os
import shutil

import pytest


class TestIntegrationUsers:
    @staticmethod
    def test_list_user(create_global_project):
        conf = create_global_project
        list_users = conf.saagie_api.users.list()
        user_logins = [user["login"] for user in list_users]
        assert conf.user in user_logins

    @staticmethod
    def test_get_info_user(create_global_project):
        conf = create_global_project
        user_info = conf.saagie_api.users.get_info(conf.user)
        assert conf.user == user_info["login"]

    @staticmethod
    def test_export_users(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.users.export(output_folder=os.path.join(conf.output_dir, "users"))
        to_validate = True
        assert result == to_validate
        shutil.rmtree(os.path.join(conf.output_dir, "users"))

    @pytest.fixture
    @staticmethod
    def create_user(create_global_project):
        conf = create_global_project
        user_name = "test_user_api_to_delete"
        pwd = "password1!"
        conf.saagie_api.users.create(user_name=user_name, password=pwd)
        return user_name

    @pytest.fixture
    @staticmethod
    def create_then_delete_user(create_user, create_global_project):
        conf = create_global_project
        user_name = create_user

        yield user_name

        conf.saagie_api.users.delete(user_name=user_name)

    @staticmethod
    def test_create_user(create_then_delete_user, create_global_project):
        conf = create_global_project
        user_name = create_then_delete_user
        user_info = conf.saagie_api.users.get_info(user_name)

        assert user_info["login"] == user_name

    @staticmethod
    def test_delete_user(create_user, create_global_project):
        conf = create_global_project
        user_name = create_user

        result = conf.saagie_api.users.delete(user_name)
        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_edit_password(create_then_delete_user, create_global_project):
        conf = create_global_project
        user_name = create_then_delete_user

        result = conf.saagie_api.users.edit_password(user_name, "password1!", "NewPassword!")
        to_validate = True
        assert result == to_validate
