import querySaagieApi

my_api = querySaagieApi.querySaagieApi(url_saagie="https://saagie-manager.prod.saagie.io", id_plateform="6", user="augustin.peyridieux", password="A3y6p#%klGV4")

r = my_api.create_job("test_api_ap.py", "file.py")
print(r.status_code)
print(r.text)