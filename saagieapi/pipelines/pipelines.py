import logging
import time
from typing import Dict, List

import deprecation
from gql import gql

from .gql_queries import *
from .graph_pipeline import GraphPipeline


class Pipelines:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_for_project(self, project_id: str, instances_limit: int = -1) -> Dict:
        """List pipelines of project with their instances.

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per pipelines. Fetch from most
            recent to oldest

        Returns
        -------
        Dict
            Dict of pipelines information
        """
        params = {"projectId": project_id}
        if instances_limit != -1:
            params["instancesLimit"] = instances_limit
        query = gql(GQL_LIST_PIPELINES_FOR_PROJECT)
        return self.client.execute(query, variable_values=params)

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
        query = gql(GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL)
        return self.client.execute(query, variable_values={"projectId": project_id})

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
        pipeline = list(filter(lambda j: j["name"] == pipeline_name, pipelines))
        if pipeline:
            return pipeline[0]["id"]
        raise NameError(f"pipeline {pipeline_name} does not exist.")

    def get_info(self, pipeline_id: str) -> Dict:
        """Get a given pipeline information

        Parameters
        ----------
        pipeline_id : str
            UUID of your pipeline  (see README on how to find it)

        Returns
        -------
        dict
            Dict of pipeline's information
        """
        query = gql(GQL_GET_PIPELINE)
        return self.client.execute(query, variable_values={"id": pipeline_id})

    def get_instance(self, pipeline_instance_id: str) -> Dict:
        """
        Get the information of a given pipeline instance id

        Parameters
        ----------
        pipeline_instance_id : str
            Pipeline instance id

        Returns
        -------
        dict
            Dict of job information
        """
        query = gql(GQL_GET_PIPELINE_INSTANCE)
        return self.client.execute(query, variable_values={"id": pipeline_instance_id})

    @deprecation.deprecated(
        deprecated_in="Saagie 2.2.1",
        details="This deprecated endpoint allows to create only linear pipeline. "
        "To create graph pipelines, use `create_graph` instead.",
    )
    def create(self, name: str, project_id: str, jobs_id: List[str], description: str = "") -> Dict:
        """
        Create a pipeline in a given project

        Parameters
        ----------
        name : str
            Name of the pipeline. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        jobs_id : List
            Ordered list of job's id (example : ["id1", "id2", "id3"]
            will result in the following pipeline id1 -> id2 -> id3)
        description : str, optional
            Description of the pipeline

        Returns
        -------
        dict
            Dict of job information
        """
        params = {"name": name, "description": description, "projectId": project_id, "jobsId": jobs_id}
        query = gql(GQL_CREATE_PIPELINE)
        return self.client.execute(query, variable_values=params)

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

        query = gql(GQL_CREATE_GRAPH_PIPELINE)
        return self.client.execute(query, variable_values=params)

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
        query = gql(GQL_DELETE_PIPELINE)

        return self.client.execute(query, variable_values={"id": pipeline_id})

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

        return self.client.execute(gql(GQL_UPGRADE_PIPELINE), variable_values=params)

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
    ):
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

        Returns
        -------
        dict
            Dict of pipeline information
        """
        params = {"id": pipeline_id}
        previous_pipeline_info = self.get_info(pipeline_id)["graphPipeline"]

        if name:
            params["name"] = name
        else:
            params["name"] = previous_pipeline_info["name"]

        if description:
            params["description"] = description
        else:
            params["description"] = previous_pipeline_info["description"]

        if is_scheduled:
            params = self.saagie_api.check_scheduling(cron_scheduling, params, schedule_timezone)

        elif is_scheduled == False:
            params["isScheduled"] = False

        else:
            params["isScheduled"] = previous_pipeline_info["isScheduled"]
            params["cronScheduling"] = previous_pipeline_info["cronScheduling"]
            params["scheduleTimezone"] = previous_pipeline_info["scheduleTimezone"]

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)
        elif isinstance(emails, List):
            params["alerting"] = None
        else:
            previous_alerting = previous_pipeline_info["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_pipeline_info["emails"],
                    "statusList": previous_pipeline_info["statusList"],
                }

        query = gql(GQL_EDIT_PIPELINE)
        return self.client.execute(query, variable_values=params)

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
        query = gql(GQL_RUN_PIPELINE)
        return self.client.execute(query, variable_values={"pipelineId": pipeline_id})

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

        pipeline_instance_info = self.get_instance(pipeline_instance_id)
        state = pipeline_instance_info.get("pipelineInstance").get("status")

        sec = 0
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED"]
        while state not in final_status_list:
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            pipeline_instance_info = self.get_instance(pipeline_instance_id)
            state = pipeline_instance_info.get("pipelineInstance").get("status")
            logging.info("Current state : %s", state)
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
        query = gql(GQL_STOP_PIPELINE_INSTANCE)
        return self.client.execute(query, variable_values={"pipelineInstanceId": pipeline_instance_id})
