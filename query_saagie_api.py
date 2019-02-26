import requests
import random
import json
import sys


class query_sagie_api:
    def __init__(self, url_saagie, id_plateform, user, password):
        """

        :param url_saagie:
        :param id_plateform:
        :param user:
        :param password:
        """
        if not url_saagie.endswith('/'):
            url_saagie += '/'
        self.url_saagie = url_saagie
        self.id_plateform = id_plateform
        self.suffix_api = 'api/v1/'
        self.auth = (user, password)

    def get_plateforms_info(self):
        """

        :return:
        """
        print(self.url_saagie + self.suffix_api + 'platform')
        return requests.get(self.url_saagie + self.suffix_api + 'platform', auth=self.auth, verify=False)

    def get_plateform_info(self):
        """

        :return:
        """
        print(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform))
        return requests.get(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform)
                            , auth=self.auth
                            , verify=False)

    def get_plateform_env_vars(self):
        """

        :return:
        """
        print(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + '/envvars')
        return requests.get(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform)  + '/envvars'
                            , auth=self.auth
                            , verify=False)

    def create_plateform_env_vars(self, name_envvar, value_envvar, is_password=False):
        """

        :param name_envvar:
        :param value_envvar:
        :return:
        """
        if is_password:
            the_password = 'true'
        else:
            the_password = 'false'

        payload = "{\"name\":\"" + str(name_envvar).upper() + '"' + \
                  ",\"value\":\"" + str(value_envvar) + '"' + \
                  ",\"isPassword\":" + the_password + \
                  ",\"platformId\":\"" + str(self.id_plateform) + '"}'

        return requests.post(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + '/envvars',
                             data=payload,
                             auth=self.auth,
                             verify=False)

    def delete_plateform_env_vars(self, id_venv):
        """

        :param id_venv:
        :return:
        """
        return requests.delete(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + '/envvars/' \
                             + str(id_venv),
                             auth=self.auth,
                             verify=False)

    def run_job(self, job_id):
        """

        :param job_id:
        :return:
        """
        return requests.post(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + '/job/'
                             + str(job_id) + '/run',
                             auth=self.auth,
                             verify=False)

    def upload_file(self, file):
        """

        :param code:
        :return:
        """

        if str(file).endswith('.py'):
            my_code = open(file, 'rt').read()
        else:
            print("This file extension is not supported at the moment. Contact augustin.peyridieux@saagie.com "
                  "to add it to the roadmap")

        random_13dig = random.randint(1000000000000, 9999999999999)
        payload = "-----------------------------" + str(random_13dig) + \
                  "Content-Disposition: form-data; name=\"file\"; filename=\"" + str(file) + "\"\
                Content-Type: text/plain\
                \
                " + str(file) + \
                  "-----------------------------" + str(random_13dig) + "--"

        headers = {
            'Content-Type': 'multipart/form-data; boundary=---------------------------' + str(random_13dig)
        }

        r = requests.post(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + "/job/upload",
                      data=payload,
                      headers=headers,
                      auth=self.auth,
                      verify=False)
        return r

    def create_job(self, job_name, file, cpu=0.3, memory=512, disk=512):
        """

        :param job_name:
        :param file:
        :param cpu:
        :param memory:
        :param disk:
        :return:
        """


        path_to_code = self.upload_file(my_code)
