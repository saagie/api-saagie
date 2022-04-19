import logging
import time
import pytz
from croniter import croniter
import deprecation
from gql import gql
from .gql_queries import *


class Pipelines:

    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client
        self.valid_status_list = saagie_api.valid_status_list

    def list_for_project(self, project_id, instances_limit=-1):
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
        instances_limit_request = f" (limit: {str(instances_limit)})" if instances_limit != -1 else ""
        query = gql(gql_list_pipelines_for_project.format(project_id, instances_limit_request))
        return self.client.execute(query)

    def list_for_project_light(self, project_id):
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
        query = gql(gql_list_pipelines_for_project_light.format(project_id))
        return self.client.execute(query)

    def get_id(self, pipeline_name, project_name):
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
        else:
            raise NameError(f"pipeline {pipeline_name} does not exist.")

    def get_info(self, pipeline_id):
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
        query = gql(gql_get_pipeline.format(pipeline_id))
        return self.client.execute(query)

    def get_instance(self, pipeline_instance_id):
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
        query = gql(gql_get_pipeline_instance.format(pipeline_instance_id))
        return self.client.execute(query)

    @deprecation.deprecated(deprecated_in="Saagie 2.2.1",
                            details="This deprecated endpoint allows to create only linear pipeline. "
                                    "To create graph pipelines, use `create_graph` instead.")
    def create(self, name, project_id, jobs_id, description=""):
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
        query = gql(gql_create_pipeline.format(
            name,
            description,
            project_id,
            f"""["{'", "'.join(jobs_id)}"]"""
        ))
        return self.client.execute(query)

    def create_graph(self, name, project_id, graph_pipeline, description="", release_note="",
                     cron_scheduling=None, schedule_timezone="UTC"):
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
                graph_pipeline.add_root_node(job_node1) # Indicates the pipeline will started with job_node1
        description : str, optional
            Description of the pipeline
        release_note: str, optional
            Release note of the pipeline
        cron_scheduling : str, optional
            Scheduling CRON format
        schedule_timezone : str, optional
            Timezone of the scheduling

        Returns
        -------
        dict
            Dict of pipeline information
        """
        gql_scheduling_payload = []
        if not graph_pipeline.list_job_nodes:
            graph_pipeline.to_pipeline_graph_input()
        if cron_scheduling:
            gql_scheduling_payload.append('isScheduled: true')

            if croniter.is_valid(cron_scheduling):
                gql_scheduling_payload.append(f'cronScheduling: "{cron_scheduling}"')
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                gql_scheduling_payload.append(f'scheduleTimezone: "{schedule_timezone}"')
            else:
                raise RuntimeError("Please specify a correct timezone")

        else:
            gql_scheduling_payload.append('isScheduled: false')

        gql_scheduling_payload_str = ", ".join(gql_scheduling_payload)

        query_str = gql_create_graph_pipeline.format(
            name,
            description,
            project_id,
            release_note,
            gql_scheduling_payload_str
        )
        params = {'jobNodes': graph_pipeline.list_job_nodes, 'conditionNodes': graph_pipeline.list_conditions_nodes}

        query = gql(query_str)
        return self.client.execute(query, variable_values=params)

    def delete(self, pipeline_id):
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
        query = gql(gql_delete_pipeline.format(pipeline_id))

        return self.client.execute(query)

    def upgrade(self, pipeline_id, graph_pipeline, release_note=""):
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

        params = {'id': pipeline_id, 'jobNodes': graph_pipeline.list_job_nodes,
                  'conditionNodes': graph_pipeline.list_conditions_nodes, 'releaseNote': release_note}

        return self.client.execute(gql(gql_upgrade_pipeline), variable_values=params)

    def edit(self, pipeline_id, name=None, description=None, emails=None,
             status_list=["FAILED"], is_scheduled=None,
             cron_scheduling=None, schedule_timezone="UTC"):
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
            params["isScheduled"] = True

            if cron_scheduling and croniter.is_valid(cron_scheduling):
                params["cronScheduling"] = cron_scheduling
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                params["scheduleTimezone"] = schedule_timezone
            else:
                raise RuntimeError("Please specify a correct timezone")

        elif is_scheduled == False:
            params["isScheduled"] = False

        else:
            params["isScheduled"] = previous_pipeline_info["isScheduled"]
            params["cronScheduling"] = previous_pipeline_info["cronScheduling"]
            params["scheduleTimezone"] = previous_pipeline_info["scheduleTimezone"]

        if emails:
            wrong_status_list = []

            for item in status_list:
                if item not in self.valid_status_list:
                    wrong_status_list.append(item)
            if wrong_status_list:
                raise RuntimeError(f"The following status are not valid: {wrong_status_list}. "
                                   f"Please make sure that each item of the parameter status_list should be "
                                   f"one of the following values: 'REQUESTED', 'QUEUED', 'RUNNING', "
                                   f"'FAILED', 'KILLED', 'KILLING', 'SUCCEEDED', 'UNKNOWN', 'AWAITING', 'SKIPPED'")

            else:
                params["alerting"] = {
                    "emails": emails,
                    "statusList": status_list
                }
        elif type(emails) == list:
            params["alerting"] = None
        else:
            previous_alerting = previous_pipeline_info["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_pipeline_info["emails"],
                    "statusList": previous_pipeline_info["statusList"]
                }

        query = gql(gql_edit_pipeline)
        return self.client.execute(query, variable_values=params)

    def run(self, pipeline_id):
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
        query = gql(gql_run_pipeline.format(pipeline_id))
        return self.client.execute(query)

    def run_with_callback(self, pipeline_id, freq=10, timeout=-1):
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
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED"]
        query = gql(gql_get_pipeline_instance.format(pipeline_instance_id))
        pipeline_instance_info = self.client.execute(query)
        state = pipeline_instance_info.get("pipelineInstance").get("status")
        sec = 0

        while state not in final_status_list:
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            pipeline_instance_info = self.client.execute(query)
            state = pipeline_instance_info.get("pipelineInstance") \
                .get("status")
            logging.info('Current state : ' + state)
        return state

    def stop(self, pipeline_instance_id):
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
        query = gql(gql_stop_pipeline_instance.format(pipeline_instance_id))
        return self.client.execute(query)
