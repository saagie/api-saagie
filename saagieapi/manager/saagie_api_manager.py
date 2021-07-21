"""
Saagie API object to interact with Saagie API in Python (API for Manager - to
interact with the Projects & Jobs API, see the projects subpackage)

"""
import requests
import json
import time


class SaagieApiManager:
    def __init__(self, url_saagie, id_plateform, user, password):
        """Initialize the class
        Doc Saagie URL example: https://saagie-manager.prod.saagie.io/api/doc

        Parameters
        ----------
        url_saagie : str
            platform URL (eg: https://saagie-manager.prod.saagie.io)
        id_plateform : int
            Platform Id (you can find in the URL when you are on your own
        user : str
            username to login with
        password : str
            password to login with
        """
        if not url_saagie.endswith('/'):
            url_saagie += '/'
        self.url_saagie = url_saagie
        self.id_plateform = id_plateform
        self.suffix_api = 'api/v1/'
        self.auth = (user, password)

    def get_plateforms_info(self):
        """Getting information on all installed platform
        (eg: id, datamart IP, datamart Port, Datalake IP etc.)

        Returns
        -------
        requests.models.Response
            the platforms informations
        """
        return requests.get(
            self.url_saagie + self.suffix_api + 'platform',
            auth=self.auth,
            verify=False
        )

    def get_plateform_info(self):
        """Getting information on a platform
        (eg: id, datamart IP, datamart Port, Datalake IP etc.)

        Returns
        -------
        requests.models.Response
            platform informations
        """
        print(self.url_saagie + self.suffix_api + 'platform/'
              + str(self.id_plateform))
        return requests.get(self.url_saagie + self.suffix_api + 'platform/'
                            + str(self.id_plateform),
                            auth=self.auth,
                            verify=False)

    def get_impala_connection_info(self):
        """Getting information on a platform
        (eg: id, datamart IP, datamart Port, Datalake IP etc.)

        Returns
        -------
        requests.models.Response
            platform informations
        """
        return requests.get(
            self.url_saagie + self.suffix_api + 'platform/'
            + str(self.id_plateform) + '/connectioninfo/impala',
            auth=self.auth,
            verify=False)

    def get_plateform_env_vars(self):
        """Getting all environment variables available on the platform

        Returns
        -------
        requests.models.Response
            platform environment variables
        """
        return requests.get(self.url_saagie + self.suffix_api + 'platform/'
                            + str(self.id_plateform) + '/envvars',
                            auth=self.auth,
                            verify=False)

    def create_plateform_env_vars(self, name_envvar, value_envvar,
                                  is_password=False):
        """Create an environment variable

        Parameters
        ----------
        name_envvar : str
            name of the environment variable
        value_envvar : str
            parameter of the environment variable
        is_password : bool, optional
            is the variable a password, by default False

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        if is_password:
            the_password = 'true'
        else:
            the_password = 'false'

        payload = "{\"name\":\"" + str(name_envvar).upper() + '"' + \
                  ",\"value\":\"" + str(value_envvar) + '"' + \
                  ",\"isPassword\":" + the_password + \
                  ",\"platformId\":\"" + str(self.id_plateform) + '"}'

        return requests.post(self.url_saagie + self.suffix_api + 'platform/'
                             + str(self.id_plateform) + '/envvars',
                             data=payload,
                             auth=self.auth,
                             verify=False)

    def delete_plateform_env_vars(self, id_venv):
        """Delete an environement variable environment variable

        Parameters
        ----------
        id_venv : int
            id of the environment variable

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.delete(self.url_saagie + self.suffix_api + 'platform/'
                               + str(self.id_plateform) + '/envvars/'
                               + str(id_venv),
                               auth=self.auth,
                               verify=False)

    def run_job(self, job_id):
        """Run a job

        Parameters
        ----------
        job_id : int
            The id of the job

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.post(self.url_saagie + self.suffix_api + 'platform/'
                             + str(self.id_plateform) + '/job/'
                             + str(job_id) + '/run',
                             auth=self.auth,
                             verify=False)

    def stop_job(self, job_id):
        """Stop a job

        Parameters
        ----------
        job_id : int
            The id of the job

        Returns
        -------
        requests.models.Response
            The result of the query
        """
        return requests.post(self.url_saagie + self.suffix_api + 'platform/'
                             + str(self.id_plateform) + '/job/'
                             + str(job_id) + '/stop',
                             auth=self.auth,
                             verify=False)

    def get_all_jobs(self):
        """Get all the jobs on the platform

        Returns
        -------
         requests.models.Response
            The result of the query
        """
        return requests.get(self.url_saagie + self.suffix_api + 'platform/'
                            + str(self.id_plateform) + '/job',
                            auth=self.auth,
                            verify=False)

    def get_job_detail(self, job_id):
        """Get the status of a job

        Parameters
        ----------
        job_id : int
            The id of the job

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.get(self.url_saagie + self.suffix_api + 'platform/'
                            + str(self.id_plateform) + '/job/' + str(job_id),
                            auth=self.auth,
                            verify=False)

    def modify_job_schedule(self, job_id, job):
        """Modify the schedule of the job. Need to send all the job object to proceed

        Parameters
        ----------
        job_id : int
            The job id
        job : Object
            param job (get it with method get_job_detail)

        Returns
        -------
        requests.models.Response
            The result of the query
        """
        return requests.post(self.url_saagie + self.suffix_api + 'platform/'
                             + str(self.id_plateform) + '/job/' + str(job_id),
                             data=json.dumps(job),
                             auth=self.auth,
                             verify=False)

    def run_job_callback(self, job_id, freq, timeout=-1):
        """Run a job and wait for the final status (KILLED, FAILED or SUCCESS)

        Parameters
        ----------
        job_id : int
            The id of the job to run
        freq : int
            The number of seconds between two state checks
        timeout : int, optional
            The number of seconds before timeout, by default -1

        Returns
        -------
        str
            The final state of the job

        Raises
        ------
        TimeoutError
            Raised if job job execution required more seconds than the value 
            provided by the timeout variable
        """
        self.run_job(job_id)
        state = ''
        sec = 0
        to = False

        while(state != "STOPPED"):
            to = False if timeout == -1 else sec >= timeout
            if to:
                raise TimeoutError("Last state known : " + state)
            time.sleep(freq)
            sec += freq
            res = self.get_job_detail(job_id)
            state = json.loads(res.text)['last_state']['state']
            print('Current state : ' + state)

        return json.loads(res.text)['last_state']['lastTaskStatus']

    def __upload_file(self, file):
        """Private method to upload a file before create a job

        Parameters
        ----------
        file : str
            The file path

        Returns
        -------
        str
            The file path in Saagie

        Raises
        ------
        NameError
            Unexpected error
        """

        response = requests.post(
            self.url_saagie + self.suffix_api + 'platform/' +
            str(self.id_plateform) + "/job/upload",
            auth=self.auth,
            files={'file': open(file, 'rb')},
            verify=False)

        if response == -1:
            raise NameError(
                "An unexpected error occured, please raise a ticket to SAAGIE"
                " to solve the problem")
        else:
            return json.loads(response.text)['fileName']

    def create_job(self, job_name, file="", capsule_code='python',
                   category='processing', template="python {file} arg1 arg2",
                   language_version='3.5.2', cpu=0.3, memory=512, disk=512,
                   extra_language='python', extra_version='3.5.2'):
        """Create a job on Saagie

        Parameters
        ----------
        job_name : str
            The name of the job
        file : str, optional
            The path of the file containing the code.
            Note that this is not required for sqoop jobs, by default ""
        capsule_code : str, optional
            The type of the capsule, by default 'python'
        category : str, optional
            The category of the job, by default 'processing'
        template : str, optional
            The code to launch the job, by default "python {file} arg1 arg2"
        language_version : str, optional
            Version of the language used, by default '3.5.2'
        cpu : float, optional
            Number of CPU(s) to allocate, by default 0.3
        memory : int, optional
            Quantity of memory to allocate (in MB), by default 512
        disk : int, optional
            Quantity of disk space to allocate (in MB), by default 512
        extra_language : str, optional
            The extra language, by default 'python'
        extra_version : str, optional
            The version of the extra language, by default '3.5.2'

        Returns
        -------
        requests.models.Response
            The request response
        """

        if file != "":
            fileName = self.__upload_file(file)

        # if you want to create a spark job, you need to specify
        # the extra language
        if capsule_code == 'spark':
            options = {
                "language_version": str(language_version),
                "extra_language": str(extra_language),
                "extra_version": str(extra_version)
            }
        else:
            options = {
                "language_version": str(language_version)
            }

        # Building data needed in the requests.post method
        current = {
            "options": options,
            "releaseNote": "",
            "template": str(template),
            "memory": str(memory),
            "cpu": str(cpu),
            "disk": str(disk),
            "file": str(file if file == "" else fileName),
            "isInternalSubDomain": False,
            "isInternalPort": False
        }

        data = {
            "platform_id": str(self.id_plateform),
            "capsule_code": str(capsule_code),
            "category": str(category),
            "current": current,
            "always_email": False,
            "manual": True,
            "retry": "",
            "schedule": "R0/2019-02-27T09:51:11.607Z/P0Y0M1DT0H0M0S",
            "name": str(job_name)
        }

        # sending the request
        r = requests.post(self.url_saagie + self.suffix_api + 'platform/'
                          + str(self.id_plateform) + "/job",
                          data=json.dumps(data),
                          auth=self.auth,
                          verify=False
                          )

        return r

    def update_job(self, job_id, file="", capsule_code='python',
                   template="python {file} arg1 arg2", release_note="",
                   language_version='3.5.2', cpu=0.3, memory=512, disk=512,
                   extra_language='python', extra_version='3.5.2'):
        """[summary]

        Parameters
        ----------
        job_name : str
            The name of the job
        file : str, optional
            The path of the file containing the code.
            Note that this is not required for sqoop jobs, by default ""
        capsule_code : str, optional
            The type of the capsule, by default 'python'
        category : str, optional
            The category of the job, by default 'processing'
        template : str, optional
            The code to launch the job, by default "python {file} arg1 arg2"
        language_version : str, optional
            Version of the language used, by default '3.5.2'
        cpu : float, optional
            Number of CPU(s) to allocate, by default 0.3
        memory : int, optional
            Quantity of memory to allocate (in MB), by default 512
        disk : int, optional
            Quantity of disk space to allocate (in MB), by default 512
        extra_language : str, optional
            The extra language, by default 'python'
        extra_version : str, optional
            The version of the extra language, by default '3.5.2'

        Returns
        -------
        requests.models.Response
            The query response
        """

        if file != "":
            fileName = self.__upload_file(file)

        # if you want to create a spark job, you need to specifye the extra
        # language
        if capsule_code == 'spark':
            options = {
                "language_version": str(language_version),
                "extra_language": str(extra_language),
                "extra_version": str(extra_version)
            }
        else:
            options = {
                "language_version": str(language_version)
            }

        # Building data needed in the requests.post method
        current = {
            "options": options,
            "releaseNote": str(release_note),
            "template": str(template),
            "memory": str(memory),
            "cpu": str(cpu),
            "disk": str(disk),
            "file": str(file if file == "" else fileName),
            "isInternalSubDomain": False,
            "isInternalPort": False
        }

        data = {"current": current}

        # sending the request
        r = requests.post(self.url_saagie + self.suffix_api + 'platform/'
                          + str(self.id_plateform) + "/job/" +
                          str(job_id) + "/version",
                          data=json.dumps(data),
                          auth=self.auth,
                          verify=False
                          )

        return r

    def create_pipeline(self, list_id_jobs, pipeline_name):
        """Create a pipeline on Saagie

        Parameters
        ----------
        list_id_jobs : List[int]
            A list of job ids
        pipeline_name : string
            The name of the pipeline

        Returns
        -------
        requests.models.Response
            Tje response of the query
        """
        dict_workflow = {}
        dict_workflow['name'] = pipeline_name
        list_worklfow = []
        position_job_workflow = 0
        for id in list_id_jobs:
            list_worklfow.append(
                {"id": int(id), "position": position_job_workflow})
            position_job_workflow += 1
        dict_workflow['jobs'] = list_worklfow

        r = requests.post(self.url_saagie + self.suffix_api + 'platform/'
                          + str(self.id_plateform) + "/workflow",
                          data=json.dumps(dict_workflow),
                          auth=self.auth,
                          verify=False
                          )
        return r

    def run_pipeline(self, pipeline_id):
        """Run a pipeline

        Parameters
        ----------
        pipeline_id : int
            The id of the pipeline

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.post(self.url_saagie + self.suffix_api + 'platform/'
                             + str(self.id_plateform) + '/workflow/'
                             + str(pipeline_id) + '/run',
                             auth=self.auth,
                             verify=False)

    def delete_job(self, id_job):
        """Delete a job on Saagie

        Parameters
        ----------
        id_job : int
            The ID of the job to delete

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.delete(self.url_saagie + self.suffix_api + 'platform/'
                               + str(self.id_plateform) + '/job/'
                               + str(id_job),
                               auth=self.auth,
                               verify=False)

    def delete_pipeline(self, id_pipeline):
        """Delete a pipeline on Saagie

        Parameters
        ----------
        id_pipeline : int
            The pipeline ID

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.delete(self.url_saagie + self.suffix_api + 'platform/'
                               + str(self.id_plateform) + '/workflow/'
                               + str(id_pipeline),
                               auth=self.auth,
                               verify=False)

    def get_all_pipelines(self):
        """The all the pipeline(s) from Saagie

        Returns
        -------
        requests.models.Response
            The query response
        """
        return requests.get(self.url_saagie + self.suffix_api + 'platform/'
                            + str(self.id_plateform) + '/workflow',
                            auth=self.auth,
                            verify=False)

    def get_pipeline_detail(self, pipeline_id):
        """The the details of a pipeline

        Parameters
        ----------
        pipeline_id : int
            The id of the pipeline

        Returns
        -------
        request.models.Response
            The query response
        """
        return requests.get(self.url_saagie + self.suffix_api + 'platform/'
                            + str(self.id_plateform) +
                            '/workflow/' + str(pipeline_id),
                            auth=self.auth,
                            verify=False)

    def modify_pipeline_schedule(self, pipeline_id, pipeline):
        """Update the schedule of a pipeline

        Parameters
        ----------
        pipeline_id : int
            The pipeline ID
        pipeline : Object
            param pipeline (get it with method get_pipeline_detail)

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.post(self.url_saagie + self.suffix_api + 'platform/'
                             + str(self.id_plateform) +
                             '/workflow/' + str(pipeline_id),
                             data=json.dumps(pipeline),
                             auth=self.auth,
                             verify=False)

    def stop_pipeline(self, pipeline_id):
        """Stop a pipeline

        Parameters
        ----------
        pipeline_id : int
            The id of the pipeline to update

        Returns
        -------
        requests.models.Response
            The response of the query
        """
        return requests.post(self.url_saagie + self.suffix_api + 'platform/'
                             + str(self.id_plateform) + '/workflow/'
                             + str(pipeline_id) + '/stop',
                             auth=self.auth,
                             verify=False)
