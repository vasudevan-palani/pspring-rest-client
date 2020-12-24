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

    def __call__(self,func_obj):
        def new_func(*args,**kargs):
            argspec = inspect.getfullargspec(func_obj)
            argument_names = argspec[0]
            url = self.url
            for i in range(len(argument_names)):
                if(len(args) > i ):
                    url = url.replace("{"+argument_names[i]+"}",str(args[i]))

            for (karg_key,karg_val) in kargs.items():
                url = url.replace("{"+karg_key+"}",str(karg_val))

            self_obj = args[0]
            kargs.update({
                "url" : self_obj.getUrl()+url
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

            kargs_to_update = func_obj(*args,**kargs)

            if(kargs != None and kargs_to_update != None):
                kargs.update(kargs_to_update)

            if(hasattr(self_obj,"queryString") and self_obj.queryString != None):
                kargs.update({
                    "url" : kargs.get("url") + "?" + self_obj.queryString
                })

            if (hasattr(self_obj,"proxies") and self_obj.proxies != None):
                kargs.update({
                    "proxies" : self_obj.proxies
                })

            if(hasattr(self_obj,"timeout") and self_obj.timeout != None):
                kargs.update({
                    "timeout" : float(self_obj.timeout)
                })

            if (hasattr(self_obj,"data") and self_obj.data != None):
                kargs.update({
                    "data" : self_obj.data
                })

            if (hasattr(self_obj,"json") and self_obj.json != None):
                kargs.update({
                    "json" : self_obj.json
                })


            return self_obj.send(**kargs)
        return new_func
