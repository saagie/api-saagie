from datetime import datetime

import pytest


class TestIntegrationStorages:
    @pytest.fixture
    @staticmethod
    def create_storage(create_global_project):
        conf = create_global_project
        storage_name = f"hello_world{datetime.now()}"
        storage = conf.saagie_api.storages.create(
            project_id=conf.project_id,
            storage_name=storage_name,
            storage_size="128 MB",
            storage_description="Be happy",
        )
        return storage["createVolume"]

    @pytest.fixture
    @staticmethod
    def create_then_delete_storage(create_storage, create_global_project):
        conf = create_global_project
        storage = create_storage

        yield storage

        conf.saagie_api.storages.delete(storage_id=storage["id"], project_id=conf.project_id)

    @staticmethod
    def test_create_storage(create_then_delete_storage, create_global_project):
        conf = create_global_project
        storage = create_then_delete_storage
        storages = conf.saagie_api.storages.list_for_project(project_id=conf.project_id)["project"]
        is_created = any(elem["id"] == storage["id"] for elem in storages["volumes"])
        assert is_created

    @staticmethod
    def test_get_info(create_then_delete_storage, create_global_project):
        conf = create_global_project

        storage = create_then_delete_storage

        result = conf.saagie_api.storages.get_info(project_id=conf.project_id, storage_id=storage["id"])
        del result["creationDate"]

        assert storage == result

    @staticmethod
    def test_get_info_not_found(create_global_project):
        conf = create_global_project

        storage_id = "my-best-id"

        with pytest.raises(ValueError) as vale:
            conf.saagie_api.storages.get_info(project_id=conf.project_id, storage_id=storage_id)
        assert str(vale.value).startswith(f"❌ Storage '{storage_id}' not found in project '{conf.project_id}'")

    @staticmethod
    def test_edit_storage(create_then_delete_storage, create_global_project):
        conf = create_global_project
        storage = create_then_delete_storage

        storage_input = {
            "id": storage["id"],
            "name": "storage new name",
            "size": "128.0 MB",
            "description": "storage new description",
        }

        conf.saagie_api.storages.edit(
            storage_id=storage_input["id"],
            storage_name=storage_input["name"],
            description=storage_input["description"],
        )

        storages = conf.saagie_api.storages.list_for_project(project_id=conf.project_id)["project"]
        to_validate = {}
        for elem in storages["volumes"]:
            if elem["id"] == storage["id"]:
                to_validate["id"] = elem["id"]
                to_validate["name"] = elem["name"]
                to_validate["size"] = elem["size"]
                to_validate["description"] = elem["description"]
                break

        assert storage_input == to_validate

    @staticmethod
    def test_delete_unused_storage(create_storage, create_global_project):
        conf = create_global_project
        storage = create_storage

        result = conf.saagie_api.storages.delete(storage["id"], conf.project_id)

        assert result == {"deleteVolume": {"id": storage["id"], "name": storage["name"]}}

    @staticmethod
    def test_delete_used_storage(create_global_project):
        conf = create_global_project
        # need to create an app with a storage, upgrage the app to associated another storage then unlink the first one
        create_app = conf.saagie_api.apps.create_from_catalog(
            project_id=conf.project_id,
            technology_catalog="Saagie",
            technology_name="Jupyter Notebook",
            context="JupyterLab Python 3.8 / 3.9 / 3.10",
        )

        app_id = create_app["installApp"]["id"]
        app_info = conf.saagie_api.apps.get_info(app_id)

        for volume in app_info["app"]["currentVersion"]["volumesWithPath"]:
            storage_id = volume["volume"]["id"]

        with pytest.raises(ValueError) as vale:
            conf.saagie_api.storages.delete(storage_id, conf.project_id)
        assert str(vale.value).startswith(f"❌ Storage '{storage_id}' is currently used by an App. Deletion impossible.")

    @staticmethod
    def test_unlink_unused_storage(create_storage, create_global_project):
        conf = create_global_project

        # need to create an app with a storage, upgrage the app to associated another storage then unlink the first one
        create_app = conf.saagie_api.apps.create_from_catalog(
            project_id=conf.project_id,
            technology_catalog="Saagie",
            technology_name="Jupyter Notebook",
            context="JupyterLab Python 3.8 / 3.9 / 3.10",
        )
        app_id = create_app["installApp"]["id"]
        app_info = conf.saagie_api.apps.get_info(app_id)

        storage2 = create_storage

        for volume in app_info["app"]["currentVersion"]["volumesWithPath"]:
            storage_id = volume["volume"]["id"]
            storage_name = volume["volume"]["name"]
            volume_with_path = volume

        if "volume" in volume_with_path.keys():
            del volume_with_path["volume"]
        volume_with_path["volumeId"] = storage2["id"]
        conf.saagie_api.apps.upgrade(app_id=app_id, storage_paths=volume_with_path)

        unlink_storage = conf.saagie_api.storages.unlink(storage_id, conf.project_id)

        assert unlink_storage == {"unlinkVolume": {"id": storage_id, "name": storage_name}}

    @staticmethod
    def test_unlink_used_storage(create_global_project):
        conf = create_global_project

        create_app = conf.saagie_api.apps.create_from_catalog(
            project_id=conf.project_id,
            technology_catalog="Saagie",
            technology_name="Jupyter Notebook",
            context="JupyterLab Python 3.8 / 3.9 / 3.10",
        )

        app_id = create_app["installApp"]["id"]
        app_info = conf.saagie_api.apps.get_info(app_id)

        for volume in app_info["app"]["currentVersion"]["volumesWithPath"]:
            storage_id = volume["volume"]["id"]

        with pytest.raises(ValueError) as vale:
            conf.saagie_api.storages.unlink(storage_id, conf.project_id)
        assert str(vale.value).startswith(f"❌ Storage '{storage_id}' is currently used by an App. Unlink impossible.")
