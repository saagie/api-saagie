import querySaagieApi as qsa
import os

my_api_saagie = qsa.QuerySaagieApi(url_saagie='https://saagie-beta.prod.saagie.io/manager/'
                   , id_plateform=6
                   , user='login.saagie'
                   , password=os.environ['NAME_ENV_VAR_PWD_SAAGIE'])

print(my_api_saagie.get_plateform_info())