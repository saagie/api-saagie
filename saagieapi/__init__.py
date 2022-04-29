import logging

import urllib3

from .pipelines import *
from .saagie_api import SaagieApi

# Disable urllib3 InsecureRequestsWarnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = ["SaagieApi", "Node", "JobNode", "ConditionNode", "GraphPipeline"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARN)
logging.getLogger("gql").setLevel(logging.WARN)
