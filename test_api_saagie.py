import query_saagie_api

my_api_saagie = query_saagie_api.query_sagie_api(url_saagie='https://vallourec-manager.a4.saagie.io/',
                                                 id_plateform=9,
                                                 user='augustin.peyridieux',
                                                 password='5Wn#v1*pgBYT')

#print(my_api_saagie.get_plateform_env_vars().text)

print(query_saagie_api.get_plateforms_info())

r = my_api_saagie.upload_file('test.py')
r.json()
print(r)
print(r.text)

"""
import requests

url = "https://vallourec-manager.a4.saagie.io/api/v1/platform/9/envvars"

querystring = {"name":"test_name","value":"my_value","isPassword":"false","platformId":"9"}

payload = ""
headers = {
    'Authorization': "Basic YXVndXN0aW4ucGV5cmlkaWV1eDo1V24jdjEqcGdCWVQ=",
    'cache-control': "no-cache",
    'Postman-Token': "9ca85edc-2be5-4409-883c-d816d99e68e8"
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

print(response)
print(response.text)
"""

