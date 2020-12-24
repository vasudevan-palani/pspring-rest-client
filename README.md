# pspring-rest-client

This framework is member of pspring based family of frameworks. It provides a means to create rest clients with minimal code. `requests` library is used internally for http requests.

Annotations / Decorators that come along with this framework are listed below

* `@RestClient(url="")`
  This decorator will add few boiler plate code that is required to interact with any rest endpoint. The methods significant are `send`, `getUrl`, `addHeader`.

  The `send` method would accept all arguments that `requests.request` method would. This method will throw `PayloadException` for all not HTTP 200 responses. The `PayloadException` has `response` and `statusCode` attributes which can be further used for error handling.
  The `addHeader(name,value)` method would add an header
  The `getUrl` will get the url that is configured along with `@RestClient` decorator.
  The `handleError` method is exists on the object will be invoked when received a non http 200 response.

* `@Mapping(method="",url="")`
  This decorator will take care of replacing parameters in the url from arguments passed, send the request and return the response

Useful classes in this framework

`RegExResponseMapper` - this class can be used to tranform one dictionary to another using regex. An example is shown below. The source dictionary fields can be accessed using `$` notation. In the below example `message` is a field inside the `response dictionary.
```python
regexmapper = RegExResponseMapper({
    ".*Customer does not exist.*" :  {
        "statusCode" : "404",
        "code" : "APS-1001",
        "message" : "$response.message"
    },
    ".*" : {
        "statusCode" : "500",
        "code" : "APS-1002",
        "message" : "$response.message"
    }
})

@RestClient(url="https://myapi.com")
class MyRestClient():

  @Mapping(method="GET",url="/user/{firstName}")
  def getCustomer(self,firstName):
    pass

  @Mapping(method="POST",url="/user/",data=json)
  def saveCustomer(self):
    pass

  @Mapping(method="POST",url="/user/")
  def saveCustomer(self,customer):
    self.json=customer

  def handleError(self,response):
        return regexmapper.map(response)
```

Documentation at [pspring-rest-client](https://vasudevan-palani.github.io/pspring-rest-client/)

 To do:

 * To return objects based on the return type from the response received.
