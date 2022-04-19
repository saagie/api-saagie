import logging
import time
import pytz
from pathlib import Path
from croniter import croniter

from gql import gql

from .gql_queries import *


class Jobs:

    def __init__(self, saagie_api):
        self.saagie_api = saagie_api
        self.client = saagie_api.client
        self.valid_status_list = saagie_api.valid_status_list

    def list_for_project(self, project_id, instances_limit=-1):
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
        instances_limit_request = f" (limit: {str(instances_limit)})" if instances_limit != -1 else ""
        query = gql(gql_get_project_jobs.format(project_id, instances_limit_request))
        return self.client.execute(query)

    def get_instance(self, job_instance_id):
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
        query = gql(gql_get_job_instance.format(job_instance_id))
        return self.client.execute(query)

    def get_id(self, job_name, project_name):
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
        jobs = self.saagie_api.jobs.list_for_project(project_id, instances_limit=1)["jobs"]
        job = list(filter(lambda j: j["name"] == job_name, jobs))
        if job:
            return job[0]["id"]
        else:
            raise NameError(f"Job {job_name} does not exist.")

    def get_info(self, job_id):
        """Get job's info

        Parameters
        ----------
        job_id : str
            UUID of your job

        Returns
        -------
        dict
            Dict of job's info

        """
        query = gql_get_info_job.format(job_id)
        return self.client.execute(gql(query))

    def create(self, job_name, project_id, file=None, description='',
               category='Processing', technology='python',
               technology_catalog='Saagie',
               runtime_version='3.6',
               command_line='python {file} arg1 arg2', release_note='',
               extra_technology='', extra_technology_version='',
               cron_scheduling=None, schedule_timezone="UTC", resources=None,
               emails=None, status_list=["FAILED"]):
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
            "projectId": project_id, "name": job_name, "description": description, "category": category,
            "releaseNote": release_note, "runtimeVersion": runtime_version, "commandLine": command_line}

        technologies_for_project = self.saagie_api.projects.get_technologies(project_id)['technologiesByCategory']
        technologies_for_project_and_category = [
            tech['id'] for tech in
            [
                tech['technologies'] for tech in technologies_for_project
                if tech['jobCategory'] == category
            ][0]
        ]
        all_technologies_in_catalog = [
            catalog['technologies'] for catalog in self.saagie_api.get_repositories_info()['repositories']
            if catalog['name'] == technology_catalog
        ]
        if not all_technologies_in_catalog:
            raise RuntimeError(
                f"Catalog {technology_catalog} does not exist or does not contain technologies")

        technology_in_catalog = [tech['id'] for tech in
                                 all_technologies_in_catalog[0]
                                 if tech["label"].lower() == technology.lower()]

        if not technology_in_catalog:
            raise RuntimeError(
                f"Technology {technology} does not exist in the catalog {technology_catalog}")

        if technology_in_catalog[0] not in technologies_for_project_and_category:
            raise RuntimeError(
                f"Technology {technology} does not exist in the target project {project_id} "
                f"for the {category} category "
                f"and for the {technology_catalog} catalog")
        else:
            technology_id = technology_in_catalog[0]
            params["technologyId"] = technology_id

        if extra_technology != '':
            extra_tech = gql_extra_technology.format(extra_technology,
                                                     extra_technology_version)
        else:
            extra_tech = ''

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

        if cron_scheduling:
            params["isScheduled"] = True

            if croniter.is_valid(cron_scheduling):
                params["cronScheduling"] = cron_scheduling
            else:
                raise RuntimeError(f"{cron_scheduling} is not valid cron format")

            if schedule_timezone in list(pytz.all_timezones):
                params["scheduleTimezone"] = schedule_timezone
            else:
                raise RuntimeError("Please specify a correct timezone")

        else:
            params["isScheduled"] = False

        if resources:
            params["resources"] = resources

        payload_str = gql_create_job.format(extra_technology=extra_tech)
        return self.__launch_request(file, payload_str, params)

    def edit(self, job_id, job_name=None, description=None, is_scheduled=None,
             cron_scheduling=None, schedule_timezone="UTC", resources=None,
             emails=None, status_list=["FAILED"]):
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
        params = {"id": job_id}
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
            params["isScheduled"] = previous_job_version["isScheduled"]
            params["cronScheduling"] = previous_job_version["cronScheduling"]
            params["scheduleTimezone"] = previous_job_version["scheduleTimezone"]

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
            previous_alerting = previous_job_version["alerting"]
            if previous_alerting:
                params["alerting"] = {
                    "emails": previous_alerting["emails"],
                    "statusList": previous_alerting["statusList"]
                }

        query = gql(gql_edit_job)
        return self.client.execute(query, variable_values=params)

    def upgrade(self, job_id, file=None, use_previous_artifact=False, runtime_version='3.6',
                command_line='python {file} arg1 arg2', release_note=None,
                extra_technology='', extra_technology_version=''):
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
                f"Available runtimes : {','.join(available_runtimes)}.")

        if file and use_previous_artifact:
            logging.warning(
                "You can not specify a file and use the previous artifact. "
                "By default, the specified file will be used.")

        if extra_technology != '':
            extra_tech = gql_extra_technology.format(extra_technology,
                                                     extra_technology_version)
        else:
            extra_tech = ''
        payload_str = gql_upgrade_job.format(extra_technology=extra_tech)
        params = {"jobId": job_id, "releaseNote": release_note, "runtimeVersion": runtime_version,
                  "commandLine": command_line, "usePreviousArtifact": use_previous_artifact}

        return self.__launch_request(file, payload_str, params)

    def upgrade_by_name(self, job_name, project_name, file=None, use_previous_artifact=False, runtime_version='3.6',
                        command_line='python {file} arg1 arg2', release_note=None,
                        extra_technology='', extra_technology_version=''
                        ):
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
        return self.upgrade(job_id, file, use_previous_artifact, runtime_version, command_line, release_note,
                            extra_technology, extra_technology_version)

    def delete(self, job_id):
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
        query = gql(gql_delete_job.format(job_id))
        return self.client.execute(query)

    def run(self, job_id):
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
        query = gql(gql_run_job.format(job_id))
        return self.client.execute(query)

    def run_with_callback(self, job_id, freq=10, timeout=-1):
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
        query = gql(gql_get_job_instance.format(job_instance_id))
        job_instance_info = self.client.execute(query)
        state = job_instance_info.get("jobInstance").get("status")
        sec = 0
        while state not in final_status_list:
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            job_instance_info = self.client.execute(query)
            state = job_instance_info.get("jobInstance").get("status")
            print('Current state : ' + state)
        return state

    def stop(self, job_instance_id):
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
        query = gql(gql_stop_job_instance.format(job_instance_id))
        return self.client.execute(query)

    def __launch_request(self, file, payload_str, params):
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
            with file.open(mode='rb') as f:
                params["file"] = f
                try:
                    req = self.client.execute(gql(payload_str), variable_values=params, upload_files=True)
                    res = {"data": req}
                except Exception as e:
                    logging.error(f"Something went wrong: {e}")
                    raise e
                return res

        else:
            try:
                req = self.client.execute(gql(payload_str), variable_values=params)
                res = {"data": req}
            except Exception as e:
                logging.error(f"Something went wrong: {e}")
                raise e
            return res
