import time
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
            storage_size="1 GB",
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
            "size": "1.0 GB",
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

    @pytest.fixture
    @staticmethod
    def create_app_from_catalog(create_global_project):
        conf = create_global_project

        create_app = conf.saagie_api.apps.create_from_catalog(
            project_id=conf.project_id,
            technology_catalog="Saagie",
            technology_name="Jupyter Notebook",
            context="JupyterLab+GenAI 4.0 Python 3.10",
        )
        app_id = create_app["installApp"]["id"]

        yield app_id

        app_info = conf.saagie_api.apps.get_info(app_id)
        conf.saagie_api.apps.delete(app_id)

        for storage in app_info["app"]["currentVersion"]["volumesWithPath"]:
            conf.saagie_api.storages.delete(storage["volume"]["id"], conf.project_id)

    @staticmethod
    def test_delete_used_storage(create_global_project, create_app_from_catalog):
        conf = create_global_project
        # need to create an app with a storage, upgrage the app to associated another storage then unlink the first one
        app_id = create_app_from_catalog
        app_info = conf.saagie_api.apps.get_info(app_id)

        for volume in app_info["app"]["currentVersion"]["volumesWithPath"]:
            storage_id = volume["volume"]["id"]

        with pytest.raises(ValueError) as vale:
            conf.saagie_api.storages.delete(storage_id, conf.project_id)
        assert str(vale.value).startswith(f"❌ Storage '{storage_id}' is currently used by an App. Deletion impossible.")

    @staticmethod
    def test_unlink_unused_storage(create_global_project, create_storage, create_app_from_catalog):
        conf = create_global_project

        # need to create an app with a storage, upgrage the app to associated another storage then unlink the first one
        app_id = create_app_from_catalog
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

        conf.saagie_api.storages.delete(storage_id, conf.project_id)

        assert unlink_storage == {"unlinkVolume": {"id": storage_id, "name": storage_name}}

    @staticmethod
    def test_unlink_used_storage(create_global_project, create_app_from_catalog):
        conf = create_global_project

        app_id = create_app_from_catalog
        app_info = conf.saagie_api.apps.get_info(app_id)

        for volume in app_info["app"]["currentVersion"]["volumesWithPath"]:
            storage_id = volume["volume"]["id"]

        with pytest.raises(ValueError) as vale:
            conf.saagie_api.storages.unlink(storage_id, conf.project_id)
        assert str(vale.value).startswith(f"❌ Storage '{storage_id}' is currently used by an App. Unlink impossible.")

    @staticmethod
    def test_move_storage(create_global_project, create_storage):
        conf = create_global_project

        storage = create_storage

        res_proj = conf.saagie_api.projects.create(
            name="test_move_storage",
            group=conf.group,
            role="Manager",
            jobs_technologies_allowed={"saagie": ["python", "spark", "bash"]},
            description="test_move_storage",
        )

        project_id = res_proj["createProject"]["id"]

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

        result = conf.saagie_api.storages.move(
            storage_id=storage["id"],
            target_platform_id=1,
            target_project_id=project_id,
        )

        res = conf.saagie_api.storages.get(storage_id=result["moveVolume"])

        conf.saagie_api.projects.delete(project_id)

        # assert result == {"moveVolume": storage["id"]}
        assert res["volume"]["name"] == storage["name"]

    @staticmethod
    def test_get_storage_info(create_then_delete_storage, create_global_project):
        conf = create_global_project

        storage = create_then_delete_storage

        result = conf.saagie_api.storages.get(storage_id=storage["id"])
        del result["volume"]["creationDate"]

        assert storage == result["volume"]

    @staticmethod
    def test_duplicate_storage(create_then_delete_storage, create_global_project):
        conf = create_global_project

        storage = create_then_delete_storage

        # needed to let the time to the storage to be created and ready in the orchestrator
        time.sleep(5)

        result = conf.saagie_api.storages.duplicate(storage_id=storage["id"])

        time.sleep(15)

        conf.saagie_api.storages.delete(result["duplicateVolume"]["id"], conf.project_id)

        assert result["duplicateVolume"]["originalVolumeId"] == storage["id"]
