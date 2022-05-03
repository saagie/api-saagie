import logging
import time
from pathlib import Path
from typing import Dict, List

from gql import gql

from .gql_queries import *


class Jobs:
    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client

    def list_for_project(self, project_id: str, instances_limit: int = -1) -> Dict:
        """List jobs in the given project with their instances.
        NB: You can only list jobs if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest

        Returns
        -------
        dict
            Dict of jobs information
        """
        params = {"projectId": project_id}
        if instances_limit != -1:
            params["instancesLimit"] = instances_limit
        query = gql(GQL_LIST_JOBS_FOR_PROJECT)
        return self.client.execute(query, variable_values=params)

    def list_for_project_minimal(self, project_id: str) -> Dict:
        """List only job names and ids in the given project .
        NB: You can only list jobs if you have at least the viewer role on the
        project

        Parameters
        ----------
        project_id : str
            UUID of your project (see README on how to find it)

        Returns
        -------
        dict
            Dict of jobs ids and names
        """
        query = gql(GQL_LIST_JOBS_FOR_PROJECT_MINIMAL)
        return self.client.execute(query, variable_values={"projectId": project_id})

    def get_instance(self, job_instance_id: str) -> Dict:
        """Get the given job instance

        Parameters
        ----------
        job_instance_id : str
            UUID of your job instance (see README on how to find it)

        Returns
        -------
        dict
            Dict of instance information
        """
        query = gql(GQL_GET_JOB_INSTANCE)
        return self.client.execute(query, variable_values={"jobInstanceId": job_instance_id})

    def get_id(self, job_name: str, project_name: str) -> str:
        """Get the job id with the job name and project name

        Parameters
        ----------
        job_name : str
            Name of your job
        project_name : str
            Name of your project

        Returns
        -------
        str
            Job UUID

        """
        project_id = self.saagie_api.projects.get_id(project_name)
        jobs = self.saagie_api.jobs.list_for_project_minimal(project_id)["jobs"]
        job = list(filter(lambda j: j["name"] == job_name, jobs))
        if job:
            return job[0]["id"]
        raise NameError(f"Job {job_name} does not exist.")

    def get_info(self, job_id: str, instances_limit: int = -1) -> Dict:
        """Get job's info

        Parameters
        ----------
        job_id : str
            UUID of your job
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest

        Returns
        -------
        dict
            Dict of job's info

        """
        params = {"jobId": job_id}
        if instances_limit != -1:
            params["instancesLimit"] = instances_limit
        query = gql(GQL_GET_JOB_INFO)
        return self.client.execute(query, variable_values=params)

    def create(
        self,
        job_name: str,
        project_id: str,
        file: str = None,
        description: str = "",
        category: str = "Processing",
        technology: str = "python",
        technology_catalog: str = "Saagie",
        runtime_version: str = "3.7",
        command_line: str = "python {file} arg1 arg2",
        release_note: str = "",
        extra_technology: str = "",
        extra_technology_version: str = "",
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        resources: Dict = None,
        emails: List = None,
        status_list: List = None,
    ) -> Dict:
        """Create job in given project

        NOTE
        ----
        - Only work for gql>=3.0.0

        Parameters
        ----------
        job_name : str
            Name of the job. Must not already exist in the project
        project_id : str
            UUID of your project (see README on how to find it)
        file : str, optional
            Local path of the file to upload
        description : str, optional
            Description of the job
        category : str, optional
            Category to create the job into. Must be 'Extraction', 'Processing'
            or 'Smart App'
        technology : str, optional
            Technology label of the job to create.
        technology_catalog : str, optional
            Technology catalog containing the technology to use for this job
        runtime_version : str, optional
            Technology version of the job
        command_line : str, optional
            Command line of the job
        release_note : str, optional
            Release note of the job
        extra_technology : str, optional
            Extra technology when needed (spark jobs). If not needed, leave to
            empty string or the request will not work
        extra_technology_version : str, optional
            Version of the extra technology. Leave to empty string when not
            needed
        cron_scheduling : str, optional
            Scheduling CRON format
            Example: "0 0 * * *" (for every day At 00:00)
        schedule_timezone : str, optional
            Timezone of the scheduling
            Example: "UTC", "Pacific/Pago_Pago"
        resources : dict, optional
            CPU, memory limit and requests
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}
        emails: List[String], optional
            Emails to receive alerts for the job, each item should be a valid email
        status_list: List[String], optional
            Receive an email when the job status change to a specific status
            Each item of the list should be one of these following values: "REQUESTED", "QUEUED",
            "RUNNING", "FAILED", "KILLED", "KILLING", "SUCCEEDED", "UNKNOWN", "AWAITING", "SKIPPED"

        Returns
        -------
        dict
            Dict of job information

        """
        params = {
            "projectId": project_id,
            "name": job_name,
            "description": description,
            "category": category,
            "releaseNote": release_note,
            "runtimeVersion": runtime_version,
            "commandLine": command_line,
        }

        technologies_for_project = self.saagie_api.projects.get_jobs_technologies(project_id)["technologiesByCategory"]
        technologies_for_project_and_category = [
            tech["id"]
            for tech in [tech["technologies"] for tech in technologies_for_project if tech["jobCategory"] == category][
                0
            ]
        ]
        params = self.saagie_api.check_technology(
            params, technology, technology_catalog, technologies_for_project_and_category
        )
        available_runtimes = [
            tech["label"]
            for tech in self.saagie_api.get_runtimes(params["technologyId"])["technology"]["contexts"]
            if tech["available"] is True
        ]
        if runtime_version not in available_runtimes:
            raise RuntimeError(
                f"Runtime {runtime_version} for technology {technology} does not exist "
                f"in the catalog {technology_catalog} or is deprecated"
            )
        if extra_technology != "":
            params["extraTechnology"] = {"language": extra_technology, "version": extra_technology_version}

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)

        if cron_scheduling:
            params = self.saagie_api.check_scheduling(cron_scheduling, params, schedule_timezone)

        else:
            params["isScheduled"] = False

        if resources:
            params["resources"] = resources

        return self.__launch_request(file, GQL_CREATE_JOB, params)

    def edit(
        self,
        job_id: str,
        job_name: str = None,
        description: str = None,
        is_scheduled: str = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        resources: Dict = None,
        emails: List = None,
        status_list: List = None,
    ) -> Dict:
        # pylint: disable=singleton-comparison
        """Edit a job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        job_name : str, optional
            Job name
            If not filled, defaults to current value, else it will change the job's name
        description : str, optional
            Description of job
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
        resources : dict, optional
            CPU, memory limit and requests
            if not filled, defaults to current value
            Example: {"cpu":{"request":0.5, "limit":2.6},"memory":{"request":1.0}}
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
            Dict of job information
        """
        params = {"jobId": job_id}
        previous_job_version = self.get_info(job_id)["job"]

        if job_name:
            params["name"] = job_name
        else:
            params["name"] = previous_job_version["name"]

        if description:
            params["description"] = description
        else:
            params["description"] = previous_job_version["description"]

        if resources:
            params["resources"] = resources
        else:
            params["resources"] = previous_job_version["resources"]

        if is_scheduled:
            params = self.saagie_api.check_scheduling(cron_scheduling, params, schedule_timezone)

        elif is_scheduled == False:
            params["isScheduled"] = False

        else:
            params["isScheduled"] = previous_job_version["isScheduled"]
            params["cronScheduling"] = previous_job_version["cronScheduling"]
            params["scheduleTimezone"] = previous_job_version["scheduleTimezone"]

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)
        elif isinstance(emails, List):
            params["alerting"] = None
        else:
            previous_alerting = previous_job_version["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_alerting["emails"],
                    "statusList": previous_alerting["statusList"],
                }

        query = gql(GQL_EDIT_JOB)
        return self.client.execute(query, variable_values=params)

    def upgrade(
        self,
        job_id: str,
        file: str = None,
        use_previous_artifact: bool = False,
        runtime_version: str = "3.7",
        command_line: str = "python {file} arg1 arg2",
        release_note: str = None,
        extra_technology: str = "",
        extra_technology_version: str = "",
    ) -> Dict:
        """Upgrade a job

        Parameters
        ----------
        job_id : str
            UUID of your job
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        runtime_version: str (optional)
            Runtime version
        command_line: str (optional)
            Command line
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            empty string or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to empty string when not
            needed

        Returns
        -------
        dict
            Dict with version number
            Example: {'addJobVersion': {'number': 5, '__typename': 'JobVersion'}}

        """

        # Verify if specified runtime exists
        technology_id = self.get_info(job_id)["job"]["technology"]["id"]
        available_runtimes = [c["label"] for c in self.saagie_api.get_runtimes(technology_id)["technology"]["contexts"]]
        if runtime_version not in available_runtimes:
            raise RuntimeError(
                f"Specified runtime does not exist ({runtime_version}). "
                f"Available runtimes : {','.join(available_runtimes)}."
            )

        if file and use_previous_artifact:
            logging.warning(
                "You can not specify a file and use the previous artifact. "
                "By default, the specified file will be used."
            )

        params = {
            "jobId": job_id,
            "releaseNote": release_note,
            "runtimeVersion": runtime_version,
            "commandLine": command_line,
            "usePreviousArtifact": use_previous_artifact,
        }

        if extra_technology != "":
            params["extraTechnology"] = {"language": extra_technology, "version": extra_technology_version}
        return self.__launch_request(file, GQL_UPGRADE_JOB, params)

    def upgrade_by_name(
        self,
        job_name: str,
        project_name: str,
        file=None,
        use_previous_artifact: bool = False,
        runtime_version: str = "3.6",
        command_line: str = "python {file} arg1 arg2",
        release_note: str = None,
        extra_technology: str = "",
        extra_technology_version: str = "",
    ) -> Dict:
        """Upgrade a job

        Parameters
        ----------
        job_name : str
            Name of your job
        project_name : str
            Name of your project
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        runtime_version: str (optional)
            Runtime version
        command_line: str (optional)
            Command line
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            empty string or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to empty string when not
            needed

        Returns
        -------
        dict
            Dict with version number
            Example: {'addJobVersion': {'number': 5, '__typename': 'JobVersion'}}

        """
        job_id = self.get_id(job_name, project_name)
        return self.upgrade(
            job_id,
            file,
            use_previous_artifact,
            runtime_version,
            command_line,
            release_note,
            extra_technology,
            extra_technology_version,
        )

    def delete(self, job_id: str) -> Dict:
        """Delete a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted job

        """
        query = gql(GQL_DELETE_JOB)
        return self.client.execute(query, variable_values={"jobId": job_id})

    def run(self, job_id: str) -> Dict:
        """Run a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of the given job information
        """
        query = gql(GQL_RUN_JOB)
        return self.client.execute(query, variable_values={"jobId": job_id})

    def run_with_callback(self, job_id: str, freq: int = 10, timeout: int = -1) -> Dict:
        """Run a job and wait for the final status (KILLED, FAILED or SUCCESS).
        Regularly check (default to 10s) the job's status.

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        freq : int, optional
            Seconds to wait between two state checks
        timeout : int, optional
            Seconds before timeout for a status check call

        Returns
        -------
        str
            Final state of the job

        Raises
        ------
        TimeoutError
            When the status check is not responding
        """
        res = self.run(job_id)
        job_instance_id = res.get("runJob").get("id")
        final_status_list = ["SUCCEEDED", "FAILED", "KILLED"]
        job_instance_info = self.get_instance(job_instance_id)
        state = job_instance_info.get("jobInstance").get("status")
        sec = 0
        while state not in final_status_list:
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            job_instance_info = self.get_instance(job_instance_id)
            state = job_instance_info.get("jobInstance").get("status")
            logging.info(f"Job id {job_id} with instance {job_instance_id} is currently : " + state)
        return state

    def stop(self, job_instance_id: str) -> Dict:
        """Stop a given job instance

        Parameters
        ----------
        job_instance_id : str
            UUID of your job instance (see README on how to find it)

        Returns
        -------
        dict
            Job instance information
        """
        query = gql(GQL_STOP_JOB_INSTANCE)
        return self.client.execute(query, variable_values={"jobInstanceId": job_instance_id})

    def __launch_request(self, file: str, payload_str: str, params: Dict) -> Dict:
        """Launch a GQL request with specified file, payload and params
        GQL3 needed to use this function
        Parameters
        ----------
        file : str
            Path to your file
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
            with file.open(mode="rb") as f:
                params["file"] = f
                try:
                    req = self.client.execute(gql(payload_str), variable_values=params, upload_files=True)
                    res = {"data": req}
                except Exception as e:
                    logging.error("Something went wrong %s", e)
                    raise e
                return res

        else:
            try:
                req = self.client.execute(gql(payload_str), variable_values=params)
                res = {"data": req}
            except Exception as e:
                logging.error("Something went wrong %s", e)
                raise e
            return res
