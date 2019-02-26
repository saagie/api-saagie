import requests

url = "https://vallourec-manager.a4.saagie.io/api/v1/platform/9/envvars"

payload = "{\"name\":\"MY_VAR\",\"value\":\"vamue_var\",\"isPassword\":false,\"platformId\":\"9\"}"
headers = {
    'accept': "application/json, text/plain, */*",
    'origin': "https://vallourec-manager.a4.saagie.io",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
    'content-type': "application/json;charset=UTF-8",
    'cache-control': "no-cache",
    'postman-token': "42ca899b-4775-56a5-42a0-1095179f26fe"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)