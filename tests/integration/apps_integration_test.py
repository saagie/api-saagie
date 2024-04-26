import json
import os
import time
from datetime import datetime
from pathlib import Path

import pytest


class TestIntegrationApps:
    @pytest.fixture
    @staticmethod
    def create_app_from_scratch(create_global_project):
        conf = create_global_project
        app_name = f"hello_world{datetime.now()}"
        app = conf.saagie_api.apps.create_from_scratch(
            project_id=conf.project_id,
            app_name=app_name,
            image="httpd:2.4.54-alpine",
            description="Be happy",
            exposed_ports=[{"number": 80, "isRewriteUrl": True, "scope": "PROJECT"}],
        )
        return app["createApp"]["id"]

    @pytest.fixture
    @staticmethod
    def create_then_delete_app_from_scratch(create_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_app_from_scratch

        yield app_id

        conf.saagie_api.apps.delete(app_id=app_id)

    @staticmethod
    def test_create_app_from_scratch(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch
        app = conf.saagie_api.apps.get_info(app_id)

        assert app["app"]["description"] == "Be happy"

    @staticmethod
    def test_upgrade_app_from_scratch(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project

        app_id = create_then_delete_app_from_scratch
        app = conf.saagie_api.apps.get_info(app_id)["app"]

        app_upgraded = conf.saagie_api.apps.upgrade(app_id, "my new release note")

        assert app_upgraded["addAppVersion"]["number"] == app["currentVersion"]["number"] + 1

    @staticmethod
    def test_upgrade_app_wrong_parameter(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project

        app_id = create_then_delete_app_from_scratch

        with pytest.raises(ValueError) as vale:
            conf.saagie_api.apps.upgrade(
                app_id=app_id, release_note="my new release note", technology_context="jupyter", image="nginx"
            )

        assert str(vale.value).startswith("❌ Incompatible parameters set up.")

    @staticmethod
    def test_export_app(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch
        result = conf.saagie_api.apps.export(app_id, os.path.join(conf.output_dir, "apps"))
        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_export_app_only_current_version(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch
        result = conf.saagie_api.apps.export(app_id, os.path.join(conf.output_dir, "apps"), versions_only_current=True)
        to_validate = True
        assert result == to_validate

    @staticmethod
    def test_import_app_from_catalog(create_global_project):
        conf = create_global_project

        json_path = conf.import_dir / "project" / "apps" / "from-catalog" / "app.json"

        result = conf.saagie_api.apps.import_from_json(
            json_file=json_path,
            project_id=conf.project_id,
        )

        with Path(json_path).open("r", encoding="utf-8") as file:
            app_info = json.load(file)

        app = conf.saagie_api.apps.get_info(conf.saagie_api.apps.get_id(app_info["name"], conf.project_name))

        conf.saagie_api.apps.delete(app["app"]["id"])
        # need to delete the storage linked
        for storage in app["app"]["currentVersion"]["volumesWithPath"]:
            conf.saagie_api.storages.delete(storage["volume"]["id"], conf.project_id)

        assert result is True

    @staticmethod
    def test_import_app_from_scratch(create_global_project):
        conf = create_global_project

        json_path = conf.import_dir / "project" / "apps" / "from-scratch" / "app.json"

        result = conf.saagie_api.apps.import_from_json(
            json_file=json_path,
            project_id=conf.project_id,
        )

        with Path(json_path).open("r", encoding="utf-8") as file:
            app_info = json.load(file)

        app = conf.saagie_api.apps.get_info(conf.saagie_api.apps.get_id(app_info["name"], conf.project_name))

        conf.saagie_api.apps.delete(app["app"]["id"])
        # need to delete the storage linked
        for storage in app["app"]["currentVersion"]["volumesWithPath"]:
            conf.saagie_api.storages.delete(storage["volume"]["id"], conf.project_id)

        assert result is True

    @staticmethod
    def test_run_app(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

        app_info = conf.saagie_api.apps.get_info(app_id=app_id)
        if app_info["app"]["history"]["currentStatus"].startswith("START"):
            conf.saagie_api.apps.stop(app_id=app_id)
            tries = 60
            while app_info["app"]["history"]["currentStatus"] != "STOPPED" and tries > 0:
                app_info = conf.saagie_api.apps.get_info(app_id=app_id)
                time.sleep(1)
                tries -= 1
            if tries == 0:
                raise TimeoutError("App is not stopped")

        conf.saagie_api.apps.run(app_id=app_id)

        app_after_run = conf.saagie_api.apps.get_info(app_id=app_id)

        assert app_after_run["app"]["history"]["currentStatus"].startswith("START")

    @staticmethod
    def test_stop_app(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

        app_info = conf.saagie_api.apps.get_info(app_id=app_id)
        tries = 60
        while app_info["app"]["history"]["currentStatus"] != "STARTED" and tries > 0:
            app_info = conf.saagie_api.apps.get_info(app_id=app_id)
            time.sleep(1)
            tries -= 1
        if tries == 0:
            raise TimeoutError("App is not started")

        conf.saagie_api.apps.stop(app_id=app_id)

        app_after_run = conf.saagie_api.apps.get_info(app_id=app_id)

        assert app_after_run["app"]["history"]["currentStatus"].startswith("STOP")

    @staticmethod
    def test_edit_app(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

        app_input = {
            "name": "hi new name",
            "description": "new description",
            "alerting": {
                "emails": ["hello.world@gmail.com"],
                "statusList": ["FAILED", "STOPPED"],
            },
        }
        conf.saagie_api.apps.edit(
            app_id,
            app_name=app_input["name"],
            description=app_input["description"],
            emails=app_input["alerting"]["emails"],
            status_list=app_input["alerting"]["statusList"],
        )

        app_info = conf.saagie_api.apps.get_info(app_id)
        to_validate = {
            "name": app_info["app"]["name"],
            "description": app_info["app"]["description"],
            "alerting": app_info["app"]["alerting"],
        }
        del to_validate["alerting"]["loginEmails"]
        assert app_input == to_validate

    @staticmethod
    def test_edit_app_without_alerting(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

        app_input = {
            "name": "hi new name",
            "description": "new description",
        }
        conf.saagie_api.apps.edit(app_id, app_name=app_input["name"], description=app_input["description"])

        app_info = conf.saagie_api.apps.get_info(app_id)
        to_validate = {"name": app_info["app"]["name"], "description": app_info["app"]["description"]}
        assert app_input == to_validate

    @pytest.fixture
    @staticmethod
    def create_app_from_catalog(create_global_project):
        conf = create_global_project
        app = conf.saagie_api.apps.create_from_catalog(
            project_id=conf.project_id,
            technology_name="Kibana",
            context="7.15.1",
        )

        yield app["installApp"]["id"]

        conf.saagie_api.apps.delete(app["installApp"]["id"])

    @pytest.fixture
    @staticmethod
    def create_grafana_from_catalog(create_global_project):
        conf = create_global_project
        app = conf.saagie_api.apps.create_from_catalog(
            project_id=conf.project_id,
            technology_name="Grafana",
            context="8.2",
        )

        yield app["installApp"]["id"]

        app_info = conf.saagie_api.apps.get_info(app["installApp"]["id"])

        conf.saagie_api.apps.delete(app["installApp"]["id"])

        # need to delete the storage linked
        for storage in app_info["app"]["currentVersion"]["volumesWithPath"]:
            conf.saagie_api.storages.delete(storage["volume"]["id"], conf.project_id)

    @pytest.fixture
    @staticmethod
    def create_then_delete_app_from_catalog(create_app_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_app_from_catalog

        yield app_id

        conf.saagie_api.apps.delete(app_id=app_id)

    @staticmethod
    def test_create_app_from_catalog(create_then_delete_app_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_catalog

        app = conf.saagie_api.apps.get_info(app_id)

        assert app["app"]["name"] == "Kibana"

    @staticmethod
    def test_delete_app_from_catalog(create_app_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_app_from_catalog
        result = conf.saagie_api.apps.delete(app_id)

        assert result == {"deleteApp": {"id": app_id}}

    @staticmethod
    def test_get_app_id(create_grafana_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_grafana_from_catalog

        app_name = "Grafana"
        output_app_id = conf.saagie_api.apps.get_id(app_name, conf.project_name)

        assert app_id == output_app_id

    @staticmethod
    def test_rollback_app_version(create_app_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_app_from_catalog
        conf.saagie_api.apps.upgrade(
            app_id=app_id,
            release_note="new version",
        )

        app_rollback = conf.saagie_api.apps.rollback(app_id=app_id, version_number="1")

        assert app_rollback["rollbackAppVersion"]["currentVersion"]["number"] == 1

    @staticmethod
    def test_get_stats(create_global_project, create_app_from_catalog):
        conf = create_global_project
        app_id = create_app_from_catalog

        app_info = conf.saagie_api.apps.get_info(app_id=app_id)

        app_history_id = app_info["app"]["history"]["id"]
        version = app_info["app"]["currentVersion"]["number"]
        start_time = app_info["app"]["currentVersion"]["creationDate"]

        result = conf.saagie_api.apps.get_stats(
            history_id=app_history_id, version_number=version, start_time=start_time
        )

        assert "appStats" in result

    @staticmethod
    def test_get_history_statuses(create_global_project, create_then_delete_app_from_scratch):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

        app_info = conf.saagie_api.apps.get_info(app_id=app_id)

        app_history_id = app_info["app"]["history"]["id"]
        version = app_info["app"]["currentVersion"]["number"]
        start_time = app_info["app"]["currentVersion"]["creationDate"]

        result = conf.saagie_api.apps.get_history_statuses(
            history_id=app_history_id, version_number=version, start_time=start_time
        )

        assert "appHistoryStatuses" in result

    @staticmethod
    def test_count_history_statuses(create_global_project, create_then_delete_app_from_scratch):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

        app_info = conf.saagie_api.apps.get_info(app_id=app_id)

        app_history_id = app_info["app"]["history"]["id"]
        version = app_info["app"]["currentVersion"]["number"]
        start_time = app_info["app"]["currentVersion"]["creationDate"]

        result = conf.saagie_api.apps.count_history_statuses(
            history_id=app_history_id, version_number=version, start_time=start_time
        )

        assert "countAppHistoryStatuses" in result

    @staticmethod
    def test_get_app_logs(create_global_project, create_then_delete_app_from_scratch):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

        app_info = conf.saagie_api.apps.run(app_id=app_id)

        app_info = conf.saagie_api.apps.get_info(app_id=app_id)

        app_execution_id = app_info["app"]["history"]["currentExecutionId"]

        result = conf.saagie_api.apps.get_logs(app_id=app_id, app_execution_id=app_execution_id)

        assert "appLogs" in result
