import requests

from pspring import *

import logging
import json

logger = logging.getLogger("pspring-rest-client")

class Backend():
    def __init__(self,*args,**kargs):
        self.url = kargs.get("url")

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

            response = requests.request(**kargs)

            try:
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
            except Exception as ex:
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

            if response.ok:
                return response.json()
            else:
                raise PayloadException("backend error",response.status_code,response.text)

        def getUrl(*args,**kargs):
            selfOrig = args[0]
            return selfOrig.url

        def finalize(*args,**kargs):
            pass

        classObj.__init__ = constructor
        classObj.addHeader = addHeader
        classObj.send = send
        classObj.getUrl = getUrl
        classObj.finalize = finalize

        return classObj
