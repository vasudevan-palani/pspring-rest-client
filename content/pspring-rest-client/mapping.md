<a name="pspringrestclient.mapping"></a>
# pspringrestclient.mapping

Pspring Mapping decorator

<a name="pspringrestclient.mapping.Mapping"></a>
## Mapping Objects

```python
class Mapping()
```

A decorator for methods inside a class that is decorated by RestClient. When this decorator is applied to a method, turns that method to
send a http request based on the arguments

**Example**:

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

