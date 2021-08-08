""" Pspring Rest Client module provides an easy interface and decorators to turn any class into a http client
"""
import logging
import json
import inspect
import requests

from requests.exceptions import HTTPError

from pspring import *


logger = logging.getLogger("pspring-rest-client")

class PayloadException(Exception):
    """[summary]

    Args:
        Exception ([type]): [description]
    """
    def __init__(self,*args):
        super().__init__(*args)
        self.response = args[2]
        self.statusCode = args[1]

class RestClient():
    """ RestClient is a class decorator that adds below capabilities to the class
    
        * Adds a method called add_header with which we can add headers to the http request
        * Adds a method called add_middleware, this method will allow hooks to modify the http request and response before it is returned
        * Adds a method called send, which will trigger the http request
        * Adds a method called finalize, which will be a pre-hook before http request is sent
        * Adds a method called getUrl which retuns the current url
    """
    middlewares = []
    def __init__(self,*args,**kargs):
        self.url = kargs.get("url")
        self.headers = kargs.get("headers",{})
        self.middlewares = kargs.get("middlewares",[])
        self.timeout = kargs.get("timeout")
        self.responsemapper = kargs.get("responsemapper")

    def __getattribute__(self, name):
        """
        Called for every attribute access in this class.
        Allows callback functions to be passed as values for instance variables by replacing the instance variable
        access functionality with an additional check for whether the instance variable is a callback, calling it and
        returning its result if it is.
        """
        attribute_value = object.__getattribute__(self, name)  # Existing behavior
        if name not in type(self).__dict__.keys() and callable(attribute_value):  # First condition ensures that class methods are never called here.
            return attribute_value()
        else:
            return attribute_value
            
    def __call__(self,class_obj):
        prev_init = class_obj.__init__

        def constructor(*args,**kargs):

            self_orig = args[0]
            def middleware(*args,**kargs):
                index = args[0] if len(args) == 1 else None
                def newfunc(func_obj):
                    self_orig.add_middleware(func_obj,index)
                    return func_obj
                return newfunc
            self_orig.headers = self.headers
            self_orig.url = self.url
            self_orig.middleware = middleware
            if(hasattr(self_orig,"middlewares") and self_orig.middlewares is not None):
                self_orig.middlewares = self_orig.middlewares + RestClient.middlewares+ self.middlewares
            else:
                self_orig.middlewares = RestClient.middlewares+ self.middlewares
            prev_init(*args,**kargs)

        def add_middleware(self_orig,func_obj,index=None):
            if index is not None:
                self_orig.middlewares.insert(index,func_obj)
            else:
                self_orig.middlewares.append(func_obj)

        def addHeader(self_orig,name,value):
            self_orig.headers.update({name:value})

        def clearHeader(self_orig):
            self_orig.headers = {}

        def send(*args,**kargs):
            self_orig = args[0]
            additional_args = self_orig.finalize()

            if isinstance(additional_args,dict):
                kargs.update(additional_args)

            if kargs.get("timeout") == None and self.timeout != None:
                kargs["timeout"] = float(self.timeout)

            kargs["headers"] = self_orig.headers

            for middleware in self_orig.middlewares:
                middleware(kargs,None)
            
            logger.info({
                "message" : "request details",
                "timeout" : kargs.get("timeout"),
                "method" : kargs.get("method"),
                "url" : kargs.get("url"),
                "data" : kargs.get("data"),
                "json" : kargs.get("json"),
                "proxies" : kargs.get("proxies"),
                "headers" : self_orig.headers
            })
            try:
                response = requests.request(**kargs)

                finalresponse = {}
                response.raise_for_status()

                if "json" in response.headers.get("Content-Type",""):
                    response_json = {}
                    if response.status_code != 204:
                        response_json = response.json()

                    if self.responsemapper != None:
                        response_json = self.responsemapper.map(response_json)
                    
                    finalresponse = {
                        "body":response_json,
                        "headers" : response.headers
                    }

                    logger.info({
                        "message" : "response details",
                        "method" : kargs.get("method"),
                        "url" : kargs.get("url"),
                        "data" : kargs.get("data"),
                        "json" : kargs.get("json"),
                        "proxies" : kargs.get("proxies"),
                        "headers" : self_orig.headers,
                        "status_code" : response.status_code,
                        "responseHeaders" : str(response.headers),
                        "response" : response_json,
                        "elapsed" : response.elapsed.total_seconds()
                    })
                
                else:
                    
                    finalresponse = {
                        "body":response.text,
                        "headers" : response.headers
                    }

                    logger.info({
                        "message" : "response details",
                        "method" : kargs.get("method"),
                        "url" : kargs.get("url"),
                        "data" : kargs.get("data"),
                        "json" : kargs.get("json"),
                        "proxies" : kargs.get("proxies"),
                        "headers" : self_orig.headers,
                        "status_code" : response.status_code,
                        "responseHeaders" : str(response.headers),
                        "response" : response.text,
                        "elapsed" : response.elapsed.total_seconds()
                    })

                for middleware in reversed(self_orig.middlewares):
                    middleware(kargs,finalresponse)
                return finalresponse
            except HTTPError as ex:
                logger.error({
                    "message" : str(ex)
                })
                logger.info({
                    "message" : "response details",
                    "method" : kargs.get("method"),
                    "url" : kargs.get("url"),
                    "data" : kargs.get("data"),
                    "proxies" : kargs.get("proxies"),
                    "headers" : self_orig.headers,
                    "status_code" : response.status_code,
                    "responseHeaders" : response.headers,
                    "response" : response.text,
                    "elapsed" : response.elapsed.total_seconds()
                })

                if hasattr(self_orig,"get_error_code"):
                    try:
                        if "json" in response.headers.get("Content-Type",""):
                            error_code = self_orig.get_error_code(ex.response.json())
                            ex.code = error_code
                    except Exception as excep_code:
                        excep_code_str = str(excep_code)
                        logger.error({
                            "message" : f"Exception while retrieving error code : {excep_code_str}"
                        })
                raise ex



        def getUrl(*args,**kargs):
            self_orig = args[0]
            return self_orig.url

        def finalize(*args,**kargs):
            pass

        class_obj.__init__ = constructor
        class_obj.addHeader = addHeader
        class_obj.clearHeader = clearHeader
        class_obj.add_middleware = add_middleware
        class_obj.send = send
        class_obj.getUrl = getUrl
        if not hasattr(class_obj,"finalize"):
            class_obj.finalize = finalize

        return class_obj
