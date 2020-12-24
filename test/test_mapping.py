import sys
sys.path.append("./deps")
sys.path.append(".")
import os
os.environ["pspring.aws.secretsMngr.secretName"] = "sales-ctp-prod"
os.environ["pspring.soo.security.cacheTable"] = "dev-token-cache"

from pspring import *
from unittest import mock
import logging
import logging.config
from pythoncloudlogger import *
from loggingconfig import config as filelogconfig
logging.config.dictConfig(filelogconfig)
logger = logging.getLogger(__name__)
import requests
from pspringrestclient import RestClient,Mapping

from mock_response import MockResponse

def test_mapping_url_method():
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            @Mapping(url="/api/users?page=2",method="GET")
            def get_users(self,*args,**kargs):
                pass

        test_client = Test()
        response = test_client.get_users()
        assert response.get("body").get("message") == "Hello from the other side"

def test_mapping_dynamic_url():
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            @Mapping(url="/api/users?page={page_number}",method="GET")
            def get_users(self,page_number,*args,**kargs):
                self._url = kargs.get("url")
        
        test_client = Test()
        response = test_client.get_users(1)
        assert test_client._url == "https://reqres.in/api/users?page=1"

def test_mapping_post_json():
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            @Mapping(url="/api/users",method="POST")
            def create_user(self,*args,**kargs):
                self.json = {"message":"hi"}
        
        test_client = Test()
        response = test_client.create_user(1)
        assert response.get("body").get("message") == "Hello from the other side"

def test_mapping_post_xml():
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse(content_type="xml")

        @RestClient(url="https://reqres.in")
        class Test():
            @Mapping(url="/api/users",method="POST")
            def create_user(self,*args,**kargs):
                self.data = "<xml><user></user></xml>"
        
        test_client = Test()
        test_client.addHeader("Content-Type","text/xml")
        response = test_client.create_user(1)
        assert response.get("body") == "<xml><message>Hello from the other side</message></xml>"

def test_mapping_get():
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

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

def test_mapping_query_string():
    """test query string set manually
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            @Mapping(url="/api/users",method="GET")
            def get_users(self,page_number,*args,**kargs):
                self.queryString = "page=4"
        
        test_client = Test()
        def send_decorator(func_obj):
            def new_send(*args,**kargs):
                self = test_client
                self.kargs = kargs
                func_obj(*args,**kargs)
            return new_send
        test_client.send = send_decorator(test_client.send)
        response = test_client.get_users(1)
        assert test_client.kargs.get("url") == "https://reqres.in/api/users?page=4"