import urllib3

# Disable urllib3 InsecureRequestsWarnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from saagie_api import SaagieApi

__all__ = ["SaagieApi"]
