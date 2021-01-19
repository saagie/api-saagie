import requests


def authenticate(realm, url, login, password):
    """
    Retrieve a Bearer connection token
    :param realm: platform url prefix (eg: saagie)
    :param url: platform URL (eg: https://saagie-workspace.prod.saagie.io)
    :param login: username to login with
    :param password: password to login with
    :return: a token
    """
    s = requests.session()
    s.headers["Content-Type"] = "application/json"
    s.headers["Saagie-Realm"] = realm
    r = s.post(url + '/authentication/api/open/authenticate',
               json={'login': login, 'password': password},
               verify=False)
    return r.text


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, realm, url, platform, login, password):
        self.token = authenticate(realm, url, login, password)
        self.platform = platform
        self.url = url

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r
