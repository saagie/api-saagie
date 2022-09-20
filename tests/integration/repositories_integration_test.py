# pylint: disable=attribute-defined-outside-init
import os

import pytest


class TestIntegrationRepository:
    @pytest.fixture
    @staticmethod
    def create_repository_from_url(create_global_project):
        conf = create_global_project
        repository_name = "repository from url"
        repository = conf.saagie_api.repositories.create(
            name=repository_name,
            url="https://github.com/saagie/technologies-community/releases/latest/download/technologies.zip",
        )

        return repository["addRepository"]["objects"][0]["id"]

    @pytest.fixture
    @staticmethod
    def create_then_delete_repository_from_url(create_repository_from_url, create_global_project):
        conf = create_global_project
        repository_id = create_repository_from_url

        yield repository_id

        conf.saagie_api.repositories.delete(repository_id)

    @staticmethod
    def test_edit_repository_from_url(create_then_delete_repository_from_url, create_global_project):
        conf = create_global_project
        repository_id = create_then_delete_repository_from_url

        repository_input = {
            "name": "new repository from url",
            "url": "https://github.com/saagie/technologies/releases/latest/download/technologie.zip",
        }

        conf.saagie_api.repositories.edit(
            repository_id, name=repository_input["name"], url=repository_input["url"], trigger_synchronization=True
        )
        repository_info = conf.saagie_api.repositories.get_info(repository_id)

        to_validate = {
            "name": repository_info["repository"]["name"],
            "url": repository_info["repository"]["source"]["url"],
        }
        assert repository_input == to_validate

    @staticmethod
    def test_delete_repository_from_url(create_then_delete_repository_from_url, create_global_project):
        conf = create_global_project
        repository_id = create_then_delete_repository_from_url
        result = conf.saagie_api.repositories.delete(repository_id)

        assert result == {"removeRepository": {"id": repository_id, "name": "repository from url"}}

    @staticmethod
    def test_synchronize_repository_from_zip(create_then_delete_repository_from_zip, create_global_project):
        conf = create_global_project
        repository_id = create_then_delete_repository_from_zip

        repository_input = {"file_name": "new_technologies.zip"}
        file_path = os.path.join(conf.dir_path, "resources", "repositories", repository_input["file_name"])

        conf.saagie_api.repositories.synchronize(repository_id, file=file_path)
        repository_info = conf.saagie_api.repositories.get_info(repository_id)

        to_validate = {"file_name": repository_info["repository"]["source"]["name"]}
        assert repository_input == to_validate

    @pytest.fixture
    @staticmethod
    def create_repository_from_zip(create_global_project):
        conf = create_global_project
        repository_name = "repository from zip"
        file_path = os.path.join(conf.dir_path, "resources", "repositories", "technologies.zip")
        repository = conf.saagie_api.repositories.create(name=repository_name, file=file_path)
        print(repository, flush=True)

        return repository["addRepository"]["objects"][0]["id"]

    @pytest.fixture
    @staticmethod
    def create_then_delete_repository_from_zip(create_repository_from_zip, create_global_project):
        conf = create_global_project
        repository_id = create_repository_from_zip

        yield repository_id

        conf.saagie_api.repositories.delete(repository_id)

    @staticmethod
    def test_revert_last_synchronization_from_zip(create_then_delete_repository_from_zip, create_global_project):
        conf = create_global_project
        repository_id = create_then_delete_repository_from_zip
        previous_zip_name = "technologies.zip"
        new_zip_name = "new_technologies.zip"
        new_file_path = os.path.join(conf.dir_path, "resources", "repositories", new_zip_name)

        conf.saagie_api.repositories.synchronize(repository_id, file=new_file_path)
        new_repository_info = conf.saagie_api.repositories.get_info(repository_id)

        conf.saagie_api.repositories.revert_last_synchronization(repository_id)
        repository_info = conf.saagie_api.repositories.get_info(repository_id)

        assert new_repository_info["repository"]["source"]["name"] == new_zip_name
        assert repository_info["repository"]["source"]["name"] == previous_zip_name

    @staticmethod
    def test_create_repository_from_zip(create_then_delete_repository_from_zip, create_global_project):
        conf = create_global_project
        repository_id = create_then_delete_repository_from_zip

        repository = conf.saagie_api.repositories.get_info(repository_id, last_synchronization=True)

        assert repository["repository"]["name"] == "repository from zip"

    @staticmethod
    def test_delete_repository_from_zip(create_repository_from_zip, create_global_project):
        conf = create_global_project
        repository_id = create_repository_from_zip
        result = conf.saagie_api.repositories.delete(repository_id)

        assert result == {"removeRepository": {"id": repository_id, "name": "repository from zip"}}
