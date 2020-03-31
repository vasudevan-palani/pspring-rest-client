import sys
sys.path.append("./deps")
import os

os.environ["pspring.aws.secretsMngr.secretName"] = "sales-ctp-prod"
os.environ["pspring.soo.security.cacheTable"] = "dev-token-cache"

from pspring import *
from pspringsoosecurity import *
from pspringaws import *
from pspringsoobackend import *

import logging
#logging.basicConfig(level=logging.DEBUG)
from logging import config

logger = logging.getLogger("pspring")

config.fileConfig("./logging.conf")

@EnableWebsec(scope="esp",header="Authorization")
@Backend(url="")
class AccountProfileBackend():

    def getProfileByAccountNumber(self):
        url = self.getUrl().replace("ACCOUNT_NUMBER","")
        response = self.send(url=url,method="GET")
        logger.debug(response)



context.initialize()
backend = AccountProfileBackend()
backend.getProfileByAccountNumber()
