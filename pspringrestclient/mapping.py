""" Pspring Mapping decorator 
"""
import logging
import json
import inspect
import requests

from requests.exceptions import HTTPError

from pspring import *


logger = logging.getLogger("pspring-rest-client")

class Mapping():
    """A decorator for methods inside a class that is decorated by RestClient. When this decorator is applied to a method, turns that method to
        send a http request based on the arguments

        Example:
        ```python
        
        import pspringrestclient

        @RestClient(url="https://myapi.com")
        class TestClient():
            @Mapping(url="/users",method="GET")
            def get_users(self):
                pass

        client = TestClient()
        client.get_users() # will trigger a http GET requedt to https://myapi.com/users

        ```
        The list of features of the mapping decorator are
        * provides easy access to make methods of a class that send http requests
        * kargs that are recognized are, method, url, data, timeout
        * can have dynamic variables in the url which will be evaluated with the function arguments
        * send non json payload in POST
        * set proxies in the request
        * set query string in HTTP request
        * send json payload in POST
    """
    def __init__(self,*args,**kargs):
        self.method = kargs.get("method")
        self.url = kargs.get("url")
        self.data = kargs.get("data")
        self.timeout = kargs.get("timeout")

    def __call__(self,funcObj):
        def newFunc(*args,**kargs):
            argspec = inspect.getfullargspec(funcObj)
            argumentNames = argspec[0]
            url = self.url
            for i in range(len(argumentNames)):
                if(len(args) > i ):
                    url = url.replace("{"+argumentNames[i]+"}",str(args[i]))

            for (kargKey,kargVal) in kargs.items():
                url = url.replace("{"+kargKey+"}",str(kargVal))

            selfObj = args[0]
            kargs.update({
                "url" : selfObj.getUrl()+url
            })
            kargs.update({
                "method" : self.method
            })

            if(self.timeout != None):
                kargs.update({
                    "timeout" : float(self.timeout)
                })

            if self.data != None:
                kargs.update({
                    "data" : self.data
                })

            kargsToUpdate = funcObj(*args,**kargs)

            if(kargs != None and kargsToUpdate != None):
                kargs.update(kargsToUpdate)

            if(hasattr(selfObj,"queryString") and selfObj.queryString != None):
                kargs.update({
                    "url" : kargs.get("url") + "?" + selfObj.queryString
                })

            if (hasattr(selfObj,"proxies") and selfObj.proxies != None):
                kargs.update({
                    "proxies" : selfObj.proxies
                })

            if(hasattr(selfObj,"timeout") and selfObj.timeout != None):
                kargs.update({
                    "timeout" : float(selfObj.timeout)
                })

            if (hasattr(selfObj,"data") and selfObj.data != None):
                kargs.update({
                    "data" : selfObj.data
                })

            if (hasattr(selfObj,"json") and selfObj.json != None):
                kargs.update({
                    "json" : selfObj.json
                })


            return selfObj.send(**kargs)
        return newFunc
