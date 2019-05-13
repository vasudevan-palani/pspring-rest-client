import requests

from requests.exceptions import HTTPError

from pspring import *

import logging
import json
import inspect

logger = logging.getLogger("pspring-rest-client")

class PayloadException(Exception):
    def __init__(self,*args):
        super().__init__(*args)
        self.response = args[2]
        self.statusCode = args[1]

class Mapping():
    def __init__(self,*args,**kargs):
        self.method = kargs.get("method")
        self.url = kargs.get("url")
        self.data = kargs.get("data")

    def __call__(self,funcObj):
        def newFunc(*args,**kargs):
            argspec = inspect.getfullargspec(funcObj)
            argumentNames = argspec[0]
            for i in range(len(argumentNames)):
                self.url = self.url.replace("{"+argumentNames[i]+"}",str(args[i]))

            for (kargKey,kargVal) in kargs.items():
                self.url = self.url.replace("{"+kargKey+"}",str(kargVal))

            selfObj = args[0]
            kargs.update({
                "url" : selfObj.getUrl()+self.url
            })
            kargs.update({
                "method" : self.method
            })

            if self.data != None:
                kargs.update({
                    "data" : self.data
                })

            funcObj(*args,**kargs)
            return selfObj.send(**kargs)
        return newFunc


class RestClient():
    def __init__(self,*args,**kargs):
        self.url = kargs.get("url")
        self.responsemapper = kargs.get("responsemapper")

    def __call__(self,classObj):
        def constructor(*args,**kargs):
            selfOrig = args[0]
            selfOrig.headers = {}
            selfOrig.url = self.url

        def addHeader(selfOrig,name,value):
            selfOrig.headers.update({name:value})

        def send(*args,**kargs):
            selfOrig = args[0]
            selfOrig.finalize()

            logger.info({
                "message" : "request details",
                "method" : kargs.get("method"),
                "url" : kargs.get("url"),
                "data" : kargs.get("data"),
                "proxies" : kargs.get("proxies"),
                "headers" : selfOrig.headers
            })

            kargs["headers"] = selfOrig.headers


            try:
                response = requests.request(**kargs)

                finalresponse = {}
                
                response.raise_for_status()

                if "json" in response.headers.get("Content-Type"):
                    responseJson = response.json()
                    if self.responsemapper != None:
                        responseJson = self.responsemapper.map(response.json())
                    
                    finalresponse = {
                        "body":responseJson,
                        "headers" : response.headers
                    }
                
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
                    "proxies" : kargs.get("proxies"),
                    "headers" : selfOrig.headers,
                    "status_code" : response.status_code,
                    "responseHeaders" : json.loads(str(response.headers).replace("'","\"")),
                    "response" : response.json(),
                    "elapsed" : response.elapsed.total_seconds()
                })

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
                    "headers" : selfOrig.headers,
                    "status_code" : response.status_code,
                    "responseHeaders" : response.headers,
                    "response" : response.text,
                    "elapsed" : response.elapsed.total_seconds()
                })
                raise ex



        def getUrl(*args,**kargs):
            selfOrig = args[0]
            return selfOrig.url

        def finalize(*args,**kargs):
            pass

        classObj.__init__ = constructor
        classObj.addHeader = addHeader
        classObj.send = send
        classObj.getUrl = getUrl
        if not hasattr(classObj,"finalize"):
            classObj.finalize = finalize

        return classObj
