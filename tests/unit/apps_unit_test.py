# pylint: disable=attribute-defined-outside-init
import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from gql import gql

from saagieapi.apps import Apps
from saagieapi.apps.gql_queries import *

from .saagie_api_unit_test import create_gql_client


class TestApps:
    @pytest.fixture
    def saagie_api_mock(self):
        saagie_api_mock = Mock()

        saagie_api_mock.client.execute = MagicMock()
        return saagie_api_mock

    def setup_method(self):
        self.client = create_gql_client()

    def test_list_apps_for_project_gql(self):
        query = gql(GQL_LIST_APPS_FOR_PROJECT)
        self.client.validate(query)

    def test_list_apps_for_project(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": project_id,
            "minimal": False,
            "versionsOnlyCurrent": False,
        }

        expected_query = gql(GQL_LIST_APPS_FOR_PROJECT)

        app.list_for_project(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_list_apps_for_project_minimal(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": project_id,
            "minimal": True,
            "versionsOnlyCurrent": True,
        }

        expected_query = gql(GQL_LIST_APPS_FOR_PROJECT)

        app.list_for_project_minimal(project_id=project_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=False
        )

    def test_get_app_info_gql(self):
        query = gql(GQL_GET_APP_INFO)
        self.client.validate(query)

    def test_get_app_info(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": app_id,
            "versionsOnlyCurrent": True,
        }

        expected_query = gql(GQL_GET_APP_INFO)

        app.get_info(app_id=app_id)

        saagie_api_mock.client.execute.assert_called_with(
            query=expected_query, variable_values=params, pprint_result=None
        )

    def test_create_app_scratch_gql(self):
        query = gql(GQL_CREATE_APP_SCRATCH)
        self.client.validate(query)

    def test_create_app_scratch_success(self, saagie_api_mock):
        saagie_api_mock.get_repositories_info.return_value = {
            "repositories": [
                {
                    "id": "9fcbddfe-a7b7-4d25-807c-ad030782c923",
                    "name": "Saagie",
                    "technologies": [
                        {
                            "id": "5cbb55aa-8ce9-449b-b0b9-64cc6781ea89",
                            "label": "R",
                            "available": True,
                        },
                        {
                            "id": "36912c68-d084-43b9-9fda-b5ded8eb7b13",
                            "label": "Docker image",
                            "available": True,
                        },
                        {
                            "id": "1d117fb6-0697-438a-b419-a69e0e7406e8",
                            "label": "Spark",
                            "available": True,
                        },
                    ],
                },
                {
                    "id": "fff42d30-2029-4f23-b326-d751f256f533",
                    "name": "Saagie Community",
                    "technologies": [
                        {
                            "id": "034c28d7-c21f-4d7c-8dd9-7d09bc02f33f",
                            "label": "ShinyProxy",
                            "available": True,
                        }
                    ],
                },
            ]
        }
        app = Apps(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        exposed_ports = [
            {
                "basePathVariableName": "SAAGIE_BASE_PATH",
                "isRewriteUrl": True,
                "scope": "PROJECT",
                "number": 5000,
                "name": "Test Port",
            }
        ]

        params = {
            "app": {
                "projectId": project_id,
                "name": "name",
                "description": "",
                "version": {
                    "dockerInfo": {
                        "image": "",
                        "dockerCredentialsId": "credentials",
                    },
                    "ports": exposed_ports,
                    "releaseNote": "",
                    "volumesWithPath": [],
                },
                "technologyId": "36912c68-d084-43b9-9fda-b5ded8eb7b13",
                "alerting": {"statusList": ["RECOVERING", "FAILED"], "emails": ["test@email.com"]},
                "resources": {"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}},
            }
        }

        expected_query = gql(GQL_CREATE_APP_SCRATCH)

        app.create_from_scratch(
            project_id=project_id,
            app_name="name",
            exposed_ports=exposed_ports,
            emails=["test@email.com"],
            status_list=["RECOVERING", "FAILED"],
            docker_credentials_id="credentials",
            resources={"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}},
        )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_app_scratch_error(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        with pytest.raises(ValueError):
            app.create_from_scratch(
                project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                app_name="name",
            )

    def test_create_app_catalog_gql(self):
        query = gql(GQL_CREATE_APP_CATALOG)
        self.client.validate(query)

    def test_create_app_catalog_success(self, saagie_api_mock):
        saagie_api_mock.projects.get_apps_technologies.return_value = {
            "appTechnologies": [
                {"id": "11d63963-0a74-4821-b17b-8fcec4882863"},
                {"id": "56ad4996-7285-49a6-aece-b9525c57c619"},
                {"id": "d0b55623-9dc0-4e03-89c7-6a2494387a4f"},
            ]
        }
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        saagie_api_mock.get_runtimes.return_value = {
            "technology": {"appContexts": [{"id": "7.15.1", "available": True, "label": "7.15.1"}]}
        }
        app = Apps(saagie_api_mock)

        project_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "projectId": project_id,
            "contextId": "7.15.1",
        }

        expected_query = gql(GQL_CREATE_APP_CATALOG)

        app.create_from_catalog(
            project_id=project_id,
            context="7.15.1",
            technology_name="kibana",
        )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_create_app_catalog_error(self, saagie_api_mock):
        saagie_api_mock.projects.get_apps_technologies.return_value = {
            "appTechnologies": [
                {"id": "11d63963-0a74-4821-b17b-8fcec4882863"},
                {"id": "56ad4996-7285-49a6-aece-b9525c57c619"},
                {"id": "d0b55623-9dc0-4e03-89c7-6a2494387a4f"},
            ]
        }
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        saagie_api_mock.get_runtimes.return_value = {
            "technology": {"appContexts": [{"id": "7.15.1", "available": False, "label": "7.15.1"}]}
        }
        app = Apps(saagie_api_mock)

        with pytest.raises(ValueError):
            app.create_from_catalog(
                project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                context="7.15.1",
                technology_name="kibana",
            )

    def test_edit_app_gql(self):
        query = gql(GQL_EDIT_APP)
        self.client.validate(query)

    def test_edit_app(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        name = "new_name"
        description = "new_description"
        emails = ["test@email.com"]
        status = ["RECOVERING", "FAILED"]
        resources = {"cpu": {"request": 1.5, "limit": 2.2}, "memory": {"request": 2.0}}

        params = {
            "app": {
                "id": app_id,
                "name": name,
                "description": description,
                "alerting": {"statusList": status, "emails": emails},
                "resources": resources,
            }
        }

        expected_query = gql(GQL_EDIT_APP)

        with patch.object(app, "get_info") as info, patch.object(app, "check_alerting") as chk_alert:
            info.return_value = {"app": {"alerting": {"statusList": status, "emails": emails}}}
            chk_alert.return_value = {"statusList": status, "emails": emails}
            app.edit(
                app_id=app_id,
                app_name=name,
                description=description,
                emails=emails,
                status_list=status,
                resources=resources,
            )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_delete_app_gql(self):
        query = gql(GQL_DELETE_APP)
        self.client.validate(query)

    def test_delete_app(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {"appId": app_id}

        expected_query = gql(GQL_DELETE_APP)

        app.delete(app_id=app_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_run_app_gql(self):
        query = gql(GQL_RUN_APP)
        self.client.validate(query)

    def test_run_app(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {"id": app_id}

        expected_query = gql(GQL_RUN_APP)

        app.run(app_id=app_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_stop_app_gql(self):
        query = gql(GQL_STOP_APP)
        self.client.validate(query)

    def test_stop_app(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "id": app_id,
        }

        expected_query = gql(GQL_STOP_APP)

        app.stop(app_id=app_id)

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    @staticmethod
    def test_check_exposed_ports():
        valid_exposed_ports = [
            {
                "number": 80,
                "basePathVariableName": "my-variable",
                "isRewriteUrl": False,
                "scope": "PROJECT",
            }
        ]

        invalid_exposed_ports = valid_exposed_ports + [
            {
                "ports": 80,
                "basePathVariableName": "my-variable",
                "isRewriteUrl": False,
                "scope": "PROJECT",
            }
        ]

        invalid_keys = valid_exposed_ports + [
            {
                "number": 81,
                "basePathVariableName": "my-variable2",
                "isRewriteUrl": True,
                "isAuthenticationRequired": True,
            }
        ]
        assert Apps.check_exposed_ports(valid_exposed_ports)
        assert not Apps.check_exposed_ports([])
        assert not Apps.check_exposed_ports(invalid_exposed_ports)
        assert not Apps.check_exposed_ports(invalid_keys)

    @staticmethod
    def test_check_app_alerting():
        emails = ["email1@saagie.com", "email2@saagie.com"]
        logins = ["login1", "login2"]
        status_list = ["STARTED", "FAILED"]

        # Test a valid and complete app alerting
        result = Apps.check_alerting(emails, logins, status_list)
        assert result["emails"] == emails
        assert result["logins"] == logins
        assert result["statusList"] == status_list

        # Test with a a missing logins parameter
        assert Apps.check_alerting(status_list=status_list, emails=emails)

        # Test with a wrong status_list parameter
        with pytest.raises(RuntimeError) as rte:
            Apps.check_alerting(status_list=["FAILED", "RUNNING", "WRONGSTATUS"])
        assert str(rte.value).startswith("❌ The following status are not valid: ['RUNNING', 'WRONGSTATUS']")

        # Test without emails or logins
        with pytest.raises(RuntimeError) as rte:
            Apps.check_alerting(status_list=status_list)
        assert str(rte.value) == (
            "❌ You must provide a status list and either an email or a login to enable the alerting"
        )

    def test_upgrade_app_gql(self):
        query = gql(GQL_UPDATE_APP)
        self.client.validate(query)

    def test_upgrade_app(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "appId": app_id,
            "appVersion": {
                "ports": [
                    {
                        "name": "Notebook",
                        "number": 8888,
                        "isRewriteUrl": False,
                        "basePathVariableName": "SAAGIE_BASE_PATH",
                        "scope": "PROJECT",
                    },
                    {
                        "name": "SparkUI",
                        "number": 8080,
                        "isRewriteUrl": False,
                        "basePathVariableName": "SPARK_UI_PATH",
                        "scope": "PROJECT",
                    },
                ],
                "releaseNote": "",
                "volumesWithPath": None,
                "runtimeContextId": "jupyter-spark-3.1",
            },
        }

        expected_query = gql(GQL_UPDATE_APP)

        with patch.object(app, "get_info") as info:
            info.return_value = {
                "app": {
                    "currentVersion": {
                        "number": 1,
                        "creator": "toto.hi",
                        "creationDate": "2022-05-09T14:12:31.819Z",
                        "releaseNote": "First version of Jupyter Notebook with Spark 3.1 into Saagie.",
                        "dockerInfo": {"image": "dockerImageName"},
                        "runtimeContextId": "jupyter-spark-3.1",
                        "ports": [
                            {
                                "name": "Notebook",
                                "number": 8888,
                                "isRewriteUrl": False,
                                "basePathVariableName": "SAAGIE_BASE_PATH",
                                "scope": "PROJECT",
                                "internalUrl": "http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8888",
                            },
                            {
                                "name": "SparkUI",
                                "number": 8080,
                                "isRewriteUrl": False,
                                "basePathVariableName": "SPARK_UI_PATH",
                                "scope": "PROJECT",
                                "internalUrl": "http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8080",
                            },
                        ],
                        "volumesWithPath": [
                            {
                                "path": "/notebooks-dir",
                                "volume": {
                                    "id": "c163216a-b024-4cb1-8aae-0664bf2f58b4",
                                    "name": "storage Jupyter lab",
                                    "creator": "toto.hi",
                                    "description": "Created by migration from app c163216a-b024-4cb1-8aae-0664bf2f58b4",
                                    "size": "128 MB",
                                    "projectId": "96a74193-303d-43cf-adb2-a7300d5bb9df",
                                    "creationDate": "2022-05-09T14:12:31.819Z",
                                    "linkedApp": {"id": "b6e846d7-d871-46db-b858-7d39d6b60146", "name": "Jupyter lab"},
                                },
                            }
                        ],
                        "isMajor": False,
                    },
                }
            }
            app.upgrade(app_id=app_id, docker_credentials_id="credentials")

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_upgrade_app_error(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        with pytest.raises(ValueError):
            app.upgrade(
                app_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                technology_context=[],
                image="",
                docker_credentials_id="",
            )

    def test_rollback_app_gql(self):
        query = gql(GQL_ROLLBACK_APP_VERSION)
        self.client.validate(query)

    def test_rollback_app(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {
            "appId": app_id,
            "versionNumber": "1",
        }

        expected_query = gql(GQL_ROLLBACK_APP_VERSION)

        app.rollback(app_id=app_id, version_number="1")

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_export_success(self, saagie_api_mock, tmp_path):
        saagie_api_mock.get_technology_name_by_id.return_value = ("Saagie", "VS Code")
        app = Apps(saagie_api_mock)

        with patch.object(app, "get_info") as info, patch.object(app, "get_runtime_label_by_id") as runtime:
            info.return_value = {
                "app": {
                    "technology": {"id": "7d3f247c-b5a9-4a34-a0a2-f6b209bc2b63"},
                    "versions": [
                        {
                            "number": 1,
                            "creator": "toto.hi",
                            "creationDate": "2022-05-09T14:12:31.819Z",
                            "releaseNote": "First version of Jupyter Notebook with Spark 3.1 into Saagie.",
                            "dockerInfo": {"image": "dockerImageName"},
                            "runtimeContextId": "jupyter-spark-3.1",
                            "ports": [
                                {
                                    "name": "Notebook",
                                    "number": 8888,
                                    "isRewriteUrl": False,
                                    "basePathVariableName": "SAAGIE_BASE_PATH",
                                    "scope": "PROJECT",
                                    "internalUrl": "http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8888",
                                },
                                {
                                    "name": "SparkUI",
                                    "number": 8080,
                                    "isRewriteUrl": False,
                                    "basePathVariableName": "SPARK_UI_PATH",
                                    "scope": "PROJECT",
                                    "internalUrl": "http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8080",
                                },
                            ],
                            "volumesWithPath": [
                                {
                                    "path": "/notebooks-dir",
                                    "volume": {
                                        "id": "c163216a-b024-4cb1-8aae-0664bf2f58b4",
                                        "name": "storage Jupyter lab",
                                        "creator": "toto.hi",
                                        "description": "Created by migration from c163216a-b024-4cb1-8aae-0664bf2f58b4",
                                        "size": "128 MB",
                                        "projectId": "96a74193-303d-43cf-adb2-a7300d5bb9df",
                                        "creationDate": "2022-05-09T14:12:31.819Z",
                                        "linkedApp": {
                                            "id": "b6e846d7-d871-46db-b858-7d39d6b60146",
                                            "name": "Jupyter lab",
                                        },
                                    },
                                }
                            ],
                            "isMajor": False,
                        },
                    ],
                    "currentVersion": {
                        "number": 1,
                        "creator": "toto.hi",
                        "creationDate": "2022-05-09T14:12:31.819Z",
                        "releaseNote": "First version of Jupyter Notebook with Spark 3.1 into Saagie.",
                        "dockerInfo": {"image": "dockerImageName"},
                        "runtimeContextId": "jupyter-spark-3.1",
                        "ports": [
                            {
                                "name": "Notebook",
                                "number": 8888,
                                "isRewriteUrl": False,
                                "basePathVariableName": "SAAGIE_BASE_PATH",
                                "scope": "PROJECT",
                                "internalUrl": "http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8888",
                            },
                            {
                                "name": "SparkUI",
                                "number": 8080,
                                "isRewriteUrl": False,
                                "basePathVariableName": "SPARK_UI_PATH",
                                "scope": "PROJECT",
                                "internalUrl": "http://app-b6e846d7-d871-46db-b858-7d39d6b60146:8080",
                            },
                        ],
                        "volumesWithPath": [
                            {
                                "path": "/notebooks-dir",
                                "volume": {
                                    "id": "c163216a-b024-4cb1-8aae-0664bf2f58b4",
                                    "name": "storage Jupyter lab",
                                    "creator": "toto.hi",
                                    "description": "Created by migration from app c163216a-b024-4cb1-8aae-0664bf2f58b4",
                                    "size": "128 MB",
                                    "projectId": "96a74193-303d-43cf-adb2-a7300d5bb9df",
                                    "creationDate": "2022-05-09T14:12:31.819Z",
                                    "linkedApp": {"id": "b6e846d7-d871-46db-b858-7d39d6b60146", "name": "Jupyter lab"},
                                },
                            }
                        ],
                        "isMajor": False,
                    },
                }
            }
            runtime.side_effect = ["jupyter-spark-3.1", "jupyter-spark-3.1"]
            res = app.export(app_id="app_id", output_folder=tmp_path)

        assert res is True

    def test_export_error(self, saagie_api_mock, tmp_path):
        saagie_api_mock.get_technology_name_by_id.return_value = ("Saagie", "VS Code")
        app = Apps(saagie_api_mock)

        with patch.object(app, "get_info") as info:
            info.return_value = {}
            res = app.export(app_id="app_id", output_folder=tmp_path)

        assert res is False

    def test_import_app_success(self, saagie_api_mock, tmp_path):
        saagie_api_mock.projects.get_apps_technologies.return_value = {
            "appTechnologies": [
                {"id": "11d63963-0a74-4821-b17b-8fcec4882863"},
                {"id": "56ad4996-7285-49a6-aece-b9525c57c619"},
                {"id": "d0b55623-9dc0-4e03-89c7-6a2494387a4f"},
            ]
        }
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        saagie_api_mock.get_runtimes.return_value = {
            "technology": {
                "appContexts": [
                    {
                        "id": "JupyterLab+GenAI 4.0 Python 3.10",
                        "available": True,
                        "label": "JupyterLab+GenAI 4.0 Python 3.10",
                    }
                ]
            }
        }
        app = Apps(saagie_api_mock)

        cur_path = Path(__file__).parent
        cur_path = cur_path.parent / "integration" / "resources" / "import" / "project"

        origin_path = cur_path / "apps" / "from-catalog" / "app.json"
        with origin_path.open("r", encoding="utf-8") as file:
            app_info = json.load(file)

        tmp_file = Path(tmp_path / "apps" / "app" / "app.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(app_info, file, indent=4)

        with patch.object(app, "create_from_scratch") as create:
            create.return_value = {"createApp": {"id": "1221f83e-52de-4beb-89a0-1505de4e875f"}}
            app_result = app.import_from_json(json_file=tmp_file, project_id="project_id")

        assert app_result is True

    def test_import_app_error_runtime(self, saagie_api_mock, tmp_path):
        saagie_api_mock.projects.get_apps_technologies.return_value = {
            "appTechnologies": [
                {"id": "11d63963-0a74-4821-b17b-8fcec4882863"},
                {"id": "56ad4996-7285-49a6-aece-b9525c57c619"},
                {"id": "d0b55623-9dc0-4e03-89c7-6a2494387a4f"},
            ]
        }
        saagie_api_mock.check_technology.return_value = {"technologyId": "1234"}
        saagie_api_mock.get_runtimes.return_value = {
            "technology": {
                "appContexts": [
                    {
                        "id": "JupyterLab+GenAI 4.0 Python 3.10",
                        "available": False,
                        "label": "JupyterLab+GenAI 4.0 Python 3.10",
                    }
                ]
            }
        }
        app = Apps(saagie_api_mock)

        cur_path = Path(__file__).parent
        cur_path = cur_path.parent / "integration" / "resources" / "import" / "project"

        origin_path = cur_path / "apps" / "from-catalog" / "app.json"
        with origin_path.open("r", encoding="utf-8") as file:
            app_info = json.load(file)

        tmp_file = Path(tmp_path / "apps" / "app" / "app.json")
        tmp_file.parent.mkdir(parents=True)
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(app_info, file, indent=4)

        app_result = app.import_from_json(json_file=tmp_file, project_id="project_id")

        assert app_result is False

    def test_import_app_error_reading_json(self, saagie_api_mock, tmp_path):
        app = Apps(saagie_api_mock)

        tmp_file = Path(tmp_path / "app.json")
        tmp_file.write_text("This is not a json format.", encoding="utf-8")

        app_result = app.import_from_json(json_file=tmp_file, project_id="project_id")

        assert app_result is False

    def test_get_app_id_found(self, saagie_api_mock):
        saagie_api_mock.projects.get_id.return_value = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        app = Apps(saagie_api_mock)

        with patch.object(app, "list_for_project_minimal") as list_apps:
            list_apps.return_value = {
                "project": {"apps": [{"id": "d0d6a466-10d9-4120-8101-56e46563e05a", "name": "Jupyter Notebook"}]}
            }
            res = app.get_id(app_name="Jupyter Notebook", project_name="project_name")

        assert res == "d0d6a466-10d9-4120-8101-56e46563e05a"

    def test_get_app_id_not_found(self, saagie_api_mock):
        saagie_api_mock.projects.get_id.return_value = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"
        app = Apps(saagie_api_mock)

        with patch.object(app, "list_for_project_minimal") as list_apps, pytest.raises(NameError):
            list_apps.return_value = {
                "project": {"apps": [{"id": "d0d6a466-10d9-4120-8101-56e46563e05a", "name": "Jupyter Notebook"}]}
            }
            app.get_id(app_name="app_name", project_name="project_name")

    def test_stats_app_gql(self):
        query = gql(GQL_STATS_APP)
        self.client.validate(query)

    def test_stats_app(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        history_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {"appHistoryId": history_id, "versionNumber": 1, "startTime": "2024-04-10T14:26:27.073Z"}

        expected_query = gql(GQL_STATS_APP)

        app.get_stats(history_id=history_id, version_number=1, start_time="2024-04-10T14:26:27.073Z")

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_history_app_statuses_gql(self):
        query = gql(GQL_HISTORY_APP_STATUS)
        self.client.validate(query)

    def test_history_app_statuses(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        history_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {"appHistoryId": history_id, "versionNumber": 1, "startTime": "2024-04-10T14:26:27.073Z"}

        expected_query = gql(GQL_HISTORY_APP_STATUS)

        app.get_history_statuses(history_id=history_id, version_number=1, start_time="2024-04-10T14:26:27.073Z")

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_count_history_app_statuses_gql(self):
        query = gql(GQL_COUNT_HISTORY_APP_STATUS)
        self.client.validate(query)

    def test_count_history_app_statuses(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        history_id = "860b8dc8-e634-4c98-b2e7-f9ec32ab4771"

        params = {"appHistoryId": history_id, "versionNumber": 1, "startTime": "2024-04-10T14:26:27.073Z"}

        expected_query = gql(GQL_COUNT_HISTORY_APP_STATUS)

        app.count_history_statuses(history_id=history_id, version_number=1, start_time="2024-04-10T14:26:27.073Z")

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)

    def test_get_app_logs_gql(self):
        query = gql(GQL_GET_APP_LOG)
        self.client.validate(query)

    def test_get_app_logs(self, saagie_api_mock):
        app = Apps(saagie_api_mock)

        app_id = "70e85ade-d6cc-4a90-8d7d-639adbd25e5d"
        app_execution_id = "e3e31074-4a12-450e-96e4-0eae7801dfca"
        limit = 2
        skip = 5
        stream = "STDERR"
        start_at = "2024-04-09 10:00:00"

        params = {
            "appId": app_id,
            "appExecutionId": app_execution_id,
            "limit": limit,
            "skip": skip,
            "stream": stream,
            "recordAt": start_at,
        }

        expected_query = gql(GQL_GET_APP_LOG)

        app.get_logs(
            app_id=app_id,
            app_execution_id=app_execution_id,
            limit=limit,
            skip=skip,
            log_stream=stream,
            start_at=start_at,
        )

        saagie_api_mock.client.execute.assert_called_with(query=expected_query, variable_values=params)
