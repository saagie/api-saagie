from . import manager
from . import projects

import urllib3

# Disable urllib3 InsecureRequestsWarnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
