import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from gql import gql

from ..utils.folder_functions import (
    check_folder_path,
    create_folder,
    remove_slash_folder_path,
    write_error,
    write_request_response_to_file,
    write_to_json_file,
)
from ..utils.rich_console import console
from .gql_queries import *


def handle_write_error(msg, job_id, error_folder):
    logging.warning(msg, job_id)
    write_error(error_folder, "jobs", job_id)
    return False


def handle_log_error(msg, exception):
    logging.warning(msg)
    logging.error("Something went wrong %s", exception)
    return False


class Jobs:
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
        versions_limit : int, optional
            Maximum limit of versions to fetch per job. Fetch from most recent
            to oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of jobs information
        """
        params = {
            "projectId": project_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_JOBS_FOR_PROJECT), variable_values=params, pprint_result=pprint_result
        )

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

        return self.saagie_api.client.execute(
            query=gql(GQL_LIST_JOBS_FOR_PROJECT_MINIMAL), variable_values={"projectId": project_id}
        )

    def get_instance(self, job_instance_id: str, pprint_result: Optional[bool] = None) -> Dict:
        """Get the given job instance

        Parameters
        ----------
        job_instance_id : str
            UUID of your job instance (see README on how to find it)
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of instance information
        """

        return self.saagie_api.client.execute(
            query=gql(GQL_GET_JOB_INSTANCE),
            variable_values={"jobInstanceId": job_instance_id},
            pprint_result=pprint_result,
        )

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
        jobs = self.saagie_api.jobs.list_for_project_minimal(self.saagie_api.projects.get_id(project_name))["jobs"]
        if job := next((j for j in jobs if j["name"] == job_name), None):
            return job["id"]
        raise NameError(f"❌ Job {job_name} does not exist.")

    def get_info(
        self,
        job_id: str,
        instances_limit: Optional[int] = None,
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
        pprint_result: Optional[bool] = None,
    ) -> Dict:
        """Get job's info

        Parameters
        ----------
        job_id : str
            UUID of your job
        instances_limit : int, optional
            Maximum limit of instances to fetch per job. Fetch from most recent
            to oldest
        versions_limit : int, optional
            Maximum limit of versions to fetch per job. Fetch from most recent
            to oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job
        pprint_result : bool, optional
            Whether to pretty print the result of the query, default to
            saagie_api.pprint_global

        Returns
        -------
        dict
            Dict of job's info

        """
        params = {
            "jobId": job_id,
            "instancesLimit": instances_limit,
            "versionsLimit": versions_limit,
            "versionsOnlyCurrent": versions_only_current,
        }

        return self.saagie_api.client.execute(
            query=gql(GQL_GET_JOB_INFO), variable_values=params, pprint_result=pprint_result
        )

    def create(
        self,
        job_name: str,
        project_id: str,
        file: str = None,
        description: str = "",
        category: str = "Processing",
        technology: str = "python",
        technology_catalog: str = "Saagie",
        runtime_version: str = "3.10",
        command_line: str = "python {file} arg1 arg2",
        release_note: str = "",
        extra_technology: str = None,
        extra_technology_version: str = None,
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
            Technology version of the job, the ID of the context
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

        if category not in ("Extraction", "Processing", "Smart App"):
            raise RuntimeError(
                f"❌ Category {category} does not exist in Saagie. "
                f"Please specify either Extraction, Processing or Smart App"
            )

        technos_project = self.saagie_api.projects.get_jobs_technologies(project_id, pprint_result=False)[
            "technologiesByCategory"
        ]

        technos_project_category = [
            tech["id"]
            for tech in next(tech["technologies"] for tech in technos_project if tech["jobCategory"] == category)
        ]
        params = self.saagie_api.check_technology(params, technology, technology_catalog, technos_project_category)
        available_runtimes = [
            tech["id"]
            for tech in self.saagie_api.get_runtimes(params["technologyId"])["technology"]["contexts"]
            if tech["available"] is True
        ]
        if runtime_version not in available_runtimes:
            raise RuntimeError(
                f"❌ Runtime {runtime_version} for technology {technology} does not exist "
                f"in the catalog {technology_catalog} or is deprecated"
            )
        if extra_technology is not None or extra_technology != "":
            params["extraTechnology"] = {"language": extra_technology, "version": extra_technology_version}

        if emails:
            params = self.saagie_api.check_alerting(emails, params, status_list)

        if cron_scheduling:
            params = self.saagie_api.check_scheduling(cron_scheduling, params, schedule_timezone)
        else:
            params["isScheduled"] = False

        if resources:
            params["resources"] = resources

        result = self.__launch_request(file, GQL_CREATE_JOB, params)
        logging.info("✅ Job [%s] successfully created", job_name)
        return result

    def edit(
        self,
        job_id: str,
        job_name: str = None,
        description: str = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        resources: Dict = None,
        emails: List = None,
        status_list: List = None,
    ) -> Dict:  # sourcery skip: remove-redundant-if, simplify-boolean-comparison
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
        previous_job_version = self.get_info(job_id, pprint_result=False)["job"]
        if not previous_job_version:
            raise RuntimeError(f"❌ The job {job_id} you're trying to edit does not exist")

        params = {
            "jobId": job_id,
            "name": job_name or previous_job_version["name"],
            "description": description or previous_job_version["description"],
            "resources": resources or previous_job_version["resources"],
        }

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
        elif previous_alerting := previous_job_version["alerting"]:
            params["alerting"] = {
                "emails": previous_alerting["emails"],
                "statusList": previous_alerting["statusList"],
            }

        result = self.saagie_api.client.execute(query=gql(GQL_EDIT_JOB), variable_values=params)
        logging.info("✅ Job [%s] successfully edited", job_id)
        return result

    def upgrade(
        self,
        job_id: str,
        file: str = None,
        use_previous_artifact: bool = True,
        runtime_version: str = None,
        command_line: str = None,
        release_note: str = "",
        extra_technology: str = None,
        extra_technology_version: str = None,
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
            Runtime version, the ID of the context
            Example: "3.10"
        command_line: str (optional)
            Command line used to run the job
            Example: "python3 {file} arg1 arg2"
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            None or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to None when not needed

        Returns
        -------
        dict
            Dict with version number
            Example: {'addJobVersion': {'number': 5, '__typename': 'JobVersion'}}

        """

        # Get the job's current informations
        job_info = self.get_info(job_id, instances_limit=1, versions_only_current=True, pprint_result=False)["job"]

        # Verify if specified runtime exists
        technology_id = job_info["technology"]["id"]
        available_runtimes = [
            tech["id"]
            for tech in self.saagie_api.get_runtimes(technology_id)["technology"]["contexts"]
            if tech["available"] is True
        ]
        if runtime_version is not None and runtime_version not in available_runtimes:
            raise RuntimeError(
                f"❌ Specified runtime does not exist ({runtime_version}). "
                f"Available runtimes : {','.join(available_runtimes)}."
            )

        if file and use_previous_artifact:
            logging.warning(
                "You can not specify a file and use the previous artifact. "
                "By default, the specified file will be used."
            )

        # Create the params dict with new values when specified or old values otherwise
        params = {
            "jobId": job_id,
            "releaseNote": release_note,
            "runtimeVersion": runtime_version or job_info["versions"][0]["runtimeVersion"],
            "commandLine": command_line or job_info["versions"][0]["commandLine"],
            "usePreviousArtifact": bool(use_previous_artifact and job_info["versions"][0]["packageInfo"]),
        }

        # Add extra technology parameter if needed
        if extra_technology is not None:
            params["extraTechnology"] = {"language": extra_technology, "version": extra_technology_version}
        result = self.__launch_request(file, GQL_UPGRADE_JOB, params)
        logging.info("✅ Job [%s] successfully upgraded", job_id)
        return result

    def upgrade_by_name(
        self,
        job_name: str,
        project_name: str,
        file=None,
        use_previous_artifact: bool = True,
        runtime_version: str = None,
        command_line: str = None,
        release_note: str = None,
        extra_technology: str = None,
        extra_technology_version: str = None,
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
            Extra technology when needed (spark jobs). If not needed, leave to None or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to None when not needed

        Returns
        -------
        dict
            Dict with version number
            Example: {'addJobVersion': {'number': 5, '__typename': 'JobVersion'}}

        """
        return self.upgrade(
            self.get_id(job_name, project_name),
            file,
            use_previous_artifact,
            runtime_version,
            command_line,
            release_note,
            extra_technology,
            extra_technology_version,
        )

    def create_or_upgrade(
        self,
        job_name: str,
        project_id: str,
        file: str = None,
        use_previous_artifact: bool = True,
        description: str = None,
        category: str = None,
        technology: str = None,
        technology_catalog: str = None,
        runtime_version: str = None,
        command_line: str = None,
        release_note: str = None,
        extra_technology: str = None,
        extra_technology_version: str = None,
        is_scheduled: bool = None,
        cron_scheduling: str = None,
        schedule_timezone: str = "UTC",
        resources: Dict = None,
        emails: List = None,
        status_list: List = None,
    ) -> Dict:
        """Create or upgrade a job

        Parameters
        ----------
        job_name : str
            Name of your job
        project_id : str
            UUID of your project
        file: str (optional)
            Path to your file
        use_previous_artifact: bool (optional)
            Use previous artifact
        description: str (optional)
            Description of your job
        category: str (optional)
            Category of your job
        technology: str (optional)
            Technology of your job
        technology_catalog: str (optional)
            Technology catalog of your job
        runtime_version: str (optional)
            Runtime version
        command_line: str (optional)
            Command line
        release_note: str (optional)
            Release note
        extra_technology: str (optional)
            Extra technology when needed (spark jobs). If not needed, leave to
            None or the request will not work
        extra_technology_version: str (optional)
            Version of the extra technology. Leave to None when not needed
        is_scheduled: bool (optional)
            True if the job is scheduled, False to deactivate scheduling
        cron_scheduling: str (optional)
            Cron scheduling
        schedule_timezone: str (optional)
            Schedule timezone
        resources: dict (optional)
            Resources
        emails: list (optional)
            Emails
        status_list: list (optional)
            Status list

        Returns
        -------
        dict
            Either the same dict as create_job, or the one returned by
            concatenation of upgrade_job and edit_job
        """

        job_list = self.saagie_api.jobs.list_for_project_minimal(project_id)["jobs"]

        # If the job already exists, upgrade it
        if job_name in [job["name"] for job in job_list]:
            job_id = next(job["id"] for job in job_list if job["name"] == job_name)

            responses = {
                "addJobVersion": self.upgrade(
                    job_id=job_id,
                    file=file,
                    use_previous_artifact=use_previous_artifact,
                    runtime_version=runtime_version,
                    command_line=command_line,
                    release_note=release_note,
                    extra_technology=extra_technology,
                    extra_technology_version=extra_technology_version,
                )["data"]["addJobVersion"]
            }

            responses["editJob"] = self.edit(
                job_id=job_id,
                job_name=job_name,
                description=description,
                is_scheduled=is_scheduled,
                cron_scheduling=cron_scheduling,
                schedule_timezone=schedule_timezone,
                resources=resources,
                emails=emails,
                status_list=status_list,
            )["editJob"]

            return responses

        # If the job does not exist, create it
        args = {
            k: v
            for k, v in {
                "job_name": job_name,
                "project_id": project_id,
                "file": file,
                "description": description,
                "category": category,
                "technology": technology,
                "technology_catalog": technology_catalog,
                "runtime_version": runtime_version,
                "command_line": command_line,
                "release_note": release_note,
                "extra_technology": extra_technology,
                "extra_technology_version": extra_technology_version,
                "cron_scheduling": cron_scheduling,
                "schedule_timezone": schedule_timezone,
                "resources": resources,
                "emails": emails,
                "status_list": status_list,
            }.items()
            if v is not None  # Remove None values from the dict
        }

        return self.create(**args)

    def rollback(self, job_id: str, version_number: str):
        """Rollback a given job to the given version

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        version_number : str
            Number of the version to rollback

        Returns
        -------
        dict
            Dict of rollback job

        """
        result = self.saagie_api.client.execute(
            query=gql(GQL_ROLLBACK_JOB_VERSION), variable_values={"jobId": job_id, "versionNumber": version_number}
        )
        logging.info("✅ Job [%s] successfully rollbacked to version [%s]", job_id, version_number)
        return result

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

        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB), variable_values={"jobId": job_id})
        logging.info("✅ Job [%s] successfully deleted", job_id)
        return result

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

        result = self.saagie_api.client.execute(query=gql(GQL_RUN_JOB), variable_values={"jobId": job_id})
        logging.info("✅ Job [%s] successfully launched", job_id)
        return result

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
        job_instance_info = self.get_instance(job_instance_id, pprint_result=False)
        state = job_instance_info.get("jobInstance").get("status")
        sec = 0
        if timeout == -1:
            timeout = float("inf")

        logging.info("⏳ Job id %s with instance %s has just been requested", job_id, job_instance_id)
        while state not in final_status_list:
            with console.status(f"Job is currently {state}", refresh_per_second=100):
                if sec >= timeout:
                    raise TimeoutError(f"❌ Last state known : {state}")
                time.sleep(freq)
                sec += freq
                job_instance_info = self.get_instance(job_instance_id, pprint_result=False)
                state = job_instance_info.get("jobInstance").get("status")
        if state == "SUCCEEDED":
            logging.info("✅ Job id %s with instance %s has the status %s", job_id, job_instance_id, state)
        elif state in ("FAILED", "KILLED"):
            logging.error("❌ Job id %s with instance %s has the status %s", job_id, job_instance_id, state)
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

        result = self.saagie_api.client.execute(
            query=gql(GQL_STOP_JOB_INSTANCE), variable_values={"jobInstanceId": job_instance_id}
        )
        logging.info("✅ Job instance [%s] successfully stopped", job_instance_id)
        return result

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
            file_info = Path(file)
            os.chdir(file_info.parent)
            file = Path(file_info.name)
            with file.open(mode="rb") as file_content:
                params["file"] = file_content
                try:
                    req = self.saagie_api.client.execute(
                        query=gql(payload_str), variable_values=params, upload_files=True
                    )
                    res = {"data": req}
                except Exception as exception:
                    logging.error("Something went wrong %s", exception)
                    raise exception
                return res
        else:
            try:
                return {"data": self.saagie_api.client.execute(query=gql(payload_str), variable_values=params)}
            except Exception as exception:
                logging.error("Something went wrong %s", exception)
                raise exception

    def export(
        self,
        job_id: str,
        output_folder: str,
        error_folder: Optional[str] = "",
        versions_limit: Optional[int] = None,
        versions_only_current: bool = False,
    ) -> bool:
        """Export the job in a folder

        Parameters
        ----------
        job_id : str
            Job ID
        output_folder : str
            Path to store the exported job
        error_folder : str, optional
            Path to store the job ID in case of error. If not set, job ID is not write
        versions_limit : int, optional
            Maximum limit of versions to fetch per job. Fetch from most recent
            to the oldest
        versions_only_current : bool, optional
            Whether to only fetch the current version of each job
        Returns
        -------
        bool
            True if job is exported False otherwise
        """
        job_info = None
        output_folder = Path(check_folder_path(output_folder))

        try:
            job_info = self.get_info(
                job_id=job_id,
                instances_limit=1,
                versions_limit=versions_limit,
                versions_only_current=versions_only_current,
            )["job"]
        except Exception as exception:
            logging.error("Something went wrong %s", exception)
            return handle_write_error("Cannot get the information of the job [%s]", job_id, error_folder)

        if not job_info:
            return handle_write_error("Cannot get the information of the job [%s]", job_id, error_folder)

        create_folder(output_folder / job_id)
        repo_name, techno_name = self.saagie_api.get_technology_name_by_id(job_info["technology"]["id"])

        if not repo_name:
            return handle_write_error(
                "Cannot export the job: [%s] because the technology used for this job was deleted",
                job_id,
                error_folder,
            )
        job_info["technology"]["name"] = techno_name
        job_info["technology"]["technology_catalog"] = repo_name
        write_to_json_file(output_folder / job_id / "job.json", job_info)

        for version in [version for version in job_info.get("versions", []) if version["packageInfo"]]:
            local_folder = output_folder / job_id / "version" / str(version["number"])
            create_folder(local_folder)
            req = requests.get(
                remove_slash_folder_path(self.saagie_api.url_saagie) + version["packageInfo"]["downloadUrl"],
                auth=self.saagie_api.auth,
                stream=True,
                timeout=60,
            )
            if req.status_code == 200:
                logging.info("Downloading the version %s of the job", version["number"])
                write_request_response_to_file(local_folder / version["packageInfo"]["name"], req)
            else:
                handle_write_error(
                    f"❌ Cannot download the version [{version['number']}] of the job [%s], \
                        please verify if everything is ok",
                    job_id,
                    error_folder,
                )

        logging.info("✅ Job [%s] successfully exported", job_id)
        return True

    def import_from_json(
        self,
        project_id: str,
        path_to_folder: str,
    ) -> bool:
        """Import a job from JSON format

        Parameters
        ----------
        project_id : str
            Project ID to import the job
        path_to_folder : str
            Path to the folder of the job to import
        Returns
        -------
        bool
            True if job is imported False otherwise
        """
        json_file = next(Path(path_to_folder).rglob("job.json"))

        try:
            with json_file.open("r", encoding="utf-8") as file:
                job_info = json.load(file)
        except Exception as exception:
            return handle_log_error(f"Cannot open the JSON file {json_file}", exception)
        try:
            job_name = job_info["name"]

            version = next(version for version in job_info["versions"] if version["isCurrent"])

            if path_to_package := next((json_file.parent / "version" / str(version["number"])).iterdir(), None):
                os.chdir(path_to_package.parent)
                file_name = path_to_package.name
            else:
                file_name = ""

            self.create(
                job_name=job_name,
                project_id=project_id,
                file=file_name,
                description=job_info["description"],
                category=job_info["category"],
                technology=job_info["technology"]["name"],
                technology_catalog=job_info["technology"]["technology_catalog"],
                runtime_version=version["runtimeVersion"],
                command_line=version["commandLine"],
                release_note=version["releaseNote"],
                extra_technology=(version.get("extraTechnology") or {}).get("language", ""),
                extra_technology_version=(version.get("extraTechnology") or {}).get("version", ""),
                cron_scheduling=job_info["cronScheduling"],
                schedule_timezone=job_info["scheduleTimezone"],
                resources=job_info["resources"],
                emails=(job_info.get("alerting") or {}).get("emails", ""),
                status_list=(job_info.get("alerting") or {}).get("statusList", ""),
            )

            logging.info("✅ Job [%s] successfully imported", job_name)
        except Exception as exception:
            return handle_log_error(
                f"❌ Job [{job_name}] has not been successfully imported",
                exception,
            )
        return True

    def delete_instances(self, job_id, job_instances_id):
        """Delete given job's instances
        NB: You can only delete an instance not associated to a pipeline instance
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        job_instances_id : [str]
            List of UUID of instances to delete (see README on how to find it)

        Returns
        -------
        dict
            Dict of deleted instances

        """
        params = {"jobId": job_id, "jobInstancesId": job_instances_id}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB_INSTANCE), variable_values=params)
        logging.info("✅ Instances of job [%s] successfully deleted", job_id)
        return result

    def delete_instances_by_selector(
        self, job_id, selector, exclude_instances_id: List = None, include_instances_id: List = None
    ):
        """Delete given job's instances by selector
        NB: You can only delete an instance not associated to a pipeline instance.
        Also you can only delete instances if they aren't processing by the orchestrator

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        selector : str
            Name of status to select in this list : ALL, SUCCEEDED, FAILED, STOPPED, UNKNOWN
        exclude_instances_id : [str]
            List of UUID of instances of your job to exclude from the deletion
        include_instances_id: [str]
            List of UUID of instances of your job to include from the deletion

        Returns
        -------
        int
            Return the number of instances deleted

        """
        params = {
            "jobId": job_id,
            "selector": selector,
            "minusInstancesId": [] if exclude_instances_id is None else exclude_instances_id,
            "moreInstancesId": [] if include_instances_id is None else include_instances_id,
        }
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB_INSTANCES_BY_SELECTOR), variable_values=params)
        logging.info("✅ Instances of job [%s] successfully deleted", job_id)
        return result

    def delete_versions(self, job_id, versions):
        """Delete given job's versions
        NB: You can only delete a version not associated to a pipeline instance

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)
        versions : [str]
            List of version numbers to delete

        Returns
        -------
        dict
            Dict of deleted versions

        """
        params = {"jobId": job_id, "jobVersionsNumber": versions}
        result = self.saagie_api.client.execute(query=gql(GQL_DELETE_JOB_VERSION), variable_values=params)
        logging.info("✅ Versions of job [%s] successfully deleted", job_id)
        return result

    def duplicate(self, job_id):
        """Duplicate a given job

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of duplicate job
        """
        result = self.saagie_api.client.execute(query=gql(GQL_DUPLICATE_JOB), variable_values={"jobId": job_id})
        logging.info("✅ Job [%s] successfully duplicated", job_id)
        return result

    def count_instances_by_status(self, job_id):
        """Count job instances by status

        Parameters
        ----------
        job_id : str
            UUID of your job (see README on how to find it)

        Returns
        -------
        dict
            Dict of job instances number by status
        """
        return self.saagie_api.client.execute(
            query=gql(GQL_COUNT_INSTANCES_BY_SELECTOR), variable_values={"jobId": job_id}
        )
