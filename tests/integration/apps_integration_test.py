import os
import time
from datetime import datetime

import pytest


class TestIntegrationApps:
    @pytest.fixture
    @staticmethod
    def create_app_from_scratch(create_global_project):
        conf = create_global_project
        app_name = "hello_world" + str(datetime.now())
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
    def test_create_app_from_scratch(create_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_app_from_scratch
        app = conf.saagie_api.apps.get_info(app_id)

        assert app["app"]["description"] == "Be happy"

    @staticmethod
    def test_upgrade_app_from_scratch(create_app_from_scratch, create_global_project):
        conf = create_global_project

        app_id = create_app_from_scratch
        app = conf.saagie_api.apps.get_info(app_id)["app"]

        app_upgraded = conf.saagie_api.apps.upgrade(app_id, "my new release note")

        assert app_upgraded["addAppVersion"]["number"] == app["currentVersion"]["number"] + 1

    @staticmethod
    def test_upgrade_app_wrong_parameter(create_app_from_scratch, create_global_project):
        conf = create_global_project

        app_id = create_app_from_scratch

        with pytest.raises(ValueError) as vale:
            conf.saagie_api.apps.upgrade(
                app_id=app_id, release_note="my new release note", technology_context="jupyter", image="nginx"
            )

        assert str(vale.value).startswith(f"❌ Incompatible parameters setted up.")

    @staticmethod
    def export_app(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch
        result = conf.saagie_api.apps.export(app_id, os.path.join(conf.output_dir, "apps"))
        to_validate = True
        assert result == to_validate

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
                raise Exception("App is not stopped")

        conf.saagie_api.apps.run(app_id=app_id)

        app_after_run = conf.saagie_api.apps.get_info(app_id=app_id)

        assert app_after_run["app"]["history"]["currentStatus"].startswith("START")

    @staticmethod
    def test_stop_app(create_then_delete_app_from_scratch, create_global_project):
        conf = create_global_project
        app_id = create_then_delete_app_from_scratch

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

    @pytest.fixture
    @staticmethod
    def create_app_from_catalog(create_global_project):
        conf = create_global_project
        app = conf.saagie_api.apps.create_from_catalog(
            project_id=conf.project_id,
            technology_name="Kibana",
            context="7.15.1",
        )

        return app["installApp"]["id"]

    @pytest.fixture
    @staticmethod
    def create_then_delete_app_from_catalog(create_app_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_app_from_catalog

        yield app_id

        conf.saagie_api.apps.delete(app_id=app_id)

    @staticmethod
    def test_create_app_from_catalog(create_app_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_app_from_catalog

        app = conf.saagie_api.apps.get_info(app_id)

        assert app["app"]["name"] == "Kibana"

    @staticmethod
    def test_delete_app_from_catalog(create_app_from_catalog, create_global_project):
        conf = create_global_project
        app_id = create_app_from_catalog
        result = conf.saagie_api.apps.delete(app_id)

        assert result == {"deleteApp": {"id": app_id}}
