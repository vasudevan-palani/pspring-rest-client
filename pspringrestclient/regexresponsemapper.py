from .responsemapper import ResponseMapper
import re

import operator
from functools import reduce


def find(element, json):
    return reduce(operator.getitem, element.split('.'), json)

class RegExResponseMapper(ResponseMapper):
    def __init__(self,maps):
        self.maps = maps

    def map(self,response):
        for regex in self.maps:
            if re.match(regex,str(response)) != None:
                return self.getResponse(self.maps[regex],response)

        return self.getResponse(self.maps[".*"],response)

    def getResponse(self,mapValue,response):
        finalresponse = {}
        for key in mapValue:
            if type(mapValue[key]) == type({}):
                finalresponse[key] = self.getResponse(mapValue[key],response)
            elif mapValue[key].startswith("$"):
                finalresponse[key] = find(mapValue[key].replace("$",""),response)
            else:
                finalresponse[key] = mapValue[key]
        return finalresponse
