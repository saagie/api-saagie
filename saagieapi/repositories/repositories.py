import logging
from pathlib import Path
from typing import Dict, Optional

from gql import gql

from .gql_queries import *


class Repositories:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list(
        self, minimal: Optional[bool] = False, last_synchronization: bool = True, pprint_result: Optional[bool] = None
    ) -> Dict:
        """
        Get information for all repositories
        NB: You can only get repositories information if you have the right to
        access the technology catalog

        Parameters
        ----------
        minimal : bool, optional
            Whether to only return the repository's name and id, default to False
        last_synchronization : bool, optional
            Whether to only fetch the last synchronization of each repository
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of repositories

        Examples
        --------
        >>> saagieapi.repositories.list()
        {
            'repositories': [
                {
                    'id': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
                    'name': 'Saagie',
                    'synchronizationReports': {
                        'lastReversibleId': 'a17c73ed-fca1-4f25-a343-914c7ac23bae',
                        'count': 1,
                        'list': [
                            {
                                'endedAt': '2022-09-12T10:27:44.549Z',
                                'issues': [],
                                'revert': None
                            }
                        ]
                    },
                    'technologies': [
                        {
                            'available': True,
                            'id': '9f188511-d49f-4129-9d6d-f4d451f42acd',
                            'label': 'Java/Scala'
                        },
                        {
                            'available': True,
                            'id': '46cede50-c22a-4b95-9088-3251d0466458',
                            'label': 'SQOOP'
                        },
                        {
                            'available': True,
                            'id': '0db6d0a7-ad4b-45cd-8082-913a192daa25',
                            'label': 'Python'
                        },
                        {
                            'available': True,
                            'id': 'db34c9b9-47c7-4dc6-8c3c-2d8ccf5afa11',
                            'label': 'AWS Lambda'
                        }
                    ],
                    'source': {
                        'url': 'https://github.com/saagie/technologies/releases/latest/download/technologies.zip'
                    }
                }
            ]
        }
        """

        params = {
            "minimal": minimal,
            "lastSynchronization": last_synchronization,
        }
        query = gql(GQL_LIST_REPOSITORIES)
        return self.saagie_api.client_gateway.execute(query=query, variable_values=params, pprint_result=pprint_result)

    def get_info(
        self,
        repository_id: str,
        with_reverted: bool = False,
        synchronization_reports_limit: Optional[int] = None,
        last_synchronization: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get information for a given repository
        NB: You can only get repository information if you have at least the
        viewer role on the catalog

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)
        with_reverted : bool, optional
            Whether to only fetch not reverted synchronization reports
        synchronization_reports_limit : int, optional
            Maximum limit of synchronization reports per repository. Fetch from most recent
            to oldest
        last_synchronization : bool, optional
            Whether to only fetch the last synchronization of each repository
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of repository information

        Examples
        --------
        >>> saagieapi.repositories.get_info(repository_id="9fcbddfe-a7b7-4d25-807c-ad030782c923")
        {
            'repository': {
                'creationDate': '2020-07-28T08:14:03.134Z',
                'creator': 'Saagie',
                'editor': 'Saagie',
                'id': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
                'modificationDate': '2020-07-28T08:14:03.134Z',
                'name': 'Saagie',
                'readOnly': True,
                'source': {
                    'url': 'https://github.com/saagie/technologies/releases/latest/download/technologies.zip'
                },
                'synchronizationReports': {
                    'count': 6,
                    'list': [
                        {
                            'source': {
                                'url': 'https://github.com/saagie/technologies/releases/latest/download/technologies.zip'
                            },
                            'endedAt': '2022-09-12T10:27:44.549Z',
                            'startedAt': '2022-09-12T10:27:44.549Z',
                            'trigger': {
                                'author': 'hello.world',
                                'type': 'MANUAL'
                            },
                            'technologyReports': [
                                {
                                    'status': 'UNCHANGED',
                                    'technologyId': 'sqoop',
                                    'message': None
                                },
                                {
                                    'status': 'UNCHANGED',
                                    'technologyId': 'talend',
                                    'message': None
                                }
                            ],
                            'issues': [],
                            'revert': None
                        }
                    ],
                    'lastReversibleId': 'a17c73ed-fca1-4f25-a343-914c7ac23bae'
                },
                'connectionTypes': [
                    {
                        'id': '5b4b8ffb-9228-4f7a-9d39-67fd3c2862d3',
                        'label': 'AWS Connection',
                        'actions': {
                            'checkConnection': {
                                'scriptId': '9359e392-58a0-42db-9ce9-b68679aa9131'
                            }
                        }
                    }
                ],
                'technologies': [
                    {
                        'id': '1bf79f1d-7e2d-4daf-976d-8702114ab507',
                        'technologyId': 'generic',
                        'label': 'Generic',
                        'icon': 'docker',
                        'repositoryId': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
                        'available': True,
                        'missingFacets': [],
                        'description': 'A generic Docker image that can be used to execute code in a Docker container.',
                        'contexts': [
                            {
                                'id': 'docker',
                                'label': 'Docker',
                                'available': True,
                                'missingFacets': [],
                                'description': None,
                                'recommended': False,
                                'dockerInfo': None,
                                'trustLevel': 'Stable',
                                'deprecationDate': None,
                                'lastUpdate': '2022-02-21T14:35:41.692Z'
                            }
                        ]
                    },
                    {
                        'id': 'db34c9b9-47c7-4dc6-8c3c-2d8ccf5afa11',
                        'technologyId': 'aws-lambda',
                        'label': 'AWS Lambda',
                        'icon': 'aws-lambda',
                        'repositoryId': '9fcbddfe-a7b7-4d25-807c-ad030782c923',
                        'available': True,
                        'missingFacets': [],
                        'description': 'Run code without thinking about servers. Pay only for the compute time you consume',
                        'iconUrl': None,
                        'contexts': [
                            {
                                'id': 'functions',
                                'label': 'Functions',
                                'available': True,
                                'missingFacets': [],
                                'description': 'AWS Lambda Functions',
                                'recommended': False,
                                'trustLevel': 'Experimental',
                                'deprecationDate': None,
                                'lastUpdate': '2022-08-31T13:05:32.031Z',
                                'connectionTypeUUID': '5b4b8ffb-9228-4f7a-9d39-67fd3c2862d3',
                                'actions': {
                                    'getStatus': {
                                        'scriptId': '50794533-091b-4d66-9463-96f0ce255785'
                                    },
                                    'start': {
                                        'scriptId': '50794533-091b-4d66-9463-96f0ce255785'
                                    },
                                    'stop': None,
                                    'getLogs': {
                                        'scriptId': '50794533-091b-4d66-9463-96f0ce255785'
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }
        """  # pylint: disable=line-too-long

        params = {
            "id": repository_id,
            "withReverted": with_reverted,
            "lastSynchronization": last_synchronization,
            "limit": synchronization_reports_limit,
        }
        return self.saagie_api.client_gateway.execute(
            query=gql(GQL_GET_REPOSITORY_INFO), variable_values=params, pprint_result=pprint_result
        )

    def create(self, name: str, file: str = None, url: str = None) -> Dict:
        """Create a new repository on the platform.

        Parameters
        ----------
        name : str
            Name of the repository (must not already exist)
        file : str, optional
            Local path of the repository zip to upload
        url : str, optional
            Repository URL, should have public access

        Returns
        -------
        dict
            Dict of created repository

        Raises
        ------
        ValueError
            If the parameters 'file' and 'url' are not filled

        Examples
        --------
        >>> saagie.repositories.create(
        ...     name="hello world repo",
        ...     file="./test_input/technologies.zip"
        ... )
        {
            'addRepository': {
                'count': 1,
                'objects': [
                    {
                        'id': 'd04e578f-546a-41bf-bb8c-790e99a4f6c8',
                        'name': 'hello world repo'
                    }
                ]
            }
        }
        """

        params = {"repositoryInput": {"name": name}}
        result = self.__launch_request(file, url, GQL_CREATE_REPOSITORY, params)
        logging.info("✅ Repository [%s] successfully created", name)
        return result

    def __launch_request(self, file: str, url: str, payload_str: str, params: Dict) -> Dict:
        """Launch a GQL request with specified file, payload and params
        GQL3 needed to use this function

        Parameters
        ----------
        file : str
            Path to your file
        url : str
            Repository URL
        payload_str : str
            Payload to send
        params: dict
            variable values to pass to the GQL request

        Returns
        -------
        dict
            Dict of the request response
        """

        if file:
            file = Path(file)
            with file.open(mode="rb") as file_content:
                params["upload"] = file_content
                try:
                    res = self.saagie_api.client_gateway.execute(
                        query=gql(payload_str), variable_values=params, upload_files=True
                    )
                except Exception as exception:
                    logging.error("Something went wrong %s", exception)
                    raise exception
                return res

        elif url:
            params["repositoryInput"]["url"] = url
            try:
                res = self.saagie_api.client_gateway.execute(query=gql(payload_str), variable_values=params)
            except Exception as exception:
                logging.error("Something went wrong %s", exception)
                raise exception
            return res

        else:
            raise ValueError("❌ Value error: Must specify a fill 'file' or 'url'")

    def delete(self, repository_id: str) -> Dict:
        """Delete a given repository

        Parameters
        ----------
        repository_id : str
            UUID of your repository

        Returns
        -------
        dict
            Dict of deleted repository

        Examples
        --------
        >>> saagieapi.repositories.delete(repository_id="163360ba-3254-490e-9eec-ccd1dc096fd7")
        {
            'removeRepository': {
                'id': '163360ba-3254-490e-9eec-ccd1dc096fd7',
                'name': 'new name repo'
            }
        }
        """

        result = self.saagie_api.client_gateway.execute(
            query=gql(GQL_DELETE_REPOSITORY), variable_values={"removeRepositoryId": repository_id}
        )
        logging.info("✅ Repository [%s] successfully deleted", repository_id)
        return result

    def edit(
        self, repository_id: str, name: str = None, url: str = None, trigger_synchronization: bool = False
    ) -> Dict:
        """
        Edit a repository information only for repository fetch from URL.
        If you want to change the zip file for a repository, please use the function synchronize

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)
        name : str, optional
            Repository name
            If not filled, defaults to current value, else it will change the repository's name
        url : str, optional
            Repository URL
            if not filled, defaults to current value, else it will change the URL of the repository
        trigger_synchronization : bool, optional
            If URL is modified and this flag is set to true, the update triggers the synchronization
            if not filled, it will no trigger the synchronization

        Returns
        -------
        dict
            Dict of repository information

        Examples
        --------
        >>> saagieapi.repositories.edit(
        ...     repository_id="163360ba-3254-490e-9eec-ccd1dc096fd7",
        ...     name="new name repo",
        ...     url="https://github.com/saagie/technologies-community/releases/download/0.62.0/technologies.zip",
        ...     trigger_synchronization=True
        ... )
        {
            'editRepository': {
                'count': 1,
                'objects': [
                    {
                        'name': 'new name repo',
                        'source': {
                            'url': 'https://github.com/saagie/technologies-community/releases/download/0.62.0/technologies.zip'
                        },
                        'id': '163360ba-3254-490e-9eec-ccd1dc096fd7'
                    }
                ]
            }
        }
        """  # pylint: disable=line-too-long

        params = {"repositoryInput": {"id": repository_id, "triggerSynchronization": trigger_synchronization}}
        if name:
            params["repositoryInput"]["name"] = name

        if url:
            params["repositoryInput"]["url"] = url

        result = self.saagie_api.client_gateway.execute(query=gql(GQL_EDIT_REPOSITORY), variable_values=params)
        logging.info("✅ Repository [%s] successfully edited", repository_id)
        return result

    def synchronize(self, repository_id: str, file: str = None) -> Dict:
        """
        Synchronize manually a repository.
        If you repository has created by zip file, you should provide a new path of the local repository zip file

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)
        file : str, optional
            Path to your file

        Returns
        -------
        dict
            Dict of repository information

        Examples
        --------
        >>> saagie.repositories.synchronize(
        ...     repository_id="d04e578f-546a-41bf-bb8c-790e99a4f6c8",
        ...     file="./test_input/new_technologies.zip"
        ... )
        {
            'synchronizeRepository': {
                'count': 5,
                'report': {
                    'id': '47589bad-729d-4afe-99e8-05824dd66858',
                    'endedAt': '2022-09-21T12:15:50.513Z',
                    'startedAt': '2022-09-21T12:15:50.513Z',
                    'trigger': {
                        'author': 'hello.world',
                        'type': 'MANUAL'
                    },
                    'technologyReports': [
                        {
                            'status': 'DELETED',
                            'technologyId': 'aws-batch'
                        },
                        {
                            'status': 'DELETED',
                            'technologyId': 'aws-emr'
                        },
                        {
                            'status': 'DELETED',
                            'technologyId': 'aws-glue'
                        },
                        {
                            'status': 'DELETED',
                            'technologyId': 'aws-lambda'
                        },
                        {
                            'status': 'UNCHANGED',
                            'technologyId': 'cloudbeaver'
                        },
                        {
                            'status': 'UNCHANGED',
                            'technologyId': 'dash'
                        }
                    ],
                    'issues': []
                },
                'repositoryId': '0e09c160-7f68-402e-9156-0d414e53318b',
                'repositoryName': 'hello world repo'
            }
        }
        """

        params = {"id": repository_id}
        if file:
            result = self.__launch_request(file, "", GQL_SYNCHRONIZE_REPOSITORY, params)
        else:
            result = self.saagie_api.client_gateway.execute(
                query=gql(GQL_SYNCHRONIZE_REPOSITORY), variable_values=params
            )
        logging.info("✅ Repository [%s] successfully synchronized", repository_id)
        return result

    def revert_last_synchronization(self, repository_id: str) -> Dict:
        """
        Revert the last synchronization

        Parameters
        ----------
        repository_id : str
            UUID of your repository (see README on how to find it)

        Returns
        -------
        dict
            Dict of repository information

        Raises
        ------
        NameError
            If the repository does not exist or the user don't have the permission to see it or can not be revert

        Examples
        --------
        >>> saagieapi.repositories.revert_last_synchronization(repository_id="163360ba-3254-490e-9eec-ccd1dc096fd7")
        {
            'revertLastSynchronization': {
                'report': {
                    'id': 'f40650aa-73c0-4388-9742-331f8147b1a9',
                    'trigger': {
                        'author': 'hello.world',
                        'type': 'URL_UPDATE'
                    },
                    'endedAt': '2022-09-21T12:04:41.551Z',
                    'startedAt': '2022-09-21T12:04:41.551Z'
                },
                'repositoryName': 'new name repo',
                'repositoryId': '163360ba-3254-490e-9eec-ccd1dc096fd7'
            }
        }
        """
        repositories = self.list(minimal=True, last_synchronization=True)["repositories"]
        if repository := list(filter(lambda p: p["id"] == repository_id, repositories)):
            if synchronization_report_id := repository[0]["synchronizationReports"]["lastReversibleId"]:
                params = {"repositoryId": repository_id, "synchronizationReportId": synchronization_report_id}
                return self.saagie_api.client_gateway.execute(
                    query=gql(GQL_REVERT_LAST_SYNCHRONISATION), variable_values=params
                )
        raise NameError(
            f"❌ Repository [{repository_id}] does not exist or "
            f"you don't have permission to see it or can not be revert."
        )

    def get_id(self, repository_name: str) -> str:
        """Get the repository id with the repository name
        Parameters
        ----------
        repository_name : str
            Name of your project

        Returns
        -------
        str
            Repository UUID

        Raises
        ------
        NameError
            If repository does not exist or the user don't have permission to see it

        Examples
        --------
        >>> saagieapi.repositories.get_id(repository_name="Saagie")
        '9fcbddfe-a7b7-4d25-807c-ad030782c923'
        """
        repositories = self.list(minimal=True, last_synchronization=True)["repositories"]
        if repository := list(filter(lambda p: p["name"] == repository_name, repositories)):
            return repository[0]["id"]
        raise NameError(f"❌ Repository {repository_name} does not exist or you don't have permission to see it.")
