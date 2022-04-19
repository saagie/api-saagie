import urllib3
from .saagie_api import SaagieApi

# Disable urllib3 InsecureRequestsWarnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = ["SaagieApi"]
