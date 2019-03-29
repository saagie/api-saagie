import requests
import random
import json
import sys


class querySaagieApi:
    def __init__(self, url_saagie, id_plateform, user, password):
        """
        Exemple d'URL: https://saagie-manager.prod.saagie.io/api/doc
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

    def __upload_file(self, file):
        """

        :param code:
        :return:
        """

        if str(file).endswith('.py'):
            my_code = open(file, 'rt').read()
        else:
            print("This file extension is not supported at the moment. Contact augustin.peyridieux@saagie.com "
                  "to add it to the roadmap")
            return -1

        random_13dig = random.randint(1000000000000, 9999999999999)
        payload = "-----------------------------" + str(random_13dig) + '\n' + \
                  "Content-Disposition: form-data; name=\"file\"; filename=\"" + str(file) + "\" \n" + \
                  "Content-Type: text/plain\n" + \
                  "\n" + \
                  str(my_code) + "\n" +\
                  "-----------------------------" + str(random_13dig) + "--"

        headers = {
            #  Content-Type: multipart/form-data; boundary=---------------------------222042934130865
            'Content-Type': 'multipart/form-data; boundary=---------------------------' + str(random_13dig)
        }

        r = requests.post(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + "/job/upload",
                      data=payload,
                      headers=headers,
                      auth=self.auth,
                      verify=False)
        return r

    def create_job(self, job_name, file, capsule_code='python', category='processing',
                   template="python {file} arg1 arg2", language_version='3.5.2', cpu=0.3,
                   memory=512, disk=512):
        """

        :param job_name:
        :param file:
        :param cpu:
        :param memory:
        :param disk:
        :return:
        """
        """
        {"platform_id":"9","capsule_code":"python","category":"processing","current":{"options":{"language_version":"3.5.2"},
        "releaseNote":"","template":"python {file} arg1 arg2","cpu":0.3,"memory":512,"disk":512,"file":"5c765d9739b05/test.py",
        "isInternalSubDomain":false,"isInternalPort":false},"always_email":false,"manual":true,"retry":"",
        "schedule":"R0/2019-02-27T09:51:11.607Z/P0Y0M1DT0H0M0S","name":"testtt"}
        """

        response = self.__upload_file(file)

        if response == -1:
            return -1
        else:
            fileName = json.loads(response.text)['fileName']

        print("#################################################")
        print(fileName)
        print("#################################################")

        current = {
                    "options": {"language_version": str(language_version)},
                    "releaseNote": "",
                    "template": str(template),
                    "memory": str(memory),
                    "cpu": str(cpu),
                    "disk": str(disk),
                    "file": str(fileName),
                    "isInternalSubDomain": "false",
                    "isInternalPort": "false"
                }


        headers = {
            'platform_id': str(self.id_plateform),
            "capsule_code": str(capsule_code),
            "category": str(category),
            "current": str(current),
            "always_email": "false",
            "manual": "true",
            "retry": "",
            "schedule": "R0/2019-02-27T09:51:11.607Z/P0Y0M1DT0H0M0S",
            "name": str(job_name)
        }

        print("#################################################")
        print(headers)

        """
        r = requests.post(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + "/job/upload",
                      data=payload,
                      headers=headers,
                      auth=self.auth,
                      verify=False)

        """
        r = requests.post(self.url_saagie + self.suffix_api + 'platform/' + str(self.id_plateform) + "/job",
                          headers=headers,
                          auth=self.auth,
                          verify=False
                          )

        return r
