import os
import shutil


class TestIntegrationProfiles:
    @staticmethod
    def test_list_profiles(create_global_project):
        conf = create_global_project
        list_profiles = conf.saagie_api.profiles.list()
        profile_logins = [profile["login"] for profile in list_profiles]
        assert conf.user in profile_logins

    @staticmethod
    def test_get_info(create_global_project):
        conf = create_global_project
        info_profile = conf.saagie_api.profiles.get_info(conf.user)
        assert conf.user == info_profile["login"]

    @staticmethod
    def test_export_profiles(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.profiles.export(output_folder=os.path.join(conf.output_dir, "profiles"))
        to_validate = True
        assert result == to_validate
        shutil.rmtree(os.path.join(conf.output_dir, "profiles"))

    @staticmethod
    @staticmethod
    def test_edit_profile(create_global_project):
        conf = create_global_project
        new_job_title = "DATA_ENGINEER"
        conf.saagie_api.profiles.edit(user_name=conf.user, job_title=new_job_title)
        res = conf.saagie_api.profiles.get_info(conf.user)
        assert res["job"] == new_job_title
