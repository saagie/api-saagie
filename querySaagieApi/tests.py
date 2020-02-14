import querySaagieApi as qsa
import os

my_api_saagie = qsa.QuerySaagieApi(url_saagie='https://saagie-beta.prod.saagie.io/manager/'
                   , id_plateform=6
                   , user='augustin.peyridieux'
                   , password=os.environ['PWD_SAAGIE'])


list_jobs = [22320, 22321, 22322, 22323, 22324]

print(my_api_saagie.create_pipeline(list_jobs).status_code)