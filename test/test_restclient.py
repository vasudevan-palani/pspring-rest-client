""" Test suite for RestClient class
"""
import os
import sys
from mock_response import MockResponse
from requests.exceptions import HTTPError
import requests
import logging.config
import logging
from unittest import mock
from loggingconfig import config as filelogconfig

sys.path.append("./deps")
sys.path.append(".")

from pspringrestclient import RestClient, Mapping
from pythoncloudlogger import *
from pspring import *

logging.config.dictConfig(filelogconfig)
logger = logging.getLogger(__name__)


def test_restclient_add_header():
    """Test for addHeader method
    """
    @RestClient(url="https://reqres.in")
    class Test():
        """ Test client
        """
        pass

    test_client = Test()
    test_client.addHeader("key", "value")
    assert test_client.headers.get("key") == "value"


def test_restclient_add_middleware():
    """Test for add_middleware method
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            """ Test client
            """
            pass

        def add_timestamp_middleware(request, response):
            headers = request.get("headers")
            headers["timestamp"] = "12345"
        test_client = Test()
        test_client.add_middleware(add_timestamp_middleware)
        response = test_client.send(url="https://abc.com/users", method="GET")
        assert test_client.headers.get("timestamp") == "12345"

def test_restclient_class_middleware():
    """Test for class level middlewares
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            middlewares=[]
            """ Test client
            """
            pass

        def add_timestamp_middleware(request, response):
            headers = request.get("headers")
            headers["timestamp"] = "12345"

        Test.middlewares.append(add_timestamp_middleware)
        test_client = Test()
        response = test_client.send(url="https://abc.com/users", method="GET")
        assert test_client.headers.get("timestamp") == "12345"


def test_restclient_finalize():
    """Test for finalize method
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            """TestClient
            """
            def finalize(self):
                self.headers["trackingId"] = "3456"

        test_client = Test()
        response = test_client.send(url="https://abc.com/users", method="GET")
        assert test_client.headers.get("trackingId") == "3456"


def test_restclient_json_content_type():
    """Test for json content type
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse()

        @RestClient(url="https://reqres.in")
        class Test():
            """ Test Client
            """
            pass

        test_client = Test()
        response = test_client.send(url="https://abc.com/users", method="GET")
        assert response.get("body").get(
            "message") == "Hello from the other side"


def test_restclient_xml_content_type():
    """Test for xml content type
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse(content_type="xml")

        @RestClient(url="https://reqres.in")
        class Test():
            """ Test client
            """
            pass

        test_client = Test()
        response = test_client.send(url="https://abc.com/users", method="GET")
        assert response.get(
            "body") == "<xml><message>Hello from the other side</message></xml>"


def test_restclient_500_error():
    """Test for 500 error
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse(error_code=500)

        @RestClient(url="https://reqres.in")
        class Test():
            """ Test client
            """
            pass

        test_client = Test()
        exception = False
        try:
            response = test_client.send(
                url="https://abc.com/users", method="GET")
        except HTTPError as e:
            exception = True
        assert exception == True


def test_restclient_geturl():
    """Test for getUrl method
    """
    with mock.patch("requests.request") as mock_get:
        mock_get.return_value = MockResponse(error_code=500)

        @RestClient(url="https://reqres.in")
        class Test():
            """ Test client
            """
            pass

        test_client = Test()
        assert test_client.getUrl() == "https://reqres.in"
