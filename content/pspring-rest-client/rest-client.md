<a name="pspringrestclient.restclient"></a>
# pspringrestclient.restclient

Pspring Rest Client module provides an easy interface and decorators to turn any class into a http client

<a name="pspringrestclient.restclient.PayloadException"></a>
## PayloadException Objects

```python
class PayloadException(Exception)
```

[summary]

**Arguments**:

- `Exception` _[type]_ - [description]

<a name="pspringrestclient.restclient.RestClient"></a>
## RestClient Objects

```python
class RestClient()
```

RestClient is a class decorator that adds below capabilities to the class

* Adds a method called add_header with which we can add headers to the http request
* Adds a method called add_middleware, this method will allow hooks to modify the http request and response before it is returned
* Adds a method called send, which will trigger the http request
* Adds a method called finalize, which will be a pre-hook before http request is sent
* Adds a method called getUrl which retuns the current url

