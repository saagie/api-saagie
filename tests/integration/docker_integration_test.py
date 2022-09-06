# pylint: disable=attribute-defined-outside-init
import pytest


class TestIntegrationDocker:
    @pytest.fixture
    @staticmethod
    def create_docker_credential(create_global_project):
        conf = create_global_project
        cred = conf.saagie_api.docker_credentials.create(
            project_id=conf.project_id, username="myuser", registry="test-registry", password="mypassword"
        )

        return cred["createDockerCredentials"]["id"]

    @pytest.fixture
    @staticmethod
    def create_then_delete_docker_credential(create_docker_credential, create_global_project):
        conf = create_global_project
        cred_id = create_docker_credential

        yield cred_id

        conf.saagie_api.docker_credentials.delete(project_id=conf.project_id, credential_id=cred_id)

    @staticmethod
    def test_create_docker_credential(create_then_delete_docker_credential, create_global_project):
        conf = create_global_project
        cred_id = create_then_delete_docker_credential

        cred = conf.saagie_api.docker_credentials.get_info(conf.project_id, cred_id)

        assert cred["dockerCredentials"]["username"] == "myuser"

    @staticmethod
    def test_delete_docker_credential(create_docker_credential, create_global_project):
        conf = create_global_project
        cred_id = create_docker_credential
        result = conf.saagie_api.docker_credentials.delete(conf.project_id, cred_id)
        all_creds = conf.saagie_api.docker_credentials.list_for_project(conf.project_id)

        assert result == {"deleteDockerCredentials": True}
        assert len(all_creds["allDockerCredentials"]) == 0

    @staticmethod
    def test_upgrade_docker_credential(create_then_delete_docker_credential, create_global_project):
        conf = create_global_project
        cred_id = create_then_delete_docker_credential

        result = conf.saagie_api.docker_credentials.upgrade(
            conf.project_id, cred_id, username="myuser", password="mypassword", registry="new-registry"
        )
        cred = conf.saagie_api.docker_credentials.get_info(conf.project_id, cred_id)
        assert result["updateDockerCredentials"]["id"] == cred_id
        assert cred["dockerCredentials"]["registry"] == "new-registry"

    @staticmethod
    def test_delete_docker_credential_for_username(create_docker_credential, create_global_project):
        conf = create_global_project
        _ = create_docker_credential
        result = conf.saagie_api.docker_credentials.delete_for_username(
            conf.project_id, username="myuser", registry="test-registry"
        )
        all_creds = conf.saagie_api.docker_credentials.list_for_project(conf.project_id)

        assert result == {"deleteDockerCredentials": True}
        assert len(all_creds["allDockerCredentials"]) == 0

    @staticmethod
    def test_upgrade_docker_credential_for_username(create_then_delete_docker_credential, create_global_project):
        conf = create_global_project
        cred_id = create_then_delete_docker_credential

        result = conf.saagie_api.docker_credentials.upgrade_for_username(
            conf.project_id, username="myuser", password="newpassword", registry="test-registry"
        )
        cred = conf.saagie_api.docker_credentials.get_info_for_username(
            conf.project_id, username="myuser", registry="test-registry"
        )
        assert result["updateDockerCredentials"]["id"] == cred_id
        assert cred["registry"] == "test-registry"
