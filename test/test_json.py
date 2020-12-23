import sys
sys.path.append("./deps")
sys.path.append(".")
import os

os.environ["pspring.aws.secretsMngr.secretName"] = "sales-ctp-prod"
os.environ["pspring.soo.security.cacheTable"] = "dev-token-cache"

from pspring import *

import logging
import logging.config
from pythoncloudlogger import *
from loggingconfig import config as filelogconfig
logging.config.dictConfig(filelogconfig)
from pspringrestclient import *


def test_json_content():
    @RestClient(url="https://reqres.in")
    class Test():
        @Mapping(url="/api/users?page=2",method="GET")
        def get_users(self,*args,**kargs):
            pass
    logger.info("Test here")    
    def timestamp_middleware(request,response):
        if response is None:
            headers = request.get("headers")
            headers.update({
                "timestamp1" : "121342423423"
            })
            logger.info({
                "message":"in timestamp middleware",
                "request":request
            })
        else:
            logger.info({
                "message":"in timestamp middleware",
                "response":response
            })
    RestClient.middlewares.append(timestamp_middleware)

    testClient = Test()
    response = testClient.get_users()
    logger.info(response)
    assert response.get("body",None) != None