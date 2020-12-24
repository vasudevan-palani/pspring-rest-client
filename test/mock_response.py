""" Mock response for requests library
"""
from datetime import datetime, timedelta
import json
from  requests.exceptions import HTTPError
class MockResponse():
    """ Emulates the response stucture returned by the requests library
    """
    def __init__(self,**kargs):
        self.headers = {"Content-Type":"application/json"}
        self.text = "{\"message\":\"Hello from the other side\"}"
        self.status_code=200
        self.kargs = kargs
        self.elapsed=timedelta(seconds=57)

        if kargs.get("content_type") == "xml":
            self.text = "<xml><message>Hello from the other side</message></xml>"
            self.headers = {"Content-Type":"text/xml"}
    
    def raise_for_status(self):
        """ emulates raise_for_status in requests.Response
        """
        if self.kargs.get("error_code") is not None:
            self.status_code = self.kargs.get("error_code")
            raise HTTPError()

    def json(self):
        """ Exports the response text to json
        """
        return json.loads(self.text)