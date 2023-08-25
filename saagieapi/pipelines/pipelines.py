import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from gql import gql

from ..utils.folder_functions import check_folder_path, create_folder, write_error, write_to_json_file
from ..utils.rich_console import console
from .gql_queries import *
from .graph_pipeline import GraphPipeline


def handle_error(msg, pipeline_name):
    logging.error("❌ Something went wrong %s", msg)
    logging.warning("❌ Pipeline [%s] has not been successfully imported", pipeline_name)
    return False


def parse_version_conditions(version):
    conditions_found = []
    for condition_node in version["graph"]["conditionNodes"]:
        condition_dict = {
            "id": condition_node["id"],
            "nextNodesSuccess": condition_node["nextNodesSuccess"],
            "nextNodesFailure": condition_node["nextNodesFailure"],
        }
        if "ConditionStatus" in condition_node["condition"]["toString"]:
            # example : ConditionStatus(value=AtLeastOneSuccess)
            condition_dict["condition"] = {
                "status": {"value": condition_node["condition"]["toString"].split("=")[1].split(")")[0]}
            }

        if "ConditionExpression" in condition_node["condition"]["toString"]:
            # example : ConditionExpression(expression=\"1 + 1 == 2\")
            condition_dict["condition"] = {
                "custom": {"expression": condition_node["condition"]["toString"].split('="')[1].split('")')[0]}
            }

        conditions_found.append(condition_dict)
    return conditions_found


def parse_version_jobs(jobs_target_pj, version):
    jobs_not_found = []
    jobs_found = []
    for job_node in version["graph"]["jobNodes"]:
        if job := next((job for job in jobs_target_pj if job["name"] == job_node["job"]["name"]), None):
            node_dict = {
                "id": job_node["id"],
                "job": {"id": job["id"]},
                "nextNodes": job_node["nextNodes"],
            }
            jobs_found.append(node_dict)
        else:
            jobs_not_found.append(job_node["job"]["name"])
    return jobs_not_found, jobs_found


class Pipelines:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api

    def list_for_project(
        self,
        project_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """List pipelines of project with their instances.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per pipelines. Fetch from most
            recent to oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        Dict
            Dict of pipelines information
        """
        params = {
            "projectId": project_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_PIPELINES_FOR_PROJECT), variable_values=params, pprint_result=pprint_result
        )

    def list_for_project_minimal(self, project_id: str) -> Dict:
        """List pipelines ids and names of project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        Dict
            Dict of pipelines ids and names
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL), variable_values={"projectId": project_id}
        )

    def get_id(self, pipeline_name: str, project_name: str) -> str:
        """Get the pipeline id with the pipeline name and project name

        Parameters
        ----------
        pipeline_name : str
            Name of your pipeline
        project_name : str
            Name of your project

        Returns
        -------
        str
            Pipeline UUID
        """
        project_id = self.saagie_api.projects.get_id(project_name)
        pipelines = self.list_for_project(project_id, instances_limit=1)["project"]["pipelines"]
        if pipeline := list(filter(lambda j: j["name"] == pipeline_name, pipelines)):
            return pipeline[0]["id"]
        raise NameError(f"❌ pipeline {pipeline_name} does not exist.")

    def get_info(
        self,
        pipeline_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get a given pipeline information

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to the oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of pipeline's information
        """
        params = {
            "id": pipeline_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PIPELINE), variable_values=params, pprint_result=pprint_result
        )

    def get_instance(self, pipeline_instance_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """
        Get the information of a given pipeline instance id

        Parameters
        ----------
        pipeline_instance_id : str
            Pipeline instance id
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of pipeline information
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_GET_PIPELINE_INSTANCE),
            variable_values={"id": pipeline_instance_id},
            pprint_result=pprint_result,
        )

    def create_graph(
        self,
        name: str,
        project_id: str,
        graph_pipeline: GraphPipeline,
        description: str = "",
        release_note: str = "",
        emails: List[str] = None,
        status_list: List[str] = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        has_execution_variables_enabled: bool = None,
    ) -> Dict:
        """
        Create a pipeline in a given project

        Parameters
        ----------
        name : str
            Name of the pipeline. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        graph_pipeline : GraphPipeline
            Example: If you want to create a simple pipeline with 2 jobs that started by job_node_1,
            you can use the following example
                job_node1 = JobNode(job_id_1)
                job_node2 = JobNode(job_id_2)
                job_node1.add_next_node(job_node2) # Indicates that the job_node_1 is followed by job_node_2
                graph_pipeline = GraphPipeline()
                graph_pipeline.add_root_node(job_node1) # Indicates the pipeline will start with job_node1
        description : str, optional
            Description of the pipeline
        release_note: str, optional
            Release note of the pipeline
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email,
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        cron_scheduling : str, optional
            Scheduling CRON format
        schedule_timezone : str, optional
            Timezone of the scheduling
        has_execution_variables_enabled: bool, optional
            Boolean to activate or desactivate the execution variables

        Returns
        -------
        dict
            Dict of pipeline information
        """
        if not graph_pipeline.list_job_nodes:
            graph_pipeline.to_pipeline_graph_input()

        params = {
            "name": name,
            "description": description,
            "projectId": project_id,
            "releaseNote": release_note,
            "jobNodes": graph_pipeline.list_job_nodes,
            "conditionNodes": graph_pipeline.list_conditions_nodes,
        }

        if cron_scheduling:
            params = self.saagie_api.check_scheduling(cron_scheduling, params, schedule_timezone)
        else:
            params["isScheduled"] = False

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)

        if has_execution_variables_enabled:
            params["hasExecutionVariablesEnabled"] = has_execution_variables_enabled

        result = self.saagie_api.client.execute(query=gql(GQL_CREATE_GRAPH_PIPELINE), variable_values=params)
        logging.info("✅ Pipeline [%s] successfully created", name)
        return result

    def delete(self, pipeline_id: str) -> Dict:
        """Delete a pipeline given pipeline id

        Parameters
        ----------
        pipeline_id : str
            Pipeline id

        Returns
        -------
        dict
            Dict containing status of deletion
        """

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_PIPELINE), variable_values={"id": pipeline_id})
        logging.info("✅ Pipeline [%s] successfully deleted", pipeline_id)
        return result

    def upgrade(self, pipeline_id: str, graph_pipeline: GraphPipeline, release_note: str = "") -> Dict:
        """
        Create a pipeline in a given project

        Parameters
        ----------
        pipeline_id: str, ID of pipeline
        graph_pipeline : GraphPipeline
        release_note: str, optional
            Release note of the pipeline

        Returns
        -------
        dict
            Dict of pipeline information
        """
        if not graph_pipeline.list_job_nodes:
            graph_pipeline.to_pipeline_graph_input()

        params = {
            "id": pipeline_id,
            "jobNodes": graph_pipeline.list_job_nodes,
            "conditionNodes": graph_pipeline.list_conditions_nodes,
            "releaseNote": release_note,
        }

        result = self.saagie_api.client.execute(query=gql(GQL_UPGRADE_PIPELINE), variable_values=params)
        logging.info("✅ Pipeline [%s] successfully upgraded", pipeline_id)
        return result

    def edit(
        self,
        pipeline_id: str,
        name: str = None,
        description: str = None,
        emails: List[str] = None,
        status_list: List[str] = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        has_execution_variables_enabled: bool = None,
    ) -> Dict:  # sourcery skip: remove-redundant-if, simplify-boolean-comparison
        # pylint: disable=singleton-comparison
        """Edit a pipeline
        NB : You can only edit pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        name : str, optional
            Pipeline name,
            if not filled, defaults to current value, else it will change the pipeline name
        description : str, optional
            Description of the pipeline
            if not filled, defaults to current value, else it will change the description of the pipeline
        is_scheduled : bool, optional
            True if the job is scheduled, else False
            if not filled, defaults to current value
        cron_scheduling : str, optional
            Scheduling CRON format
            When is_scheduled is set to True, it will be mandatory to fill this value
            if not filled, defaults to current value
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        has_execution_variables_enabled: bool, optional
            Boolean to activate or desactivate the execution variables

        Returns
        -------
        dict
            Dict of pipeline information
        """
        previous_pipeline_info = self.get_info(pipeline_id, pprint_result=False)["graphPipeline"]

        params = {
            "id": pipeline_id,
            "name": name or previous_pipeline_info["name"],
            "description": description or previous_pipeline_info["description"],
        }

        # cases test : True, False and None
        if is_scheduled:
            params = self.saagie_api.check_scheduling(cron_scheduling, params, schedule_timezone)
        elif is_scheduled == False:
            params["isScheduled"] = False
        else:
            for k in ("isScheduled", "cronScheduling", "scheduleTimezone"):
                params[k] = previous_pipeline_info[k]

        # cases test : List non empty, List empty, None
        if isinstance(emails, List) and emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)
        elif isinstance(emails, List):
            params["alerting"] = None
        elif previous_alerting := previous_pipeline_info["alerting"]:
            params["alerting"] = {
                "emails": previous_alerting["emails"],
                "statusList": previous_alerting["statusList"],
            }

        if has_execution_variables_enabled in {True, False}:
            params["hasExecutionVariablesEnabled"] = has_execution_variables_enabled
        else:
            params["hasExecutionVariablesEnabled"] = previous_pipeline_info["hasExecutionVariablesEnabled"]

        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_PIPELINE), variable_values=params)
        logging.info("✅ Pipeline [%s] successfully edited", name)
        return result

    def create_or_upgrade(
        self,
        name: str,
        project_id: str,
        graph_pipeline: GraphPipeline,
        description: str = None,
        release_note: str = None,
        emails: List[str] = None,
        status_list: List[str] = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        has_execution_variables_enabled: bool = None,
    ) -> Dict:
        """Create or upgrade a pipeline in a given project

        Parameters
        ----------
        name : str
            Pipeline name
        project_id : str
            UUID of your project (see README on how to find it)
        graph_pipeline : GraphPipeline
            Example: If you want to create a simple pipeline with 2 jobs that started by job_node_1,
            you can use the following example
                job_node1 = JobNode(job_id_1)
                job_node2 = JobNode(job_id_2)
                job_node1.add_next_node(job_node2) # Indicates that the job_node_1 is followed by job_node_2
                graph_pipeline = GraphPipeline()
                graph_pipeline.add_root_node(job_node1) # Indicates the pipeline will start with job_node1
        description : str, optional
            Description of the pipeline
            if not filled, defaults to current value, else it will change the description of the pipeline
        release_note: str, optional
            Release note of the pipeline
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email,
            If you want to remove alerting, please set emails to [] or list()
            if not filled, defaults to current value
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"
        is_scheduled : bool, optional
            True to activate the pipeline scheduling
        cron_scheduling : str, optional
            Scheduling CRON format
            When is_scheduled is set to True, it will be mandatory to fill this value
            if not filled, defaults to current value
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        has_execution_variables_enabled: bool, optional
            Boolean to activate or desactivate the execution variables

        Returns
        -------
        dict
            Dict of pipeline information
        """
        pipeline_list = self.saagie_api.pipelines.list_for_project_minimal(project_id)["project"]["pipelines"]

        if name in [pipeline["name"] for pipeline in pipeline_list]:
            pipeline_id = next(pipeline["id"] for pipeline in pipeline_list if pipeline["name"] == name)

            responses = {
                "editPipeline": self.edit(
                    pipeline_id=pipeline_id,
                    name=name,
                    description=description,
                    emails=emails,
                    status_list=status_list,
                    is_scheduled=is_scheduled,
                    cron_scheduling=cron_scheduling,
                    schedule_timezone=schedule_timezone,
                    has_execution_variables_enabled=has_execution_variables_enabled,
                )["editPipeline"]
            }
            responses["addGraphPipelineVersion"] = self.upgrade(pipeline_id, graph_pipeline, release_note)[
                "addGraphPipelineVersion"
            ]

            return responses

        args = {
            k: v
            for k, v in {
                "name": name,
                "project_id": project_id,
                "graph_pipeline": graph_pipeline,
                "description": description,
                "release_note": release_note,
                "emails": emails,
                "status_list": status_list,
                "cron_scheduling": cron_scheduling,
                "schedule_timezone": schedule_timezone,
                "has_execution_variables_enabled": has_execution_variables_enabled,
            }.items()
            if v is not None  # Remove None values from the dict
        }
        return self.create_graph(**args)

    def rollback(self, pipeline_id: str, version_number: str) -> Dict:
        """Rollback a given job to the given version

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline (see README on how to find it)
        version_number : str
            Number of the version to rollback

        Returns
        -------
        dict
            Dict of rollback pipeline

        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_ROLLBACK_PIPELINE_VERSION),
            variable_values={"pipelineId": pipeline_id, "versionNumber": version_number},
        )
        logging.info("✅ Pipeline [%s] successfully rollbacked to version [%s]", pipeline_id, version_number)
        return result

    def run(self, pipeline_id: str) -> Dict:
        """Run a given pipeline
        NB : You can only run pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline instance's information
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_RUN_PIPELINE), variable_values={"pipelineId": pipeline_id}
        )
        logging.info("✅ Pipeline [%s] successfully launched", pipeline_id)
        return result

    def run_with_callback(self, pipeline_id: str, freq: int = 10, timeout: int = -1) -> str:
        """Run a given pipeline and wait for its final status (KILLED, FAILED
        or SUCCESS).
        NB : You can only run pipeline if you have at least the editor role on
        the project

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)
        freq : int, optional
            Number of seconds between 2 state checks
        timeout : int, optional
            Number of seconds before timeout

        Returns
        -------
        str
            the final state of the pipeline

        Raises
        ------
        TimeoutError
            the last state known of the pipeline before timeout
        """
        res = self.run(pipeline_id)
        pipeline_instance_id = res.get("runPipeline").get("id")

        pipeline_instance_info = self.get_instance(pipeline_instance_id, pprint_result=False)
        state = pipeline_instance_info.get("pipelineInstance").get("status")

        sec = 0
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED"]

        logging.info("⏳ Pipeline id %s with instance %s has just been requested", pipeline_id, pipeline_instance_id)

        while state not in final_status_list:
            with console.status(f"Job is currently {state}", refresh_per_second=100):
                t_out = False if timeout == -1 else sec >= timeout
                if t_out:
                    raise TimeoutError(f"❌ Last state known : {state}")
                time.sleep(freq)
                sec += freq
                pipeline_instance_info = self.get_instance(pipeline_instance_id, pprint_result=False)
                state = pipeline_instance_info.get("pipelineInstance").get("status")

        if state == "SUCCEEDED":
            logging.info(
                "✅ Pipeline id %s with instance %s has the status %s", pipeline_id, pipeline_instance_id, state
            )
        elif state in ("FAILED", "KILLED"):
            logging.error(
                "❌ Pipeline id %s with instance %s has the status %s", pipeline_id, pipeline_instance_id, state
            )

        return state

    def stop(self, pipeline_instance_id: str) -> Dict:
        """Stop a given pipeline instance
        NB : You can only stop pipeline instance if you have at least the
        editor role on the project.

        Parameters
        ----------
        pipeline_instance_id : str
            UUID of your pipeline instance  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline's instance information
        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_STOP_PIPELINE_INSTANCE), variable_values={"pipelineInstanceId": pipeline_instance_id}
        )
        logging.info("✅ Pipeline instance [%s] successfully stopped", pipeline_instance_id)
        return result

    def export(
        self,
        pipeline_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
    ) -> bool:
        """Export the pipeline in a folder

        Parameters
        ----------
        pipeline_id : str
            Pipeline ID
        output_folder : str
            Path to store the exported pipeline
        error_folder : str, optional
            Path to store the pipeline ID in case of error. If not set, pipeline ID is not write
        versions_limit : int, optional
            Maximum limit of versions to fetch per pipeline. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each pipeline
        Returns
        -------
        bool
            True if pipeline is exported
        """
        output_folder = Path(output_folder)
        try:
            pipeline_info = self.get_info(
                pipeline_id,
                instances_limit=1,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )["graphPipeline"]

            create_folder(output_folder / pipeline_id)
            write_to_json_file(output_folder / pipeline_id / "pipeline.json", pipeline_info)

            # TODO : Export pipeline env vars

            logging.info("✅ Pipeline [%s] successfully exported", pipeline_id)
        except Exception as exception:
            logging.warning("Cannot get the information of the pipeline [%s]", pipeline_id)
            logging.error("Something went wrong %s", exception)
            logging.warning("❌ Pipeline [%s] has not been successfully exported", pipeline_id)
            write_error(error_folder, "pipelines", pipeline_id)
            return False

        return True

    def import_from_json(self, json_file: str, project_id: str) -> bool:
        """Import pipeline from JSON format
        Parameters
        ----------
        json_file : str
            Path to the JSON file that contains pipeline information
        project_id : str
            Project ID
        Returns
        -------
        bool
            True if pipelines are imported False otherwise
        """
        json_file = Path(json_file)
        try:
            with json_file.open("r", encoding="utf-8") as file:
                pipeline_info = json.load(file)
        except Exception as exception:
            return handle_error(f"Cannot open the JSON file {json_file}", "<name not found>")

        try:
            pipeline_name = pipeline_info["name"]

            jobs_target_pj = self.saagie_api.jobs.list_for_project_minimal(project_id)["jobs"]

            version = next((version for version in pipeline_info["versions"] if version["isCurrent"]), None)
            if not version:
                return handle_error("❌ Current version not found", pipeline_name)

            jobs_not_found, jobs_found = parse_version_jobs(jobs_target_pj, version)

            if jobs_not_found:
                not_found = "".join(f"{job}, " for job in jobs_not_found)
                return handle_error(
                    f"❌ Import aborted, in target project (id : {project_id}), \
                        the following jobs were not found: {not_found}",
                    pipeline_name,
                )

            graph_pipeline = GraphPipeline()
            graph_pipeline.list_job_nodes = jobs_found
            graph_pipeline.list_conditions_nodes = parse_version_conditions(version)
            res = self.create_graph(
                name=pipeline_name,
                project_id=project_id,
                graph_pipeline=graph_pipeline,
                description=pipeline_info["description"],
                release_note=version["releaseNote"],
                emails=(pipeline_info.get("alerting") or {}).get("emails", ""),
                status_list=(pipeline_info.get("alerting") or {}).get("statusList", ""),
                cron_scheduling=pipeline_info["cronScheduling"],
                schedule_timezone=pipeline_info["scheduleTimezone"],
                has_execution_variables_enabled=pipeline_info["hasExecutionVariablesEnabled"],
            )
            if res["createGraphPipeline"] is None:
                return handle_error(res, pipeline_name)

            # TODO : Import pipeline env vars
            # elif env_var_scope == "PIPELINE":
            #     res = self.create_for_pipeline(
            #         pipeline_id=,
            #         name=env_var_name,
            #         value=env_var_value,
            #         description=env_var_description,
            #         is_password=env_var_is_password,
            #     )
            #     if res["saveEnvironmentVariable"] is None:
            #         return handle_error(res, project_id)
        except Exception as exception:
            return handle_error(exception, pipeline_name)

        logging.info("✅ Pipeline [%s] has been successfully imported", pipeline_name)
        return True
